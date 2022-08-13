from flask import Flask, render_template, url_for, request, jsonify, json
from flask import redirect as redir
from pyxtension import *
from cryptos import *

from wallet import *
from send import *
from mnemonic import Mnemonic
from addresses import *
from txs import *

app = Flask(__name__)
app.secret_key = 'dslpkg1523tiuouh33t7hbpzkvcbhp66453gfdjhhgd12'

b_url = 'https://api.binance.com/api/v3/'
selected_ticker_name = 'BTCUSDT'
mnemo = Mnemonic('english')

def islogged():
    try:
        xpub = session['HDWallet']
        return redir('/main', 302)
    except KeyError:
        return redir('/index', 301)

def new_Mnemonic():
    newmnemonic = mnemo.generate(strength=128)
    return newmnemonic

def ticker_update(ticker_name):
    point = b_url + 'ticker/price'
    ticker_symbol = 'symbol=' + ticker_name
    t = requests.get(point, ticker_symbol)
    ticker_data = t.json()
    tick = ticker_data['price'].split('.')
    return tick[0]

@app.route("/")
@app.route("/index")
def index_template():
    try:
        xpub = session['HDWallet']
        return redir('/main', 302)
    except KeyError:
        return render_template('index.html', ticker_price=ticker_update(selected_ticker_name))

@app.route("/register")
def register_template():
    try:
        xpub = session['HDWallet']
        return redir('/main', 302)
    except KeyError:
        return render_template('register.html', ticker_price=ticker_update(selected_ticker_name), newMnemonic=new_Mnemonic())

@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        req = request.get_json()
        mnemonic_user = req['mnemonic_phrase']
        hdwal = Bitcoin().p2wpkh_p2sh_wallet(mnemonic_user)
        hdwal.keystore.root_derivation = "m/49'/0'/0"
        xpub = hdwal.keystore.xpub
        xprv = hdwal.keystore.xprv
        session['HDWallet'] = xpub
        session['Trash'] = xprv
        session['thumbnails'] = mnemonic_user
        return make_response(redir('/main', 302))
    else:
        return redir('/', 301)

@app.route("/main", methods=["GET", "POST"])
def main_template():
    try:
        xpub = session['HDWallet']
    except KeyError:
        return redir("/", 301)
    addresses = new_addresses()
    data = get_data(xpub)
    balance = get_balance(data)
    balance_in_usd = str(balance * int(ticker_update(selected_ticker_name))).split('.')[0]
    last5tx = get_last_tx(data)
    return render_template("main.html", ticker_price=ticker_update(selected_ticker_name), current1Address=addresses[0], current3Address=addresses[1], currentbAddress=addresses[2], balance=balance, latest5tx=last5tx, curQrcode=addresses[4].decode('utf-8'), convertedBalance=balance_in_usd)


@app.route("/txs", methods=["GET", "POST"])
def txs_template(page=1):
    try:
        xpub = session['HDWallet']
    except KeyError:
        return redir("/", 301)
    addresses = new_addresses()
    data = get_data(xpub)
    balance = get_balance(data)
    balance_in_usd = str(balance * int(ticker_update(selected_ticker_name))).split('.')[0]
    jdata = json.loads(data)
    last20tx = get_all_tx(data, page)
    try:
        pages_count = count_pages(jdata['txs'])
        paginations = pagination(page, pages_count, '/txs/')
        return render_template("txs.html", ticker_price=ticker_update(selected_ticker_name), current1Address=addresses[0], current3Address=addresses[1], currentbAddress=addresses[2], balance=balance, latest20tx=last20tx, curQrcode=addresses[4].decode('utf-8'), pagination=paginations, convertedBalance=balance_in_usd)
    except KeyError:
        paginations = ''
        return render_template("txs.html", ticker_price=ticker_update(selected_ticker_name), current1Address=addresses[0], current3Address=addresses[1], currentbAddress=addresses[2], balance=balance, latest20tx=last20tx, curQrcode=addresses[4].decode('utf-8'), pagination=paginations, convertedBalance=balance_in_usd)


@app.route("/address", methods=["GET", "POST"])
@app.route("/address/<int:page>", methods=["GET", "POST"])
def address_template(page=1):
    try:
        xpub = session['HDWallet']
    except KeyError:
        return redir("/", 301)
    addresses = new_addresses()
    data = get_data(xpub)
    balance = get_balance(data)
    balance_in_usd = str(balance * int(ticker_update(selected_ticker_name))).split('.')[0]
    jdata = json.loads(data)
    full_addresses = get_used_addresses(data, page)
    try:
        pages_count = count_pages(jdata['txs'])
        paginations = pagination(page, pages_count, '/address/')
        return render_template("address.html", ticker_price=ticker_update(selected_ticker_name), current1Address=addresses[0], current3Address=addresses[1], currentbAddress=addresses[2], balance=balance, alladdresses=full_addresses, curQrcode=addresses[4].decode('utf-8'), pagination=paginations, convertedBalance=balance_in_usd)
    except KeyError:
        paginations = ''
        full_addresses = r'<tr class="table-info"><td colspan="2" class="centred">Try to generate new addresses! :)</td></tr>'
        return render_template("address.html", ticker_price=ticker_update(selected_ticker_name), current1Address=addresses[0], current3Address=addresses[1], currentbAddress=addresses[2], balance=balance, alladdresses=full_addresses, curQrcode=addresses[4].decode('utf-8'), pagination=paginations, convertedBalance=balance_in_usd)


@app.route("/address/generate", methods=["GET"])
def generate():
    if request.method == "GET":
        counted = request.args.get('count', type=int)
        types = request.args.get('type', type=int)
        addresses = generateAddrs(counted, types)
        resp_data = { 'new_addrs': addresses }
        return resp_data, 200
    else:
        return redir('/', 301)

@app.route("/send", methods=["GET", "POST"])
def send_template():
    try:
        xpub = session['HDWallet']
    except KeyError:
        return redir("/", 301)
    xprv = session['Trash']
    addresses = new_addresses()
    data = get_data(xpub)
    balance = get_balance(data)
    balance_in_usd = str(balance * int(ticker_update(selected_ticker_name))).split('.')[0]
    recom_fees = get_rec_fees()
    if request.method == "POST":
        txdata = request.get_json()
        txaddr = txdata['addresses']
        sums = txdata['sums']
        fee = int(txdata['fee'])
        xprvp = sha256(xprv)
        tx_id = make_raw_tx(xprvp, txaddr, sums, fee)
        return tx_id, 200
    else:
        return render_template("send.html", ticker_price=ticker_update(selected_ticker_name), current1Address=addresses[0], current3Address=addresses[1], currentbAddress=addresses[2], balance=balance, curQrcode=addresses[4].decode('utf-8'), recComis=recom_fees, convertedBalance=balance_in_usd)

@app.route("/wallet/readdr", methods=["GET"])
def readdr():
    if request.method == "GET":
        press = request.args.get('press', type=int)
        addresses = new_addresses()
        resp_data = { 'legacy': addresses[0], 'segwit': addresses[1], 'bech32': addresses[2], 'variant': addresses[3], 'qrcode': addresses[4].decode('utf-8') }
        return resp_data, 200
    else:
        return redir('/', 301)

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redir('/', 302)

if __name__ == '__main__':
    app.run(host='127.0.0.1')

