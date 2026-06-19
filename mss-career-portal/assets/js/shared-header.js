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

  // Strip them ALL, regardless of count or where they land, before parsing.
  function stripLiveServerInjections(html) {
    if (!html) return html;
    // Live Server's injected comment + script block (handles both the
    // commented and uncommented variants it has shipped over time).
    var liveServerBlock = /<!--\s*Code injected by live-server\s*-->[\s\S]*?<\/script>/gi;
    return html.replace(liveServerBlock, '');
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

  injectCriticalModalFix();

  var headerPath = new URL('../../components/header.html', document.baseURI || window.location.href).href;

  function setBodyPaddingFromHeader() {
    var hdr = document.getElementById('mss-header');
    if (!hdr) return;
    document.body.style.paddingTop = hdr.offsetHeight + 'px';
  }

  fetch(headerPath, { cache: 'no-cache' })
    .then(function (response) {
      if (!response.ok) throw new Error('Failed to load shared header: ' + response.status);
      return response.text();
    })
    .then(function (html) {
      // Strip ALL Live Server injections (there can be more than one in a
      // fragment with no <body>) before handing the string to the parser.
      html = stripLiveServerInjections(html);
      var parser = new DOMParser();
      var doc = parser.parseFromString(html, 'text/html');

      var headerEl = doc.querySelector('#mss-header');
      if (!headerEl) throw new Error('Shared header markup missing #mss-header');

      placeholders.forEach(function (placeholder) {
        placeholder.innerHTML = headerEl.outerHTML;
      });

      var modalHost = getModalHost();

      // Replace modals atomically: clear any previously injected fragments
      // so we never end up with partial/duplicated modal markup.
      removeModalsById('candidateLoginModal');
      removeModalsById('candidateRegisterModal');
      dedupeModals(['candidateLoginModal', 'candidateRegisterModal']);

      // Import only the modals we care about.
      ['candidateLoginModal', 'candidateRegisterModal'].forEach(function (modalId) {
        var modal = doc.getElementById(modalId);
        if (!modal) return;
        modalHost.appendChild(document.importNode(modal, true));
      });
      injectCriticalModalFix();

      var regModal = document.getElementById('candidateRegisterModal');
      if (regModal) {
        var inputCount = regModal.querySelectorAll('input').length;
        if (inputCount < 6) {
          console.warn('shared-header.js: register modal missing form fields (' + inputCount + ' inputs)');
        }
      }

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

      // Logged-in candidates see their avatar instead of Login/Apply Now —
      // must run after every header (re)injection.
      if (typeof applyAuthUI === 'function') applyAuthUI();

      document.dispatchEvent(new CustomEvent('shared-header:loaded'));
    })
    .catch(function (error) {
      console.error('shared-header.js:', error);
    });
})();


// document.getElementById("loginBtn").addEventListener("click", loginUser);
document.addEventListener("click", function(e) {

    const btn = e.target.closest("#loginBtn");

    if (btn) {
        loginUser();
    }

});

var AUTH_API_BASE = 'http://127.0.0.1:8000';

// Roles that belong to internal portals get redirected straight there on
// login since they have no place on the public candidate-facing site.
var HR_ROLES = ['hr_head', 'hr_admin', 'hr_team'];
var SCHOOL_ADMIN_ROLE = 'school_admin';

function getBaseUrl() {
    var url = new URL(window.location.href);
    var pathParts = url.pathname.split('/');
    var pagesIndex = pathParts.indexOf('pages');
    if (pagesIndex !== -1) {
        return url.origin + pathParts.slice(0, pagesIndex).join('/') + '/';
    }
    var idx = pathParts.indexOf('mss-career-portal');
    if (idx !== -1) {
        return url.origin + pathParts.slice(0, idx + 1).join('/') + '/';
    }
    return url.origin + '/';
}

function getDashboardUrl(userType) {
    if (HR_ROLES.indexOf(userType) !== -1) {
        return '/mss-career-portal/hr/dashboard';
    }
    if (userType === SCHOOL_ADMIN_ROLE) {
        return '/mss-career-portal/school/dashboard';
    }
    return null;
}

