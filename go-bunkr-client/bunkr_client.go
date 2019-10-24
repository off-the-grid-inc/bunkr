package bunkr_client

// Bunkr client is an RPC client designed to communicate with an already running Bunkr daemon process
// It provides the basic operations available within Bunkr itself:
// * new-text-secret 	-> create a new secret whose content is a simple text
// * create 			-> create a new secret
// * write 				-> write content to an specified secret
// * access				-> retrieve the content of a secret
// * delete				-> delete a secret from Bunkr
// * sign-ecdsa			-> sign some content with a Bunkr stored ecdsa key
// * ssh-public-data -> retrieve the public data of a secret (b64-json)

import (
	"errors"
	"fmt"
	"net"
	"net/rpc"
	"net/rpc/jsonrpc"
)

const (
	NEW_TEXT_SECRET    CommandName = "new-text-secret"
	NEW_SSH_KEY                    = "new-ssh-key"
	NEW_FILE_SECRET                = "new-file-secret"
	NEW_GROUP                      = "new-group"
	IMPORT_SSH_KEY                 = "import-ssh-key"
	LIST_SECRETS                   = "list-secrets"
	LIST_DEVICES                   = "list-devices"
	LIST_GROUPS                    = "list-groups"
	SEND_DEVICE                    = "send-device"
	RECEIVE_DEVICE                 = "receive-device"
	REMOVE_DEVICE                  = "remove-device"
	REMOVE_LOCAL                   = "remove-local"
	RENAME                         = "rename"
	CREATE                         = "create"
	WRITE                          = "write"
	ACCESS                         = "access"
	GRANT                          = "grant"
	REVOKE                         = "revoke"
	DELETE                         = "delete"
	RECEIVE_CAPABILITY             = "receive-capability"
	RESET_TRIPLES                  = "reset-triples"
	NOOP                           = "noop-test"
	SECRET_INFO                    = "secret-info"
	SIGN_ECDSA                     = "sign-ecdsa"
	SSH_PUBLIC_DATA                = "ssh-public-data"
	SIGNIN                         = "signin"
	CONFIRM_SIGNIN                 = "confirm-signin"
)

type SecretType string

const (
	ECDSASECP256k1Key SecretType = "ECDSA-SECP256k1"
	ECDSAP256Key                 = "ECDSA-P256"
	HMACKey                      = "HMAC"
	GenericGF256                 = "GENERIC-GF256"
	GenericPF                    = "GENERIC-PF"
)

// OperationResult is a wrapper over an arbitrary json object. Operations result a json like object with diverse content.
// It will be a map object that would look like:
// {
// 		"msg" : "Some feedback message"
// 		"some_content_key" : ["some_content_item"]
// }
type OperationResult map[string]interface{}

type CommandName string
type CommandArgs []string

// OperationArgs is the Bunkr RPC command wrapper, it has a single Line attribute that holds Bunkr commands
// ex: OperationArgs { Line: "new-text-secret foo foocontent"}
type OperationArgs struct {
	Command CommandName
	Args    CommandArgs
}

// Result is the Bunkr RPC operations result wrapper. It holds a Result attribute which have the operation result as a string
// and a Error attribute that holds an error message as a string in case the operation itself failed.
// The Result string will be empty if there is any error, as well, the Error string will be empty if everything went well.
// Notice that the Error attribute relates to the operation error, not any error due to connection issues
type Result struct {
	Result OperationResult
	Error  string
}

// RPC client that connects to a running Bunkr daemon process
type BunkrRPCClient struct {
	rpcClient *rpc.Client
}

func NewBunkrClient(socketAddress string) (*BunkrRPCClient, error) {
	conn, err := net.Dial("unix", socketAddress)
	if err != nil || conn == nil {
		return nil, errors.New(fmt.Sprintf("Could not connect to Bunkr API server: %v", err))
	}

	jsonClient := jsonrpc.NewClient(conn)
	return &BunkrRPCClient{rpcClient: jsonClient}, nil
}

