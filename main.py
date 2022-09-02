from addresses import *
from flask import Flask, render_template, request, make_response, session
from flask import redirect as redir
from flask_babel import Babel, gettext
from txs import *
from send import *
from wallet import *

app = Flask(__name__)
app.secret_key = 'dslpkg1523tiuouh33t7hbpzkvcbhp66453gfdjhhgd12'
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
babel = Babel(app)
selected_ticker_name = 'BTCUSDT'

def js_lang():
    script_line = '<script type="text/javascript" src="/static/js/' + get_locale() + '.js"></script>'
    return script_line

@babel.localeselector
def get_locale():
    try:
        session['lang']
        return session['lang']
    except KeyError:
        return 'en'


@app.route("/")
@app.route("/index", methods=["POST"])
def index_template():
    try:
        session['mpub']
        return redir('/main', 302)
    except KeyError:
        return render_template('index.html', ticker_price=ticker_update(selected_ticker_name), script=js_lang())


@app.route("/lang", methods=["GET"])
def chLang():
    if request.method == "GET":
        session['lang'] = request.args.get('lang')
        resp_data = { 'success':'true' }
        return resp_data, 200
    else:
        return 404


@app.route("/register")
def register_template():
    try:
        session['mpub']
        return redir('/main', 302)
    except KeyError:
        return render_template('register.html', ticker_price=ticker_update(selected_ticker_name), newMnemonic=new_mnemonic(), script=js_lang())


@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        req = request.get_json()
        session['ph'] = req['mnemonic_phrase']
        init_wallet()
        top_addresses()
        return make_response('/main', 302)
    else:
        return redir('/', 301)


@app.route("/main", methods=["GET", "POST"])
def main_template():
    try:
        session['mpub']
    except KeyError:
        return redir("/", 301)
    data = get_data()
    balance = get_balance(jdata=data)
    balance_in_usd = str(balance * int(ticker_update(selected_ticker_name))).split('.')[0]
    last5tx = get_all_tx(data, last=True)
    return render_template("main.html", ticker_price=ticker_update(selected_ticker_name), script=js_lang(),
                           current1Address=session['p2sh'], current3Address=session['p2wpkh'], currentbAddress=session['p2tr'],
                           curQrcode=preqrcode(), balance=balance, latest5tx=last5tx, convertedBalance=balance_in_usd)


@app.route("/txs", methods=["GET", "POST"])
def txs_template(page=1):
    try:
        session['mpub']
    except KeyError:
        return redir("/", 301)
    data = get_data()
    balance = get_balance(data)
    balance_in_usd = str(balance * int(ticker_update(selected_ticker_name))).split('.')[0]
    jdata = json.loads(data)
    last20tx = get_all_tx(data, page=page)
    try:
        pages_count = count_pages(jdata['txs'])
        paginations = pagination(page, pages_count, '/txs/')
        return render_template("txs.html", ticker_price=ticker_update(selected_ticker_name), script=js_lang(),
                               current1Address=session['p2sh'], current3Address=session['p2wpkh'], currentbAddress=session['p2tr'],
                               curQrcode=preqrcode(), balance=balance, latest20tx=last20tx, pagination=paginations, convertedBalance=balance_in_usd)
    except KeyError or TypeError:
        paginations = ''
        return render_template("txs.html", ticker_price=ticker_update(selected_ticker_name), script=js_lang(),
                               current1Address=session['p2sh'], current3Address=session['p2wpkh'], currentbAddress=session['p2tr'],
                               curQrcode=preqrcode(), balance=balance, latest20tx=last20tx, pagination=paginations, convertedBalance=balance_in_usd)


@app.route("/address", methods=["GET", "POST"])
@app.route("/address/<int:page>", methods=["GET", "POST"])
def address_template(page=1):
    try:
        session['mpub']
    except KeyError:
        return redir("/", 301)
    data = get_data()
    balance = get_balance(data)
    balance_in_usd = str(balance * int(ticker_update(selected_ticker_name))).split('.')[0]
    jdata = json.loads(data)
    full_addresses = get_used_addresses(data, page)
    try:
        pages_count = count_pages(jdata['txs'])
        paginations = pagination(page, pages_count, '/address/')
        return render_template("address.html", ticker_price=ticker_update(selected_ticker_name), script=js_lang(),
                               current1Address=session['p2sh'], current3Address=session['p2wpkh'], currentbAddress=session['p2tr'],
                               curQrcode=preqrcode(), balance=balance, alladdresses=full_addresses, pagination=paginations, convertedBalance=balance_in_usd)
    except KeyError or TypeError:
        paginations = ''
        full_addresses = r'<tr class="table-info"><td colspan="2" class="centred">' + gettext('Try to generate new addresses! :)') + '</td></tr>'
        return render_template("address.html", ticker_price=ticker_update(selected_ticker_name), script=js_lang(),
                               current1Address=session['p2sh'], current3Address=session['p2wpkh'], currentbAddress=session['p2tr'],
                               curQrcode=preqrcode(), balance=balance, alladdresses=full_addresses, pagination=paginations, convertedBalance=balance_in_usd)


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
        session['mpub']
    except KeyError:
        return redir("/", 301)
    xprv = session['mprv']
    data = get_data()
    balance = get_balance(data)
    balance_in_usd = str(balance * int(ticker_update(selected_ticker_name))).split('.')[0]
    if request.method == "POST":
        txdata = request.get_json()
        txaddr = txdata['addresses']
        sums = txdata['sums']
        fee = int(txdata['fee'])
        raw_tx, vsize = make_raw_tx(xprv, session['mpub'], txaddr, sums, fee)
        resp_data = { 'raw_tx': raw_tx, 'vsize': vsize}
        return resp_data, 200
    else:
        return render_template("send.html", ticker_price=ticker_update(selected_ticker_name), script=js_lang(),
                               current1Address=session['p2sh'], current3Address=session['p2wpkh'], currentbAddress=session['p2tr'],
                               curQrcode=preqrcode(), balance=balance, recComis=get_rec_fees(), convertedBalance=balance_in_usd)


@app.route("/wallet/readdr", methods=["GET"])
def readdr():
    if request.method == "GET":
        press = request.args.get('press', type=int)
        addresses = top_addresses()
        resp_data = { 'legacy': addresses[0], 'segwit': addresses[1], 'bech32': addresses[2], 'variant': addresses[3], 'qrcode': preqrcode() }
        return resp_data, 200
    else:
        return redir('/', 301)


@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redir('/', 302)


if __name__ == '__main__':
    app.run(host='127.0.0.1')
