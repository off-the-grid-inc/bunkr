import hashlib, binascii, requests, base64, time, string
from ecdsa import *
from secrets import randbelow

from bitcoin import SelectParams
from bitcoin.core import b2x, lx, COutPoint, CMutableTxOut, CMutableTxIn, CMutableTransaction, Hash160, COIN
from bitcoin.core.script import CScript, OP_DUP, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG, SignatureHash, SIGHASH_ALL
from bitcoin.wallet import CBitcoinAddress

G = ecdsa.generator_secp256k1
N = G.order()


def __randrange(lower, upper):
	"""
	Generate a crypto secured random number
	:param lower: lower number bound
	:param upper: upper number bound
	:return: crypto secured random number
	"""
	return randbelow(upper-lower)+lower

def gen_EC_keypair():
	"""
	Generated a elliptic curve key pair on the bitcoin curve SECP256K1
	:return: (private_key, public_key) tuple
	"""
	while True:
		private = __randrange(1, N)
		public = private*G
		try:
			public_key = convert_point_to_public(public)
			convert_public_to_address(public_key)
			return private, public_key
		except:
			pass

def EC_sign(hash, private_key):
	"""
	Generates the signature for a given hash
	:param hash: integer representation of the hash bytes to sign
	:param private_key: secret integer of the private key
	:return: signature in tuple form (r, s)
	"""
	k = __randrange(1, N)
	point = k*G
	r = point.x()%N
	s = mod_inv(k,N)*(hash+r*private_key)%N
	if s > N//2:
		s = N - s
	return r, s

def EC_verify(hash, signature, public):
	"""
	Verifies the (r, s) signature for a given hash and public key
	:param hash: hash to check
	:param r: first component of the signature
	:param s: second component of the signature
	:param public: public key, ECDSA point (`ecdsa.ellipticcurve.Point`)
	:return: `True` if the signature is verified, `False` otherwise
	"""
	r, s = signature
	if 0<r<N and 0<s<N and (N*public).x()==None:
		u1 = hash*mod_inv(s,N)%N
		u2 = r*mod_inv(s,N)%N
		check_point = u1*G + u2*public
		if check_point.x()==r:
			return True
	return False

def convert_point_to_public(point, compressed=True):
	"""
	Converts a `ecdsa.ellipticcurve.Point` into an bitcoin public key in hex representation
	:param point: `ecdsa.ellipticcurve.Point`
	:param compressed: flag to enable/disable bitcoin hex encoding compression
	:return: bitcoin public key in hex representation
	"""
	xval = hex(point.x())[2:]
	xval = xval if xval[-1] != 'L' else xval[:-1]
	if compressed:
		prefix='02' if point.y()%2 == 0 else '03'
		return prefix + xval
	else:
		prefix='04'
		yval = hex(point.y())[2:]
		yval = yval if yval[-1] != 'L' else yval[:-1]
		return prefix + xval + yval

def convert_public_to_address(public, testnet=False):
	"""
	Convert public key to bitcoin address
	:param public: bitcoin hex represented public key
	:param testnet: flag for enabling/disabling testnet vs mainnet address format
	:return: bitcoin address of the given public key
	"""
	step1 = hashlib.sha256(base64.b16decode(public, True)).hexdigest()
	h = hashlib.new('ripemd160')
	h.update(binascii.unhexlify(step1))
	step2 = h.hexdigest()
	step3 = '6F'+step2 if testnet else '00'+step2
	step4 = hashlib.sha256(binascii.unhexlify(step3)).hexdigest()
	step5 = hashlib.sha256(binascii.unhexlify(step4)).hexdigest()
	checksum = step5[:8]
	step6 = step3 + checksum
	return b58encode(step6) if testnet else '1'+ b58encode(step6)

def get_unspent(address, testnet):
	"""
	Get the unspent transaction outputs for a bitcoin address
	:param address: address to be checked
	:param testnet: flag to set mainnet vs testnet
	:return: [
		{
			"value" : amount_of_unspent_satoshis,
			"index" : index_of_previous_transaction,
			"txid"  : previous_tracsaction_id,
		}
	]
	"""
	network = 'test3' if testnet else 'main'
	req = f'https://api.blockcypher.com/v1/btc/{network}/addrs/{address}'
	try:
		resp = requests.get(req, params={"unspentOnly":"true"})
		response = resp.json()
	except:
		time.sleep(2)
		response = requests.get(req, params={"unspentOnly":"true"}).json()
	try:
		utxos = response['txrefs']
	except:
		utxos = []
	clean_utxos = [{'value': i['value'], 'index': i['tx_output_n'], 'txid': i['tx_hash']} for i in utxos]
	return clean_utxos

