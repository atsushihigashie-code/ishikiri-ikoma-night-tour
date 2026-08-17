/**
 * access-guard.js
 * Include this on every protected page (route-main/*, route-alt/*, route-select.html).
 * If the visitor has not verified a valid access code this session, bounce them
 * to gate.html, preserving the page they were trying to reach via ?next=.
 *
 * Mirrors the pattern used in the Osaka Castle Tour app (see osaka-castle-tour
 * project notes: gate.html sets a sessionStorage flag on success; every
 * protected page must independently check it, or the page is reachable by
 * anyone who guesses/shares the direct URL).
 */
(function () {
  var SESSION_KEY = "nightTourAccessGranted";
  var granted = sessionStorage.getItem(SESSION_KEY) === "true";

  if (!granted) {
    var here = window.location.pathname + window.location.search;
    var gateUrl = computeGateUrl();
    window.location.replace(gateUrl + "?next=" + encodeURIComponent(here));
  }

  function computeGateUrl() {
    // Pages live at /, /route-main/, /route-alt/, /purchase/ — walk up to root.
    var depth = window.location.pathname.replace(/^\//, "").split("/").length - 1;
    var prefix = "";
    for (var i = 0; i < depth; i++) prefix += "../";
    return prefix + "gate.html";
  }
})();
