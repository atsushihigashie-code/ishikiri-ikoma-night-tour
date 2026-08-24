// Lowers the background music volume while any narration (.stop-audio) is
// playing, and restores it when narration pauses or ends. Fades smoothly
// rather than jumping, so the transition isn't jarring.
//
// NOTE: iOS Safari ignores JS-set values on <audio>.volume (it always plays
// at 1.0 and only the hardware buttons change it), so simply setting
// bgm.volume — which works fine on desktop/Android — has no effect on
// iPhone. To duck reliably everywhere, the BGM element is routed through
// the Web Audio API (AudioContext -> GainNode -> destination) and we fade
// the gain instead. Gain changes DO work on iOS. If Web Audio isn't
// available for some reason, this falls back to the old .volume approach.

(function () {
  var BGM_NORMAL_VOLUME = 0.35;
  var BGM_DUCKED_VOLUME = 0.08;
  var FADE_STEP_MS = 40;
  var FADE_STEPS = 12;

  document.addEventListener("DOMContentLoaded", function () {
    var bgm = document.querySelector(".bgm-audio");
    if (!bgm) return;

    var AudioContextClass = window.AudioContext || window.webkitAudioContext;
    var gainNode = null;
    var audioCtx = null;

    if (AudioContextClass) {
      try {
        audioCtx = new AudioContextClass();
        var source = audioCtx.createMediaElementSource(bgm);
        gainNode = audioCtx.createGain();
        gainNode.gain.value = BGM_NORMAL_VOLUME;
        source.connect(gainNode).connect(audioCtx.destination);
      } catch (e) {
        // Some browsers throw if createMediaElementSource is unsupported or
        // called twice; just fall back to element.volume in that case.
        audioCtx = null;
        gainNode = null;
      }
    }

    if (!gainNode) {
      bgm.volume = BGM_NORMAL_VOLUME;
    }

    // Some browsers block autoplay with sound (and/or keep the AudioContext
    // suspended) until the user has interacted with the page. Retry / resume
    // on the first tap/click if that happens.
    var tryPlay = function () {
      if (audioCtx && audioCtx.state === "suspended") {
        audioCtx.resume().catch(function () {});
      }
      var p = bgm.play();
      if (p && typeof p.catch === "function") {
        p.catch(function () {
          document.addEventListener("click", function onceClick() {
            if (audioCtx && audioCtx.state === "suspended") {
              audioCtx.resume().catch(function () {});
            }
            bgm.play().catch(function () {});
            document.removeEventListener("click", onceClick);
          });
        });
      }
    };
    tryPlay();

    var fadeTo = function (target) {
      if (gainNode) {
        var start = gainNode.gain.value;
        var diff = target - start;
        var step = 0;
        clearInterval(bgm._fadeTimer);
        bgm._fadeTimer = setInterval(function () {
          step++;
          gainNode.gain.value = Math.max(0, Math.min(1, start + diff * (step / FADE_STEPS)));
          if (step >= FADE_STEPS) clearInterval(bgm._fadeTimer);
        }, FADE_STEP_MS);
      } else {
        var startVol = bgm.volume;
        var diffVol = target - startVol;
        var stepVol = 0;
        clearInterval(bgm._fadeTimer);
        bgm._fadeTimer = setInterval(function () {
          stepVol++;
          bgm.volume = Math.max(0, Math.min(1, startVol + diffVol * (stepVol / FADE_STEPS)));
          if (stepVol >= FADE_STEPS) clearInterval(bgm._fadeTimer);
        }, FADE_STEP_MS);
      }
    };

    var narrationTracks = document.querySelectorAll(".stop-audio");
    if (!narrationTracks.length) return;

    narrationTracks.forEach(function (track) {
      track.addEventListener("play", function () {
        if (audioCtx && audioCtx.state === "suspended") {
          audioCtx.resume().catch(function () {});
        }
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
