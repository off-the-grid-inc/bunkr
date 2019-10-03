package main

import (
	"flag"
	"os/user"
	"path"
)

var (
	bunkrSocketAddr = flag.String("bunkrSocketAddr", "/tmp/bunkr_daemon.sock", "The address where the client will run")
	agentSocketAddr = flag.String("agentSocketAddr", "/tmp/agent.sock", "The address where the ssh-agent will run")
	storageAddr     = flag.String("storageAddr", path.Join(getHomeDir(), ".bunkr/agent_storage.json"), "The address where the client will run")
	version         = flag.Bool("version", false, "Show version information")
	addKey          = flag.String("addBunkrKey", "", "Enables importing and ssh key fomr Bunkr")
	sshPublicKey    = flag.String("sshPubliKey", "", "Retrieve the public key associated to a Bunkr ssh secret key")
)

func getHomeDir() string {
	usr, err := user.Current()
	if err != nil {
		return ""
	}
	return usr.HomeDir
}

type options struct {
	BunkrAddr    string
	AgentAddr    string
	StorageAddr  string
	AddKey       string
	SSHPublicKey string
	Version      bool
}

func getOpts() *options {

	flag.Parse()
	opts := &options{
		BunkrAddr:    *bunkrSocketAddr,
		AgentAddr:    *agentSocketAddr,
		StorageAddr:  *storageAddr,
		AddKey:       *addKey,
		SSHPublicKey: *sshPublicKey,
		Version:      *version,
	}
	return opts
}
