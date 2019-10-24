package bunkr_client

import (
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
	"encoding/base64"
	"fmt"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestClient(t *testing.T) {
	//t.SkipNow()
	require := require.New(t)
	client, err := NewBunkrClient("/tmp/bunkr_daemon.sock")
	require.NoError(err)
	content := "foo content"
	res, err := client.NewTextSecret("foo_secret_test", content)
	require.NoError(err)
	fmt.Println(res)
	res, err = client.Access("foo_secret_test")
	require.NoError(err)
	fmt.Println(res)
	require.Equal(content, res["content"])
	res, err = client.Delete("foo_secret_test")
	require.NoError(err)
	fmt.Println(res)
	res, err = client.Create("foo_key", "ECDSA-P256")
	require.NoError(err)
	fmt.Println(res)
	k, err := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	require.NoError(err)
	b64key := base64.StdEncoding.EncodeToString(k.D.Bytes())
	res, err = client.Write("foo_key", "b64", b64key)
	require.NoError(err)
	fmt.Println(res)
	res, err = client.SSHPublicData("foo_key")
	require.NoError(err)
	fmt.Println(res)
	res, err = client.Delete("foo_key")
	require.NoError(err)
	fmt.Println(res)
	_, err = client.NewSSHKey("foo_key")
	require.NoError(err)
	_, err = client.SignECDSA("foo_key", "Zm9v")
	require.NoError(err)
	res, err = client.Delete("foo_key")
	require.NoError(err)
	secretsCount := 3
	for i := 0; i < secretsCount; i++ {
		_, err := client.NewTextSecret(fmt.Sprintf("secret_%d", i), "foo content")
		require.NoError(err)
		_, err = client.NewGroup(fmt.Sprintf("group_%d", i))
		require.NoError(err)
	}

	res, err = client.ListGroups()
	require.NoError(err)
	fmt.Println(res)

	res, err = client.ListSecrets()
	require.NoError(err)
	fmt.Println(res)

	_, err = client.NoOp("secret_1")
	require.NoError(err)

	_, err = client.Grant("group_0", "secret_0")
	require.NoError(err)
	_, err = client.Revoke("group_0", "secret_0")
	require.NoError(err)

	_, err = client.Rename("secret_1", "secret_foo")
	_, err = client.Rename("secret_foo", "secret_1")
	res, err = client.SecretInfo("secret_1")
	fmt.Println(res)

	for i := 0; i < secretsCount; i++ {
		_, err := client.Delete(fmt.Sprintf("secret_%d", i))
		require.NoError(err)
		_, err = client.Delete(fmt.Sprintf("group_%d", i))
		require.NoError(err)
	}

}
