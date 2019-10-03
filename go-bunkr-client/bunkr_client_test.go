package bunkr_client

import (
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
	"encoding/base64"
	"fmt"
	"strings"
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
	fmt.Print(res)
	res, err = client.Access("foo_secret_test")
	require.NoError(err)
	fmt.Print(res)
	require.Equal(content, strings.TrimRight(res, "\n"))
	res, err = client.Delete("foo_secret_test")
	require.NoError(err)
	fmt.Print(res)
	res, err = client.Create("foo_key", "ECDSA-P256")
	require.NoError(err)
	fmt.Print(res)
	k, err := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	require.NoError(err)
	b64key := base64.StdEncoding.EncodeToString(k.D.Bytes())
	res, err = client.Write("foo_key", "b64", b64key)
	require.NoError(err)
	fmt.Print(res)
	res, err = client.SSHPublicData("foo_key")
	require.NoError(err)
	fmt.Print(res)
	res, err = client.Delete("foo_key")
	require.NoError(err)
	fmt.Print(res)
}
