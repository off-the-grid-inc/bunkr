# Bunkr Client


Bunkr client is an RPC client designed to communicate with an already running Bunkr daemon process
It provides the basic operations available within Bunkr itself:

* new-text-secret 	    -> create a new secret whose content is a simple text
* create 			    -> create a new secret
* write 				-> write content to an specified secret
* access				-> retrieve the content of a secret
* delete				-> delete a secret from Bunkr
* sign-ecdsa			-> sign some content with a Bunkr stored ecdsa key
* export-public-data    -> retrieve the public data of a secret (b64-json)


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

#### Contact

For more information or request please contact us at:
[info@bunkr.app](info@bunkr.app)


Copyright <2019> <Off-the-grid-inc> All rights reserved.