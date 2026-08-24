// Lowers the background music volume while any narration (.stop-audio) is
// playing, and restores it when narration pauses or ends. Fades smoothly
// rather than jumping, so the transition isn't jarring.

(function () {
  var BGM_NORMAL_VOLUME = 0.35;
  var BGM_DUCKED_VOLUME = 0.08;
  var FADE_STEP_MS = 40;
  var FADE_STEPS = 12;

  document.addEventListener("DOMContentLoaded", function () {
    var bgm = document.querySelector(".bgm-audio");
    if (!bgm) return;

    bgm.volume = BGM_NORMAL_VOLUME;

    // Some browsers block autoplay with sound until the user has interacted
    // with the page. If autoplay was blocked, retry on the first tap/click.
    var tryPlay = function () {
      var p = bgm.play();
      if (p && typeof p.catch === "function") {
        p.catch(function () {
          document.addEventListener("click", function onceClick() {
            bgm.play().catch(function () {});
            document.removeEventListener("click", onceClick);
          });
        });
      }
    };
    tryPlay();

    var fadeTo = function (target) {
      var start = bgm.volume;
      var diff = target - start;
      var step = 0;
      clearInterval(bgm._fadeTimer);
      bgm._fadeTimer = setInterval(function () {
        step++;
        bgm.volume = Math.max(0, Math.min(1, start + diff * (step / FADE_STEPS)));
        if (step >= FADE_STEPS) clearInterval(bgm._fadeTimer);
      }, FADE_STEP_MS);
    };

    var narrationTracks = document.querySelectorAll(".stop-audio");
    if (!narrationTracks.length) return;

    narrationTracks.forEach(function (track) {
      track.addEventListener("play", function () {
        fadeTo(BGM_DUCKED_VOLUME);
      });
      track.addEventListener("pause", function () {
        fadeTo(BGM_NORMAL_VOLUME);
      });
      track.addEventListener("ended", function () {
        fadeTo(BGM_NORMAL_VOLUME);
      });
    });
  });
})();
