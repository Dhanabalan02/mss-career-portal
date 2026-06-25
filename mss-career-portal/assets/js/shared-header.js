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
        var clonedModal = document.importNode(modal, true);

        // Rewrite social buttons dynamically to use the correct API Base URL
        clonedModal.querySelectorAll('.mss-social-btn').forEach(function (btn) {
          var href = btn.getAttribute('href');
          if (href && href.indexOf('http://localhost:8000') === 0) {
            btn.setAttribute('href', href.replace('http://localhost:8000', AUTH_API_BASE));
          }
        });

        modalHost.appendChild(clonedModal);
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
document.addEventListener("click", function (e) {

  const btn = e.target.closest("#loginBtn");

  if (btn) {
    loginUser();
  }

});

window.AUTH_API_BASE = window.AUTH_API_BASE || (
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://127.0.0.1:8000'
    : window.location.origin
);
var AUTH_API_BASE = window.AUTH_API_BASE;

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

window.showMssToast = function (message, type) {
  var toastType = type || 'success';
  var toast = document.createElement('div');
  toast.className = 'mss-toast ' + toastType;

  var iconClass = 'feather-check-circle';
  if (toastType === 'error') {
    iconClass = 'feather-alert-circle';
  } else if (toastType === 'warning') {
    iconClass = 'feather-alert-triangle';
  } else if (toastType === 'info') {
    iconClass = 'feather-info';
  }

  toast.innerHTML = '<i class="' + iconClass + '"></i><span>' + message + '</span>';
  document.body.appendChild(toast);
  if (window.feather) window.feather.replace();

  requestAnimationFrame(function () {
    toast.classList.add('show');
  });

  setTimeout(function () {
    toast.classList.remove('show');
    setTimeout(function () {
      toast.remove();
    }, 250);
  }, 3000);
};

window.mssNotifications = [];

function buildNotificationBellHtml() {
  return '' +
    '<div class="mss-notification-wrap" style="position:relative; margin-right: 12px; display: flex; align-items: center;">' +
    '<button type="button" class="mss-notification-btn" onclick="toggleMssNotificationMenu(event)" ' +
    'style="width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,0.06);' +
    'color:#94A3B8;border:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:center;' +
    'cursor:pointer;flex-shrink:0;position:relative;transition:all 0.2s;" ' +
    'onmouseover="this.style.color=\'#F8FAFC\';this.style.borderColor=\'rgba(255,255,255,0.25)\';this.style.background=\'rgba(255,255,255,0.1)\'" ' +
    'onmouseout="this.style.color=\'#94A3B8\';this.style.borderColor=\'rgba(255,255,255,0.1)\';this.style.background=\'rgba(255,255,255,0.06)\'">' +
    '<i class="feather-bell" style="font-size:1.1rem;"></i>' +
    '<span class="mss-notification-badge" id="mssNotificationBadge" style="display:none;position:absolute;top:-2px;right:-2px;' +
    'background:#EF4444;color:#fff;border-radius:50%;width:16px;height:16px;font-size:0.68rem;font-weight:700;' +
    'display:flex;align-items:center;justify-content:center;border:2px solid #0F172A;line-height:1;">0</span>' +
    '</button>' +
    '<div class="mss-notification-dropdown" id="mssNotificationDropdown" style="display:none;position:absolute;top:46px;right:0;' +
    'background:#fff;border-radius:12px;box-shadow:0 16px 40px rgba(0,0,0,0.18);width:320px;z-index:1100;overflow:hidden;">' +
    '<div style="padding:12px 16px;border-bottom:1px solid #F1F5F9;display:flex;justify-content:space-between;align-items:center;">' +
    '<span style="font-family:\'Rubik\',sans-serif;font-weight:700;font-size:0.9rem;color:#0F172A;">Notifications</span>' +
    '<button onclick="mssMarkAllRead(event)" style="background:none;border:none;color:#3B82F6;font-family:\'Rubik\',sans-serif;' +
    'font-size:0.75rem;font-weight:600;cursor:pointer;padding:0;">Mark all read</button>' +
    '</div>' +
    '<div id="mssNotificationList" style="max-height:280px;overflow-y:auto;font-family:\'Rubik\',sans-serif;font-size:0.82rem;color:#475569;">' +
    '<div style="padding:20px;text-align:center;color:#94A3B8;">Loading...</div>' +
    '</div>' +
    '</div>' +
    '</div>';
}

