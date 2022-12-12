
function login() {
    var mnemo = document.getElementById('mnemo').innerHTML;
    const seed = bip39.mnemonicToSeed(mnemo);
	const hdKey = bip32.fromSeed(seed);
	let xpub = hdKey.neutered().toBase58();
	sessionStorage.setItem("mpub", xpub);
    window.location = "main.html";
}

function register() {
    const mnemo = bip39.generateMnemonic();
    $("#regBtn").hide();
    if (document.contains(document.getElementById('mnemo'))){
        $("#mnemo").remove();
    }
    var str = document.createElement('input');
        str.id = 'mnemo';
        str.className = 'form-text';
        str.setAttribute('value', mnemo);
        str.setAttribute('rows', 4);
        str.innerHTML = mnemo;
    var row = document.getElementById('indexlogo');
        row.appendChild(str);
    document.getElementById('logBtn').setAttribute("onclick", "login()");
}

function changeLang(value) {
        $.getJSON('/lang', { 'lang': value }, function(data, textStatus, jqXHR){
            if (data.success == 'true') {
                location.reload();
            }
        });
}

function showLoginField() {
    var str = document.createElement('input');
        str.id = 'mnemo';
        str.className = 'form-text';
        str.setAttribute('value', '');
        str.setAttribute('rows', 4);
    var row = document.getElementById('indexlogo');
        row.appendChild(str);
    document.getElementById('logBtn').onclick = "login()";
}

function changeBtn() {
var saved_checker = document.getElementById('saved');
var reg_login = document.getElementById('logBtn');
    if (saved_checker.checked == true) {
    reg_login.className = 'btn btn-primary btn-lg log';
    } else {
    reg_login.className = 'btn btn-primary disabled btn-lg log';
    }
}



function trlogin() {
    var mnemo = document.getElementById('mnemo');
    var asklog = $.ajax({
        type: "POST",
        url: "/login",
        async: false,
        contentType: "application/json",
        data: JSON.stringify({ 'mnemonic_phrase': mnemo.value })
    });
}

function addAddrNew(no) {
    var addrdiv = document.getElementById('rec-addresses');
    var sumdiv = document.getElementById('rec-sums');
    var addbtn = document.getElementById('moreAddr');
    var btndiv = document.getElementById('addrBtns');
    if (no == 9) {
        const addrinput = document.createElement('input');
        addrinput.type = 'text';
        addrinput.className = 'form-control';
        addrinput.id = 'to_address' + no;
        addrinput.setAttribute('placeholder', 'Address');
        addrinput.value = '';
        addrdiv.appendChild(addrinput);
        const suminput = document.createElement('input');
        suminput.type = 'text';
        suminput.className = 'form-control';
        suminput.id = 'sum' + no;
        suminput.setAttribute('placeholder', 'Value');
        suminput.value = '';
        sumdiv.appendChild(suminput);
        const deleteAddrBtn = document.createElement('button');
        deleteAddrBtn.type = 'button';
        deleteAddrBtn.className = 'btn btn-danger moreAddr';
        deleteAddrBtn.id = 'del' + no;
        deleteAddrBtn.setAttribute("onclick", 'deleteAddr(' + no + ')');
        deleteAddrBtn.innerHTML = '<img src="https://github.com/google/material-design-icons/raw/master/src/navigation/cancel/materialiconsoutlined/24px.svg">';
        btndiv.appendChild(deleteAddrBtn);
        addbtn.outerHTML = '<button type="button" class="btn btn-primary moreAddr" id="moreAddr" onclick=""><img src="https://github.com/google/material-design-icons/raw/master/src/editor/add_comment/materialiconsoutlined/24px.svg"></button>';
    } else {
        const addrinput = document.createElement('input');
        addrinput.type = 'text';
        addrinput.className = 'form-control';
        addrinput.id = 'to_address' + no;
        addrinput.setAttribute('placeholder', 'Address');
        addrinput.value = '';
        addrdiv.appendChild(addrinput);
        const suminput = document.createElement('input');
        suminput.type = 'text';
        suminput.className = 'form-control';
        suminput.id = 'sum' + no;
        suminput.setAttribute('placeholder', 'Value');
        suminput.value = '';
        sumdiv.appendChild(suminput);
        const deleteAddrBtn = document.createElement('button');
        deleteAddrBtn.type = 'button';
        deleteAddrBtn.className = 'btn btn-danger moreAddr';
        deleteAddrBtn.id = 'del' + no;
        deleteAddrBtn.setAttribute("onclick", 'deleteAddr(' + no + ')');
        deleteAddrBtn.innerHTML = '<img src="https://github.com/google/material-design-icons/raw/master/src/navigation/cancel/materialiconsoutlined/24px.svg">';
        btndiv.appendChild(deleteAddrBtn);
        addbtn.outerHTML = '<button type="button" class="btn btn-primary moreAddr" id="moreAddr" onclick="addAddrNew(' + (no + 1) + ')"><img src="https://github.com/google/material-design-icons/raw/master/src/editor/add_comment/materialiconsoutlined/24px.svg"></button>';
    }
}



