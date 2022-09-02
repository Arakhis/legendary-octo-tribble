import json
import random
import requests
import qrcode

from btclib.bip32.bip32 import rootxprv_from_seed, xpub_from_xprv, NETWORKS, derive
from btclib import b32, b58
from cryptos.mnemonic import mnemonic_to_seed
from flask import session
from flask import redirect as redir
from mnemonic import Mnemonic
from qrcode.image import svg

pointB = 'https://blockchain.info/'
b_url = 'https://api.binance.com/api/v3/'


def islogged():
    try:
        assert session['mpub']
        return redir('/main', 302)
    except AssertionError:
        return redir('/index', 301)


def new_mnemonic():
    mnemo = Mnemonic('english')
    return mnemo.generate(strength=128)


def ticker_update(ticker_name):
    point = b_url + 'ticker/price'
    ticker_symbol = 'symbol=' + ticker_name
    t = requests.get(point, ticker_symbol)
    ticker_data = t.json()
    tick = ticker_data['price'].split('.')
    return tick[0]


def init_wallet():
    seed = mnemonic_to_seed(session['ph'])
    session['mprv'] = rootxprv_from_seed(seed, NETWORKS['mainnet'].bip32_prv)
    session['mpub'] = xpub_from_xprv(session['mprv'])
    return session


def top_addresses():
    r_factor = random.randrange(20, 255)
    pub = derive(session['mpub'], 'm/86/0/4/0/' + str(r_factor))
    addresses = []
    session['p2sh'] = b58.p2wpkh_p2sh(pub, network='mainnet')
    session['p2wpkh'] = b32.p2wpkh(pub, network='mainnet')
    session['p2tr'] = b32.p2tr(pub, network='mainnet')
    addresses.append(session['p2sh'])
    addresses.append(session['p2wpkh'])
    addresses.append(session['p2tr'])
    addresses.append('')
    return addresses


def preqrcode():
    preqr = qrcode.make(session['p2sh'], image_factory=qrcode.image.svg.SvgPathImage).to_string()
    return preqr.decode('utf-8')


def get_data():
    multiaddr = pointB + 'multiaddr?active=' + session['mpub']
    data = requests.get(multiaddr).json()
    return str(json.dumps(data))


def get_balance(jdata):
    data = json.loads(jdata)
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
        pagination_e = "<ul class='pagination'><li class='page-item'><a class='page-link' href='{2}{0}'>{0}</li>\
        <li class='page-item active'><a class='page-link' href='{2}{1}'>{1}</li></ul>".format(page - 1, page, prefix)
    elif pages_count == 2 and page == 1:
        pagination_e = "<ul class='pagination'><li class='page-item'><a class='page-link' href='{2}{0}'>{0}</li>\
        <li class='page-item active'><a class='page-link' href='{2}{1}'>{1}</li></ul>".format(page, page + 1, prefix)
    elif pages_count == 1 and page == 1:
        pagination_e = ''
    else:
        pagination_e = "<ul class='pagination'><li class='page-item'><a class='page-link' href='{3}{0}'>{0}</li>\
        <li class='page-item active'><a class='page-link' href='{3}{1}'>{1}</li><li class='page-item'>\
        <a class='page-link' href='{3}{2}'>{2}</li></ul>".format(page - 1, page, page + 1, prefix)
    return pagination_e