from main import *
from addresses import *
from wallet import *
import json

def txs_way(data):
    txs_ways = []
    i = 0
    while i < len(data):
        if data[i] > 0:
            x = 1
            txs_ways.append(x)
        else:
            x = 0
            txs_ways.append(x)
        i = i + 1
    return txs_ways

def row_color(way):
    color = []
    y = 0
    while y < len(way):
        if way[y] == True:
            color.append('<tr class="table-success">')
        else:
            color.append('<tr class="table-danger">')
        y = y + 1
    return color

def make_tx_table(count, sum, way, address, date, block, txid):
    colors = row_color(way)
    table = ''
    y = 0
    get_curblock = requests.get(pointB + 'latestblock').json()
    curblock = get_curblock['height']
    while y < count:
        temp = '<td>{0}</td><td class="tabletx"><a class="tabletx" href="https://mempool.space/tx/{1}" target="_blank">{1}</a></td><td>{2}</td><td>{3}</td><td>{4}</td></tr>'
        table = table + str(colors[y]) + temp.format(str(sum[y]), txid[y], address[y], str(dt.fromtimestamp(date[y])), str(curblock - block[y]))
        y = y + 1
    return table

def get_last_tx(jdata):
    data = json.loads(jdata)
    try:
        txs = data['txs']
        wallet = data['wallet']
        lasttxaddresses = []
        lasttxsum = []
        lasttxdate = []
        lasttxid = []
        ways = []
        block_heights = []
        if wallet['n_tx'] > 0:
            i = 0
            while i < 5:
                curtx = txs[i]
                out = curtx['out']
                zero = out[0]
                lasttxaddresses.append(zero['addr'])
                lasttxsum.append(np.format_float_positional(float(curtx['result'] / 100000000), trim='-'))
                ways.append(curtx['result'])
                lasttxdate.append(curtx['time'])
                block_heights.append(curtx['block_height'])
                lasttxid.append(curtx['hash'])
                i = i + 1
            lasttxway = txs_way(ways)
            return make_tx_table(5, lasttxsum, lasttxway, lasttxaddresses, lasttxdate, block_heights, lasttxid)
        else:
            return r'<tr class="table-info"><td colspan="5" class="centred">You have no transactions yet</td></tr>'
    except KeyError:
        return r'<tr class="table-info"><td colspan="5" class="centred">You have no transactions yet</td></tr>'


def get_all_tx(jdata, page):
    data = json.loads(jdata)
    try:
        txs = data['txs']
        wallet = data['wallet']
        items = page * 20
        if wallet['n_tx'] != 0:
            txadresses = []
            txdates = []
            tx_block_heights = []
            ways = []
            txsum = []
            txids = []
            y = items - 20
            while y < items:
                curtx = txs[y]
                out = curtx['out']
                zero = out[0]
                txadresses.append(zero['addr'])
                txsum.append(np.format_float_positional(float(curtx['result'] / 100000000), trim='-'))
                ways.append(curtx['result'])
                txdates.append(curtx['time'])
                tx_block_heights.append(curtx['block_height'])
                txids.append(curtx['hash'])
                y = y + 1
            txsways = txs_way(ways)
            table = make_tx_table(20, txsum, txsways, txadresses, txdates, tx_block_heights, txids)
            return table
        else:
            return r'<tr class="table-info"><td colspan="5" class="centred">You have no transactions yet</td></tr>'
    except KeyError:
        return r'<tr class="table-info"><td colspan="5" class="centred">You have no transactions yet</td></tr>'