function getInitial(name, email) {
    var source = (name || '').trim() || (email || '').trim();
    return source ? source.charAt(0).toUpperCase() : '?';
}

function buildAvatarHtml(initial) {
    return '' +
        '<div class="mss-profile-wrap" style="position:relative;">' +
            '<button type="button" class="mss-profile-btn" onclick="toggleMssProfileMenu(event)" ' +
                'style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#3B82F6,#6366F1);' +
                'color:#fff;border:none;font-family:\'Rubik\',sans-serif;font-weight:700;font-size:0.95rem;' +
                'cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;">' + initial + '</button>' +
            '<div class="mss-profile-menu" id="mssProfileMenu" style="display:none;position:absolute;top:46px;right:0;' +
                'background:#fff;border-radius:12px;box-shadow:0 16px 40px rgba(0,0,0,0.18);min-width:160px;overflow:hidden;z-index:1100;">' +
                '<a href="/mss-career-portal/profile" style="display:block;padding:10px 16px;font-family:\'Rubik\',sans-serif;font-size:0.85rem;' +
                    'color:#0F172A;text-decoration:none;">My Profile</a>' +
                '<a href="javascript:;" onclick="mssLogout()" style="display:block;padding:10px 16px;font-family:\'Rubik\',sans-serif;' +
                    'font-size:0.85rem;color:#DC2626;text-decoration:none;border-top:1px solid #F1F5F9;">Logout</a>' +
            '</div>' +
        '</div>';
}

window.toggleMssProfileMenu = function (e) {
    if (e) e.stopPropagation();
    var menu = document.getElementById('mssProfileMenu');
    if (!menu) return;
    menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
};

document.addEventListener('click', function (e) {
    var menu = document.getElementById('mssProfileMenu');
    if (!menu || menu.style.display !== 'block') return;
    if (!e.target.closest('.mss-profile-wrap')) menu.style.display = 'none';
});

window.mssLogout = function () {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_type');
    localStorage.removeItem('user_name');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_id');
    window.location.reload();
};

function applyAuthUI() {
    var token = localStorage.getItem('access_token');
    var userType = localStorage.getItem('user_type');
    if (!token || userType !== 'candidate') return;

    var initial = getInitial(localStorage.getItem('user_name'), localStorage.getItem('user_email'));
    var avatarHtml = buildAvatarHtml(initial);

    document.querySelectorAll('#mss-header').forEach(function (header) {
        var loginLinks = header.querySelectorAll('[data-bs-target="#candidateLoginModal"]');
        var applyLinks = header.querySelectorAll('[data-bs-target="#candidateRegisterModal"]');

        loginLinks.forEach(function (loginLink, idx) {
            var applyLink = applyLinks[idx];
            var container = loginLink.parentElement;
            if (!container) return;

            loginLink.style.display = 'none';
            if (applyLink) applyLink.style.display = 'none';

            if (!container.querySelector('.mss-profile-wrap')) {
                var wrap = document.createElement('div');
                wrap.innerHTML = avatarHtml;
                container.appendChild(wrap.firstChild);
            }
        });
    });
}


async function loginUser() {

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("lp1").value;



    if (!email || !password) {
        alert("Please enter email and password");
        return;
    }

    try {
        const response = await fetch(
            AUTH_API_BASE + "/auth/user/login",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email,
                    password
                })
            }
        );

        const result = await response.json();

        console.log("Login response:", result);

        if (!response.ok) {
            alert(result.message || result.detail || "Login Failed");
            return;
        }

        if (result.access_token) {
            localStorage.setItem("access_token", result.access_token);
            localStorage.setItem("user_type", result.user_type || "");
            localStorage.setItem("user_name", result.name || "");
            localStorage.setItem("user_email", email);
            localStorage.setItem("user_id", result.user_id != null ? String(result.user_id) : "");
        }

        // HR and school-admin roles have no place on the public site —
        // send them straight to their respective internal dashboards.
        const dashboardUrl = getDashboardUrl(result.user_type);
        if (dashboardUrl) {
            window.location.href = dashboardUrl;
            return;
        }

        // Candidate: stay on the current page, just close the login modal
        // and swap it for the profile avatar.
        const loginModalEl = document.getElementById('candidateLoginModal');
        if (loginModalEl && typeof bootstrap !== 'undefined') {
            const instance = bootstrap.Modal.getInstance(loginModalEl);
            if (instance) instance.hide();
        }

        applyAuthUI();
        alert("Login Successful");

        // var pendingJobId = sessionStorage.getItem('pending_apply_job_id');
        // if (pendingJobId) {
        //     sessionStorage.removeItem('pending_apply_job_id');
        //     window.location.href = 'apply.html?id=' + encodeURIComponent(pendingJobId);
        // }

    } catch (error) {
        console.error(error);
        alert("Unable to connect to server");
    }
}