window.toggleMssNotificationMenu = function (e) {
  if (e) e.stopPropagation();
  var menu = document.getElementById('mssNotificationDropdown');
  if (!menu) return;

  var profileMenu = document.getElementById('mssProfileMenu');
  if (profileMenu) profileMenu.style.display = 'none';

  var isOpen = menu.style.display === 'block';
  if (isOpen) {
    menu.style.display = 'none';
  } else {
    menu.style.display = 'block';
    fetchCandidateNotifications();
  }
};

async function fetchCandidateNotifications() {
  var token = localStorage.getItem('access_token');
  if (!token) return;
  try {
    var response = await fetch(AUTH_API_BASE + '/notifications/', {
      headers: {
        'Authorization': 'Bearer ' + token
      }
    });
    if (response.ok) {
      var data = await response.json();
      window.mssNotifications = data;
      renderCandidateNotifications();
    }
  } catch (e) {
    console.warn('Failed to fetch candidate notifications', e);
  }
}

function renderCandidateNotifications() {
  var listContainer = document.getElementById('mssNotificationList');
  var badge = document.getElementById('mssNotificationBadge');

  var notes = window.mssNotifications || [];
  var unreadCount = notes.filter(function (n) { return !n.read; }).length;

  if (badge) {
    if (unreadCount > 0) {
      badge.style.display = 'flex';
      badge.textContent = unreadCount > 99 ? '99+' : unreadCount;
    } else {
      badge.style.display = 'none';
    }
  }

  if (!listContainer) return;

  if (notes.length === 0) {
    listContainer.innerHTML = '<div style="padding:20px;text-align:center;color:#94A3B8;">No notifications.</div>';
    return;
  }

  var html = notes.map(function (n) {
    var itemBg = n.read ? '#ffffff' : '#F8FAFC';
    var titleColor = n.read ? '#64748B' : '#0F172A';
    var fontWeight = n.read ? '500' : '700';
    return '' +
      '<div class="mss-notification-item" onclick="mssMarkSingleRead(event, ' + n.id + ')" ' +
      'style="padding:12px 16px;border-bottom:1px solid #F1F5F9;cursor:pointer;transition:all 0.2s;' +
      'background:' + itemBg + ';display:flex;flex-direction:column;gap:4px;" ' +
      'onmouseover="this.style.background=\'#F1F5F9\'" ' +
      'onmouseout="this.style.background=\'' + itemBg + '\'">' +
      '<div style="display:flex;justify-content:space-between;align-items:start;gap:8px;">' +
      '<span style="font-weight:' + fontWeight + ';color:' + titleColor + ';font-size:0.82rem;line-height:1.25;">' + n.title + '</span>' +
      '<span style="font-size:0.7rem;color:#94A3B8;white-space:nowrap;">' + n.time + '</span>' +
      '</div>' +
      '<span style="color:#64748B;font-size:0.78rem;line-height:1.4;">' + n.message + '</span>' +
      '</div>';
  }).join('');

  listContainer.innerHTML = html;
}

window.mssMarkSingleRead = async function (e, id) {
  if (e) e.stopPropagation();
  var token = localStorage.getItem('access_token');
  if (!token) return;

  var note = (window.mssNotifications || []).find(function (n) { return n.id === id; });
  if (note && !note.read) {
    note.read = true;
    renderCandidateNotifications();
  }

  try {
    await fetch(AUTH_API_BASE + '/notifications/' + id + '/read', {
      method: 'PUT',
      headers: {
        'Authorization': 'Bearer ' + token
      }
    });
    fetchCandidateNotifications();
  } catch (e) {
    console.error('Error marking notification as read', e);
  }
};

window.mssMarkAllRead = async function (e) {
  if (e) e.stopPropagation();
  var token = localStorage.getItem('access_token');
  if (!token) return;

  (window.mssNotifications || []).forEach(function (n) { n.read = true; });
  renderCandidateNotifications();

  try {
    await fetch(AUTH_API_BASE + '/notifications/mark-all-read', {
      method: 'PUT',
      headers: {
        'Authorization': 'Bearer ' + token
      }
    });
    fetchCandidateNotifications();
  } catch (e) {
    console.error('Error marking all notifications as read', e);
  }
};

