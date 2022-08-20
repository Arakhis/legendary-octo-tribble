import qrcode.image.svg
from flask import Flask, render_template, url_for, request, jsonify, json, make_response
from flask import redirect as redir
from flask_babel import Babel, gettext
from pyxtension import *
from cryptos import *
from config import *
import qrcode


from wallet import *
from send import *
from mnemonic import Mnemonic
from addresses import *
from txs import *

app = Flask(__name__)
app.secret_key = 'dslpkg1523tiuouh33t7hbpzkvcbhp66453gfdjhhgd12'
babel = Babel(app)
b_url = 'https://api.binance.com/api/v3/'
selected_ticker_name = 'BTCUSDT'
mnemo = Mnemonic('english')


def islogged():
    try:
        xpub = Bitcoin().p2wpkh_p2sh_wallet(session['thumbnails']).keystore.xpub
        return redir('/main', 302)
    except KeyError:
        return redir('/index', 301)


def new_mnemonic():
    return mnemo.generate(strength=128)


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
        xpub = Bitcoin().p2wpkh_p2sh_wallet(session['thumbnails']).keystore.xpub
        return redir('/main', 302)
    except KeyError or TypeError:
        return render_template('index.html', ticker_price=ticker_update(selected_ticker_name))


@app.route("/register")
def register_template():
    try:
        xpub = Bitcoin().p2wpkh_p2sh_wallet(session['thumbnails']).keystore.xpub
        return redir('/main', 302)
    except KeyError or TypeError:
        return render_template('register.html', ticker_price=ticker_update(selected_ticker_name), newMnemonic=new_mnemonic())


@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        req = request.get_json()
        mnemonic_user = req['mnemonic_phrase']
        hdwal = Bitcoin().p2wpkh_p2sh_wallet(mnemonic_user)
        hdwal.keystore.root_derivation = "m/49'/0'/0"
        session['xp'] = hdwal.keystore.xpub
        session['xr'] = hdwal.keystore.xprv
        session['thumbnails'] = mnemonic_user
        new_addresses()
        return make_response('/main', 302)
    else:
        return redir('/', 301)


@app.route("/main", methods=["GET", "POST"])
def main_template():
    try:
        xpub = session['xp']
    except KeyError or TypeError:
        return redir("/", 301)
    data = get_data(xpub)
    balance = get_balance(data)
    balance_in_usd = str(balance * int(ticker_update(selected_ticker_name))).split('.')[0]
    last5tx = get_all_tx(data, last=True)
    return render_template("main.html", ticker_price=ticker_update(selected_ticker_name), current1Address=session['1a'], current3Address=session['3a'], currentbAddress=session['bca'], curQrcode=preqrcode(), balance=balance, latest5tx=last5tx, convertedBalance=balance_in_usd)


@app.route("/txs", methods=["GET", "POST"])
def txs_template(page=1):
    try:
        xpub = session['xp']
    except KeyError or TypeError:
        return redir("/", 301)
    data = get_data(xpub)
    balance = get_balance(data)
    balance_in_usd = str(balance * int(ticker_update(selected_ticker_name))).split('.')[0]
    jdata = json.loads(data)
    last20tx = get_all_tx(data, page=page)
    try:
        pages_count = count_pages(jdata['txs'])
        paginations = pagination(page, pages_count, '/txs/')
        return render_template("txs.html", ticker_price=ticker_update(selected_ticker_name), current1Address=session['1a'], current3Address=session['3a'], currentbAddress=session['bca'], curQrcode=preqrcode(), balance=balance, latest20tx=last20tx, pagination=paginations, convertedBalance=balance_in_usd)
    except KeyError or TypeError:
        paginations = ''
        return render_template("txs.html", ticker_price=ticker_update(selected_ticker_name), current1Address=session['1a'], current3Address=session['3a'], currentbAddress=session['bca'], curQrcode=preqrcode(), balance=balance, latest20tx=last20tx, pagination=paginations, convertedBalance=balance_in_usd)


@app.route("/address", methods=["GET", "POST"])
@app.route("/address/<int:page>", methods=["GET", "POST"])
def address_template(page=1):
    try:
        xpub = session['xp']
    except KeyError or TypeError:
        return redir("/", 301)
    data = get_data(xpub)
    balance = get_balance(data)
    balance_in_usd = str(balance * int(ticker_update(selected_ticker_name))).split('.')[0]
    jdata = json.loads(data)
    full_addresses = get_used_addresses(data, page)
    try:
        pages_count = count_pages(jdata['txs'])
        paginations = pagination(page, pages_count, '/address/')
        return render_template("address.html", ticker_price=ticker_update(selected_ticker_name), current1Address=session['1a'], current3Address=session['3a'], currentbAddress=session['bca'], curQrcode=preqrcode(), balance=balance, alladdresses=full_addresses, pagination=paginations, convertedBalance=balance_in_usd)
    except KeyError or TypeError:
        paginations = ''
        full_addresses = r'<tr class="table-info"><td colspan="2" class="centred">' + gettext('Try to generate new addresses! :)') + '</td></tr>'
        return render_template("address.html", ticker_price=ticker_update(selected_ticker_name), current1Address=session['1a'], current3Address=session['3a'], currentbAddress=session['bca'], curQrcode=preqrcode(), balance=balance, alladdresses=full_addresses, pagination=paginations, convertedBalance=balance_in_usd)


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
        xpub = session['xp']
    except KeyError or TypeError:
        return redir("/", 301)
    xprv = session['xr']
    data = get_data(xpub)
    balance = get_balance(data)
    balance_in_usd = str(balance * int(ticker_update(selected_ticker_name))).split('.')[0]
    if request.method == "POST":
        txdata = request.get_json()
        txaddr = txdata['addresses']
        sums = txdata['sums']
        fee = int(txdata['fee'])
        xprvp = sha256(xprv)
        tx_id = make_raw_tx(xprvp, txaddr, sums, fee)
        return tx_id, 200
    else:
        return render_template("send.html", ticker_price=ticker_update(selected_ticker_name), current1Address=session['1a'], current3Address=session['3a'], currentbAddress=session['bca'], curQrcode=preqrcode(), balance=balance, recComis=get_rec_fees(), convertedBalance=balance_in_usd)


@app.route("/wallet/readdr", methods=["GET"])
def readdr():
    if request.method == "GET":
        press = request.args.get('press', type=int)
        addresses = new_addresses()
        resp_data = { 'legacy': addresses[0], 'segwit': addresses[1], 'bech32': addresses[2], 'variant': addresses[3], 'qrcode': preqrcode() }
        return resp_data, 200
    else:
        return redir('/', 301)


@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redir('/', 302)


if __name__ == '__main__':
    app.run(host='192.168.1.60')
