/* global YT */

$(function() {
	var popupPhoto = $("<div>")
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
	$("body").on("click", "img", function() {
		popupPhoto.show("fade").css("background-image", "url(" + $(this).attr("src") + ")");
		$("body").css("overflow", "hidden");
	});
    $(window).on("keydown", function(evt) {
        if(evt.keyCode == 27) {
            popupPhoto.hide("fade");
			$("body").css("overflow", "");
		}
	});

	// https://maxl.us/hide-related

	// Activate only if not already activated
	if(window.hideYTActivated)
		return;
	// Load API
	if(typeof YT === "undefined")
		$("<script>").attr("src", "https://www.youtube.com/iframe_api").insertBefore($("script").first());

	// Activate on all players
	var ytAPIReadyCallbacks = [];
	$(".hytPlayerWrap").each(function(_i, playerWrap) {
		var playerFrame = playerWrap.find("iframe").get(0);

		function onPlayerStateChange(event) {
			if(event.data == YT.PlayerState.ENDED) {
				playerWrap.classList.add("ended");
			} else if(event.data == YT.PlayerState.PAUSED) {
				playerWrap.classList.add("paused");
			} else if(event.data == YT.PlayerState.PLAYING) {
				playerWrap.classList.remove("ended");
				playerWrap.classList.remove("paused");
			}
		}

		var player;
		ytAPIReadyCallbacks.push(function() {
			player = new YT.Player(playerFrame, {events: {onStateChange: onPlayerStateChange}});
		});

		playerWrap.on("click", function() {
			var playerState = player.getPlayerState();
			if(playerState == YT.PlayerState.ENDED)
				player.seekTo(0);
			else if(playerState == YT.PlayerState.PAUSED)
				player.playVideo();
		});
	});

	window.onYouTubeIframeAPIReady = function() {
		for(var callback of ytAPIReadyCallbacks)
			callback();
	};

	window.hideYTActivated = true;
});