package main

import (
	"fmt"
	"log"
	"os"
	"os/signal"
	"sync"
	"syscall"

	ssh_agent "github.com/off-the-grid-inc/murmur/ssh-agent/ssh-agent"
)

var Version string

func main() {
	opts := getOpts()
	if opts.Version {
		fmt.Printf("Version: %s\n", Version)
		return
	}

	ssha, err := ssh_agent.NewSSHAgent(
		opts.BunkrAddr,
		opts.AgentAddr,
		opts.StorageAddr,
	)
	if err != nil {
		log.Fatalf("Error loading ssh-agent: %v", err)
	}

	if opts.AddKey != "" {
		if err := ssha.ImportKey(opts.AddKey); err != nil {
			log.Fatal(err)
		}
		return
	}

	if opts.SSHPublicKey != "" {
		if err := ssha.SecretPublicKey(opts.SSHPublicKey); err != nil {
			log.Fatal(err)
		}
		return
	}

	if err := ssha.Start(); err != nil {
		log.Fatalf("Error starting ssh-agent: %v", err)
	}

	var once sync.Once
	defer once.Do(ssha.Shutdown)

	var closeFileOnce sync.Once
	closeFile := func() {
		if err := os.Remove(opts.AgentAddr); err != nil {
			log.Print(err)
		}
	}
	defer closeFileOnce.Do(closeFile)

	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)
	go func() {
		<-sigs
		once.Do(ssha.Shutdown)
		defer closeFileOnce.Do(closeFile)
		os.Exit(-1)
	}()

	if err := ssha.Run(); err != nil {
		log.Fatal(err)
	}
}
