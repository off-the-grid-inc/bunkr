![alt text](https://github.com/off-the-grid-inc/bunkr/blob/master/logo.jpg "Bunkr logo")

Bunkr is a command line tool for secure storage and dynamic access management of sensitive or private data. Bunkr users store their private data across a decentralized network of remote machines using state of the art cryptographic techniques (Shamir Secret Sharing, Secure Multi Party Computation) that make sure the data is maximally resistant to either theft or loss. Data stored in Bunkr is accessible only to the exact devices specified by the user(s), and permissions can be granted and revoked dynamically. Even the remote machines that collectively store and serve data to Bunkr users have no way of individually knowing the underlying data they process. Passwords, API Keys, Cryptographic Keys and more can all be handled with previously inconceivable security and convenience thanks to Bunkr.

[Visit Our Website](https://bunkr.app)

## IMPORTANT BETA DISCLAIMER

_**This repository is a pre-release beta version of Bunkr. We highly recommend keeping back ups of any important data you store on the beta platform**_. This is the first open public testing of our cli and the majority of the code is not yet open source. We are providing free and unlimited use of our state of the art distributed secrets management platform, but the binary is offered as is, with no guarantees. 

If you think you have found any bugs or security leaks please open an issue here on github or contact us at contact@bunkr.app.

## Table of Contents

 1. [Installation and Setup](#Bunkr-Install)
 2. [Bunkr CLI Cheatsheet](#cheatsheet)
 3. [Basic Secret Storage](#Tut-1)
 4. [Share Secret Across Devices](#Tut-2)
 5. [Bunkr Groups](#Tut-3)
 6. [Bunkr CLI Configuration](#Bunkr-Config)
 7. [Bunkr CLI Documentation](#Docs)

## <a name="Bunkr-Install"> Installation and Setup </a>

Set up your free Bunkr Beta account in seconds. Follow the instructions to `Install` the CLI and `Sign In` your device:

#### Install

The Bunkr CLI Beta binary file can be downloaded from this repository's [releases](https://github.com/off-the-grid-inc/bunkr/releases). To use the binary from the command-line, make sure to place it somewhere on your `PATH` (e.g. `/usr/local/bin`).

OSX Installation:
```
$ wget https://github.com/off-the-grid-inc/bunkr/releases/download/2.0.0/bunkr-osx -O /usr/local/bin/bunkr
$ chmod +x /usr/local/bin/bunkr
$ bunkr -version
Version: 2.0.0
```

Linux Installation:
```
$ wget https://github.com/off-the-grid-inc/bunkr/releases/download/2.0.0/bunkr-linux -O /usr/local/bin/bunkr
$ chmod +x /usr/local/bin/bunkr
$ bunkr -version
Version: 2.0.0
```

#### Sign In
Before you can store bunkr secrets on a new device you must "sign in" the device and verify your email. It is a two step process:

1. Sign in with an email address (`signin`)
2. Verify the 8 digit confirmation code that was emailed to you (`confirm-signin`)

```
$ bunkr -I
Choose Bunkr Passphrase:
Re-enter Bunkr Passphrase:
bunkr: >> signin myEmail@email.com myDeviceName;
bunkr: >> confirm-signin myEmail@email.com XXXXXXXX;
bunkr: >> quit;
```

*If you do not see the verification code in your email after a few minutes- it may be in your spam folder*

Note that the first time you use bunkr you will be prompted to create a passphrase. Be sure to back it up (to learn more about bunkr password protection [see here](#passphrase)).

## <a name="cheatsheet"> Bunkr CLI Cheatsheet: </a>

* Running interactive bunkr cli: 
    * `$ bunkr -I`
* Execute commands in interactive cli:
    * `bunkr: >> access nameOfSecret;`
* Execute single shot commands:
    * `$ bunkr access nameOfSecret`
* Running bunkr daemon:
    * `$ bunkr -D`
    * `$ ./nohup_bunkr.sh`
* Stopping daemon:
    * `$ ps aux | grep bunkr` to get the PID and then `kill 25678`
    * `$ ./stop_nohup_bunkr.sh`

All commands work identically as single shot commands or in the interactive cli. For a comprehensive list of bunkr commands see [Bunkr CLI Documentation](#Docs). 

For detailed information on bunkr execution see [Bunkr CLI Configuration](#Bunkr-Config)

## <a name="Tut-1"> Basic Secret Storage </a>

#### Run Bunkr in Interactive mode

```
$ bunkr -I
Enter Bunkr Passphrase:
bunkr: >> 
```

We recommend running an interactive session when writing secret data to Bunkr when possible. This way no secrets will be unwittingly cached in the command line history.

#### Store a text secret in Bunkr

```
bunkr: >> new-text-secret API_KEY K9ERzWzhyNB3egjJfBer-PgpvzKDHgYBsdd43;
Secret created
bunkr: >> quit;
```

#### Access your secret

```
$ bunkr access API_KEY
Enter Bunkr Passphrase:
K9ERzWzhyNB3egjJfBer-PgpvzKDHgYBsdd43
```

#### Using the Daemon

You can run the bunkr daemon to keep your bunkr "unlocked" indefinitely. This way you will not be prompted for your password every single time you run a `bunkr` command.

```
$ bunkr -D
Serving RPC handler at /tmp/bunkr_daemon.sock
```

Now (in another terminal) we see commands execute without the passphrase:

```
$ bunkr access API_KEY
K9ERzWzhyNB3egjJfBer-PgpvzKDHgYBsdd43
$ bunkr -I
bunkr: >> 
```

To use the bunkr client libraries, or any software built on top of bunkr, the bunkr daemon will need to be running.

Stop the Bunkr Daemon at any time with `Ctrl+C` (i.e. kill the daemon process). To run a daemon in the background use the shell scripts `nohup_bunkr.sh` and `stop_nohup_bunkr.sh`.

## <a name="Tut-2"> Share Secrets Across Devices </a>

#### Exchange device information

Before devices can authorize each other on their secrets, they have to know each other. In this scenario Device A and Device B are both running Bunkr.

Device B:
```
$ bunkr send-device device-B
This is my device device-B: 

raw link (lasts forever): <raw url>

shortened (lasts 24hrs): https://url.bunkr.app/BG6213ghHyDW2iXPTGxUun
```
 
It is up to user/s to communicate links via some outside channel (since no private information is being passed, there is nothing insecure about sending this information over normal channels like email or sms). However, only import bunkr information that you are sure is coming from a trusted source (i.e. beware of phishing).

#### Grant capabilities

After receiving a link from Device B, Device A imports the device information and begins granting capabilities to Device B.

Device A:
```
$ bunkr receive-device https://url.bunkr.app/BG6213ghHyDW2iXPTGxUun
New device stored as device-B
$ bunkr grant device-B API_KEY
Capability granted: 

raw link (lasts forever): <raw url>

shortened (lasts 24hrs): https://url.bunkr.app/K4StLbTFCQmxxDYDH1tmxf
```

This link imports the capability information allowing Device B to access the secret.

#### Receive capability

From Device B:
```
$ bunkr receive-capability https://url.bunkr.app/K4StLbTFCQmxxDYDH1tmxf
You now have capability on a new secret: API_KEY
$ bunkr access API_KEY
K9ERzWzhyNB3egjJfBer-PgpvzKDHgYBsdd43
```

Note that while Device A fully controls the secret (can grant or revoke permissions as well as overwrite or delete the secret value), Device B is limited to the access operation.

#### Revoke access at any time

Device A can revoke Device B's permission to access the secret at any time.

From Device A:
```
$ bunkr revoke device-B API_KEY
Capability revoked
```

From Device B:
```
$ bunkr access API_KEY
SendRequest failed with error: {"Traces":[{"Msg":"Operation failed, [timed out = false] replies expected 7, received 3, failed 3 [errors: [DENIED DENIED DENIED]]" ...}
```

## <a name="Tut-3"> Bunkr Groups </a>

We introduce a new concept which is the Bunkr `Group`. A group is simply a private key stored as a Bunkr Secret, but it will be put to use in a specific way so that we can conveniently define a whole set of capabilities with just one capability. If a device is given permissions on a group it immediately inherits the permissions that the group has on any other secrets.

We will continue using Device A and Device B from the previous tutorial and assume these devices are already aware of each other.

#### Create secrets to group together

Lets imagine that we are the admin of our company's secrets. First we will write the company secrets to Bunkr.
```
$ bunkr -I
bunkr: >> new-text-secret companyPassword foobar;
Secret created
bunkr: >> quit;
$ bunkr new-ssh-key companyKey;
Secret created
```

Notice that when writing a text secret we use interactive mode but since the value of a key is generated internally, this is not necessary with the command `new-ssh-key`. Essentially, use the interactive mode if you are passing a secret value as an argument directly. In all other cases, either mode suffices.

#### Step 3: Create and define group

In the example below we grant the group "company" permission to sign with "companyKey" and permission to access "companyPassword". Anyone who obtains a "company" signature inherits these capabilities.

```
$ bunkr new-group company
$ bunkr grant company companyKey
Capability Granted:
...
$ bunkr grant company companyPassword
Capability Granted:
...
```

#### Grant permission on the group

Device A:
```
$ bunkr grant device-B company
Capability Granted:

raw link (lasts forever): <raw url>

shortened (lasts 24hrs): https://url.bunkr.app/K4StLbTFCQmxxDYDH1tmxf
```

Device B:
```
$ bunkr receive-capability https://url.bunkr.app/K4StLbTFCQmxxDYDH1tmxf
You now have capability on a new secret: company
$ bunkr list-secrets
Your Secrets:
    company (type ECDSA-P256)
company Secrets:
    companyPassword (type GENERIC-GF256)
    companyKey (type ECDSA-P256)
$ bunkr access companyPassword
foobar
```

## <a name="Bunkr-Config"> Bunkr CLI Configuration </a>

#### Excution modes

Bunkr CLI has 3 main execution modes

 1. Daemonized (`-D`)
 2. Interactive session (`-I`)
 3. Single command execution 


When running **daemonized** it will listen to commands from another instance of the tool or any of the available client libraries.
This means that when running single commands or `bunkr -I` the cli tool will send the
commands to the already running daemon. In case no daemon is found they will start a session
client that will be killed once the process is finished.

It is easy to start the daemon using the `nohup_bunkr.sh` script in the root of this repository.
This script redirects the output to a file (`bunkr.out`) that can be used to debug the daemonized process.
Since the process is running in the background we need to manually stop it. Or use the `stop_nohup_bunkr.sh` script. The first script dumps the PID of the daemonized process into a `bunkr_pid.txt` file which then is read by the stop script. Notice that they only work when the current working directory is the same root as the Bunkr executable.

#### Execution flags

`-bindAddr        ` => Address where the client will be listening to incoming messages. By default `localhost`

`-bindPort        ` => Port where the client will be listening. By default `8086`

`-D               ` => Run the Bunkr as a daemon 

`-I               ` => Run an interactive Bunkr session 

`-disablePassword ` => Disable password protection (only for first runs)

`-daemonAddr      ` => Unix socket address where the daemon will be listening. By default `/tmp/bunkr_daemon.sock`

`-version         ` => Show binary version

`-debug           ` => Activate debug logging

`-logFile         ` => Path to output log file. By default `./bunkr.log`

`-identityFilename` => Set identity file name. By default `client_identity`

`-proposalTimeout ` => Set operations timeout. By default `120000ms`


#### <a name="passphrase"> The passphrase </a>
The first time we run the cli it will prompt for a passphrase. You can simply skip through it or use the flag to disable it for no password protection, but it's strongly advised against. The passphrase is used to protect the identity file that will be stored on your device. Each time we run a new instance Bunkr will ask for the passphrase to decrypt the identity file:
```
$ bunkr -I 
Enter Bunkr Passphrase:
```

Alternately you can generate the identity file for Bunkr yourself (it must be an PEM formatted EC private key on NIST-P256 elliptic curve, either encrypted with the aes-128-cbc algorithm or unencrypted):
```
$ openssl ecparam -genkey -name prime256v1 | openssl ec -aes-128-cbc -out <path-to-file>
```

The key you generate must go into your Bunkr Directory: `~/.bunkr` and should be named `client_identity` or else the identityFilename execution flag can be used.

If you lose/alter your identity file or forget the passphrase that decrypts it, then that device will not be able to interact with its existing Bunkr secrets. Bunkr cannot help you to recover your identity since that is private information that is only generated and stored locally.

#### The commands
Once we are inside the Bunkr interactive terminal we can use `tab` to list the available commands:
```
bunkr: »  
quit                 help                 ssh-public-data      rename               create
write                access               grant                revoke               new-text-secret
new-file-secret      new-ssh-key          import-ssh-key       list-secrets         send-device
receive-device       remove-device        list-devices         receive-capability   secret-info
delete               noop-test            reset-triples        new-group            sign-ecdsa
```
If we start writing a command, then `tab` will autocomplete the command.

We can also use the command `help;` to show the list of available commands.

We can show the help for any command by invoking it incomplete or malformed:
```
bunkr: » new-text-secret;
Wrong number of arguments provided.
new-text-secret creates and stores a text secret.
Usage: new-text-secret <secret name> <utf8 text content>
```

Notice that in the interactive terminal multi-line commands are permitted, so all commands must end with `;`

## <a name="Docs"> Bunkr CLI Documentation </a>

#### access

`bunkr: >> access <secret name> (optional: <mode>);`

The access command recomposes the data securely stored in Bunkr on your local machine. The access command will only succeed if the device requesting access actually has permission to do so.

The optional mode argument specifies how to output the retrieved data. There are three options:

- `b64` which will return the data as a base64 encoded string
- `text` which assumes the data to be text and encodes it as a utf-8 string.
- `file <path to file>` which will write the data as a file (and saved to the path specified).

#### confirm-signin

`bunkr: >> confirm-signin <email> <confirmation code>;`

Second part of Sign In process for a new device running the CLI (for first part see `signin` command).

The 8 digit `confirmation code` should have been emailed to you after a proper signin command. `email` must be the address where the confirmation code was received.

#### create

`bunkr: >> create <secret name> <secret type>;`

The create command is a low level command (use `new-file-secret`/`new-text-secret`/etc. instead unless you have a good reason). It creates a new namespace in Bunkr without writing any data to Bunkr yet.

The possible secret types are: 
- GENERIC-GF256 (used for text)
- ECDSA-P256 (used for ssh keys)
- ECDSA-SECP256k1 (used for bitcoin keys)

After a `create` a coalition expects the next operation to be a `write` to fully initialize the secret (see `write` command).

#### delete

`bunkr: >> delete <secret name>;`

Delete completely removes a secret from Bunkr. This includes all information about permissions, and any secret data. This operation is only permitted for an Admin on the secret.

#### grant

`bunkr: >> grant <device name> <secret name> (optional: <admin flag>);`

Grant installs a new capability on a bunkr secret.

When creating a new bunkr secret the device used, and that device alone, has unlimited permissions on the secret. It can access the data, overwrite it, and change or extend the permissions arbitrarily. To grant permission for any other device on a secret you’ll first have to know other devices (see: receive-device).

Here you are granting permission to the specified device on the specified secret. The optional `admin` flag specifies whether the permission is admin level or not. Admin level permissions means that this new device will also be able to alter permissions and overwrite the secret. Without the admin flag the permission is access-only (in the case of text secrets) or to signature-only (in the case of ssh keys). Here is an example of granting admin capabilities:

`bunkr: >> grant “Home Computer” myBitcoinKey admin;`

Now the device “Home Computer” would be able to query, overwrite, and add permissions to the secret myBitcoinKey. If you are not an admin on a secret then a grant operation will fail (you are not authorized to change the permissions, so the operation will not be executed)

Grant operations always output links in case you want to send that capability along to the apropriate devices.

#### import-ssh-key

`bunkr: >> import-ssh-key <secret name> <path to private key file>;`

Import ssh key takes a local PEM ecdsa-p256 private key file and stores the key as a Bunkr secret.

#### list-devices

`bunkr: >> list-devices;`

This command lists all the devices known to your bunkr

#### list-groups

`bunkr: >> list-groups;`

This command lists all the groups known to your bunkr

#### list-secrets

`bunkr: >> list-secrets;`

This command lists all the secrets known to your bunkr. The secrets are categorized by which devices or groups have permissions on them e.g.

```
bunkr: >> list-secrets;
Your Secrets:
    myGroup (type ECDSA-P256)
myGroup Secrets:
    password (type GENERIC-GF256)
    serverKey (type ECDSA-P256)
```

#### new-file-secret

`bunkr: >> new-file-secret <secret name> <path to file>;`

This command stores a local file directly into Bunkr (the size limit is currently ~1MB).

#### new-group

`bunkr: >> new-group <group name>;`

A group is an intermediary Private Key stored in Bunkr which is used to group a number of Bunkr Secrets under a single capability. If you grant a group capability on a secret this means the group key has the capability to query that secret. In this way, if you grant a device capability on the Group Private Key, that device immediately inherits access to all the secrets attached to the group. 

Create a group private key:
`bunkr: >> new-group myGroup;`

Grant a group capability on a secret:
`bunkr: >> grant myGroup <secret name>;`

Grant a device capability on a group:
`bunkr: >> grant <device name> myGroup;`

Note that operations to grouped secrets have a computational cost because it means performing Bunkr operations from the device to the group private key (to get signatures on the requests to the actual secret of interest) and then finally executing the Bunkr operation on the secret of interest (which is attached to that group).

#### new-ssh-key 

`bunkr: >> new-ssh-key <secret name>;`

Store an ssh key (an ecdsa private key on nist-p256 curve) as a bunkr secret.

#### new-text-secret

`bunkr: >> new-text-secret <secret name> <text>;`

Store a basic text secret (e.g. a password).

The `secret name` is just a reference name for your stored secret data. `text` can be any set of utf-8 symbols that you want to store as a secret.

If you want to include spaces in the command arguments then frame them with quotes. For example:

`bunkr: >> new-text-secret “Visa Credit Card” “9999 8888 7777 6666 05/23 Jonathan Martin”;`

#### receive-capability

`bunkr: >> receive-capability <url> (optional: <custom secret name>);`

Import a capability granted to you. If the capability is a group secret all the inherited capabilities will also be automatically imported.

#### receive-device

`bunkr: >> receive-device <url> (optional: <custom device name>);`

Store information about a third party device. This will store the device information locally, under the provided device name (optional parameter). If no name is provided it will default to the name the user gave the device on sending it.

If using an unshortened "raw" link make sure to keep the link with surrounded double quotes or it may have issues being parsed by the cli.

#### remove-local

`bunkr: >> remove-local <secret name>;`

Stop tracking a secret in your bunkr (without removing the secret from bunkr entirely).

Bunkr will not allow you to remove a secret without deleting it if you are the only admin on the secret (to avoid phantom secrets that exist but are irretreivable by any clients)

#### rename

`bunkr: >> rename <old name> <new name>;`

Rename a secret or device. All Bunkr secrets and devices have unique file identifiers that never change, but the human readable reference names to secrets are arbitrary and can be changed at any time.

To avoid confusion secrets cannot share the same reference names. When receiving capabilities, if the secrets being received have the same name as existing secrets the operation will fail, and in this case the rename function may becomes necessary (rename the existing secret and then the import will succeed).

#### reset-triples

`bunkr: >> reset-triples <secret name>;`

In the (unlikely) case that a bunkr key you use is having trouble executing valid signatures it may be that the Secure Triple Shares which provide randomness to every signature computation are not synched across the nodes (this can happen if a node dies exactly during signature execution). 

This operation will flush the existing Triple Shares and resync the nodes so signatures can succeed again. It will only work if all the nodes are back online (since we want to sync them). This command does not alter or reveal anything about the secret values in Bunkr so anyone with capability (admin or not) can execute this.

#### revoke

`bunkr: >> revoke <device name> <secret name>;`

This command completely removes a device's permissions on a secret. If a device has been compromised, no longer exists, or you simply don’t want it to have capabilities on a secret anymore you can revoke their access. If you are not an admin on the secret then the revoke operation will fail.

#### send-device

`bunkr: >> send-device (optional: <custom device name>);`

Send your Bunkr Device information.

This will output a link which you can send by any means (sms, email etc.) to any other desired device running Bunkr. The optional argument is to give your device a custom name. For example:

`bunkr: >> send-device “John’s Work Computer”;`

THe output link comes in two forms a shortened url which is more portable but only lasts 24hrs and a raw url which is long and ugly but lasts forever.

#### signin

`bunkr: >> signin <email> <device name>;`

First part of Sign In process for a new device running the CLI (for second part see `confirm-signin` command).

A confirmation code will be sent to whatever `email` you provide (the code will be verified in `confirm-signin`). `device name` is just any identifier you choose for your device. ANy device that is signed in under this email address will be considered part of the same Bunkr account.

#### write

`bunkr: >> write <secret name> <mode> <data>;`

The write command is used to write (or overwrite) data to a Bunkr Secret. Execute:

The possible mode and data combinations are:
- `b64 <base 64 encoded data>`
- `text <utf-8 string>`

As an example we can use the create and write commands to store a Bitcoin Private Key in Bunkr:

```
bunkr: >> create myBitcoinKey ECDSA-SECP256k1;
bunkr: >> write myBitcoinKey b64 3ABFM/7485746283498BFAC/2==;
```

Note in the above example that when writing ECDSA keys manually (either NIST-P256 or SECP256k1 curves) the content of the secret is expected to be the raw big endian bytes of the secret multiplier of the private key (encoded in base64 or utf-8)
