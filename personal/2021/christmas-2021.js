$(async function() {
    var response = await fetch("../paroles.lrc")
	var lrc = await response.text();
	var lrc2 = lrc.split("\n").map(function(e) {
		var t = e.match(/^\[(\d{2}):(\d{2}\.\d{2})\]/);
		var l = t ? e.match(/^\[\d{2}:\d{2}\.\d{2}\]\s*(.*)\s*$/)[1] : e;
		return {t: t ? t[1] * 60 + t[2] * 1 : null, l: l};
	}).filter(function(e) {
		return e.t != null;
	});
	lrc2.sort(function(a, b) {
		return a.t - b.t;
	});
	/*
	var lrc3 = [];
	$.each(lrc2, function(i, e) {
		lrc3.push({a: e.t, b: lrc2[i + 1] ? lrc2[i + 1].t : d, l: e.l});
	});
	console.log(lrc3);
	*/
	var audio = $("#musique").eq(0);
	var ct = $("<div>").addClass("paroles").insertBefore("audio");
	var el = $("<div>").addClass("lignes").appendTo(ct);
	var a = audio.clone().appendTo(ct);
	audio.remove();
	el.append($("<div>").attr("data-id", -1).html(""));
	for(var i=0, l=lrc2.length; i<l; i++) {
		el.append($("<div>").attr("data-id", i).html(lrc2[i].l));
	}
	var idp = -2;
	a.on("timeupdate", function(evt) {
		var p = {t: 0, l: ""};
		for(var i=0, l=lrc2.length; i<l; i++) {
			if(lrc2[i].t > this.currentTime) break;
			p = lrc2[i];
		}
		var id = i - 1;
		if($(".act", el).attr("data-id") != id) {
			$(".act", el).removeClass("act");
			var l = $("[data-id=" + id + "]", el).addClass("act");
			var t = l.get(0).offsetTop;
			el.scrollTop(((t - el.get(0).offsetTop) + l.height() / 2) - el.height() / 2);
		}
		idp = id;
	});
});