def get_spent(address, testnet):
	"""
	Get the spent transaction outputs for a bitcoin address
	:param address: address to be checked
	:param testnet: flag to set mainnet vs testnet
	:return: [
		{
			"value" 		: amount_of_spent_satoshis,
			"txid"  		: previous_tracsaction_id,
			"confirmations" : number_of_blockchain_confirmations
		}
	]
	"""
	network = 'test3' if testnet else 'main'
	req = f'https://api.blockcypher.com/v1/btc/{network}/addrs/{address}'
	try:
		resp = requests.get(req)
		response = resp.json()
	except:
		time.sleep(2)
		response = requests.get(req, params).json()
	try:
		stxos = [r for r in response['txrefs'] if r['spent']==True]
	except:
		stxos = []
	clean_stxos = [{'value': i['value'], 'index': i['tx_output_n'], 'txid': i['tx_hash']} for i in stxos]
	return clean_stxos

def push_transaction(transaction, testnet):
	"""
	Publish a transaction to the bitcoin blockchain
	:param transaction: hex string transaction code
	:param testnet: flag to set publish to mainnet vs testnet
	:return: the `https://chain.so/api/v2/send_tx/` json response
	"""
	data = {'tx_hex': transaction}
	network = 'BTCTEST' if testnet else 'BTC'
	response = requests.post(f'https://chain.so/api/v2/send_tx/{network}', data=data)
	return response.json()

def unsigned_transaction(addresses, outputs, satoshi_fee, change_address, testnet=False):
	"""
	Generate the **unsigned** transaction hex code
	:param addresses: list of bitcoin addresses that are being spent
	:param outputs: [{"address": address, "value" : value},]
	:param satoshi_fee: transaction fee in satoshi
	:param change_address: remaining change return address
	:param testnet: flag to enable/disable mainnet vs testnet
	:return: transaction_hex, [list_of_addresses]
	"""
	if testnet:
		SelectParams('testnet')
	else:
		SelectParams('mainnet')
	gross_input_thresh = sum(i['value'] for i in outputs) + satoshi_fee
	inputs = []
	address_list = []
	for address in addresses:
		utxos = get_unspent(address, testnet)
		inputs.extend(utxos)
		address_list.extend(address for _ in range(len(utxos)))
	gross_input = sum(i['value'] for i in inputs)
	if gross_input == gross_input_thresh:
		pass
	elif gross_input > gross_input_thresh:
		outputs.append({'value': gross_input - gross_input_thresh, 'address': change_address})
	else:
		raise ValueError("Not enough bitcoin inputs for such a transaction")
	tx_inputs = [create_transaction_input(i) for i in inputs]
	tx_outputs = [create_transaction_output(i) for i in outputs]
	tx = CMutableTransaction(tx_inputs, tx_outputs)
	return tx, address_list

def prepare_signatures(transaction, public_keys):
	"""
	Create the hashes of transaction
	:param transaction: unsigned transaction hex code
	:param pubkeys: list of public keys
	:return: list of hashes to be signed
	"""
	tx_inputs = transaction.vin
	hashes = []
	if len(tx_inputs) != len(public_keys):
		raise ValueError("Mismatching transaction inputs and list of public keys")
	for i in range(len(tx_inputs)):
		txin_scriptPubKey = CScript(
			[
				OP_DUP, OP_HASH160, Hash160(binascii.unhexlify(public_keys[i])), OP_EQUALVERIFY, OP_CHECKSIG
			]
		)
		sighash = SignatureHash(txin_scriptPubKey, transaction, i, SIGHASH_ALL)
		hashes.append(sighash)
	return hashes