function deleteAddr(no) {
    var addr = document.getElementById('to_address' + no);
    var sum = document.getElementById('sum' + no);
    var btn = document.getElementById('del' + no);
    addr.remove();
    sum.remove();
    btn.remove();
}

function calcFees() {
    var fee = document.getElementById('set_comis').innerHTML;
    const addrList = [];
    var addrCont = document.getElementById('rec-addresses');
    const addrs = addrCont.querySelectorAll('*[id^="to_address"]');
    const sumaList = [];
    var sumaCont = document.getElementById('rec-sums');
    const suma = sumaCont.querySelectorAll('*[id^="sum"]');
    for (var i = 0; i < suma.length; i++) {
        var ad = addrs[i].value;
        var su = parseInt(suma[i].value);
        addrList.push(ad);
        sumaList.push(su);
    };
    var nkhi = $.ajax({
        type: "POST",
        url: "/send",
        async: false,
        contentType: "application/json",
        data: JSON.stringify({ "addresses": addrList, "sums": sumaList, "fee": fee }),
        success: function (data, textStatus, jqXHR){
            var place = document.getElementById('mancon');
            if (data.vsize > 0){
                var sendbtn = document.getElementById('sendbtn');
                    sendbtn.className = 'btn-lg btn-warning centred';
                    sendbtn.setAttribute('onclick', 'send()');
                var rawtxhidden = document.createElement('span');
                    rawtxhidden.className = 'visually-hidden';
                    rawtxhidden.id = 'rawtx';
                    rawtxhidden.innerHTML = data.raw_tx;
                place.parentNode.insertBefore(rawtxhidden, place);
                var txsize = document.getElementById('txsize');
                    txsize.innerHTML = data.vsize;
                var totalfee = document.getElementById('totalFee');
                    totalfee.value = ((data.vsize * fee + 3000) / 1e-10);
            } else {
                var alert = document.createElement('div');
                    alert.className = 'alert alert-danger';
                    alert.setAttribute('role', 'alert');
                    alert.innerHTML = 'Please check you are correct!';
                place.parentNode.insertBefore(alert, place);
            }
        }
    });
}


function send() {
    var raw_tx = { 'tx': document.getElementById('rawtx').innerHTML };
    $.post('https://api.blockcypher.com/v1/bcy/test/txs/push', JSON.stringify(raw_tx))
        .then(function(d) {
            if (d.confirmations == 0) {
                var link_tx = document.createElement('a');
                    link_tx.href = 'https://mempool.space/ru/tx/' + d.hash;
                    link_tx.innerHTML = 'Explorer';
                var place = document.getElementById('mancon');
                var alert = document.createElement('div');
                    alert.className = 'alert alert-success';
                    alert.setAttribute('role', 'alert');
                    alert.innerHTML = 'Transaction successfully sent!' + link_tx.outerHTML;
                place.parentNode.insertBefore(alert, place);
            } else {
                var place = document.getElementById('mancon');
                var alert = document.createElement('div');
                    alert.className = 'alert alert-danger';
                    alert.setAttribute('role', 'alert');
                    alert.innerHTML = 'Please check you are correct!';
                place.parentNode.insertBefore(alert, place);
            }
        });
}




