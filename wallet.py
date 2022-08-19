import json
import base58
import qrcode
from qrcode import *
from qrcode.image import svg
import requests
from config import *
from hdwallet import *
from hdwallet import HDWallet as HDW
from hdwallet.symbols import BTC
from datetime import datetime as dt
from cryptos import *
from txs import *
from flask import session

pointB = 'https://blockchain.info/'


def new_addresses():
    xpub = session['xp']
    hdwallet = HDW(symbol=BTC)
    hdwallet = hdwallet.from_xpublic_key(xpub)
    hdwallet.from_index(49, hardened=False)
    hdwallet.from_index(0, hardened=False)
    hdwallet.from_index(0, hardened=False)
    hdwallet.from_index(6)
    r_factor = random.randrange(20, 100)
    hdwallet.from_index(r_factor)
    addresses = []
    addresses.append(hdwallet.p2pkh_address())
    addresses.append(hdwallet.p2wsh_in_p2sh_address())
    addresses.append(hdwallet.p2wpkh_address())
    addresses.append(r_factor)
    session['1a'] = addresses[0]
    session['3a'] = addresses[1]
    session['bca'] = addresses[2]
    return addresses


def preqrcode():
    preqr = qrcode.make(session['3a'], image_factory=qrcode.image.svg.SvgPathImage).to_string()
    return preqr.decode('utf-8')


def get_data(xpub):
    multiaddr = pointB + 'multiaddr?active=' + xpub
    data = requests.get(multiaddr).json()
    return str(json.dumps(data))


def get_balance(hdata):
    data = json.loads(hdata)
    try:
        wallet = data['wallet']
        balance = wallet['final_balance']
        return balance / 100000000
    except KeyError:
        return 0.00000000


def count_pages(data):
    page = 20
    if len(data) > page:
        page_count = len(data) / page
        return page_count
    else:
        return 1


def pagination(page, pages_count, prefix):
    if page == pages_count and page != 1:
        pagination_e = "<ul class='pagination'><li class='page-item'><a class='page-link' href='{2}{0}'>{0}</li><li class='page-item active'><a class='page-link' href='{2}{1}'>{1}</li></ul>".format(page - 1, page, prefix)
        return pagination_e
    elif pages_count == 2 and page == 1:
        pagination_e = "<ul class='pagination'><li class='page-item'><a class='page-link' href='{2}{0}'>{0}</li><li class='page-item active'><a class='page-link' href='{2}{1}'>{1}</li></ul>".format(page, page + 1, prefix)
        return pagination_e
    elif pages_count == 1 and page == 1:
        pagination_e = "<ul class='pagination'><li class='page-item-active'><a class='page-link' href='{1}{0}'>{0}</li></ul>".format(page, prefix)
        return pagination_e
    else:
        pagination_e = "<ul class='pagination'><li class='page-item'><a class='page-link' href='{3}{0}'>{0}</li><li class='page-item active'><a class='page-link' href='{3}{1}'>{1}</li><li class='page-item'><a class='page-link' href='{3}{2}'>{2}</li></ul>".format(page - 1, page, page + 1, prefix)
        return pagination_e
