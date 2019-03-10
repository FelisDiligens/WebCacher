function getURL() {
    // var regex = /(^|[\s.:;?\-\]<\(])(https?://[-\w;/?:@&=+$\|\_.!~*\|'()\[\]%#,☺]+[\w/#](\(\))?)(?=$|[\s',\|\(\).:;?\-\[\]>\)])/;
    var regex = /[-a-zA-Z0-9@:%_\+.~#?&//=]{2,256}\.[a-z]{2,4}\b(\/[-a-zA-Z0-9@:%_\+.~#?&//=]*)?/gi;
    var url = $("input[type=text]").val();
    if (url.trim().length == 0) {
        $("input[type=text]").addClass("red");
        return null;
    } else if (regex.test(url)) {
        if (url.indexOf("://") >= 0)
            url = url.substring(url.indexOf("://") + 3);
        return "/cache/" + url;
    } else {
        return "/cache/www.google.com/search?q=" + encodeURIComponent(url);
    }
}

function proceed() {
    var url = getURL();
    if (url)
        window.open(url, "_blank");
}

$(document).ready(function(){
    $("input[type=text]").click(function(e) {
        $("input[type=text]").removeClass("red");
    });
    $("input[type=text]").keypress(function(e) {
        if(e.which == 13)
            proceed();
    });
    $("input[type=button]").click(function(e) {
        proceed();
    });
});
