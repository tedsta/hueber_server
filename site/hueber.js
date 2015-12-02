function send_image() {
	alert("Called `send_image()`");
}


function toggleFullScreen() {
	var flag = document.getElementById("flag");
	if (!document.mozFullScreen && !document.webkitFullScreen) {
		if (flag.mozRequestFullScreen) {
			alert(flag);
			flag.mozRequestFullScreen();
		} else {
			flag.webkitRequestFullScreen(Element.ALLOW_KEYBOARD_INPUT);
		}
	} else {
		if (document.mozCancelFullScreen) {
			document.mozCancelFullScreen();
		} else {
			document.webkitCancelFullScreen();
		}
	}
}
