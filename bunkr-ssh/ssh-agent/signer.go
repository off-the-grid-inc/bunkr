package ssh_agent

import (
	"crypto"
	"encoding/base64"
	"errors"
	"fmt"
	"io"
	"log"
	"math/big"
	"strings"

	"golang.org/x/crypto/ssh"

	bunkr_client "github.com/off-the-grid-inc/bunkr/go-bunkr-client"
)

type Signature struct {
	R *big.Int
	S *big.Int
}

type wrappedSigner struct {
	signer     *bunkr_client.BunkrRPCClient
	pubKey     ssh.PublicKey
	secretName string
}

// NewSignerFromSigner takes any crypto.Signer implementation and
// returns a corresponding Signer interface. This can be used, for
// example, with keys kept in hardware modules.

func NewSignerFromBunkr(pubKey ssh.PublicKey, bunkrClient *bunkr_client.BunkrRPCClient, secretName string) (ssh.Signer, error) {
	return &wrappedSigner{bunkrClient, pubKey, secretName}, nil
}

func (s *wrappedSigner) PublicKey() ssh.PublicKey {
	return s.pubKey
}

func (s *wrappedSigner) Sign(rand io.Reader, data []byte) (*ssh.Signature, error) {
	log.Print("signing with bunkr...")
	return s.SignWithAlgorithm(rand, data, "")
}

func (s *wrappedSigner) SignWithAlgorithm(rand io.Reader, data []byte, algorithm string) (*ssh.Signature, error) {
	hashFunc := crypto.SHA256
	h := hashFunc.New()
	h.Write(data)
	digest := h.Sum(nil)
	b64Digest := base64.StdEncoding.EncodeToString(digest)
	var signature []byte
	var rawSignature Signature

	stringSignature, err := s.signer.SignECDSA(s.secretName, b64Digest)
	if err != nil {
		return nil, err
	}
	fmt.Printf("Operation content: %s", stringSignature)

	strSigs := strings.Split(stringSignature, " ")
	rSig, err := base64.StdEncoding.DecodeString(strSigs[0])
	if err != nil {
		return nil, err
	}
	sSig, err := base64.StdEncoding.DecodeString(strSigs[1])
	if err != nil {
		return nil, err
	}
	var success bool
	rawSignature.R, success = big.NewInt(0).SetString(string(rSig), 10)
	if !success {
		return nil, errors.New(fmt.Sprintf("Error converting number %s to big.Int", string(rSig)))
	}
	rawSignature.S, success = big.NewInt(0).SetString(string(sSig), 10)
	if !success {
		return nil, errors.New(fmt.Sprintf("Error converting number %s to big.Int", string(sSig)))
	}
	signature = ssh.Marshal(&rawSignature)

	sshSignature := &ssh.Signature{
		Format: s.pubKey.Type(),
		Blob:   signature,
	}
	if err := s.pubKey.Verify(data, sshSignature); err != nil {
		log.Print(fmt.Sprintf("Bunkr signature incorrect: %v", err))
		return nil, errors.New(fmt.Sprintf("Error verifiying signature: %v", err))
	}

	return sshSignature, nil
}
