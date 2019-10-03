package storage

import (
	"errors"
	"fmt"
	"os"
	"os/user"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestAgentStorage(t *testing.T) {
	require := require.New(t)

	// Test New Bunkr Storage
	path, err := getTestPath()
	require.NoError(err)
	bunkrStorage, err := NewAgentStorage(path)
	require.NoError(err)
	defer func() {
		_ = removeTestStorage()
	}()

	// Test Store Secrets
	secret1 := &Secret{
		Name:       "secret1",
		FileId:     "fid1",
		CapId:      "cid1",
		SecretType: "ECDSA-P256",
		PublicData: []byte("data"),
		Group:      nil,
	}
	secret2 := &Secret{
		Name:       "secret2",
		FileId:     "fid2",
		CapId:      "cid2",
		SecretType: "GENERIC-GF256",
		Group:      secret1,
	}
	secret3 := &Secret{
		Name:       "secret3",
		FileId:     "fid3",
		CapId:      "cid3",
		SecretType: "GENERIC-PF",
		Group:      nil,
	}

	err = bunkrStorage.StoreSecret(secret1)
	require.NoError(err)
	err = bunkrStorage.StoreSecret(secret2)
	require.NoError(err)
	err = bunkrStorage.StoreSecret(secret3)
	require.NoError(err)

	// Test Get Secrets
	s, err := bunkrStorage.GetSecret("secret1")
	require.NoError(err)
	require.Equal(s.Name, secret1.Name, "should be equal")
	require.Equal(s.CapId, secret1.CapId, "should be equal")
	require.Equal(s.FileId, secret1.FileId, "should be equal")
	s2, err := bunkrStorage.GetSecret("secret2")
	require.NoError(err)
	require.Equal(s2.Name, secret2.Name, "should be equal")
	require.Equal(s2.CapId, secret2.CapId, "should be equal")
	require.Equal(s2.FileId, secret2.FileId, "should be equal")
	require.Equal(s2.Group.Name, secret1.Name, "should be equal")
	require.Equal(s2.Group.CapId, secret1.CapId, "should be equal")
	require.Equal(s2.Group.FileId, secret1.FileId, "should be equal")
	require.Equal(s2.Group.Group, secret1.Group, "should both be nil")

	secrets, err := bunkrStorage.GetSecrets()
	require.NoError(err)
	require.Len(secrets, 3, "should be equal")

	secretsGF, err := bunkrStorage.GetSecretsByType("GENERIC-GF256")
	require.NoError(err)
	require.Len(secretsGF, 1, "should be equal")

	// Test Remove Secret
	err = bunkrStorage.RemoveSecret("secret1")
	_, err = bunkrStorage.GetSecret("secret1")
	require.Error(err)
	_, err = bunkrStorage.GetSecret("secret2")
	require.Error(err)
	secrets, err = bunkrStorage.GetSecrets()
	require.NoError(err)
	require.Len(secrets, 1, "should be equal")

	err = bunkrStorage.Dump()
	require.NoError(err)
	bunkrStorage2, err := NewAgentStorage(path)
	require.NoError(err)
	require.Equal(bunkrStorage.data, bunkrStorage2.data)

	require.NoError(err)
}

func getTestPath() (string, error) {
	// Get or create path to ~/.bunkr
	usr, err := user.Current()
	if err != nil {
		return "", errors.New(fmt.Sprintf("Error finding home directory: %v", err))
	}

	testPath := filepath.Join(usr.HomeDir, "test.json")
	return testPath, nil
}

func removeTestStorage() error {
	path, err := getTestPath()
	if err != nil {
		return err
	}
	if err := os.Remove(path); err != nil {
		return err
	}

	return nil
}
