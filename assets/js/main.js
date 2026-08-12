/* ==========================================================================
   ד"ר אשרף אטמנה - Site behaviour
   Vanilla JS · no dependencies · progressive enhancement
   ========================================================================== */
(function () {
  'use strict';

  var doc = document;
  var root = doc.documentElement;
  var $ = function (sel, ctx) { return (ctx || doc).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || doc).querySelectorAll(sel)); };

  /* ---------------------------------------------------------------- header */
  var header = $('.header');
  if (header) {
    var onScroll = function () {
      header.classList.toggle('is-stuck', window.scrollY > 8);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ------------------------------------------------------- mobile drawer */
  var drawer = $('#drawer');
  var burger = $('#burger');
  if (drawer && burger) {
    var lastFocus = null;

    var openDrawer = function () {
      lastFocus = doc.activeElement;
      drawer.classList.add('is-open');
      drawer.removeAttribute('inert');
      burger.setAttribute('aria-expanded', 'true');
      doc.body.style.overflow = 'hidden';
      // wait a frame: the panel is still visibility:hidden when the class lands
      window.requestAnimationFrame(function () {
        var first = $('.drawer__close', drawer);
        if (first) first.focus();
      });
    };

    var closeDrawer = function () {
      drawer.classList.remove('is-open');
      burger.setAttribute('aria-expanded', 'false');
      doc.body.style.overflow = '';
      window.setTimeout(function () {
        if (!drawer.classList.contains('is-open')) drawer.setAttribute('inert', '');
      }, 380);
      if (lastFocus) lastFocus.focus();
    };

    drawer.setAttribute('inert', '');
    burger.addEventListener('click', function () {
      drawer.classList.contains('is-open') ? closeDrawer() : openDrawer();
    });
    drawer.addEventListener('click', function (e) {
      if (e.target === drawer || e.target.closest('[data-close]')) closeDrawer();
    });
    doc.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && drawer.classList.contains('is-open')) closeDrawer();
    });
    // keep focus inside the open drawer
    drawer.addEventListener('keydown', function (e) {
      if (e.key !== 'Tab') return;
      var f = $$('a[href], button:not([disabled])', drawer).filter(function (el) { return el.offsetParent !== null; });
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && doc.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && doc.activeElement === last) { e.preventDefault(); first.focus(); }
    });
  }

  /* ------------------------------------------------ hash-free in-page links */
  /* Anchors scroll to their section but never write "#..." into the address bar,
     so the URL always stays the clean page URL. Focus still moves to the target,
     so keyboard and screen-reader users keep the normal skip-link behaviour. */
  (function cleanAnchors() {
    var samePage = function (a) {
      return a.hash && a.pathname === location.pathname && a.host === location.host;
    };

    var goTo = function (hash, smooth) {
      var target = null;
      try { target = doc.querySelector(hash); } catch (e) { return false; }
      if (!target) return false;

      if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
      var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
        || root.getAttribute('data-a11y-motion') === '1';
      target.scrollIntoView({ behavior: (smooth && !reduce) ? 'smooth' : 'auto', block: 'start' });
      target.focus({ preventScroll: true });
      return true;
    };

    doc.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[href]');
      if (!a || a.target === '_blank' || e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
      if (!samePage(a)) return;
      if (!goTo(a.hash, true)) return;
      e.preventDefault();
      if (drawer && drawer.classList.contains('is-open')) {
        var close = $('[data-close]', drawer);
        if (close) close.click();
      }
    });

    var strip = function () {
      if (window.history && history.replaceState) {
        history.replaceState(null, '', location.pathname + location.search);
      }
    };

    // arriving with a hash (e.g. from another page): scroll, then drop it from the URL
    var consume = function (smooth) {
      if (!location.hash) return;
      var jump = location.hash;
      window.requestAnimationFrame(function () {
        goTo(jump, smooth);
        strip();
      });
    };

    consume(false);
    // …and if a hash still turns up some other way, clean that too
    window.addEventListener('hashchange', function () { consume(false); });
  }());

  /* ------------------------------------------------- before / after slider */
  $$('.ba').forEach(function (ba) {
    var range = $('.ba__range', ba);
    if (!range) return;
    var apply = function () { ba.style.setProperty('--pos', range.value + '%'); };
    range.addEventListener('input', apply);
    apply();
  });

  /* -------------------------------------------- "show all results" toggle */
  (function moreResults() {
    var btn = $('#moreResults');
    if (!btn) return;
    var hiddenCards = $$('[data-more]');
    if (!hiddenCards.length) { btn.remove(); return; }

    // the label is a bare text node next to the arrow icon
    var setLabel = function (text) {
      var svg = $('svg', btn);
      btn.textContent = text;
      if (svg) btn.appendChild(svg);
    };

    btn.addEventListener('click', function () {
      var open = btn.getAttribute('aria-expanded') === 'true';
      hiddenCards.forEach(function (el) {
        if (open) el.setAttribute('hidden', '');
        else { el.removeAttribute('hidden'); el.classList.add('is-in'); }
      });
      btn.setAttribute('aria-expanded', open ? 'false' : 'true');
      setLabel(btn.getAttribute(open ? 'data-more-label' : 'data-less-label'));
      if (open) {
        var grid = $('#resultsGrid');
        if (grid) grid.scrollIntoView({ block: 'start', behavior: 'smooth' });
      }
    });
  }());

  /* ----------------------------------------------------------- map facade */
  $$('.map__facade').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var map = btn.parentNode;
      var src = btn.getAttribute('data-src');
      if (!src) return;
      var frame = doc.createElement('iframe');
      frame.src = src;
      frame.loading = 'lazy';
      frame.title = btn.getAttribute('data-title') || 'מפה';
      frame.setAttribute('referrerpolicy', 'no-referrer-when-downgrade');
      frame.setAttribute('allowfullscreen', '');
      map.appendChild(frame);
      btn.remove();
    });
  });

  /* -------------------------------------------------------- reveal on scroll */
  var reveals = $$('.reveal');
  if (reveals.length) {
    if (!('IntersectionObserver' in window) || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      reveals.forEach(function (el) { el.classList.add('is-in'); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('is-in');
          io.unobserve(entry.target);
        });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.06 });
      reveals.forEach(function (el, i) {
        el.style.transitionDelay = Math.min(i % 4, 3) * 70 + 'ms';
        io.observe(el);
      });
    }
  }

  /* -------------------------------------------------------------- footer year */
  $$('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });

  /* ---------------------------------------------------- accessibility widget */
  (function a11y() {
    var toggle = $('#a11yToggle');
    var panel = $('#a11yPanel');
    if (!toggle || !panel) return;

    var KEY = 'atamna-a11y';
    var opts = ['font', 'contrast', 'links', 'readable', 'motion'];
    var state = {};

    try { state = JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { state = {}; }

    var render = function () {
      opts.forEach(function (name) {
        var val = state[name] || 0;
        if (val) root.setAttribute('data-a11y-' + name, String(val));
        else root.removeAttribute('data-a11y-' + name);
        var btn = $('[data-a11y="' + name + '"]', panel);
        if (btn) {
          btn.setAttribute('aria-pressed', val ? 'true' : 'false');
          var out = $('[data-a11y-level]', btn);
          if (out) out.textContent = val ? ' (' + val + ')' : '';
        }
      });
      try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) { /* ignore */ }
    };

    var setOpen = function (open) {
      panel.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open) { var f = $('.a11y-opt', panel); if (f) f.focus(); }
    };

    toggle.addEventListener('click', function () {
      setOpen(!panel.classList.contains('is-open'));
    });
    doc.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && panel.classList.contains('is-open')) { setOpen(false); toggle.focus(); }
    });
    doc.addEventListener('click', function (e) {
      if (!panel.classList.contains('is-open')) return;
      if (!panel.contains(e.target) && !toggle.contains(e.target)) setOpen(false);
    });

    $$('.a11y-opt', panel).forEach(function (btn) {
      btn.addEventListener('click', function () {
        var name = btn.getAttribute('data-a11y');
        if (name === 'reset') { state = {}; render(); return; }
        var max = parseInt(btn.getAttribute('data-max') || '1', 10);
        state[name] = ((state[name] || 0) + 1) > max ? 0 : (state[name] || 0) + 1;
        render();
      });
    });

    render();
  }());

  /* --------------------------------------------------------- contact form */
  $$('form[data-contact]').forEach(function (form) {
    var status = $('.form__status', form);
    var submit = $('[type="submit"]', form);

    var say = function (msg, state) {
      if (!status) return;
      status.textContent = msg;
      status.setAttribute('data-state', state);
    };

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;

      var data = new FormData(form);
      var endpoint = form.getAttribute('data-endpoint');
      var name = (data.get('name') || '').toString().trim();
      var phone = (data.get('phone') || '').toString().trim();
      var email = (data.get('email') || '').toString().trim();
      var subject = (data.get('subject') || '').toString().trim();
      var message = (data.get('message') || '').toString().trim();

      // honeypot - silently accept bots
      if ((data.get('company') || '').toString()) { say('תודה! ההודעה נשלחה.', 'ok'); form.reset(); return; }

      if (endpoint) {
        submit.disabled = true;
        say('שולח…', '');
        fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify({ name: name, phone: phone, email: email, subject: subject, message: message })
        }).then(function (res) {
          if (!res.ok) throw new Error('bad response');
          form.reset();
          say('תודה ' + name + '! ההודעה התקבלה ונחזור אליך בהקדם.', 'ok');
        }).catch(function () {
          say('אירעה תקלה בשליחה. אפשר להתקשר אלינו ל-050-4588554 או לכתוב ל-drasrf.clinic@gmail.com', 'err');
        }).then(function () { submit.disabled = false; });
        return;
      }

      // fallback: open the visitor's mail client with a prefilled message
      var lines = [
        'שם: ' + name,
        'טלפון: ' + phone,
        email ? 'אימייל: ' + email : '',
        subject ? 'נושא: ' + subject : '',
        '',
        message
      ].filter(Boolean).join('\n');

      var href = 'mailto:drasrf.clinic@gmail.com'
        + '?subject=' + encodeURIComponent('פנייה מהאתר' + (subject ? ' - ' + subject : ''))
        + '&body=' + encodeURIComponent(lines);

      window.location.href = href;
      say('נפתחה עבורך תוכנת הדוא"ל לשליחת הפנייה. אפשר גם להתקשר ישירות: 050-4588554', 'ok');
    });
  });
}());
