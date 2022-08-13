import json
from wallet import *
from cryptos import *
from flask import session
from hdwallet import *
from txs import *
from hdwallet.symbols import BTC

def get_used_addresses(jdata, page):
    data = json.loads(jdata)
    try:
        wallet = data['wallet']
        items = page * 20
        if wallet['n_tx'] > 0:
            txs = data['txs']
            table = r''
            txaddresses = []
            i = items - 20
            while wallet['n_tx'] > i < items:
                curtx = txs[i]
                out = curtx['out']
                zero = out[0]
                txaddresses.append(zero['addr'])
                i = i + 1
            q = 0
            txaddresses = set(txaddresses)
            while q < len(txaddresses):
                table = table + '<tr><td>Used</td><td><a href="https://mempool.space/address/{0}" target="_blank">{0}</a></td></tr>'.format(
                    txaddresses[q])
                q = q + 1
            return table
        else:
            return ''
    except KeyError:
        return r'<tr class="table-info"><td colspan="2" class="centred">You have no used addresses yet. Try to generate new ones!</td></tr>'


def generateAddrs(count, type):
    xpub = session['HDWallet']
    hdwallet = HDWallet(symbol=BTC)
    hdwallet = hdwallet.from_xpublic_key(xpub)
    hdwallet.from_index(49, hardened=False)
    hdwallet.from_index(0, hardened=False)
    hdwallet.from_index(0, hardened=False)
    hdwallet.from_index(7)
    if type == 1:
        addrs = []
        while len(addrs) < count:
            hdwallet.from_index(len(addrs))
            addrs.append(hdwallet.p2pkh_address())
        return addrs
    elif type == 2:
        addrs = []
        while len(addrs) < count:
            hdwallet.from_index(len(addrs))
            addrs.append(hdwallet.p2wpkh_address())
        return addrs
    else:
        addrs = []
        while len(addrs) < count:
            hdwallet.from_index(len(addrs))
            addrs.append(hdwallet.p2wsh_in_p2sh_address())
        return addrs


