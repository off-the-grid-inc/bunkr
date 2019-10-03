# Bunkr SSH Agent

The Bunkr SSH Agent is a custom ssh agent that works over Bunkr. The most interesting feature is that you do not need to have the SSH key to operate with it. Nor will it ever be exposed, since the sign operation is computed through secure multiparty computation.
To follow this tutorial you should be familiar with Bunkr already. If not, you can check it out [here](https://github.com/off-the-grid-inc/bunkr/blob/master/README.md)

## Installation

You can install the Bunkr SSH Agent from Bunkr's [releases](https://github.com/off-the-grid-inc/bunkr/releases) or you can compile the binary yourself.

OSX Installation:
```
$ wget https://github.com/off-the-grid-inc/bunkr/releases/download/1.0.0/bunkr-ssh-osx -O bunkr-ssh
$ chmod +x bunkr-ssh
```

Linux Installation:
```
$ wget https://github.com/off-the-grid-inc/bunkr/releases/download/1.0.0/bunkr-ssh-linux -O bunkr-ssh
$ chmod +x bunkr-ssh
```

Compile binary from source:
```
$ go get github.com/off-the-grid-inc/bunkr/bunkr-ssh
$ cd $GOPATH/src/github.com/off-the-grid-inc/bunkr/bunkr-ssh
$ make bunkr-ssh
```

Place the binary on your `PATH` (e.g. `/usr/local/bin`) if you want it accessible from any command-line.

## <a name=handling-keys>Handling your SSH keys with Bunkr</a>

The main advantage of working with this SSH agent is that the keys are managed through Bunkr (and never live on your computer). You can create or import keys, as well as share and manage permissions to any of your keys stored within Bunkr. 

### What can you do?

##### I want a new key

If you want to create a new ssh key (ECDSA-P256), the simplest method is to run:
```shell script
$ bunkr new-ssh-key secret_name
```
Where `secret_name` is any name or identifier you choose for your Bunkr stored key.

##### I already have a key, let me import it!

----

**Notice**: For now only ECDSA-P256 keys are supported.
 
If you already have one, congrats, your key is ready to be used in Bunkr!

If not you can create one with `openssl` or `ssh-keygen`, for example:
```shell script
$ openssl ecparam -genkey -name prime256v1 | openssl ec -out <path/to/key>
```
or
```shell script
$ ssh-keygen -t ecdsa -m PEM
```

----
To create a secret with an already created SSH key in Bunkr you need to run:
```shell script
$ bunkr import-ssh-key secret_name path_to_your_file
```
 Where `secret_name` is any name or identifier you choose for your Bunkr stored key. And, `path_to_your_file` is the exact location of your private key.
 
 After successfully creating the secret it should be safe to remove your local stored key. Although we encourage to have a backup of it while our system is in beta.
 
#### I want to share my key
 
 You can share any of your Bunkr SSH stored keys to any other Bunkr device (it can be another of yours or any other one using Bunkr!).
 
 The first step is to link the devices, in this case you need to send the target device (the device you want your key to be shared) to your Bunkr. So, from that device:
 
```shell script
$ bunkr send-device
This is my device Desktop Device: https://url.bunkr.app/XiWu8cQFa3qtt8xKXLqJfG
``` 

Then we want to add that device to our listing, so, from our Bunkr:

```shell script
$ bunkr receive-device https://url.bunkr.app/XiWu8cQFa3qtt8xKXLqJfG myOtherDivice
New device stored as myOtherDivice
```

Once we do this, we can check that the device was actually added:

```shell script
$ bunkr list-devices
self
--------Public Key: MFkwEwYHKoZIzasdfoZIzj0DAQcDQgAEhYaTo3nNV6asdfMAxwlruj+qOAs0rfU8tWTbHEdYZyfffftsuXmCHm04MkPH/N74qTc6J63ArSwavtRUtjplEA==
myOtherDevice
--------Public Key: MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEhYaTo3nNVasdfFMAxwlruj+qOAs0rfU8tWTbHEdYZytsuXmCHm04MkPH/N74qTc6J63ArSwavtRUtjplEA==
```
Now we need to grant a capability to that device so they can use any chosen key, you can either grant signature permissions so the other device can only use it but cannot really access the key content or modify or delete it (by default) or admin permissions, that makes the other device to be able to use and/or modify the secret:
For sign permission:
```shell script
$ bunkr grant myOtherDevice fookey
Capability granted: https://url.bunkr.app/FappNKY88EG8csAFmETELp
```
For admin permission:
```shell script
$ bunkr grant myOtherDevice fookey admin
Capability granted: https://url.bunkr.app/FappNKY88EG8csAFmETELp
```

This link generated is the one we need to share with the other device so they can add the secret to their Bunkr:

```shell script
$ bunkr receive-capability https://url.bunkr.app/FappNKY88EG8csAFmETELp sharedKey
You now have capability on a new secret: sharedKey
```
From now on, that key will be available to be used by the other device!
 
#### I shared my key but I want to stop another device from using it

Once you share a key, you can also revoke the granted permissions at any time you want:

```shell script
$ bunkr revoke myOtherDevice fookey
Capability revoked
```

From this instant `myOtherDevice` will not be able to use the key anymore.

#### I have many keys and I want to share them all

Bunkr have a powerful feature called `groups`, groups holds permissions for other secrets, so it is easy to group other secrets and share them as a bunch.
Lets say that we have two SSH keys (`ssh1`,`ssh2`) and we want to share them with our team.
First we need to create a group for them:

```shell script
$ bunkr new-group mySSHGroup;
Secret created
```

Then, we need to grant that group for each of the SSH keys:

```shell script
$ bunkr grant mySSHGroup ssh1
Capability granted:

raw link (lasts forever): "bunkr://x-callback-url/import-cap?capB64pubkey=MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEfelPjSasdflXfF4W%2BVMV9j%2BiC%2BHlQpJprtLHmQFcnpC355Gou6ejldVHI%2BMBUaECk%2FKyFvexNGmKKcjjQ%3D%3D&capFileID=2cced765-f8ea-4a75-a1ee-71891b57a2f1&capID=3844d5c5-4dcf-4724-986b-2afebe241bed&capKey=MTJhMTQ2ZDgtYTc2Mi00ZTdlLWExY2MtNTU3NTFhMjI3OWJh&capName=aeb75404-4380-40f1-a508-e2a2fcc2ce48%27s+Capability&capOpTypeList=sign&capState=granted&secretB64pubkey=MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE5JXsZMht60bThaBiExNXbug9g%2BEjQjcG9bdULLDNN%2BSnIoW6%2BDGI0r995jz6OXI9op3q1jfXxObaEPG%2F3k6%2BgQ%3D%3D&secretCapID=a6a754a3-1c17-499f-8ce3-7c61bb93b788&secretFileID=2cced765-f8ea-4a75-a1ee-71891b57a2f1&secretKey=M2ZlMjNiMDMtYWE0ZC00MDBlLTg0YjctODg3NjY4YTlmYzNi&secretName=ssh1&secretType=ECDSA-P256"

shortened (lasts 24hrs): https://url.bunkr.app/MfDtVWkQriV9z84Kc3Gt1K

$ bunkr grant mySSHGroup ssh2
Capability granted:

raw link (lasts forever): "bunkr://x-callback-url/import-cap?capB64pubkey=MFkwEwYHKoZIzj0CAQYIKoZasdfcDQgAEfelPjSSqeBBQ9WilXfF4W%2BVMV9j%2BiC%2BHlQpJprtLHmQFcnpC355Gou6ejldVHI%2BMBUaECk%2FKyFvexNGmKKcjjQ%3D%3D&capFileID=493f922f-f703-443b-8ae9-f3285e7e5bbb&capID=52665942-527b-405f-96c0-484a434852a7&capKey=YTdhMmZhNGEtZTc3NC00YTFiLTk1ZmMtODYzMjNjZjQ5NGRi&capName=aeb75404-4380-40f1-a508-e2a2fcc2ce48%27s+Capability&capOpTypeList=sign&capState=granted&secretB64pubkey=MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE0uOlhYZFrIXEg6LtUhMD8FxzbRtfCBTIX%2FZ9LZEh4LS42TthF%2BkuyFk%2BCCVBLS75ttGPZOrOhc7dwuUyMlZ90w%3D%3D&secretCapID=8e936d72-55a5-4429-8f15-6aec5819b325&secretFileID=493f922f-f703-443b-8ae9-f3285e7e5bbb&secretKey=ZmI4OTEwNWUtNDQ1MS00MDk1LWFmYmEtZTA3MTZjOTI5ZjJj&secretName=ssh2&secretType=ECDSA-P256"

shortened (lasts 24hrs): https://url.bunkr.app/8XTVehJ6muN2EoCkeTiJFg
```

We can skip those links. What we do really want to share is the group now, so for that we just need to grant to the device of our chosen the group:

```shell script
$ bunkr grant myOtherDevice mySSHGroup
Capability granted:
raw link (lasts forever): "bunkr://x-callback-url/import-cap?capB64pubkey=MFkwEwYHKoZIzj0CAQYIKoZasdfcDQgAEfelPjSSqeBBQ9WilXfF4W%2BVMV9j%2BiC%2BHlQpJprtLHmQFcnpC355Gou6ejldVHI%2BMBUaECk%2FKyFvexNGmKKcjjQ%3D%3D&capFileID=493f922f-f703-443b-8ae9-f3285e7e5bbb&capID=52665942-527b-405f-96c0-484a434852a7&capKey=YTdhMmZhNGEtZTc3NC00YTFiLTk1ZmMtODYzMjNjZjQ5NGRi&capName=aeb75404-4380-40f1-a508-e2a2fcc2ce48%27s+Capability&capOpTypeList=sign&capState=granted&secretB64pubkey=MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE0uOlhYZFrIXEg6LtUhMD8FxzbRtfCBTIX%2FZ9LZEh4LS42TthF%2BkuyFk%2BCCVBLS75ttGPZOrOhc7dwuUyMlZ90w%3D%3D&secretCapID=8e936d72-55a5-4429-8f15-6aec5819b325&secretFileID=493f922f-f703-443b-8ae9-f3285e7e5bbb&secretKey=ZmI4OTEwNWUtNDQ1MS00MDk1LWFmYmEtZTA3MTZjOTI5ZjJj&secretName=ssh2&secretType=ECDSA-P256"

shortened (lasts 24hrs): https://url.bunkr.app/8XTVehJ6muN2EoCkeTiJFg
```

Then, from the other device, we import the group capability as if any other capability:
```shell script
$ bunkr receive-capability https://url.bunkr.app/8XTVehJ6muN2EoCkeTiJFg
```

The group and the secrets will be listed and ready to use now:

```shell script
$ bunkr list-secrets
Your Secrets:
     ssh1 (type ECDSA-P256)
     ssh2 (type ECDSA-P256)
     mySSHGroup (type ECDSA-P256)
mySSHGroup Secrets:
     ssh1 (type ECDSA-P256)
     ssh2 (type ECDSA-P256)
```


## How to make the SSH agent work?

### 1. Get an SSH key

First, we need to have a valid SSH key in our Bunkr. In case we don't have one still we can do it in a few steps as [shown above](#handling-keys).

 ### <a name="add-key">2. Add the key to the agent</a>
 
 Now that we have an SSH key stored in Bunkr we need to add that key to the agent. For doing so we need to run the following command with the `bunkr-ssh` binary:
 
```shell script
./bunkr-ssh -addBunkrKey secret_name
```

Where `secret_name` is any name or identifier you chose for your Bunkr stored key.

After this step, the agent will register that key as an available key to perform SSH connections.

**NOTE**: In case we already had the ssh-agent running and the key is still not available we have to do one extra step. We need to either restart the agent or run an `ssh-add` command to update the agent with the new added key/s:
```shell script
ssh-add -l
``` 

The agent will react to the command updating with the newly available keys. The command will show all the keys the agent is managing, you would be able to see that the new keys were added successfully.

### 3. Run the agent

Simply run the binary!

```shell script
./bunkr-ssh
```

The agent will run in this console session and it can be managed like any other ssh-agent.

## Additional operations

Sometimes is useful to know the public key associated with one of the Bunkr stored keys. There is a simple method to retrieve then just by invoking the agent:
```shell script
./bunkr-ssh -sshPublicKey secret_name
```
Where `secret_name` is any name or identifier you choose for your Bunkr stored key.

## Agent flags

Some configuration flags can be used when running the agent:

`-bunkrSocketAddr` => Unix socket address where Bunkr is listening, by default `/tmp/bunkr_daemon.sock`

`-agentSocketAddr` => Unix socket address where the SSH agent will be listening, by default: `/tmp/agent.sock`

`-storageAddr    ` => Path tho the agent storage file where the available keys are tracked

`-version        ` => Flag to show the version of the binary

`-addKey         ` => Flag used to [add a new key to the agent](#add-key)

`-sshPublicKey   ` => Flag to retrieve the public key of a Bunkr stored SSH key.

## Examples

Add an ssh key for personal use to some storage
```shell script
./bunkr-ssh -storageAddr /home/username/.bunkr/personal_ssh.json -addKey my_personal_ssh_key
```
Retrieve a public key
```shell script
./bunkr-ssh -storageAddr /home/username/.bunkr/personal_ssh.json -sshPublicKey my_personal_ssh_key
```

Running the agent with another storage used for business 
```shell script
./bunkr-ssh -storageAddr /home/username/.bunkr/company_ssh.json
```

### Github usecase

I want to have a single key that works for my github projects and it is shared among all my devices:

#### 1.- Create or import the key

```shell script
./bunkr new-ssh-key github_key;
```

#### 2.- Share the key with your devices
```shell script
./bunkr grant myOtherDevice github_key;
```

#### 3.- From any device add the key to your SSH agent

```shell script
./bunkr-ssh -addBunkrKey github_key
```

Notice that you will be required to run this command in any of the devices you shared the key with in order to make it 
available to the local SSH agent.

#### 3.- Retrieve the key public key

```shell script
./bunkr-ssh -sshPublicKey github_key
```
This will output the public key in the consolo

#### 4.- Add the public key to github

Just follow the available [github tutorial on how to add a key](https://help.github.com/en/articles/adding-a-new-ssh-key-to-your-github-account)

#### 5.- Run the SSH agent
```shell script
./bunkr-ssh
```

#### 6.- Execute any git operation over a github project

Do any push or clone for a key required project. The signature will be executed through Bunkr!!

## BETA notes

Bunkr an all attached projects including this SSH agent are still in beta process. Although it is safe to store your keys within Bunkr we strongly recommend to always have a backup of your data.  

