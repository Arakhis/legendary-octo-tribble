// Write JavaScript here 
function showLoginField() {
    var str = document.createElement('input');
        str.id = 'mnemo';
        str.className = 'form-control input-lg';
        str.setAttribute('value', '');
    var row = document.getElementById('indexlogo');
        row.appendChild(str);
    var str2 = '<a role="button" class="btn btn-default btn-lg log" href="/main" id="logBtn" onclick="login()">Login</a>';
    var Obj2 = document.getElementById('logBtn');
    Obj2.outerHTML=str2;
}

function changeBtn() {
var saved_checker = document.getElementById('saved');
var reg_login = document.getElementById('logBtn');
    if (saved_checker.checked == true) {
    reg_login.outerHTML='<a role="button" class="btn btn-primary btn-lg log" href="/main" id="logBtn" onclick="login()">Login</a>';
    } else {
    reg_login.outerHTML='<a role="button" class="btn disabled btn-default btn-lg log" href="/main" id="logBtn" onclick="login()">Login</a>';
    }
}

function login() {
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
        var su = suma[i].value;
        addrList.push(ad);
        sumaList.push(su);
    };
    var nkhi = $.ajax({
        type: "POST",
        url: "/send",
        async: false,
        contentType: "application/json",
        data: JSON.stringify({ "addresses": addrList, "sums": sumaList, "fee": fee })
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
        lovBtn.setAttribute('onclick', 'generateAddrs()')
        lovBtn.className = 'btn btn-warning';
        lovBtn.innerHTML = '<img src="https://github.com/google/material-design-icons/raw/master/src/device/settings_suggest/materialiconsoutlined/24px.svg">';
    var lovBtnDiv = document.createElement('div');
        lovBtnDiv.id = 'genBtn';
        lovBtnDiv.className = 'col-2';
        lovBtnDiv.innerHTML = lovBtn.outerHTML;
    var genAddr = document.getElementById('gen-addr');
    var count = document.getElementById('count').value;
    var Stype = document.getElementById('script-type').value;
    var genAgain = $.getJSON('/address/generate', { 'count': count, 'type': Stype }, async function(data, textStatus, jqXHR){
            var textnode = document.createElement('textarea');
            textnode.setAttribute('wrap', 'hard');
            textnode.setAttribute('rows', count);
            textnode.className = 'form-text generated-addresses';
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
}

