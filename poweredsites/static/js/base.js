//check general (not null, not special character etc) text or textfield
function checkGeneralTxt(id, txtname, length) {
	var data = $("#" + id).val();
	var regx = /[~!@#$%\^&\*\(\)]/g;
	var err = "";
	var errMsg = "";
	while ((arr = regx.exec(data)) != null)
		err += arr;
	if (err != "") {
		errMsg = (txtname + " " + err.replace(/&/g, "&amp;") + "is not allowed.");
	} else if (/ /g.test(data)) {
		errMsg = txtname + " whitespace is not allowed.";
	} else if (data.length > length) {
		errMsg = txtname + " not more than " + length + "characters.";
	} else {
		errMsg = ""
	}
	return errMsg;
};

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
};

jQuery.postJSON = function(url, args, callback) {
    args._xsrf = getCookie("_xsrf");
    $.ajax({url: url, data: $.param(args), dataType: "text", type: "POST",
        success: function(response) {
        callback(eval("(" + response + ")"));
    }});
};

function oo(id)
{
	return document.getElementById(id);
}