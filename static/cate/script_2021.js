$(function() {
	var p = $("<div>")
	.addClass("popup-photo")
	.attr("style", "position:fixed; left:0; right:0; top:0; bottom:0; background-color:rgba(0, 0, 255, 0.4); background-position:center; background-size:contain; background-repeat:no-repeat;")
	.append(
		$("<div>")
		.addClass("fermer")
		.click(function() {
			$(this).parent().hide("fade").css("background-image", "");
			$("body").css("overflow", "");
		})
	)
	.hide()
	.appendTo("body");
	$("body").on("click", "img", function(evt) {
		p.show("fade").css("background-image", "url(" + $(evt.target).attr("src") + ")");
		$("body").css("overflow", "hidden");
	});
    $(window).on("keydown", function(evt) {
        if(evt.keyCode == 27) {
            p.hide("fade");
			$("body").css("overflow", "");
		}
	});
});