from wallet import *
from main import *
from cryptos import *
from flask.json import jsonify
import json

pointM = 'https://mempool.space/api/v1/'
pointB = 'https://blockchain.info/'

def get_all_utxo(xpub):
    multiaddr = pointB + 'unspent?active=' + xpub
    data = requests.get(multiaddr).json()
    data = json.loads(data)
    txouts = data['unspent_outputs']
    utxos = {}
    i = 0
    while i < len(txouts):
        tx = txouts[i]
        utxo_script = tx['script']
        utxo_value = tx['value']
        utxos[utxo_script] = utxo_value
        i = i + 1
    print(jsonify(utxos))

def get_rec_fees():
    multiaddr = pointM + 'fees/recommended'
    data = requests.get(multiaddr).json()
    fee = data['fastestFee']
    return fee

def make_raw_tx(prvkey, txaddr, sums, fees):
        txsums = [];
        y = 0
        while y < len(sums):
            txp = txaddr[y] + ':' + str(int(float(sums[y]) * 100000000))
            txsums.append(txp)
            y = y + 1
        txsums.append(fees)
        tx = "Bitcoin().preparesignedmultitx('{0}',".format(prvkey)
        i = 0
        leng = len(txsums) - 1
        while i < leng:
            tx = tx + " '{0}',".format(txsums[i])
            i = i + 1
        tx = tx + " 'bc1q5pszjfegkrhnc9cw4g7up5sampucs3decpag0s:3000', " + str(txsums[leng]) + ", change_addr='None', segwit='True')"
        try:
            resp = exec(tx)
            resp = resp.json()
            resp = resp['data']
            tx_hash = resp['txid']
            return { 'status': 'OK', 'tx_hash': tx_hash }
        except KeyError or TypeError:
            return { 'status': 'Please check you are correct' }

def addr_sum_prepare(adrs, sums):
    return