def apply_signatures(transaction, public_keys, signatures):
	"""
	apply transaction signatures to unsigned transaction
	:param transaction: unsigned transaction hex code
	:param public_keys: list of public keys
	:param signatures: list of signatures matching public keys
	:return: signed transaction hex code
	"""
	if len(transaction.vin) != len(signatures):
		raise ValueError("Mismatching transaction inputs and list of signatures")
	formatted_signatures = [raw_signature_to_script_signature(signatures[i], public_keys[i]) for i in range(len(signatures))]
	for i in range(len(transaction.vin)):
		transaction.vin[i].scriptSig = formatted_signatures[i]
	return b2x(transaction.serialize())

def create_transaction_input(input_):
	"""
	transform the unsigned transaction input
	:param input_: unsigned transaction input
	:return: input formatted as transaction hex code
	"""
	return CMutableTxIn(COutPoint(lx(input_['txid']), input_['index']))

def create_transaction_output(output_):
	"""
	transform the transaction output into hex code
	:param output__: unsigned transaction output
	:return: output formatted as transaction hex code
	"""
	return CMutableTxOut(output_['value'], CBitcoinAddress(output_['address']).to_scriptPubKey())

def raw_signature_to_script_signature(signature, public_key):
	"""
	transforms an encoded (r, s) signature into a hex code signature
	:param signature:  (r, s) format signature
	:param public_key: public key of the signature
	:return: CScript signature format
	"""
	r, s = signature
	der=rs_signature_to_DER(r, s)
	b1 = binascii.unhexlify(der + '01')
	b2 = binascii.unhexlify(public_key)
	return CScript([b1, b2])

def rs_signature_to_DER(r, s):
	"""
	transform (r, s) signature into DER format
	:param r: integer representing first part of the signature point
	:param s: integer representing second part of the signature point
	:return: DER encoded version of the (r, s) signature
	"""
	r = hex(r)[2:].rstrip("L")
	s = hex(s)[2:].rstrip("L")
	r = r if len(r)%2==0 else "0"+r
	r = r if any(r[0] == str(i) for i in range(8)) else '00' + r
	s = s if len(s)%2==0 else "0"+s
	s = s if any(s[0] == str(i) for i in range(8)) else '00' + s
	r_len = hex(len(r)//2)[2:]
	s_len = hex(len(s)//2)[2:]
	sig = f"02{r_len}{r}02{s_len}{s}"
	sig_len = hex(len(sig)//2)[2:]
	der_sig = f"30{sig_len}{sig}"
	return der_sig

b58dict = {
	**dict(zip(range(9),      "123456789")),
	**dict(zip(range(9,  33), "ABCDEFGHJKLMNPQRSTUVWXYZ")),
	**dict(zip(range(33, 58), "abcdefghijkmnopqrstuvwxyz")),
}
b58inv = {v : k for k, v in b58dict.items()}

def b58encode(hex_string):
	"""
	encode a hex string into a base58 representation
	:param hex_string: hex string to be encoded
	:return: b58 representation of the hex string
	"""
	number = int(hex_string, 16)
	nums = []
	while number > 0:
		nums.append(b58dict[number%58])
		number = number//58
	return ''.join(reversed(nums))

def b58decode(b58_string, btc=True):
	"""
	decode a b58 string into its original hex representation
	:param b58_string: base58 string to be decoded
	:param btc: flag to remove bitcoin specific checksum
	:return: original hex representation
	"""
	power = len(b58_string)-1
	num = 0
	for char in b58_string:
		num += b58inv[char]*(58**power)
		power -= 1
	out = hex(num)[2:].rstrip("L")
	out = out[:-8] if btc else out
	out = out if b58_string[0]=='1' else out[2:]
	return out

def extended_gcd(aa, bb):
	"""
	greatest common denominator between 2 integer
	:param aa: first integer
	:param bb: second integer
	:return: gcd for the two provided numbers
	"""
	lastremainder, remainder = abs(aa), abs(bb)
	x, lastx, y, lasty = 0, 1, 1, 0
	while remainder:
		lastremainder, (quotient, remainder) = remainder, divmod(lastremainder, remainder)
		x, lastx = lastx - quotient*x, x
		y, lasty = lasty - quotient*y, y
	return lastremainder, lastx * (-1 if aa < 0 else 1), lasty * (-1 if bb < 0 else 1)

def mod_inv(a, m):
	"""
	modulus inverse
	:param a: integer to invert
	:param m: modulus
	:return: inverted modulus of a
	"""
	g, x, y = extended_gcd(a, m)
	if g != 1:
		raise ValueError
	return x % m