function changeAddrs() {
    var variant = document.getElementById('changeAddrsBtn').value;
    var cur1 = document.getElementById('cur1');
    var cur3 = document.getElementById('cur3');
    var curb = document.getElementById('curb');
    var qrkod = document.getElementById('curQR');
    var asknew = $.getJSON('/wallet/readdr', { 'press': variant }, function(data, textStatus, jqXHR){
            cur1.innerHTML = data.legacy;
            cur3.innerHTML = data.segwit;
            curb.innerHTML = data.bech32;
            variant = data.variant;
            qrkod.innerHTML = data.qrcode;
    });
}

function generateAddrs() {
    var count = document.getElementById('count').value;
    if (count == null) {
        alert('Please enter amount');
        return false;
    } else {
    var span4 = document.createElement('span');
        span4.className = 'visually-hidden';
        span4.innerHTML = 'Loading...';
    var loading = document.createElement('div');
        loading.id = 'loadingGen';
        loading.className = 'spinner-border text-light col-2';
        loading.setAttribute('role', 'status');
        loading.innerHTML = span4.outerHTML;
    var divBtn = document.getElementById('genBtn');
    divBtn.outerHTML = loading.outerHTML;
    var lovBtn = document.createElement('button');
        lovBtn.setAttribute('type', 'button');
        lovBtn.setAttribute('onclick', 'generateAddrs(used=true)');
        lovBtn.className = 'btn btn-info';
        lovBtn.setAttribute('style', 'width:100%;')
        lovBtn.innerHTML = '<img src="https://github.com/google/material-design-icons/raw/master/src/device/settings_suggest/materialiconsoutlined/24px.svg">';
    var lovBtnDiv = document.createElement('div');
        lovBtnDiv.id = 'genBtn';
        lovBtnDiv.className = 'col-2';
        lovBtnDiv.innerHTML = lovBtn.outerHTML;
    var genAddr = document.getElementById('gen-addr');
    var Stype = document.getElementById('script-type').value;
    var genAgain = $.getJSON('/address/generate', { 'count': count, 'type': Stype }, function(data, textStatus, jqXHR){
            if (used == true){
            document.getElementById('generated-addresses').remove();
            }
            var textnode = document.createElement('textarea');
            textnode.setAttribute('wrap', 'hard');
            textnode.setAttribute('rows', count);
            textnode.className = 'form-text generated-addresses';
            textnode.id = 'generated-addresses';
            textnode.setAttribute('col', '35');
            addrs = JSON.stringify(data.new_addrs);
            adres = addrs.replace(/,/g, '\n');
            adrs = adres.replace(/"/g, '');
            adr = adrs.replace(/\[/g, '');
            adro = adr.replace(/\]/g, '');
            textnode.innerHTML = adro;
            var now = document.getElementById('loadingGen');
            now.outerHTML = lovBtnDiv.outerHTML;
            genAddr.appendChild(textnode);
            });
    };
}



//////////////////////////// Ajax Part
// Update main ticker
$(document).ready(function(){
    $.getJSON('https://api.binance.com/api/v3/ticker/price', {'symbol': 'BTCUSDT'}, function(data, textStatus, jqXHR){
        $("#ticker").text(data.price.split(".")[0]);
    });
    if (window.location == "/main"){
    } else if (window.location == "/address"){
    } else if (window.location == "/txs"){
    } else if (window.location == "/send"){
    } else if (window.location != "/index" && window.location != "/register"){
    }
});


//