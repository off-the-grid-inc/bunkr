# Bunkr Wallet

Bunkr Wallet is a simple bitcoin wallet application built on top of Bunkr. In utilizing Bunkr our wallet shifts the paradigm of cryptocurrency wallet security: private keys are distributedly stored in Bunkr and transaction signatures are securely generated without ever recomposing a bitcoin private key on *any* device. The wallet is a bare bones proof of concept with a simple cli.

Disclaimer: This wallet is in beta and under development. Demo the wallet with testnet coins, and never publish generated transactions without decoding and looking them over first!

Notes: 
- Private keys are stored across a distributed set of machines as Bunkr secrets and never touch your local machine (after creation).
- In order to create a wallet or send funds from a wallet, the Bunkr Daemon must be running in the background.
- Bunkr Wallet is *not* an HD (heirarchical deterministic) wallet as wallet addresses are in no way correlated or derived from a master seed. One can add more addresses to the wallet keyring at any time.
- A wallet stores all public wallet information in a simple json file. It stores addresses, public keys, and reference to Bunkr secrets (for communicating with the private key distributed across remote servers). While your private keys will still be safe and secure in your Bunkr, losing the wallet json file can make it a pain to recover the wallet.

## Installation

Install Bunkr Wallet (and all underlying requirements) with:

```
$ pip install bunkrwallet
```

Verify installation with

```
$ bunkr-wallet list-wallets
Available wallets:
[]
```

## Usage

Bunkr Wallet can be used with the `bunkr-wallet` commnad line interface. For now the possible commands are very simple:

1. `list-wallets` (see the names of your different bunkr wallets)
2. `new-wallet` (create a bunkr wallet)
3. `check-balance` (check the balance of a bunkr wallet)
4. `get-address` (get a receiving address for a bunkr wallet)
5. `transaction` (send bitcoin from a bunkr wallet)

Most notably, when signing transactions, the wallet communicates with Bunkr to sign without ever recomposing the private key on any device.

## Tutorial: create and use a testnet wallet from the command line

In this tutorial we will create a testnet bitcoin wallet, and use it to receive and send bitcoin.

### Requirements

1. Bunkr binary ([download here](https://github.com/off-the-grid-inc/bunkr/releases))
2. Bunkr Daemon Running ([see here](https://github.com/off-the-grid-inc/bunkr#-bunkr-cli-configuration-))
3. Python bunkrwallet (`pip install bunkrwallet`)

#### Step 1: Create a testnet wallet

```
$ bunkr-wallet new-wallet --name myTestWallet --testnet
Creating new wallet...
Wallet created
```

### Step 2: Get an address for receiving tBTC

```
$ bunkr-wallet get-address --wallet myTestWallet
Receive address:
nfeVwF1taoNGJpT2ozRpuqpYqp37t42SMy
```

### Step 3: Receive testnet bitcoins (for free, from a faucet)

Testnet bitcoins can be found at a testnet faucet such as: https://coinfaucet.eu/en/btc-testnet/
(Input the testnet address printed from Step 2 and click "Get Bitcoins!")

You can see the transaction has succeeded (you may have to wait a few minutes for transaction to have at least one confirmation):
```
$ bunkr-wallet check-balance --wallet myTestWallet
Balance:
myTestWallet current balance: 0.03142 BTC
```

### Step 4: Send testnet bitcoin

```
$ bunkr-wallet transaction --wallet myTestWallet --address <recipient address> --amount <# satoshi to send> --fee <# satoshi as fee>
Transaction hex:
0100000001a82a36b753ba281b9ef86423648cbddbf3c6890d6f7ccd122af46b9b86937845000000006b483045022100f4e7a6d3b64357ef054ddb0644b81347c85622f05ea7c8471d65447d4bc36f5902207e867f6c138ec9ff5aba0cebcf0b59a3075afa6820614562374751ba30eafeef01210325f5fcee27815e9e273322862cf1d9b7bb5604c403010292a56f59c3c45dfd55ffffffff02e8030000000000001976a914344a0f48ca150ec2b903817660b9b68b13a6702688ac2b8c2f00000000001976a9143bb42f5f9586e5f2a33dfd3a0b40d2bd016731d588ac00000000
```

## BunkrWallet Docs

Bunkr wallet can also be controlled through a python console directly, and has extended functionality than the simple command line interface.

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