document.addEventListener("submit", function (e) {
    var form = e.target;
    if (!form || !form.closest || !form.closest("#candidateRegisterModal")) return;
    e.preventDefault();
    registerCandidate(form);
});

async function registerCandidate(form) {
    if (typeof form.reportValidity === "function" && !form.reportValidity()) return;

    var data = new FormData(form);
    var firstName = (data.get("firstname") || "").trim();
    var lastName = (data.get("lastname") || "").trim();
    var email = (data.get("email") || "").trim();
    var mobile = (data.get("phone") || "").trim();
    var password = data.get("password") || "";

    if (!firstName || !lastName || !email || !mobile || !password) {
        alert("Please fill in all fields.");
        return;
    }

    try {
        const response = await fetch(AUTH_API_BASE + "/auth/candidate/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                email: email,
                first_name: firstName,
                last_name: lastName,
                mobile: mobile,
                password: password
            })
        });

        const result = await response.json();
        console.log("Register response:", result);

        if (!response.ok) {
            alert(result.message || result.detail || "Registration failed");
            return;
        }

        if (result.access_token) {
            localStorage.setItem("access_token", result.access_token);
            localStorage.setItem("user_type", result.user_type || "candidate");
            localStorage.setItem("user_name", result.name || (firstName + " " + lastName));
            localStorage.setItem("user_email", email);
            localStorage.setItem("user_id", result.user_id != null ? String(result.user_id) : "");
        }

        const modalEl = document.getElementById("candidateRegisterModal");
        if (modalEl && typeof bootstrap !== "undefined") {
            const instance = bootstrap.Modal.getInstance(modalEl);
            if (instance) instance.hide();
        }

        form.reset();
        applyAuthUI();
        alert("Account created successfully!");

        var pendingJobId = sessionStorage.getItem('pending_apply_job_id');
        if (pendingJobId) {
            sessionStorage.removeItem('pending_apply_job_id');
            window.location.href = '/mss-career-portal/apply?id=' + encodeURIComponent(pendingJobId);
        }

    } catch (error) {
        console.error(error);
        alert("Unable to connect to server");
    }
}

