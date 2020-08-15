$(document).ready(function () {
    var ua = window.navigator.userAgent.toLowerCase();
    if (ua.indexOf('micromessenger') !== -1) {
        $("#wechat-alarm").css("display", "block");
    }
});