// execCmd wraps the rpc call for each of the exposed Bunkr commands
// cmdNAme  : name of the command to call remotely
// args		: variables to be used in the fmtCommand formatting string corresponding to the command (cmdName)
func (bc *BunkrRPCClient) execCmd(cmdName CommandName, args ...string) (OperationResult, error) {
	arg := &OperationArgs{
		Command: CommandName(cmdName),
		Args:    args,
	}
	res := new(Result)
	if err := bc.rpcClient.Call("CommandProxy.HandleCommand", arg, res); err != nil {
		return nil, err
	}
	if res.Error != "" {
		return nil, errors.New(res.Error)
	}
	return res.Result, nil
}

// Returns a JSON like object map[string]interface
// {
// 		"msg" : "<feedback message>",
// }
func (bc *BunkrRPCClient) NewTextSecret(secretName, content string) (OperationResult, error) {
	return bc.execCmd(NEW_TEXT_SECRET, secretName, content)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg" : "<feedback message>",
// }
func (bc *BunkrRPCClient) NewSSHKey(secretName string) (OperationResult, error) {
	return bc.execCmd(NEW_SSH_KEY, secretName)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg" : "<feedback message>",
// }
func (bc *BunkrRPCClient) NewFileSecret(secretName, filePath string) (OperationResult, error) {
	return bc.execCmd(NEW_FILE_SECRET, secretName, filePath)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg" : "<feedback message>",
// }
func (bc *BunkrRPCClient) NewGroup(groupName string) (OperationResult, error) {
	return bc.execCmd(NEW_GROUP, groupName)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg" : "<feedback message>",
// }
func (bc *BunkrRPCClient) ImportSSHKey(secretName, filePath string) (OperationResult, error) {
	return bc.execCmd(IMPORT_SSH_KEY, secretName, filePath)
}

// Returns a JSON like object map[string]interface
//
// {
//		"msg"     : "",
//		"content" : {
//			"secrets" : []string, # secrets names
//			"devices" : {
//				"<device name>" : []string,
//				...
//			},
//			"groups" : {
//				"<group name>" : []string,
//				...
//			},
//		}
// }
func (bc *BunkrRPCClient) ListSecrets() (OperationResult, error) {
	return bc.execCmd(LIST_SECRETS)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg" : "",
//      "devices" : []string
// }
func (bc *BunkrRPCClient) ListDevices() (OperationResult, error) {
	return bc.execCmd(LIST_DEVICES)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg"    : "",
//      "groups" : []string
// }
func (bc *BunkrRPCClient) ListGroups() (OperationResult, error) {
	return bc.execCmd(LIST_GROUPS)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg"       : "<feedback message>",
//		"url_raw"   : "<shared static url>",
//		"url_short" : "<shared short url>",
// }
func (bc *BunkrRPCClient) SendDevice(deviceName ...string) (OperationResult, error) {
	if len(deviceName) > 0 {
		return bc.execCmd(SEND_DEVICE, deviceName[0])
	}
	return bc.execCmd(SEND_DEVICE)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg" : "<feedback message>",
// }
func (bc *BunkrRPCClient) ReceiveDevice(link string, deviceName ...string) (OperationResult, error) {
	if len(deviceName) > 0 {
		return bc.execCmd(RECEIVE_DEVICE, link, deviceName[0])
	}
	return bc.execCmd(RECEIVE_DEVICE, link)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg" : "<feedback message>",
// }
func (bc *BunkrRPCClient) RemoveDevice(deviceName string) (OperationResult, error) {
	return bc.execCmd(REMOVE_DEVICE, deviceName)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg" : "<feedback message>",
// }
func (bc *BunkrRPCClient) RemoveLocal(secretName string) (OperationResult, error) {
	return bc.execCmd(REMOVE_LOCAL, secretName)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg" : "<feedback message>",
// }
func (bc *BunkrRPCClient) Rename(oldName, newName string) (OperationResult, error) {
	return bc.execCmd(RENAME, oldName, newName)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg" : "<feedback message>",
// }
func (bc *BunkrRPCClient) Create(secretName, secretType string) (OperationResult, error) {
	return bc.execCmd(CREATE, secretName, secretType)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg" : "<feedback message>",
// }
func (bc *BunkrRPCClient) Write(secretName, contentType, content string) (OperationResult, error) {
	return bc.execCmd(WRITE, secretName, contentType, content)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg"       : "<feedback message>",
//		"mode"      : "<access mode>",
//		"content"   : "<secret content just for (b64 and text)>",
// }
func (bc *BunkrRPCClient) Access(secretName string, args ...string) (OperationResult, error) {
	var mode string
	var filePath string
	switch len(args) {
	case 1:
		if args[0] != "file" {
			mode = args[0]
		}
	case 2:
		mode = args[0]
		filePath = args[1]
	default:
	}
	if filePath != "" {
		return bc.execCmd(ACCESS, secretName, mode, filePath)
	}
	return bc.execCmd(ACCESS, secretName, mode)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg"       : "<feedback message>",
//		"url_raw"   : "<shared static url>",
//		"url_short" : "<shared short url>",
// }
func (bc *BunkrRPCClient) Grant(targetName, secretName string) (OperationResult, error) {
	return bc.execCmd(GRANT, targetName, secretName)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg" : "<feedback message>",
// }
func (bc *BunkrRPCClient) Revoke(targetName, secretName string) (OperationResult, error) {
	return bc.execCmd(REVOKE, targetName, secretName)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg" : "<feedback message>",
// }
func (bc *BunkrRPCClient) ReceiveCapability(link string, secretName ...string) (OperationResult, error) {
	if len(secretName) > 0 {
		return bc.execCmd(RECEIVE_CAPABILITY, link, secretName[0])
	}
	return bc.execCmd(RECEIVE_CAPABILITY, link)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg" : "<feedback message>",
// }
func (bc *BunkrRPCClient) Delete(secretName string) (OperationResult, error) {
	return bc.execCmd(DELETE, secretName)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg" : "<feedback message>",
// }
func (bc *BunkrRPCClient) ResetTriples(secretName string) (OperationResult, error) {
	return bc.execCmd(RESET_TRIPLES, secretName)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg" : "<feedback message>",
// }
func (bc *BunkrRPCClient) NoOp(secretName string) (OperationResult, error) {
	return bc.execCmd(NOOP, secretName)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg" : "<feedback message>",
// }
func (bc *BunkrRPCClient) SecretInfo(secretName string) (OperationResult, error) {
	return bc.execCmd(SECRET_INFO, secretName)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg" : "<feedback message>",
//		"r"   : "<R component of the signature>",
//		"s"   : "<S component of the signature>",
// }
func (bc *BunkrRPCClient) SignECDSA(secretName, hash string) (OperationResult, error) {
	return bc.execCmd(SIGN_ECDSA, secretName, hash)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg"           : "<feedback message>",
//		"public_data"   : {
//		    "name"       : "<secret name>",
//          "public_key" : "<b64 encoded public key>",
//      }
// }
func (bc *BunkrRPCClient) SSHPublicData(secretName string) (OperationResult, error) {
	return bc.execCmd(SSH_PUBLIC_DATA, secretName)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg" : "<feedback message>",
// }
func (bc *BunkrRPCClient) SignIn(email, deviceName string) (OperationResult, error) {
	return bc.execCmd(SIGNIN, email, deviceName)
}

// Returns a JSON like object map[string]interface
// {
// 		"msg" : "<feedback message>",
// }
func (bc *BunkrRPCClient) ConfirmSignIn(email, code string) (OperationResult, error) {
	return bc.execCmd(CONFIRM_SIGNIN, email, code)
}
