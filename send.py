from main import *
from btclib.script.script_pub_key import *
from bitcoinlib.transactions import *
from bitcoinlib.keys import HDKey
from btclib.bip32.bip32 import derive

pointM = 'https://mempool.space/api/v1/'
pointB = 'https://blockchain.info/'


def get_inputs_and_keys(value, xpub):
    multiaddr = pointB + 'unspent?active=' + xpub
    data = requests.get(multiaddr).json()
    txouts = data['unspent_outputs']
    inputs = []
    paths = []
    i = 0
    c = 0
    while i < value:
        tx = txouts[c]
        input = Input(prev_txid=tx['tx_hash_big_endian'], output_n=tx['tx_output_n'], value=tx['value'])
        inputs.append(input)
        i = i + tx['value']
        c = c + 1
        tx = tx['xpub']
        paths.append(tx['path'])
    return inputs, paths


def get_rec_fees():
    multiaddr = pointM + 'fees/recommended'
    data = requests.get(multiaddr).json()
    fee = data['fastestFee']
    return fee


def make_raw_tx(prvkey, xpub, txaddr, sums, fees):
        inputs, paths = get_inputs_and_keys(sum(sums), xpub)
        outputs = createOutputs(txaddr, sums)
        keys = prepareKeys(paths, prvkey)
        index = get_index(txaddr)
        try:
            if index[0] or index[5]:
                raw_tx = Transaction(inputs, outputs, fee=fees, fee_per_kb=fees)
                raw_tx.sign(keys=keys)
                assert raw_tx.verify() == True
                raw_hex = raw_tx.raw_hex()
                return raw_hex, raw_tx.vsize
            elif index[3] and not index[0]:
                raw_tx = Transaction(inputs, outputs, witness_type='segwit', fee=fees, fee_per_kb=fees)
                raw_tx.sign(keys=keys)
                assert raw_tx.verify() == True
                raw_hex = raw_tx.raw_hex()
                return raw_hex, raw_tx.vsize
            elif index[6] and not index[0]:
                raw_tx = Transaction(inputs, outputs, witness_type='segwit', fee=fees, fee_per_kb=fees)
                raw_tx.sign(keys=keys, hash_type=SIGHASH_SINGLE)
                assert raw_tx.verify() == True
                raw_hex = raw_tx.raw_hex()
                return raw_hex, raw_tx.vsize
            elif index[2] and not index[0] and not index[3]:
                raw_tx = Transaction(inputs, outputs, witness_type='segwit', fee=fees, fee_per_kb=fees)
                raw_tx.sign(keys=keys)
                assert raw_tx.verify() == True
                raw_hex = raw_tx.raw_hex()
                return raw_hex, raw_tx.vsize
            else:
                return [], []
        except KeyError or ValueError or AssertionError:
            return 'Error, check values!'




def get_index(adrs):
    index = [0,0,0,0,0,0,0]
    i = 0
    while i < (len(adrs) - 1):
        c = ScriptPubKey.from_address(adrs[i])
        if c.type == 'p2pkh':
            index[0] = index[0] + 1
        elif c.type == 'p2tr':
            index[1] = index[1] + 1
        elif c.type == 'p2wpkh':
            index[2] = index[2] + 1
        elif c.type == 'p2sh':
            index[3] = index[3] + 1
        elif c.type == 'p2wsh':
            index[4] = index[4] + 1
        elif c.type == 'p2pk':
            index[5] = index[5] + 1
        else:
            index[6] = index[6] + 1
        i = i + 1
    index[2] = index[2] + 1
    return index


def prepareKeys(paths, prvkey):
    keys = []
    i = 0
    while i < len(paths):
        key = derive(prvkey, paths[i])
        hdkey = HDKey.from_wif(key)
        keys.append(hdkey)
        i = i + 1
    return keys


def createOutputs(addr, sums):
    outputs = []
    i = 0
    while i < len(addr):
        output = Output(value=sums[i], address=addr[i])
        outputs.append(output)
        i = i + 1
    return outputs