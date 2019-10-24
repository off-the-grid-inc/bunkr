# Bunkr Client


Bunkr client is an RPC client designed to communicate with an already running Bunkr daemon process
It provides the basic operations available within Bunkr itself:

* new-text-secret       -> create a new secret whose content is a simple text
* new-ssh-key           -> create a new secret whose content is an ECDSA ssh key
* new-file-secret       -> dump a file content as a new secret
* new-group             -> create a new group
* import-ssh-key        -> import an ssh key from a file into a secret
* list-secrets          -> list all stored secrets
* list-devices          -> list all shared devices
* list-groups           -> list all tracked groups
* send-device           -> share the current Bunkr device
* receive-device        -> import a shared Bunkr device
* remove-device         -> remove a shared device reference from Bunkr
* remove-local          -> untrack a secret, it does not delete the secret from the plattform
* rename                -> rename a secret, device or group
* create                -> create a new empty secret
* write                 -> write a secret with new content
* access                -> retrieve the content of a secret
* grant                 -> grant capabilities to a group or device for an specified secret or group
* revoke                -> revoke a given capability
* delete                -> erase a secret existence
* receive-capability    -> import a capability for a given secret
* reset-triples         -> synchronize triples for a secret
* noop-test             -> health check operation over a secret
* secret-info           -> get secret public information
* sign-ecdsa            -> make an ECDSA signature with a ECDSA Bunkr secret
* ssh-public-data       -> retrieve a secret public data
* signin                -> signin into the platfform
* confirm-signin        -> confirm the signin process


Notice that this operation are the same you could find in the **Bunkr** cli itself!

#### Install
Using `go get` is the easiest way:

`go get github.com/off-the-grid-inc/bunkr/go-bunkr-client`

#### Get started!

Bunkr client is really simple to use, it connects to the UNIX socket offered from Bunkr:

```go
import (
    "fmt"
    
    bunkr_client "github.com/off-the-grid/bunkr/go-bunkr-client"
)

func main(){
    client, _ := bunkr_client.NewBunkrClient("/tmp/bunkr_daemon.sock")
    res, _ := client.NewTextSecret("foo_secret_test", "foo_content")
    fmt.Print(res) // "Secret created"
    res, _ = client.Access("foo_secret_test") // "foo_content"
    fmt.Print(res)
    res, _ = client.Delete("foo_secret_test") // "Secret deleted"
    fmt.Print(res)
}
```

#### Operation results

The bunkr api returns a generic JSON object that for golang is a simple `map[string]interface{}`. 
Notice that if the object have nested objects, they are also in the form of `map[string]interface{}`.
This means that we need to recast to the type we need for it to be use, so for exampl imagine we have this object as result:

```json
{
  "msg" : "Hello Bunkr",
  "some_info" : {
    "some_content" : ["some_value"]
  }
}
```

For operating with everything in golang we would need to typecast some of the values:

```go
result, _ := client.MyBunkrOperation()

msg     := result["msg"].(string)
info    := result["some_info"].(map[string]interface{})
content := info["some_content"].([]interface{})
value   := content[0].(string)
```

The type information of the resulting operations are within the documentation of each operation.
#### Contact

For more information or request please contact us at:
[info@bunkr.app](info@bunkr.app)


Copyright <2019> <Off-the-grid-inc> All rights reserved.