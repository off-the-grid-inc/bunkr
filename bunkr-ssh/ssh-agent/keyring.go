// Copyright 2014 The Go Authors. All rights reserved.
// Use of this source code is governed by a BSD-style
// license that can be found in the LICENSE file.

package ssh_agent

import (
	"bytes"
	"crypto/rand"
	"crypto/subtle"
	"errors"
	"fmt"
	"log"
	"sync"
	"time"

	"golang.org/x/crypto/ssh"
	"golang.org/x/crypto/ssh/agent"
)

type Key = agent.Key
type Agent = agent.Agent
type AddedKey = agent.AddedKey
type SignatureFlags = agent.SignatureFlags

var ErrExtensionUnsupported = agent.ErrExtensionUnsupported

const SignatureFlagRsaSha256 = agent.SignatureFlagRsaSha256
const SignatureFlagRsaSha512 = agent.SignatureFlagRsaSha512

type privKey struct {
	signer  ssh.Signer
	comment string
	expire  *time.Time
}

type keyring struct {
	mu   sync.Mutex
	ssha *SSHAgent
	keys map[string]privKey

	locked     bool
	passphrase []byte
}

var errLocked = errors.New("agent: locked")

type BunkrAgent interface {
	Agent
	AddFromBunkr(key BunkrAddedKey) error
}

// NewKeyring returns an Agent that holds keys in memory.  It is safe
// for concurrent use by multiple goroutines.
func NewKeyring(ssha *SSHAgent) BunkrAgent {
	return &keyring{
		ssha: ssha,
		keys: make(map[string]privKey),
	}
}

// RemoveAll removes all identities.
func (r *keyring) RemoveAll() error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if r.locked {
		return errLocked
	}

	r.keys = nil
	return nil
}

// removeLocked does the actual key removal. The caller must already be holding the
// keyring mutex.
func (r *keyring) removeLocked(want []byte) error {
	key := string(want)
	if _, exists := r.keys[key]; exists {
		delete(r.keys, key)
		return nil
	}
	return errors.New("agent: key not found")
}

// Remove removes all identities with the given public key.
func (r *keyring) Remove(key ssh.PublicKey) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if r.locked {
		return errLocked
	}

	return r.removeLocked(key.Marshal())
}

// Lock locks the agent. Sign and Remove will fail, and List will return an empty list.
func (r *keyring) Lock(passphrase []byte) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if r.locked {
		return errLocked
	}

	r.locked = true
	r.passphrase = passphrase
	return nil
}

// Unlock undoes the effect of Lock
func (r *keyring) Unlock(passphrase []byte) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if !r.locked {
		return errors.New("agent: not locked")
	}
	if 1 != subtle.ConstantTimeCompare(passphrase, r.passphrase) {
		return errors.New("agent: incorrect passphrase")
	}

	r.locked = false
	r.passphrase = nil
	return nil
}

// expireKeysLocked removes expired keys from the keyring. If a key was added
// with a lifetimesecs contraint and seconds >= lifetimesecs seconds have
// ellapsed, it is removed. The caller *must* be holding the keyring mutex.
func (r *keyring) expireKeysLocked() {
	for _, k := range r.keys {
		if k.expire != nil && time.Now().After(*k.expire) {
			if err := r.removeLocked(k.signer.PublicKey().Marshal()); err != nil {
				log.Print(err)
			}
		}
	}
}

func (r *keyring) updateList() error {
	if err := r.ssha.loadKeys(); err != nil {
		return errors.New(fmt.Sprintf("agent: error listing keys from Bunkr. %v", err))
	}
	return nil
}

// List returns the identities known to the agent.
func (r *keyring) List() ([]*Key, error) {
	if err := r.updateList(); err != nil {
		return nil, err
	}
	r.mu.Lock()
	defer r.mu.Unlock()

	if r.locked {
		// section 2.7: locked agents return empty.
		return nil, nil
	}
	r.expireKeysLocked()
	var ids []*Key
	for _, k := range r.keys {
		pub := k.signer.PublicKey()
		ids = append(ids, &Key{
			Format:  pub.Type(),
			Blob:    pub.Marshal(),
			Comment: k.comment})
	}
	return ids, nil
}