document.addEventListener('click', function (e) {
  var profileMenu = document.getElementById('mssProfileMenu');
  if (profileMenu && profileMenu.style.display === 'block') {
    if (!e.target.closest('.mss-profile-wrap')) profileMenu.style.display = 'none';
  }

  var notifMenu = document.getElementById('mssNotificationDropdown');
  if (notifMenu && notifMenu.style.display === 'block') {
    if (!e.target.closest('.mss-notification-wrap')) notifMenu.style.display = 'none';
  }
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

      if (!container.querySelector('.mss-notification-wrap')) {
        var bellWrap = document.createElement('div');
        bellWrap.innerHTML = buildNotificationBellHtml();
        container.appendChild(bellWrap.firstChild);
      }

      if (!container.querySelector('.mss-profile-wrap')) {
        var wrap = document.createElement('div');
        wrap.innerHTML = avatarHtml;
        container.appendChild(wrap.firstChild);
      }
    });
  });

  if (window.feather) window.feather.replace();

  fetchCandidateNotifications();

  if (!window.mssNotificationInterval) {
    window.mssNotificationInterval = setInterval(function () {
      fetchCandidateNotifications();
    }, 30000);
  }
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
    window.dispatchEvent(new CustomEvent('candidate_login_success'));

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
    window.dispatchEvent(new CustomEvent('candidate_login_success'));

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
(function () {
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
        altInput: true,
        altFormat: 'd M Y',
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

  // Inject custom validation styles for premium look
  if (!document.getElementById('mss-shared-validation-styles')) {
    const style = document.createElement('style');
    style.id = 'mss-shared-validation-styles';
    style.textContent = `
      .mss-modal-field.is-invalid { border-color: #dc3545 !important; }
      .mss-modal-field.is-valid { border-color: #10b981 !important; }
      .form-control.is-invalid { border-color: #dc3545 !important; }
      .form-control.is-valid { border-color: #10b981 !important; }
      .mss-modal-field.is-invalid ~ .invalid-feedback,
      .form-control.is-invalid ~ .invalid-feedback,
      .is-invalid ~ .invalid-feedback {
        display: block !important;
      }
    `;
    document.head.appendChild(style);
  }

  function validateNameField(input) {
    const $input = $(input);
    const val = $input.val().trim();
    const hasDigits = /\d/.test(val);
    const $container = $input.closest('.mss-modal-field');
    const $insertAfterTarget = $container.length > 0 ? $container : $input;

    let $feedback = $insertAfterTarget.next('.invalid-feedback');
    if ($feedback.length === 0) {
      $insertAfterTarget.after('<div class="invalid-feedback" style="color: #dc3545; font-size: 0.82rem; margin-top: 0.25rem;">Name cannot contain numbers.</div>');
      $feedback = $insertAfterTarget.next('.invalid-feedback');
    }

    if (val === '') {
      $input.removeClass('is-invalid is-valid');
      $container.removeClass('is-invalid is-valid');
      $feedback.hide();
    } else if (!hasDigits) {
      $input.removeClass('is-invalid').addClass('is-valid');
      $container.removeClass('is-invalid').addClass('is-valid');
      $feedback.hide();
    } else {
      $input.removeClass('is-valid').addClass('is-invalid');
      $container.removeClass('is-valid').addClass('is-invalid');
      $feedback.show();
    }
  }

  function validateEmailField(input) {
    const $input = $(input);
    const val = $input.val().trim();

    // This regex makes the '@' symbol and everything before it optional.
    // It accepts full emails or just domain suffixes like 'test.com', 'domain.org', etc.
    const regex = /^([^\s@]+@)?[^\s@]+\.(com|org|in)$/i;

    const $container = $input.closest('.mss-modal-field');
    const $insertAfterTarget = $container.length > 0 ? $container : $input;

    let $feedback = $insertAfterTarget.next('.invalid-feedback');
    if ($feedback.length === 0) {
      $insertAfterTarget.after('<div class="invalid-feedback" style="color: #dc3545; font-size: 0.82rem; margin-top: 0.25rem;">Please enter a valid domain or email ending in .com, .org, or .in</div>');
      $feedback = $insertAfterTarget.next('.invalid-feedback');
    }

    if (val === '') {
      $input.removeClass('is-invalid is-valid');
      $container.removeClass('is-invalid is-valid');
      $feedback.hide();
    } else if (regex.test(val)) {
      $input.removeClass('is-invalid').addClass('is-valid');
      $container.removeClass('is-invalid').addClass('is-valid');
      $feedback.hide();
    } else {
      $input.removeClass('is-valid').addClass('is-invalid');
      $container.removeClass('is-valid').addClass('is-invalid');
      $feedback.show();
    }
  }

  function validatePhoneField(input) {
    const $input = $(input);
    const val = $input.val().trim();
    const hasLetters = /[a-zA-Z]/.test(val);
    const $container = $input.closest('.mss-modal-field');
    const $insertAfterTarget = $container.length > 0 ? $container : $input;

    let $feedback = $insertAfterTarget.next('.invalid-feedback');
    if ($feedback.length === 0) {
      $insertAfterTarget.after('<div class="invalid-feedback" style="color: #dc3545; font-size: 0.82rem; margin-top: 0.25rem;">Mobile number can only contain digits.</div>');
      $feedback = $insertAfterTarget.next('.invalid-feedback');
    }

    if (val === '') {
      $input.removeClass('is-invalid is-valid');
      $container.removeClass('is-invalid is-valid');
      $feedback.hide();
    } else if (!hasLetters && val.length >= 7) {
      $input.removeClass('is-invalid').addClass('is-valid');
      $container.removeClass('is-invalid').addClass('is-valid');
      $feedback.hide();
    } else {
      $input.removeClass('is-valid').addClass('is-invalid');
      $container.removeClass('is-valid').addClass('is-invalid');
      $feedback.show();
    }
  }

  // Real-time listener for inputs using jQuery delegation
  $(document).on('input keyup blur', 'input[name="firstname"], input[name="lastname"], input[name="username"], input[type="email"], input[name="email"], input[type="tel"], input[name="phone"]', function () {
    if (this.name === 'firstname' || this.name === 'lastname' || this.name === 'username') {
      validateNameField(this);
    } else if (this.type === 'email' || this.name === 'email') {
      validateEmailField(this);
    } else if (this.type === 'tel' || this.name === 'phone') {
      validatePhoneField(this);
    }
  });

  // Submit blocker if any invalid fields exist
  $(document).on('submit', 'form', function (e) {
    const form = this;
    const nameInputs = form.querySelectorAll('input[name="firstname"], input[name="lastname"], input[name="username"]');
    const emailInputs = form.querySelectorAll('input[type="email"], input[name="email"]');
    const phoneInputs = form.querySelectorAll('input[type="tel"], input[name="phone"]');

    nameInputs.forEach(validateNameField);
    emailInputs.forEach(validateEmailField);
    phoneInputs.forEach(validatePhoneField);

    if ($(form).find('.is-invalid').length > 0) {
      e.preventDefault();
      e.stopImmediatePropagation();
      alert("Please correct the errors in the form before submitting.");
    }
  });

  // Rewrite any existing static social login buttons in the document (e.g. from mockup forms)
  function rewriteAllPageSocialLinks() {
    document.querySelectorAll('a.mss-social-btn, .google-clr, .linkedin-clr').forEach(function (btn) {
      var href = btn.getAttribute('href');
      if (href) {
        if (href.indexOf('http://localhost:8000') === 0) {
          btn.setAttribute('href', href.replace('http://localhost:8000', AUTH_API_BASE));
        } else if (href === 'javascript' || href === 'javascript:;') {
          if (btn.classList.contains('google-clr') || btn.querySelector('.fa-google')) {
            btn.setAttribute('href', AUTH_API_BASE + '/auth/google/login');
          } else if (btn.classList.contains('linkedin-clr') || btn.querySelector('.fa-linkedin')) {
            btn.setAttribute('href', AUTH_API_BASE + '/auth/linkedin/login');
          }
        }
      }
    });
  }

  // Run on load and also watch for DOM changes
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', rewriteAllPageSocialLinks);
  } else {
    rewriteAllPageSocialLinks();
  }
})();