// --- Flatpickr Integration ---
(function() {
  function ensureFlatpickr(callback) {
    if (window.flatpickr) {
      if (callback) callback();
      return;
    }

    // Inject Flatpickr CSS
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css';
    document.head.appendChild(link);

    // Inject custom Flatpickr styling overrides for premium look
    const style = document.createElement('style');
    style.id = 'flatpickr-custom-theme';
    style.textContent = `
      .flatpickr-calendar {
        background: var(--portal-surface, var(--cp-surface, #ffffff)) !important;
        border: 1px solid var(--portal-border, var(--cp-border, #e4e8f4)) !important;
        border-radius: var(--portal-radius, var(--cp-radius, 12px)) !important;
        box-shadow: var(--portal-shadow-lg, var(--cp-shadow-md, 0 8px 32px rgba(0, 0, 0, 0.08))) !important;
        font-family: var(--portal-font, inherit) !important;
        width: 322px !important;
      }
      .flatpickr-calendar .flatpickr-days,
      .flatpickr-calendar .flatpickr-innerContainer,
      .flatpickr-calendar .flatpickr-rContainer,
      .flatpickr-calendar .dayContainer {
        width: 322px !important;
        min-width: 322px !important;
        max-width: 322px !important;
      }
      .flatpickr-calendar .flatpickr-day {
        max-width: 46px !important;
        height: 40px !important;
        line-height: 40px !important;
        font-size: 14px !important;
      }
      .flatpickr-calendar .flatpickr-weekday {
        max-width: 46px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
      }
      .flatpickr-day.selected, .flatpickr-day.startRange, .flatpickr-day.endRange, 
      .flatpickr-day.selected.inRange, .flatpickr-day.startRange.inRange, .flatpickr-day.endRange.inRange, 
      .flatpickr-day.selected:focus, .flatpickr-day.startRange:focus, .flatpickr-day.endRange:focus, 
      .flatpickr-day.selected:hover, .flatpickr-day.startRange:hover, .flatpickr-day.endRange:hover, 
      .flatpickr-day.selected.prevMonthDay, .flatpickr-day.selected.nextMonthDay, 
      .flatpickr-day.startRange.prevMonthDay, .flatpickr-day.startRange.nextMonthDay, 
      .flatpickr-day.endRange.prevMonthDay, .flatpickr-day.endRange.nextMonthDay {
        background: var(--portal-primary, var(--cp-accent, #5147BD)) !important;
        border-color: var(--portal-primary, var(--cp-accent, #5147BD)) !important;
        color: #fff !important;
      }
      .flatpickr-day.today {
        border-color: var(--portal-accent, var(--cp-accent-mid, #818CF8)) !important;
      }
      .flatpickr-months .flatpickr-month {
        color: var(--portal-text, var(--cp-text, #111827)) !important;
        fill: var(--portal-text, var(--cp-text, #111827)) !important;
      }
      .flatpickr-current-month .flatpickr-monthDropdown-months {
        background: var(--portal-surface, var(--cp-surface, #ffffff)) !important;
        color: var(--portal-text, var(--cp-text, #111827)) !important;
      }
      .flatpickr-day {
        color: var(--portal-text, var(--cp-text, #111827)) !important;
      }
      .flatpickr-day:hover {
        background: var(--portal-surface2, var(--cp-surface-2, #f3f4f6)) !important;
      }
      .flatpickr-day.prevMonthDay, .flatpickr-day.nextMonthDay {
        color: var(--portal-muted2, var(--cp-subtle, #9ca3af)) !important;
      }
      .flatpickr-weekday {
        color: var(--portal-muted, var(--cp-muted, #6b7280)) !important;
      }
      .flatpickr-current-month input.numInput.cur-year {
        color: inherit !important;
      }
      .flatpickr-time {
        border-top: 1px solid var(--portal-border, var(--cp-border, #e4e8f4)) !important;
      }
      .flatpickr-time input {
        color: var(--portal-text, var(--cp-text, #111827)) !important;
      }
      .flatpickr-time .flatpickr-am-pm {
        color: var(--portal-text, var(--cp-text, #111827)) !important;
      }
    `;
    document.head.appendChild(style);

    // Inject Flatpickr JS
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/flatpickr';
    script.onload = () => {
      if (callback) callback();
    };
    document.head.appendChild(script);
  }

  function initDateInputs(container) {
    const root = container || document;
    const dateInputs = root.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
      if (input._flatpickr) return;

      const minDate = input.getAttribute('min');
      const maxDate = input.getAttribute('max');
      const defaultValue = input.value;

      // Temporary change type to text to prevent native date picker overlay
      input.type = 'text';

      flatpickr(input, {
        dateFormat: 'Y-m-d',
        defaultDate: defaultValue || null,
        minDate: minDate || null,
        maxDate: maxDate || null,
        animate: true,
        allowInput: true
      });
    });
  }

  function setupMutationObserver() {
    const observer = new MutationObserver((mutations) => {
      let foundDate = false;
      for (const mutation of mutations) {
        for (const node of mutation.addedNodes) {
          if (node.nodeType === Node.ELEMENT_NODE) {
            if (node.matches('input[type="date"]') || node.querySelector('input[type="date"]')) {
              foundDate = true;
              break;
            }
          }
        }
        if (foundDate) break;
      }
      if (foundDate) {
        initDateInputs();
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      ensureFlatpickr(() => {
        initDateInputs();
        setupMutationObserver();
      });
    });
  } else {
    ensureFlatpickr(() => {
      initDateInputs();
      setupMutationObserver();
    });
  }
})();

