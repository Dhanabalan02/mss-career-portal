/* ============================================================
   portal-layout.js  –  MASSET HR / Candidate Portal Shell
   ============================================================ */
(function () {
  'use strict';

  /* ── Auth guard ───────────────────────────────────────────── */
  // HR & School Admin pages require a logged-in session. If the access
  // token is missing — after logout, or a stale/bookmarked URL — bounce
  // back to the public site before any portal UI is built. getRole() and
  // currentPage() below are function declarations, so they're hoisted and
  // safe to call this early in the script.
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

  if (['hr', 'schoolAdmin'].indexOf(getRole()) !== -1 && !localStorage.getItem('access_token')) {
    window.location.replace('/mss-career-portal/home');
    return;
  }

  var AUTH_API_BASE = 'http://127.0.0.1:8000';

  /* ── Role config ──────────────────────────────────────────── */
  const PORTAL_ROLES = {
    candidate: {
      brandTitle: 'TMSS Career',
      sidebarLogo: 'C',
      sidebarTitle: 'Career Portal',
      sidebarSubtitle: 'Candidate',
      avatarFallback: 'CA',
      notificationsTitle: 'Notifications',
      navItems: [
        { type: 'section', label: 'Main' },
        { label: 'Dashboard', icon: 'chart-bar', href: '/mss-career-portal/dashboard', pages: ['candidate-dashboard.html', 'dashboard'] },
        { label: 'Jobs', icon: 'briefcase', href: '/mss-career-portal/jobs', pages: ['candidate-job-list.html', 'candidate-job-details.html', 'jobs', 'job-detail'] },
        { label: 'Applied Jobs', icon: 'file-text', href: '/mss-career-portal/dashboard#applications', pages: ['candidate-applied-jobs.html'] },
        { label: 'Profile', icon: 'user', href: '/mss-career-portal/profile', pages: ['candidate-profile.html', 'profile'] }
      ]
    },
    hr: {
      brandTitle: 'TMSS Career',
      sidebarLogo: 'HR',
      sidebarTitle: 'HR Portal',
      sidebarSubtitle: 'Human Resources',
      avatarFallback: 'HR',
      notificationsTitle: 'HR Notifications',
      navItems: [
        { type: 'section', label: 'Main' },
        { label: 'Dashboard', icon: 'chart-bar', href: '/mss-career-portal/hr/dashboard', pages: ['hr-dashboard.html', 'dashboard'] },
        { label: 'Job Posts', icon: 'clipboard-list', href: '/mss-career-portal/hr/jobpost-list', pages: ['hr-jobpost-list.html', 'hr-jobpost-create.html', 'hr-jobpost-details.html', 'jobpost-list', 'jobpost-create', 'jobpost-details'], badge: '0' },
        { label: 'Job Applicants', icon: 'users', href: '/mss-career-portal/hr/jobapplicants-list', pages: ['hr-jobapplicants-list.html', 'hr-candidate-profile.html', 'jobapplicants-list', 'candidate-profile'], badge: '0' },
        { label: 'Interview Management', icon: 'calendar', href: '/mss-career-portal/hr/interviews', pages: ['hr-interviewlist.html', 'interviews'] },
        { label: 'ATS Pipeline', icon: 'refresh', href: '/mss-career-portal/hr/ats-pipeline', pages: ['hr-atspipeline.html', 'ats-pipeline'] },
        { type: 'section', label: 'Integrations' },
        { label: 'Masset Integration', icon: 'link', href: '/mss-career-portal/hr/masset-candidates', pages: ['masset-sync-dashboard.html', 'masset-candidates'] },
        { label: 'Reports', icon: 'chart-line', href: '/mss-career-portal/hr/reports', pages: ['hr-reports.html', 'reports'] }
      ]
    },
    schoolAdmin: {
      brandTitle: 'TMSS Career',
      sidebarLogo: 'SA',
      sidebarTitle: 'School Admin',
      sidebarSubtitle: 'School Administration',
      avatarFallback: 'SA',
      notificationsTitle: 'Admin Notifications',
      navItems: [
        { type: 'section', label: 'Main' },
        { label: 'Dashboard', icon: 'chart-bar', href: '/mss-career-portal/school/dashboard', pages: ['schooladmin-dashboard.html', 'dashboard'] },
        { label: 'Job Posts', icon: 'clipboard-list', href: '/mss-career-portal/school/jobs', pages: ['schooladmin-jobposts.html', 'schooladmin-jobpostdetails.html', 'jobs', 'job-detail'] },
        { label: 'Job Applicants', icon: 'users', href: '/mss-career-portal/school/applicants', pages: ['schooladmin-jobapplicants-list.html', 'schooladmin-candidate-profile.html', 'applicants', 'candidate-profile'] },
        { label: 'Offer Management', icon: 'file-certificate', href: '/mss-career-portal/school/offers', pages: ['schooladmin-offermanagement.html', 'offers'] }
      ]
    }
  };

  /* ── Notification data ────────────────────────────────────── */
  // Test/demo notification data removed.
  const NOTIFICATIONS = {
    candidate: [],
    hr: [],
    schoolAdmin: []
  };

  /* ── Internal state ───────────────────────────────────────── */
  let notificationFilter = 'all';

  /* ── Utilities ────────────────────────────────────────────── */
  function portalIcon(name) {
    return `<i class="ti ti-${name}" aria-hidden="true"></i>`;
  }

  function ensureTablerIcons() {
    const href = 'https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css';
    const existing = qsa('link[rel="stylesheet"]').find(link => (link.getAttribute('href') || '').includes('tabler-icons'));
    if (existing) return;
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = href;
    document.head.appendChild(link);
  }

  function getRole() {
    const path = window.location.pathname.toLowerCase();
    if (path.includes('/hr/')) return 'hr';
    if (path.includes('/school/')) return 'schoolAdmin';
    const page = currentPage();
    const storedRole = localStorage.getItem('userRole');
    if (storedRole === 'hr') return 'hr';
    if (storedRole === 'schoolAdmin') return 'schoolAdmin';
    if (page.startsWith('hr-') || page.startsWith('masset-sync')) return 'hr';
    if (page.startsWith('schooladmin-')) return 'schoolAdmin';
    return 'candidate';
  }
  function getConfig() { return PORTAL_ROLES[getRole()]; }
  function getNotes() { return NOTIFICATIONS[getRole()]; }

  function currentPage() {
    return window.location.pathname.split('/').pop().split('?')[0].toLowerCase() || 'index.html';
  }

  function qs(sel, ctx) { return (ctx || document).querySelector(sel); }
  function qsa(sel, ctx) { return [...(ctx || document).querySelectorAll(sel)]; }

  function ensurePortalStylesheet() {
    const href = 'portal-layout.css';
    const versionedHref = `${href}?v=portal-shell-3`;
    const existing = qsa('link[rel="stylesheet"]').find(link => {
      const value = link.getAttribute('href') || '';
      return value.split('?')[0].endsWith(href);
    });

    if (existing) {
      if ((existing.getAttribute('href') || '') !== versionedHref) {
        existing.setAttribute('href', versionedHref);
      }
      document.head.appendChild(existing);
      return;
    }

    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = versionedHref;
    document.head.appendChild(link);
  }

  /* ── Theme ────────────────────────────────────────────────── */
  function applyStoredTheme() {
    if (localStorage.getItem('portalTheme') === 'dark') document.body.classList.add('dark-theme');
  }

  window.toggleDarkTheme = function () {
    const dark = document.body.classList.toggle('dark-theme');
    localStorage.setItem('portalTheme', dark ? 'dark' : 'light');
  };

  /* ── Header ───────────────────────────────────────────────── */
  function buildHeader() {
    if (qs('.portal-topbar')) return;
    const cfg = getConfig();

    const el = document.createElement('header');
    el.className = 'portal-topbar';
    el.setAttribute('aria-label', 'Portal header');
    el.innerHTML = `
      <div class="portal-topbar__left">
          <button class="portal-topbar-logo">
          <a href="/mss-career-portal/home" class="portal-topbar-logo"
                  type="button"
                  aria-label="Toggle navigation"
                  data-sidebar-open>
              <img src="images/mss-logo.png" alt="MSS Logo" class="portal-topbar-logo__image">
              <span class="portal-brand">${cfg.brandTitle}</span>
          </a>
          </button>
      </div>
      <div class="portal-topbar__actions">
        <button class="portal-icon-btn portal-theme-toggle" type="button"
                aria-label="Toggle theme" data-theme-toggle>
          <span class="portal-sun-icon" aria-hidden="true">${portalIcon('sun')}</span>
          <span class="portal-moon-icon" aria-hidden="true">${portalIcon('moon')}</span>
        </button>
        <button class="portal-icon-btn portal-bell" type="button"
                aria-label="Notifications" aria-controls="portalNotifications"
                aria-expanded="false" data-notification-toggle>
          <span aria-hidden="true">${portalIcon('bell')}</span>
          <span class="portal-badge" data-notification-badge data-count="0">0</span>
        </button>
        <span class="portal-avatar" aria-label="${cfg.avatarFallback}" data-user-avatar>${cfg.avatarFallback}</span>
        <button class="portal-icon-btn portal-logout" type="button"
                aria-label="Logout" data-logout title="Logout">
          <span aria-hidden="true">${portalIcon('logout')}</span>
        </button>
      </div>`;
    document.body.prepend(el);
  }

  /* ── Sidebar ──────────────────────────────────────────────── */
  function buildSidebar() {
    if (qs('#portalSidebar')) { updateSidebar(); return; }

    const cfg = getConfig();
    const sidebar = document.createElement('aside');
    sidebar.id = 'portalSidebar';
    sidebar.className = isDesktopLayout() ? 'portal-sidebar is-open' : 'portal-sidebar';
    sidebar.setAttribute('aria-label', 'Site navigation');
    sidebar.setAttribute('aria-hidden', isDesktopLayout() ? 'false' : 'true');
    sidebar.innerHTML = `
      <div class="portal-sidebar__header">
        <div class="portal-sidebar__brand">
          <div class="portal-sidebar__logo">${cfg.sidebarLogo || 'M'}</div>
          <div>
            <div class="portal-sidebar__title">${cfg.sidebarTitle || 'Portal'}</div>
            <span class="portal-sidebar__subtitle">${cfg.sidebarSubtitle || ''}</span>
          </div>
        </div>
        <button class="portal-sidebar__close" type="button"
                aria-label="Close sidebar" data-sidebar-close>${portalIcon('x')}</button>
      </div>
      <nav aria-label="${cfg.sidebarTitle || 'Portal'} navigation">
        ${navLinks(cfg)}
      </nav>`;

    document.body.appendChild(sidebar);

    /* Backdrop */
    const backdrop = document.createElement('div');
    backdrop.className = 'portal-sidebar-backdrop';
    backdrop.setAttribute('data-sidebar-close', '');
    document.body.appendChild(backdrop);

    markActiveLink();
    syncSidebarDockState();
  }

  function isDesktopLayout() {
    return window.matchMedia('(min-width: 769px)').matches;
  }

  function updateSidebar() {
    const cfg = getConfig();
    const nav = qs('#portalSidebar nav');
    const title = qs('#portalSidebar .portal-sidebar__title');
    const logo = qs('#portalSidebar .portal-sidebar__logo');
    if (title) title.textContent = cfg.sidebarTitle;
    if (logo) logo.textContent = cfg.sidebarLogo;
    if (nav) nav.innerHTML = navLinks(cfg);
    markActiveLink();
  }

  function navLinks(cfg) {
    const userType = localStorage.getItem('user_type');
    const base = getBaseUrl();
    const folder = getRole() === 'hr' ? 'pages/hr/' : (getRole() === 'schoolAdmin' ? 'pages/school/' : 'pages/candidate/');
    return cfg.navItems
      .filter(item => {
        if (item.label === 'Reports') {
          return userType === 'hr_head';
        }
        return true;
      })
      .map(item => {
        if (item.type === 'section') {
          return `<div class="portal-sidebar__section">${item.label}</div>`;
        }

        const href = item.href.startsWith('/') ? item.href : `${base}${folder}${item.href}`;
        return `
          <a href="${href}" data-nav-pages="${item.pages.join(',')}">
            <span class="portal-sidebar__nav-icon" aria-hidden="true">${portalIcon(item.icon)}</span>
            <span class="portal-sidebar__nav-label">${item.label}</span>
            ${item.badge ? `<span class="portal-sidebar__badge" data-badge-label="${item.label}">${item.badge}</span>` : ''}
          </a>`;
      }).join('');
  }



  function markActiveLink() {
    const page = currentPage();
    qsa('#portalSidebar nav a').forEach(link => {
      const pages = (link.dataset.navPages || link.getAttribute('href') || '').split(',').map(p => p.trim());
      const active = pages.includes(page);
      link.classList.toggle('is-active', active);
      active ? link.setAttribute('aria-current', 'page') : link.removeAttribute('aria-current');
    });
  }

  function syncSidebarDockState() {
    const sidebar = qs('#portalSidebar');
    const backdrop = qs('.portal-sidebar-backdrop');
    const trigger = qs('[data-sidebar-open]');
    if (!sidebar) return;

    if (isDesktopLayout()) {
      sidebar.classList.add('is-open');
      sidebar.setAttribute('aria-hidden', 'false');
      if (backdrop) backdrop.classList.remove('is-open');
      if (trigger) trigger.setAttribute('aria-expanded', 'false');
    } else {
      if (!backdrop?.classList.contains('is-open')) {
        sidebar.classList.remove('is-open');
        sidebar.setAttribute('aria-hidden', 'true');
        if (trigger) trigger.setAttribute('aria-expanded', 'false');
      }
    }
  }

  function openSidebar() {
    const sidebar = qs('#portalSidebar');
    const backdrop = qs('.portal-sidebar-backdrop');
    const trigger = qs('[data-sidebar-open]');
    if (!sidebar) return;

    sidebar.classList.add('is-open');
    sidebar.setAttribute('aria-hidden', 'false');
    if (backdrop) backdrop.classList.add('is-open');
    if (trigger) trigger.setAttribute('aria-expanded', 'true');
  }

  function closeSidebar() {
    const sidebar = qs('#portalSidebar');
    const backdrop = qs('.portal-sidebar-backdrop');
    const trigger = qs('[data-sidebar-open]');
    if (!sidebar) return;

    if (!isDesktopLayout()) {
      sidebar.classList.remove('is-open');
      sidebar.setAttribute('aria-hidden', 'true');
    } else {
      sidebar.classList.add('is-open');
      sidebar.setAttribute('aria-hidden', 'false');
    }

    if (backdrop) backdrop.classList.remove('is-open');
    if (trigger) trigger.setAttribute('aria-expanded', 'false');
  }

  /* ── Notifications ────────────────────────────────────────── */
  function buildNotificationsPanel() {
    if (qs('.portal-notifications')) { renderNotifications(); return; }

    const cfg = getConfig();
    const panel = document.createElement('section');
    panel.id = 'portalNotifications';
    panel.className = 'portal-notifications';
    panel.setAttribute('aria-label', 'Notifications');
    panel.setAttribute('aria-hidden', 'true');
    panel.style.visibility = 'hidden';
    panel.style.transform = 'translateX(100%)';
    panel.innerHTML = `
      <div class="portal-notifications__header">
        <div>
          <h2 class="portal-notifications__title">${cfg.notificationsTitle}</h2>
          <span class="portal-notifications__count" data-notification-summary></span>
        </div>
        <button class="portal-notifications__read-all" type="button" data-mark-all-read>
          Mark All Read
        </button>
      </div>
      <div class="portal-notification-tabs" role="tablist" aria-label="Filter notifications">
        <button class="portal-notification-tab is-active" role="tab" aria-selected="true"
                data-notification-filter="all">All</button>
        <button class="portal-notification-tab" role="tab" aria-selected="false"
                data-notification-filter="unread">Unread</button>
        <button class="portal-notification-tab" role="tab" aria-selected="false"
                data-notification-filter="read">Read</button>
      </div>
      <ul class="portal-notification-list" data-notification-list role="list"></ul>`;
    document.body.appendChild(panel);
    renderNotifications();
  }

  function renderNotifications() {
    const list = qs('[data-notification-list]');
    const summary = qs('[data-notification-summary]');
    const markBtn = qs('[data-mark-all-read]');
    if (!list) return;

    const notes = getNotes();
    const unread = notes.filter(n => !n.read).length;
    const visible = notes.filter(n => {
      if (notificationFilter === 'unread') return !n.read;
      if (notificationFilter === 'read') return n.read;
      return true;
    });

    list.innerHTML = visible.length
      ? visible.map(n => `
          <li class="portal-notification-item ${n.read ? 'is-read' : 'is-unread'}"
              data-notification-id="${n.id}" tabindex="0" role="listitem">
            <span class="portal-notification-status" aria-hidden="true"></span>
            <small>${n.time}</small>
            <strong>${n.title}</strong>
            <span>${n.message}</span>
          </li>`).join('')
      : `<li class="portal-notification-empty">No notifications here.</li>`;

    /* Update filter tabs */
    qsa('[data-notification-filter]').forEach(tab => {
      const active = tab.dataset.notificationFilter === notificationFilter;
      tab.classList.toggle('is-active', active);
      tab.setAttribute('aria-selected', String(active));
    });

    if (summary) summary.textContent = `${unread} unread`;
    if (markBtn) markBtn.disabled = unread === 0;
    updateBadge(unread);
  }

  function updateBadge(count) {
    const badge = qs('[data-notification-badge]');
    if (!badge) return;
    const n = Math.max(0, count || 0);
    badge.textContent = n > 99 ? '99+' : String(n);
    badge.dataset.count = String(n);
  }

  async function fetchNotifications() {
    try {
      const res = await fetch(`${AUTH_API_BASE}/notifications/`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
      });
      if (res.ok) {
        const data = await res.json();
        NOTIFICATIONS[getRole()] = data;
        renderNotifications();
      }
    } catch(e) { console.warn('Failed to fetch notifications', e); }
  }

  function setFilter(filter) {
    notificationFilter = filter;
    renderNotifications();
  }

  async function markRead(id) {
    const note = getNotes().find(n => n.id === id);
    if (!note || note.read) return;
    try {
      const res = await fetch(`${AUTH_API_BASE}/notifications/${id}/read`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
      });
      if(res.ok) {
        note.read = true;
        renderNotifications();
      }
    } catch(e) { console.error('Error marking read', e); }
  }

  async function markAllRead() {
    const notes = getNotes();
    if (!notes.some(n => !n.read)) return;
    try {
      const res = await fetch(`${AUTH_API_BASE}/notifications/mark-all-read`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
      });
      if(res.ok) {
        notes.forEach(n => { n.read = true; });
        renderNotifications();
        showToast('All notifications marked as read.');
      }
    } catch(e) { console.error('Error marking all read', e); }
  }

  window.toggleNotifications = function (forceOpen) {
    const panel = qs('.portal-notifications');
    const trigger = qs('[data-notification-toggle]');
    if (!panel) return;
    const open = typeof forceOpen === 'boolean' ? forceOpen : !panel.classList.contains('is-open');
    panel.classList.toggle('is-open', open);
    panel.setAttribute('aria-hidden', String(!open));
    if (trigger) trigger.setAttribute('aria-expanded', String(open));
  };

  /* ── Toast ────────────────────────────────────────────────── */
  function showToast(msg) {
    let toast = qs('[data-portal-toast]');
    if (!toast) {
      toast = document.createElement('div');
      toast.className = 'portal-toast';
      toast.setAttribute('data-portal-toast', '');
      toast.setAttribute('role', 'status');
      toast.setAttribute('aria-live', 'polite');
      document.body.appendChild(toast);
    }
    toast.innerHTML = msg;
    toast.classList.add('is-visible');
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => toast.classList.remove('is-visible'), 2800);
  }

  /* ── Avatar initials from email ───────────────────────────── */
  function updateAvatar() {
    const role = getRole();
    const email = role === 'hr'
      ? localStorage.getItem('hrEmail')
      : localStorage.getItem('candidateEmail');
    const el = qs('[data-user-avatar]');
    if (!el) return;
    el.textContent = email
      ? email.substring(0, 2).toUpperCase()
      : getConfig().avatarFallback;
  }

  /* ── Logout ───────────────────────────────────────────────── */
  function clearSession() {
    ['candidateRegistration', 'googleUser', 'hrLoggedIn', 'hrEmail', 'userRole', 'candidateEmail',
      'access_token', 'user_type', 'user_name', 'user_email', 'user_id']
      .forEach(k => localStorage.removeItem(k));
  }

  function logout() {
    const userId = localStorage.getItem('user_id');
    const sessionId = localStorage.getItem('access_token');
    const goHome = () => { window.location.href = '/mss-career-portal/home'; };

    if (!userId || !sessionId) { clearSession(); goHome(); return; }

    const params = new URLSearchParams({ admin_id: userId, session_id: sessionId });
    fetch(`${AUTH_API_BASE}/auth/user/logout?${params.toString()}`, { method: 'POST' })
      .catch(err => console.error('Logout API call failed:', err))
      .finally(() => { clearSession(); goHome(); });
  }

  /* ── Event wiring ─────────────────────────────────────────── */
  function bindEvents() {
    document.addEventListener('click', e => {
      if (e.target.closest('[data-theme-toggle]')) { toggleDarkTheme(); return; }

      if (e.target.closest('[data-notification-toggle]')) {
        e.stopPropagation();
        toggleNotifications();
        return;
      }

      const filterBtn = e.target.closest('[data-notification-filter]');
      if (filterBtn) { setFilter(filterBtn.dataset.notificationFilter); return; }

      if (e.target.closest('[data-mark-all-read]')) { markAllRead(); return; }

      const noteItem = e.target.closest('[data-notification-id]');
      if (noteItem) { markRead(Number(noteItem.dataset.notificationId)); return; }

      if (e.target.closest('[data-sidebar-open]')) { openSidebar(); return; }
      if (e.target.closest('[data-sidebar-close]')) { closeSidebar(); return; }

      if (e.target.closest('[data-logout]')) { logout(); return; }

      /* Close notifications when clicking outside */
      const panel = qs('.portal-notifications');
      if (panel?.classList.contains('is-open') && !e.target.closest('.portal-notifications')) {
        toggleNotifications(false);
      }
    });

    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') {
        toggleNotifications(false);
        closeSidebar();
        return;
      }
      if ((e.key === 'Enter' || e.key === ' ') && e.target.closest('[data-notification-id]')) {
        e.preventDefault();
        markRead(Number(e.target.closest('[data-notification-id]').dataset.notificationId));
      }
    });

    window.addEventListener('resize', syncSidebarDockState);
  }

  /* ── Exposed helper for existing pages ─────────────────────── */
  window.updateNotificationBadge = updateBadge;
  window.portalIcon = portalIcon;
  window.AUTH_API_BASE = AUTH_API_BASE;
  window.showToast = showToast;

  ensurePortalStylesheet();
  ensureTablerIcons();

  async function fetchSidebarCounts() {
    const role = getRole();
    if (role !== 'hr' && role !== 'schoolAdmin') return;
    try {
      const endpoint = role === 'hr' ? '/hr/sidebar-counts' : '/school/sidebar-counts';
      const res = await fetch(AUTH_API_BASE + endpoint, {
        headers: { 'Authorization': 'Bearer ' + localStorage.getItem('access_token') }
      });
      if (!res.ok) return;
      const data = await res.json();

      const setBadge = (label, count) => {
        const badge = document.querySelector(`[data-badge-label="${label}"]`);
        if (badge) badge.textContent = count;
      };

      setBadge('Job Posts', data.job_posts_count || 0);
      setBadge('Job Applicants', data.job_applicants_count || 0);
    } catch (e) { console.warn('Sidebar counts error', e); }
  }

  /* ── Flatpickr Integration ── */
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

  /* ── Boot ─────────────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', () => {
    ensurePortalStylesheet();
    ensureTablerIcons();
    applyStoredTheme();
    buildHeader();
    buildSidebar();
    buildNotificationsPanel();
    updateAvatar();
    bindEvents();
    fetchSidebarCounts();
    fetchNotifications();

    ensureFlatpickr(() => {
      initDateInputs();
      setupMutationObserver();
    });
  });

})();

