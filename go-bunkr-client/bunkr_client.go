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
	"regexp"
	"strings"
)

// OperationArgs is the Bunkr RPC command wrapper, it has a single Line attribute that holds Bunkr commands
// ex: OperationArgs { Line: "new-text-secret foo foocontent"}
type OperationArgs struct {
	Line string
}

// Result is the Bunkr RPC operations result wrapper. It holds a Result attribute which have the operation result as a string
// and a Error attribute that holds an error message as a string in case the operation itself failed.
// The Result string will be empty if there is any error, as well, the Error string will be empty if everything went well.
// Notice that the Error attribute relates to the operation error, not any error due to connection issues
type Result struct {
	Result string
	Error  string
}

// fmtCmd holds the information for the Bunkr commands exposed in the BunkrClient
// name 		: name of the command
// fmtCommand 	: string with the formatting required for the Bunkr command
// fmtResult    : regex to parse and extract the resulting information from a Bunkr command
type fmtCmd struct {
	name, fmtCommand string
	fmtResult        *regexp.Regexp
}

// fmtCommands is the addressing dictionary with the exposed fmtCmd
var fmtCommands = map[string]fmtCmd{
	"new-text-secret": fmtCmd{
		name:       "new-text-secret",
		fmtCommand: "new-text-secret %s \"%s\"",
		fmtResult:  nil,
	},
	"create": fmtCmd{
		name:       "create",
		fmtCommand: "create %s \"%s\"",
		fmtResult:  nil,
	},
	"write": fmtCmd{
		name:       "write",
		fmtCommand: "write %s %s \"%s\"",
		fmtResult:  nil,
	},
	"access": fmtCmd{
		name:       "access",
		fmtCommand: "access %s",
		fmtResult:  nil,
	},
	"delete": fmtCmd{
		name:       "delete",
		fmtCommand: "delete %s",
		fmtResult:  nil,
	},
	"sign-ecdsa": fmtCmd{
		name:       "sign-ecdsa",
		fmtCommand: "sign-ecdsa %s %s",
		fmtResult:  nil,
	},
	"new-group": fmtCmd{
		name:       "new-group",
		fmtCommand: "new-group %s",
		fmtResult:  nil,
	},
	"ssh-public-data": fmtCmd{
		name:       "ssh-public-data",
		fmtCommand: "ssh-public-data %s",
		fmtResult:  nil,
	},
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
func (bc *BunkrRPCClient) execCmd(cmdName string, args ...interface{}) (string, error) {
	cmd, exists := fmtCommands[cmdName]
	if !exists {
		return "", errors.New(fmt.Sprintf("Cmd %s does not exist", cmdName))
	}
	line := strings.TrimRight(fmt.Sprintf(cmd.fmtCommand, args...), " ")
	arg := &OperationArgs{
		Line: line,
	}
	res := new(Result)
	if err := bc.rpcClient.Call("CommandProxy.HandleCommand", arg, res); err != nil {
		return "", err
	}
	if res.Error != "" {
		return "", errors.New(res.Error)
	}
	ret := res.Result
	// when we have a regex that extract the useful information from the returned value, extract it
	if cmd.fmtResult != nil {
		submatch := cmd.fmtResult.FindStringSubmatch(ret)
		if len(submatch) > 0 {
			ret = fmt.Sprintf("%q\n", submatch[1])
		}
	}
	return ret, nil
}

func (bc *BunkrRPCClient) NewTextSecret(secretName, content string) (string, error) {
	return bc.execCmd("new-text-secret", secretName, content)
}

func (bc *BunkrRPCClient) Create(secretName, secretType string) (string, error) {
	return bc.execCmd("create", secretName, secretType)
}

func (bc *BunkrRPCClient) Write(secretName, contentType, content string) (string, error) {
	return bc.execCmd("write", secretName, contentType, content)
}

func (bc *BunkrRPCClient) Access(secretName string) (string, error) {
	return bc.execCmd("access", secretName)
}

func (bc *BunkrRPCClient) Delete(secretName string) (string, error) {
	return bc.execCmd("delete", secretName)
}

func (bc *BunkrRPCClient) SignECDSA(secretName, hash string) (string, error) {
	return bc.execCmd("sign-ecdsa", secretName, hash)
}

func (bc *BunkrRPCClient) NewGroup(groupName string) (string, error) {
	return bc.execCmd("new-group", groupName)
}

func (bc *BunkrRPCClient) SSHPublicData(secretName string) (string, error) {
	return bc.execCmd("ssh-public-data", secretName)
}
