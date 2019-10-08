# Bunkr Wallet

Bunkr Wallet is a simple bitcoin wallet application built on top of Bunkr. In utilizing Bunkr our wallet shifts the paradigm of cryptocurrency wallet security: private keys are distributedly stored in Bunkr and transaction signatures are securely generated without ever recomposing the private key on *any* device. The wallet is a bare bones proof of concept which can be controlled easily through a python interactive terminal. 

Disclaimer: This wallet is in beta and under rapid development. Demo the wallet with testnet coins, and never publish generated transactions without decoding and looking them over first!

Notes: 
- Private keys are stored across a distributed set of machines as Bunkr secrets and never touch your local machine (after creation).
- In order to create a wallet or send funds from a wallet, the Bunkr RPC must be running in the background.
- Bunkr Wallet is *not* an HD (heirarchical deterministic) wallet as wallet addresses are in no way correlated or derived from a master seed. One can add more addresses to the wallet keyring at anytime.
- A wallet stores all public wallet information in a simple json file. It stores addresses, public keys, and reference to Bunkr secrets (for communicating with the private key distributed across remote servers). While your private keys will still be safe and secure, losing the wallet file can make it a pain to recover funds from your wallet.

## Installation

Install the Bunkr Wallet (and all underlying requirements) with:

`pip install bunkrwallet`

## Usage

To start using bunkrwallet python library run:

```
$ python3
>>> from bunkrwallet import BunkrWallet
>>> bw = BunkrWallet()
```

## Tutorial: create and use a testnet wallet

In this tutorial we will create a testnet bitcoin wallet, and use it to receive and send bitcoins.

### Requirements

1. Bunkr binary (download here)
2. Bunkr Daemon Running (see here)
3. Python bunkrwallet (`pip install bunkrwallet`)

### Step 1: Initialize the BunkrWallet

```
$ python3
>>> from bunkrwallet import BunkrWallet, COIN
>>> bw = BunkrWallet()
```

### Step 2: Create a testnet wallet

```
>>> wallet = bw.create_wallet("testnetWallet", testnet=True)
'creating new wallet...'
>>> wallet.show_fresh_address()
<prints an unused address in your wallet, for receiving>
```

### Step 3: Receive testnet bitcoin

Testnet bitcoins can be found at a testnet faucet such as: https://coinfaucet.eu/en/btc-testnet/
(Input the testnet address printed from Step 2 and click "Get Bitcoins!")

You can see the transaction has succeeded by returning to the python terminal (you may have to wait a few minutes for transaction to have confirmations):
```
>>> wallet.show_balance()
<shows total wallet balance>
```

### Step 4: Send testnet bitcoin

When creating a bitcoin transaction specify the transaction outputs in this format:

`[{"address": <bitcoin address>, "value": <number of satoshis>}, ...]`

To easily convert between BTC and satoshis use (bitcoin core standard) `COIN` variable.

```
>>> outputs = [{"address":<some address>, "value":0.01*COIN}]
>>> fee = 0.0001*COIN
>>> wallet.send(outputs, fee)
<prints transaction hex which can be pushed to the blockchain>
```

## BunkrWallet Docs

### BunkrWallet class methods

```>>> bw = BunkrWallet()```

Creates an instance of the BunkrWallet.

Optional parameters (don't change these unless you know what you are doing):

- `directory_name` is the name of the BunkrWallet directory (where all wallet files are stored). Default to `.BunkrWallet`
- `bunkr_address` is the socket address of the bunkr daemon. Defaults to `/tmp/bunkr_daemon.sock`
- `bunkr_path` is the path to your local bunkr directory. Defaults to `~/.bunkr`

#### create_wallet

```>>> w = bw.create_wallet("your-wallet-name")```

Creates a wallet instance and the file `your-wallet-name.json` in the BunkrWallet directory.

Optional parameter

- `testnet` is a boolean flag for either bitcoin testnet or mainnet (defaults to False, i.e. mainnet)

#### list_wallets

```
>>> bw.list_wallets()
['your-wallet-name', 'your-other-wallet-name', ...]
```

Lists all the wallet names in the BunkrWallet directory.

#### get_wallet

`>>> w = bw.get_wallet("your-wallet-name")`

Gets Wallet instance with the name "your-wallet-name" from the BunkrWallet.

### Wallet class methods

#### show_balance

`>>> w.show_balance()`

Prints the total balance of the wallet.

#### show_fresh_address

`>>> w.show_fresh_address()`

Shows an unused address on the wallet keyring. Use this method to get an address for receiving bitcoin. If there are no fresh addresses left in the wallet it will raise an error (to overcome this error see add_addresses)

#### send

`>>> w.send([{"address": <address 1>, "value": <satoshi amount to address 1}, ...], <fee amount>)`

Returns the signed transaction hex of a new bitcoin transaction. It is left to the user to publish the transaction.

#### add_addresses

`>>> w.add_addresses(<number of addresses>)`

Adds an amount of addresses to the wallet keyring.
