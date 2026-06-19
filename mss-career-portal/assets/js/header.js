/* header.js — same as shared-header.js (alias for pages that import header.js) */
(function () {
  window.togglePwd = function (id, el) {
    var input = document.getElementById(id);
    if (!input) return;
    var icon = el && el.querySelector ? el.querySelector('i') : null;
    if (input.type === 'password') {
      input.type = 'text';
      if (icon) icon.className = 'feather-eye-off';
    } else {
      input.type = 'password';
      if (icon) icon.className = 'feather-eye';
    }
  };

  window.switchModal = function (hideId, showId) {
    var hideEl = document.getElementById(hideId);
    var showEl = document.getElementById(showId);
    if (!hideEl || !showEl || typeof bootstrap === 'undefined') return;
    var hideModal = bootstrap.Modal.getInstance(hideEl);
    if (hideModal) hideModal.hide();
    hideEl.addEventListener('hidden.bs.modal', function handler() {
      hideEl.removeEventListener('hidden.bs.modal', handler);
      new bootstrap.Modal(showEl).show();
    });
  };

  function showModalById(modalId) {
    var modalEl = document.getElementById(modalId);
    if (!modalEl || typeof bootstrap === 'undefined') return false;
    bootstrap.Modal.getOrCreateInstance(modalEl).show();
    return true;
  }

  function getModalHost() {
    var host = document.getElementById('shared-modals');
    if (host) return host;
    host = document.createElement('div');
    host.id = 'shared-modals';
    document.body.appendChild(host);
    return host;
  }

  function removeModalsById(id) {
    document.querySelectorAll('#' + id).forEach(function (node) {
      var instance = typeof bootstrap !== 'undefined' && bootstrap.Modal
        ? bootstrap.Modal.getInstance(node)
        : null;
      if (instance) instance.dispose();
      node.parentNode.removeChild(node);
    });
  }

  function dedupeModals(ids) {
    ids.forEach(function (id) {
      var nodes = Array.from(document.querySelectorAll('#' + id));
      if (nodes.length <= 1) return;
      nodes.sort(function (a, b) {
        return b.querySelectorAll('input').length - a.querySelectorAll('input').length;
      });
      nodes.slice(1).forEach(function (node) {
        node.parentNode.removeChild(node);
      });
    });
  }

  // Strip ALL Live Server-injected reload blocks, not just the first — a
  // fragment with no <body> can get the snippet inserted after every
  // </svg> in the document, and each leftover injection corrupts parsing
  // of everything that follows it.
  function stripLiveServerInjections(html) {
    if (!html) return html;
    // Strip ALL Live Server-injected reload blocks (not just the first).
    // Without a <body> tag in the fetched fragment, Live Server can inject
    // this block multiple times throughout the markup; leaving any behind
    // corrupts parsing and can cause the register modal form fields to
    // disappear after social login.
    var liveServerBlock = /<!--\s*Code injected by live-server\s*-->[\s\S]*?<\/script>/gi;
    return html.replace(liveServerBlock, '');
  }

  // Fallback critical styling to prevent clipping/shrinking of the
  // register modal content when opened after dynamic social login.
  function injectCriticalModalFix() {
    if (document.getElementById('shared-header-modal-fix')) return;
    var style = document.createElement('style');
    style.id = 'shared-header-modal-fix';
    style.textContent = [
      '#candidateRegisterModal .modal-content{display:block!important;max-height:none!important;height:auto!important;overflow:visible!important}',
      '#candidateRegisterModal .mss-register-modal-row{display:flex!important;flex-shrink:0!important;height:auto!important;min-height:540px}',
      '#candidateRegisterModal .mss-register-form-panel{overflow:visible!important;max-height:none!important;height:auto!important}',
      '#candidateRegisterModal form{display:block!important;visibility:visible!important}'
    ].join('');
    document.head.appendChild(style);
  }


  document.addEventListener('click', function (e) {
    var trigger = e.target.closest('[data-bs-target="#candidateLoginModal"], [data-bs-target="#candidateRegisterModal"]');
    if (!trigger) return;
    var modalId = trigger.getAttribute('data-bs-target').replace('#', '');
    if (document.getElementById(modalId)) return;
    e.preventDefault();
    e.stopImmediatePropagation();
    document.addEventListener('shared-header:loaded', function () {
      showModalById(modalId);
    }, { once: true });
  }, true);

  var placeholders = Array.from(document.querySelectorAll('#shared-header'));
  if (placeholders.length === 0) return;

  if (!document.getElementById('shared-header-css')) {
    var link = document.createElement('link');
    link.id = 'shared-header-css';
    link.rel = 'stylesheet';
    link.href = new URL('../../assets/css/shared-header.css', document.baseURI || window.location.href).href;
    document.head.appendChild(link);
  }

  var headerPath = new URL('../../components/header.html', document.baseURI || window.location.href).href;

  function setBodyPaddingFromHeader() {
    var hdr = document.getElementById('mss-header');
    if (!hdr) return;
    document.body.style.paddingTop = hdr.offsetHeight + 'px';
  }

  fetch(headerPath, { cache: 'no-cache' })
    .then(function (response) {
      if (!response.ok) {
        throw new Error('Failed to load shared header: ' + response.status);
      }
      return response.text();
    })
    .then(function (html) {
      html = stripLiveServerInjections(html);
      injectCriticalModalFix();

      var temp = document.createElement('div');

      temp.innerHTML = html;

      var headerEl = temp.querySelector('#mss-header');
      if (!headerEl) {
        throw new Error('Shared header markup missing #mss-header');
      }

      placeholders.forEach(function (placeholder) {
        placeholder.innerHTML = headerEl.outerHTML;
      });

      var modalHost = getModalHost();
      temp.querySelectorAll('.modal').forEach(function (modal) {
        if (!modal.id) return;
        removeModalsById(modal.id);
        modalHost.appendChild(modal);
      });

      dedupeModals(['candidateLoginModal', 'candidateRegisterModal']);
      setBodyPaddingFromHeader();
      window.addEventListener('resize', setBodyPaddingFromHeader);

      function updateScrollProgress() {
        var winScroll = document.documentElement.scrollTop || document.body.scrollTop;
        var height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        var scrolled = height > 0 ? (winScroll / height) * 100 : 0;
        var progressBar = document.getElementById('mss-scroll-progress');
        if (progressBar) {
          progressBar.style.width = scrolled + '%';
        }
      }
      window.addEventListener('scroll', updateScrollProgress, { passive: true });
      updateScrollProgress();


      try {
        var hdrEl = document.getElementById('mss-header');
        if (hdrEl) {
          new MutationObserver(setBodyPaddingFromHeader).observe(hdrEl, {
            attributes: true, childList: true, subtree: true
          });
        }
      } catch (e) { /* ignore */ }

      document.dispatchEvent(new CustomEvent('shared-header:loaded'));
    })
    .catch(function (error) {
      console.error('header.js:', error);
    });
})();