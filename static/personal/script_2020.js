function tourner() {
	var p = document.getElementById("popup_tourner");
	if(!p) return;
	if(screen.orientation.type == "portrait-primary") {
		p.style.display = "block";
	} else {
		p.style.display = "none";
		screen.orientation.lock();
	}
}
var l_etoiles;
function etoiles_init() {
	for(var i=0; i<20; i++) {
		var e = document.createElement("span");
		e.className = "etoile";
		l_etoiles.appendChild(e);
	}
	etoiles();
	setInterval(etoiles, 1000);
}
function etoiles() {
	for(var i=0; i<l_etoiles.children.length; i++) {
		e = l_etoiles.children[i];
		e.style.left = Math.floor(Math.random() * innerWidth) + "px";
		e.style.top = Math.floor(Math.random() * innerHeight) + "px";
		e.style.transform = "rotate(" + Math.floor(Math.random() * 360) + "deg)";
		if(Math.random() < 0.2) {
			e.style.animation = "etoile 2s infinite " + (Math.floor(Math.random() * 100) / 100) + "s";
		}
		e = "";
	}
}

window.addEventListener("DOMContentLoaded", function() {
    let jours = document.querySelectorAll(".jours a");
    for(let jour of jours) {
        jour.classList.add("c" + Math.floor(Math.random() * 7 + 1));
    }
    tourner();
    screen.orientation.addEventListener("change", tourner);
	l_etoiles = document.querySelector(".etoiles");
	if(l_etoiles) etoiles_init();
});
