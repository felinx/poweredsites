var email_reg = /^[_\.0-9a-zA-Z+-]+@([0-9a-zA-Z]+[0-9a-zA-Z-]*\.)+[a-zA-Z]{2,4}$/;
var name_reg = /^([_0-9a-zA-Z]){4,40}$/;

function ck_email() {	
	var email =  $("#email");
	var email_n = $("#email_n");
	email_n.fadeOut();
	var r = 1;
	var s = email.attr('value');
	if (!s) {
		r = 0;
		email_n.fadeIn();
	} else if (!email_reg.exec(s)) {
		email_n.html('Email address is invalid.');
		email_n.fadeIn();
		r = 0;
	} else {		
		email_n.fadeOut();
		var url = '/user/check';
		try {
			$.postJSON(url, {"email":s}, function(j) {
				if (j.r) {
					r = 1;
				} else {					
					email_n.html(s + ' has been registered as an accont.');
					email_n.fadeIn();
					r = 0;
				}
			});
		} catch (e) {
			//
		}		
	}
	return r;
};

function ck_name() {
	var name =  $("#username");
	var name_n = $("#username_n");
	var r = 1;
	var s = name.attr('value');
	if (!s) {
		name_n.fadeIn();
		r = 0;
	} else if (s.length < 4) {
		name_n.html('Not less than four characters.');
		name_n.fadeIn();
		r = 0;
	} else if (s.length > 40)
	{
		name_n.html('Not more than forty characters.');
		name_n.fadeIn();
		r = 0;
	}
	else if (!name_reg.exec(s)) {
		name_n.html('This value must contain only letters, numbers and underscores.');
		name_n.fadeIn();
		r = 0;
	} else {		
		s = s.toLowerCase();
	}

	if (1 == r) {
		var url = '/user/check';
		$.postJSON(url, {"username":s}, function(j) {
			if (j.r) {
				name_n.fadeOut();
				r = 1;
			} else {
				name_n.html(s + ' has been registered as an accont.');
				name_n.fadeIn();
				r = 0;
			}
		});
	}
	return r;
};

function ck_agree() {
	r = false;
	if (null == oo("agree"))
	{		
		/ * edit profile */
		return true;
	}
	s = $("#agree").attr("checked");
	if (s) {
		$("#agree_n").fadeOut();
		r = true;
	} else {
		$("#agree_n").fadeIn();		
	}	
	return r;
};