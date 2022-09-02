from btclib import b58, b32
from btclib.bip32.bip32 import derive
from flask import session
from flask_babel import gettext
import json

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
        return r'<tr class="table-info"><td colspan="2" class="centred">' + gettext('You have no used addresses yet. Try to generate new ones!') + '</td></tr>'


def generateAddrs(count, type):
    xpub = session['mpub']
    n = 20
    deriv_path = 'm/86/1/15/0/'
    if type == 1:
        addrs = []
        while len(set(addrs)) < count:
            der_xpub = derive(xpub, deriv_path + str(n))
            addrs.append(b58.p2wpkh_p2sh(der_xpub, network='testnet'))
            n = n + 1
        return addrs
    elif type == 2:
        addrs = []
        while len(set(addrs)) < count:
            der_xpub = derive(xpub, deriv_path + str(n))
            addrs.append(b32.p2wpkh(der_xpub, network='testnet'))
            n = n + 1
        return addrs
    else:
        addrs = []
        while len(set(addrs)) < count:
            der_xpub = derive(xpub, deriv_path + str(n))
            addrs.append(b32.p2tr(der_xpub, network='testnet'))
            n = n + 1
        return addrs


