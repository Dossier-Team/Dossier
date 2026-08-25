/* ============================================================
   DOSSIER — landing interactions
   1) Enroll forms: client-side validation + STUBBED submit
   2) Scroll reveals
   ============================================================ */
(function () {
  "use strict";
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* -------- 1. ENROLL FORMS (stubbed) -------- */
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  var DIGITS_RE = /\d/g;

  function setError(input, msgEl, message) {
    if (message) {
      input.setAttribute("aria-invalid", "true");
      msgEl.textContent = message;
      msgEl.hidden = false;
    } else {
      input.removeAttribute("aria-invalid");
      msgEl.textContent = "";
      msgEl.hidden = true;
    }
    return !message;
  }

  function validate(form) {
    var email = form.querySelector('input[name="email"]');
    var phone = form.querySelector('input[name="phone"]');
    var consent = form.querySelector('input[name="consent"]');
    var errEmail = form.querySelector('[id$="-email"].field-error, [id*="err"][id*="email"]');
    var errPhone = form.querySelector('[id*="err"][id*="phone"]');
    var errConsent = form.querySelector('[id*="err"][id*="consent"]');

    var ok = true;
    ok = setError(email, errEmail, EMAIL_RE.test(email.value.trim()) ? "" : "Enter a valid email address.") && ok;

    var digits = (phone.value.match(DIGITS_RE) || []).length;
    ok = setError(phone, errPhone, digits >= 10 ? "" : "Enter a valid mobile number.") && ok;

    if (!consent.checked) {
      if (errConsent) { errConsent.textContent = "Please agree to continue."; errConsent.hidden = false; }
      consent.setAttribute("aria-invalid", "true");
      ok = false;
    } else if (errConsent) {
      errConsent.textContent = ""; errConsent.hidden = true; consent.removeAttribute("aria-invalid");
    }
    return { ok: ok, email: email, values: { email: email.value.trim(), phone: phone.value.trim() } };
  }

  function wireForm(form) {
    var plate = form.closest(".enroll");
    // clear errors as the user fixes them
    form.addEventListener("input", function (e) {
      var t = e.target;
      if (t.matches('input[name="email"]')) setError(t, form.querySelector('[id*="err"][id*="email"]'), "");
      if (t.matches('input[name="phone"]')) setError(t, form.querySelector('[id*="err"][id*="phone"]'), "");
      if (t.matches('input[name="consent"]') && t.checked) {
        var ec = form.querySelector('[id*="err"][id*="consent"]');
        if (ec) { ec.hidden = true; ec.textContent = ""; }
        t.removeAttribute("aria-invalid");
      }
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var res = validate(form);
      if (!res.ok) {
        var firstBad = form.querySelector('[aria-invalid="true"]');
        if (firstBad) firstBad.focus();
        return;
      }
      var btn = form.querySelector(".enroll__submit");
      if (btn) { btn.disabled = true; btn.textContent = "Enrolling…"; }

      // ---- STUB: no backend connected yet ----
      // TODO: replace this block with a POST to the real enrollment endpoint,
      // e.g. fetch('/api/enroll', { method:'POST', body: JSON.stringify(res.values) })
      // On success, reveal the confirmation panel below.
      console.log("[dossier] enroll (stub) →", res.values);
      setTimeout(function () {
        if (plate) plate.classList.add("is-done");
        var ok = plate && plate.querySelector(".enroll__ok");
        if (ok) { var h = ok.querySelector("h2"); if (h) { h.setAttribute("tabindex", "-1"); h.focus(); } }
      }, 420);
    });
  }

  document.querySelectorAll("form[data-enroll]").forEach(wireForm);

  /* -------- 2. SCROLL REVEALS -------- */
  // reveal only where the motion carries meaning (the sequence, the logic,
  // the index assembling) — not as an identical entrance on every section.
  var revealables = [".steps > *", ".thesis__point", ".ledger__row"];
  var nodes = [];
  revealables.forEach(function (sel) {
    document.querySelectorAll(sel).forEach(function (n) { n.classList.add("reveal"); nodes.push(n); });
  });
  if (!reduceMotion && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          var el = en.target;
          var sibs = Array.prototype.slice.call(el.parentNode.children).filter(function (c) { return c.classList.contains("reveal"); });
          var i = sibs.indexOf(el);
          el.style.transitionDelay = Math.min(i, 5) * 70 + "ms";
          el.classList.add("in");
          io.unobserve(el);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });
    nodes.forEach(function (n) { io.observe(n); });
  } else {
    nodes.forEach(function (n) { n.classList.add("in"); });
  }
})();
