from bunkrwallet import *

home_address = "mfeVwF1taoNGJpT2ozRpuqpYqp37t42SMy"
home_priv = 694343405282129039542598971331539029274109233570545233614611141232816475682
home_pub = "04d3941d56cf6d43363e2a5a4c130583ffafb996d310ae2cab613fd41abf80c648168b919b6e9d9bed132330322c524cb5bd9d7503879c16a476c8ef1b4727d7d2"

def send_from_home(testnet_address):
	tx, alist = unsigned_transaction([home_address, ], [{"address": testnet_address, "value":int(0.01*COIN)}], 10000, home_address, testnet=True)
	pubkeys = [home_pub for _ in range(len(alist))]
	hashes = [int(binascii.hexlify(i), 16) for i in prepare_signatures(tx, pubkeys)]
	sigs = [EC_sign(h, home_priv) for h in hashes]
	signed = apply_signatures(tx, pubkeys, sigs)
	return push_transaction(signed, True)

def test_wallet():
	bw = BunkrWallet()
	w = bw.create_wallet("test", testnet=True)
	print("wallet created")
	resp = send_from_home(w.wallet[0]["address"])
	print(f"wallet funded: {resp}")
	time.sleep(2)
	signed = w.send([{"address":home_address, "value":int(0.0099*COIN)}], int(0.0001*COIN))
	print(f"wallet created transaction: {signed}")
	resp = push_transaction(signed, True)
	print(f"wallet pushed transaction: {resp}")
	bw.delete(w)
	print(f"wallet deleted")

if __name__ == "__main__":
	if os.path.exists(os.path.join(DEFAULT_WALLET_DIR, "test.json")):
		os.remove(os.path.join(DEFAULT_WALLET_DIR, "test.json"))
	test_wallet()
	print("PASS!")