type BunkrAddedKey struct {
	// PrivateKey must be a *rsa.PrivateKey, *dsa.PrivateKey or
	// *ecdsa.PrivateKey, which will be inserted into the agent.
	Signer ssh.Signer
	// Comment is an optional, free-form string.
	Comment string
	// LifetimeSecs, if not zero, is the number of seconds that the
	// agent will store the key for.
	LifetimeSecs uint32
	// ConfirmBeforeUse, if true, requests that the agent confirm with the
	// user before each use of this key.
	ConfirmBeforeUse bool
}

// Insert adds a private key to the keyring from murmur. If a certificate
// is given, that certificate is added as public key. Note that
// any constraints given are ignored.
func (r *keyring) AddFromBunkr(key BunkrAddedKey) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if r.locked {
		return errLocked
	}

	p := privKey{
		signer:  key.Signer,
		comment: key.Comment,
	}

	if key.LifetimeSecs > 0 {
		t := time.Now().Add(time.Duration(key.LifetimeSecs) * time.Second)
		p.expire = &t
	}
	publicKey := string(key.Signer.PublicKey().Marshal())
	r.keys[publicKey] = p
	return nil
}

// Insert adds a private key to the keyring. If a certificate
// is given, that certificate is added as public key. Note that
// any constraints given are ignored.
func (r *keyring) Add(key AddedKey) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if r.locked {
		return errLocked
	}
	signer, err := ssh.NewSignerFromKey(key.PrivateKey)

	if err != nil {
		return err
	}

	if cert := key.Certificate; cert != nil {
		signer, err = ssh.NewCertSigner(cert, signer)
		if err != nil {
			return err
		}
	}

	p := privKey{
		signer:  signer,
		comment: key.Comment,
	}

	if key.LifetimeSecs > 0 {
		t := time.Now().Add(time.Duration(key.LifetimeSecs) * time.Second)
		p.expire = &t
	}

	publicKey := string(p.signer.PublicKey().Marshal())
	r.keys[publicKey] = p
	return nil
}

// Sign returns a signature for the data.
func (r *keyring) Sign(key ssh.PublicKey, data []byte) (*ssh.Signature, error) {
	return r.SignWithFlags(key, data, 0)
}

func (r *keyring) SignWithFlags(key ssh.PublicKey, data []byte, flags SignatureFlags) (*ssh.Signature, error) {
	r.mu.Lock()
	defer r.mu.Unlock()
	if r.locked {
		return nil, errLocked
	}

	r.expireKeysLocked()
	wanted := key.Marshal()
	pubKey := string(wanted)
	if k, exists := r.keys[pubKey]; exists {
		if bytes.Equal(k.signer.PublicKey().Marshal(), wanted) {
			if flags == 0 {
				return k.signer.Sign(rand.Reader, data)
			} else {
				if algorithmSigner, ok := k.signer.(ssh.AlgorithmSigner); !ok {
					return nil, errors.New(fmt.Sprintf("agent: signature does not support non-default signature algorithm: %T", k.signer))
				} else {
					var algorithm string
					switch flags {
					case SignatureFlagRsaSha256:
						algorithm = ssh.SigAlgoRSASHA2256
					case SignatureFlagRsaSha512:
						algorithm = ssh.SigAlgoRSASHA2512
					default:
						return nil, errors.New(fmt.Sprintf("agent: unsupported signature flags: %d", flags))
					}
					return algorithmSigner.SignWithAlgorithm(rand.Reader, data, algorithm)
				}
			}
		}
	}
	return nil, errors.New("not found")
}

// Signers returns signers for all the known keys.
func (r *keyring) Signers() ([]ssh.Signer, error) {
	r.mu.Lock()
	defer r.mu.Unlock()
	if r.locked {
		return nil, errLocked
	}

	r.expireKeysLocked()
	s := make([]ssh.Signer, 0, len(r.keys))
	for _, k := range r.keys {
		s = append(s, k.signer)
	}
	return s, nil
}

// The keyring does not support any extensions
func (r *keyring) Extension(extensionType string, contents []byte) ([]byte, error) {
	return nil, ErrExtensionUnsupported
}
