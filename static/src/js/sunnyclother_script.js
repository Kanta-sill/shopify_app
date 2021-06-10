const base_url = 'https://odoo.website'

function initJQueryWsap(e) {
    var t;
    "undefined" == typeof jQuery ? ((t = document.createElement("SCRIPT")).src = "https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js", t.type = "text/javascript", t.onload = e, document.head.appendChild(t)) : e()
}

initJQueryWsap(function () {
    if (window.AllFetchURLWsap == undefined) {
        window.AllFetchURLWsap = base_url;
        notifywhatsappthankyoupage();
    } else {
        console.log("Error Window.AllFetchURLWsap");
    }
});

window.notifywhatsappthankyoupage = function () {
    console.log('helllloo sunny')
}