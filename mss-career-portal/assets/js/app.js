/* ============================================================
   TalentBridge – app.js
   ============================================================ */

'use strict';

/* ============================================================
   DATA
   ============================================================ */
const JOBS_DATA = [
  {
    id: 1,
    title: 'Python Programming Teacher',
    company: 'Sir Mutha School',
    school: 'MSS Chennai',
    logo: 'M',
    logoColor: '#1A56DB',
    exp: '0–3 Yrs',
    salary: '2.5–4 LPA',
    skills: ['Classroom Management', 'Lesson Planning', 'Student Assessment'],
    dept: 'Teaching',
    posted: '2 days ago',
    edu: 'B.Ed',
    minExp: 0,
    minSal: 2
  },
  {
    id: 2,
    title: 'Mathematics Teacher',
    company: 'Lady Andal School',
    school: 'Lady Andal',
    logo: 'L',
    logoColor: '#7C3AED',
    exp: '2–5 Yrs',
    salary: '3–6 LPA',
    skills: ['Mathematics', 'Curriculum Development', 'Student Counseling'],
    dept: 'Teaching',
    posted: '1 week ago',
    edu: 'M.Sc Mathematics, B.Ed',
    minExp: 2,
    minSal: 3
  },
  {
    id: 3,
    title: 'Physics Teacher',
    company: 'LAOS School',
    school: 'LAOS',
    logo: 'L',
    logoColor: '#059669',
    exp: '2–5 Yrs',
    salary: '4–7 LPA',
    skills: ['Physics', 'Lesson Planning', 'Laboratory Management'],
    dept: 'Teaching',
    posted: '3 days ago',
    edu: 'M.Sc Physics, B.Ed',
    minExp: 2,
    minSal: 4
  },
  {
    id: 4,
    title: 'School Accountant',
    company: 'TMSS',
    school: 'TMSS',
    logo: 'M',
    logoColor: '#D97706',
    exp: '2–6 Yrs',
    salary: '3–6 LPA',
    skills: ['Accounting', 'Tally ERP', 'GST', 'Fee Collection'],
    dept: 'Accounts',
    posted: '1 day ago',
    edu: 'B.Com / M.Com',
    minExp: 2,
    minSal: 3
  },
  {
    id: 5,
    title: 'HR Executive',
    company: 'Sir Mutha School',
    school: 'Sir Mutha',
    logo: 'S',
    logoColor: '#DC2626',
    exp: '1–4 Yrs',
    salary: '3–5 LPA',
    skills: ['Recruitment', 'HRMS', 'Employee Relations'],
    dept: 'Human Resources',
    posted: '5 days ago',
    edu: 'MBA HR',
    minExp: 1,
    minSal: 3
  },
  {
    id: 6,
    title: 'IT Support Executive',
    company: 'Lady Andal School',
    school: 'Lady Andal',
    logo: 'L',
    logoColor: '#1D4ED8',
    exp: '1–3 Yrs',
    salary: '3–6 LPA',
    skills: ['Computer Hardware', 'Network Administration', 'Technical Support'],
    dept: 'Information Technology',
    posted: '2 weeks ago',
    edu: 'B.Sc CS / BCA',
    minExp: 1,
    minSal: 3
  },
  {
    id: 7,
    title: 'School ERP Administrator',
    company: 'MSS Group of Schools',
    school: 'TMSS',
    logo: 'M',
    logoColor: '#0891B2',
    exp: '2–5 Yrs',
    salary: '4–8 LPA',
    skills: ['School ERP', 'Database Management', 'Technical Support'],
    dept: 'Information Technology',
    posted: '4 days ago',
    edu: 'BCA / MCA',
    minExp: 2,
    minSal: 4
  },
  {
    id: 8,
    title: 'Admission Counselor',
    company: 'LAOS School',
    school: 'LAOS',
    logo: 'L',
    logoColor: '#F59E0B',
    exp: '1–4 Yrs',
    salary: '2.5–5 LPA',
    skills: ['Parent Communication', 'Student Admissions', 'Documentation'],
    dept: 'Administration',
    posted: '6 days ago',
    edu: 'Any Graduate',
    minExp: 1,
    minSal: 2
  },
  {
    id: 9,
    title: 'Receptionist',
    company: 'Sir Mutha School',
    school: 'Sirmlady',
    logo: 'S',
    logoColor: '#6D28D9',
    exp: '0–2 Yrs',
    salary: '2–4 LPA',
    skills: ['Reception Management', 'Visitor Management', 'Customer Service'],
    dept: 'Front Office',
    posted: '1 week ago',
    edu: 'Any Graduate',
    minExp: 0,
    minSal: 2
  },
  {
    id: 10,
    title: 'Librarian',
    company: 'Lady Andal School',
    school: 'Lady Andal',
    logo: 'L',
    logoColor: '#BE185D',
    exp: '2–5 Yrs',
    salary: '3–5 LPA',
    skills: ['Library Management', 'Cataloging', 'Inventory Management'],
    dept: 'Library',
    posted: '3 days ago',
    edu: 'B.Lib / M.Lib',
    minExp: 2,
    minSal: 3
  },
  {
    id: 11,
    title: 'School Nurse',
    company: 'TMSS',
    school: 'TMSS',
    logo: 'M',
    logoColor: '#0D9488',
    exp: '1–4 Yrs',
    salary: '3–5 LPA',
    skills: ['First Aid', 'Emergency Response', 'Medical Records'],
    dept: 'Healthcare',
    posted: '1 day ago',
    edu: 'B.Sc Nursing',
    minExp: 1,
    minSal: 3
  },
  {
    id: 12,
    title: 'Transport Manager',
    company: 'LAOS School',
    school: 'LAOS',
    logo: 'L',
    logoColor: '#1A56DB',
    exp: '3–6 Yrs',
    salary: '4–6 LPA',
    skills: ['Fleet Management', 'GPS Tracking', 'Route Planning'],
    dept: 'Transport',
    posted: '5 days ago',
    edu: 'Any Degree',
    minExp: 3,
    minSal: 4
  },
  {
    id: 13,
    title: 'Hostel Warden',
    company: 'Sir Mutha School',
    school: 'Sir Mutha',
    logo: 'S',
    logoColor: '#64748B',
    exp: '2–5 Yrs',
    salary: '3–5 LPA',
    skills: ['Hostel Administration', 'Student Welfare', 'Discipline Management'],
    dept: 'Hostel',
    posted: '4 days ago',
    edu: 'Any Graduate',
    minExp: 2,
    minSal: 3
  },
  {
    id: 14,
    title: 'Digital Marketing Executive',
    company: 'TMSS',
    school: 'TMSS',
    logo: 'M',
    logoColor: '#0F7ECF',
    exp: '1–4 Yrs',
    salary: '3–6 LPA',
    skills: ['SEO', 'Social Media Marketing', 'School Branding'],
    dept: 'Marketing',
    posted: '2 days ago',
    edu: 'MBA Marketing',
    minExp: 1,
    minSal: 3
  },
  {
    id: 15,
    title: 'Academic Coordinator',
    company: 'Lady Andal School',
    school: 'Lady Andal',
    logo: 'L',
    logoColor: '#B91C1C',
    exp: '5–10 Yrs',
    salary: '6–10 LPA',
    skills: ['Academic Planning', 'Curriculum Development', 'School Management'],
    dept: 'Administration',
    posted: '1 week ago',
    edu: 'Post Graduate + B.Ed',
    minExp: 5,
    minSal: 6
  },
  {
    id: 16,
    title: 'Facilities Manager',
    company: 'TMSS',
    school: 'TMSS',
    logo: 'M',
    logoColor: '#047857',
    exp: '3–8 Yrs',
    salary: '5–8 LPA',
    skills: ['Facility Management', 'Vendor Management', 'Safety Compliance'],
    dept: 'Operations',
    posted: '2 days ago',
    edu: 'Any Graduate',
    minExp: 3,
    minSal: 5
  }
];

const NOTIFICATIONS = [
  { id: 1, msg: 'Your application at Z Tech Solutions has been reviewed.', time: '2 hours ago', read: false },
  { id: 2, msg: 'New jobs matching "PHP Developer" in Chennai.', time: '5 hours ago', read: false },
  { id: 3, msg: 'Posh Automats shortlisted your profile!', time: '1 day ago', read: false },
  { id: 4, msg: 'Complete your profile to get better matches.', time: '2 days ago', read: true },
  { id: 5, msg: 'TCS Digital viewed your resume.', time: '3 days ago', read: true },
];

/* ============================================================
   STATE
   ============================================================ */
let state = {
  user: JSON.parse(localStorage.getItem('tb_user') || 'null'),
  jobs: [...JOBS_DATA],
  filteredJobs: [...JOBS_DATA],
  currentPage: 1,
  jobsPerPage: 8,
  activeCategory: 'all',
  keyword: '',
  expFilter: 30,
  salFilter: 10,          // ← max 10 LPA
  pendingApplyJob: null,
  applyStep: 1,
  notifications: JSON.parse(localStorage.getItem('tb_notifications') || JSON.stringify(NOTIFICATIONS)),
  notifTab: 'all',
};

/* ============================================================
   TOAST
   ============================================================ */
function showToast(msg, type = 'info') {
  if (window.showMssToast) {
    window.showMssToast(msg, type);
  } else {
    console.log(msg);
  }
}
window.showToast = showToast;

/* ============================================================
   AUTH
   ============================================================ */
function updateAuthUI() {
  const authBtn = document.getElementById('authButtons');
  const userMenu = document.getElementById('userMenu');
  if (!authBtn) return;

  if (state.user) {
    authBtn.classList.add('hidden');
    userMenu.classList.remove('hidden');
    const initials = (state.user.name || 'U')[0].toUpperCase();
    document.getElementById('userAvatar').textContent = initials;
    const pnEl = document.getElementById('profileName');
    const peEl = document.getElementById('profileEmail');
    const pmEl = document.getElementById('profileMobile');
    const palEl = document.getElementById('profileAvatarLg');
    if (pnEl) pnEl.textContent = state.user.name || '';
    if (peEl) peEl.textContent = state.user.email || '';
    if (pmEl) pmEl.textContent = state.user.mobile ? `+91 ${state.user.mobile}` : '';
    if (palEl) palEl.textContent = initials;
  } else {
    authBtn.classList.remove('hidden');
    userMenu.classList.add('hidden');
  }
}

function login(userData) {
  state.user = userData;
  localStorage.setItem('tb_user', JSON.stringify(userData));
  updateAuthUI();
  closeModal('loginModal');
  showToast(`Welcome, ${userData.name}!`, 'success');
  if (state.pendingApplyJob) {
    setTimeout(() => openApplyModal(state.pendingApplyJob), 400);
    state.pendingApplyJob = null;
  }
}
window.login = login;

function logout() {
  state.user = null;
  localStorage.removeItem('tb_user');
  updateAuthUI();
  closeDropdowns();
  showToast('Logged out successfully.', 'info');
  if (!window.location.pathname.includes('index.html') && !window.location.pathname.endsWith('/')) {
    window.location.href = 'index.html';
  }
}

/* ============================================================
   MODALS
   ============================================================ */
function openModal(id) {
  document.getElementById(id).classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeModal(id) {
  document.getElementById(id)?.classList.remove('open');
  document.body.style.overflow = '';
}
window.closeModal = closeModal;
window.openModal = openModal;

/* ============================================================
   LOGIN MODAL LOGIC
   ============================================================ */
function initLoginModal() {
  const loginBtn = document.getElementById('loginBtn');
  if (loginBtn) loginBtn.addEventListener('click', () => openModal('loginModal'));

  const modalClose = document.getElementById('modalClose');
  if (modalClose) modalClose.addEventListener('click', () => closeModal('loginModal'));

  const overlay = document.getElementById('loginModal');
  if (overlay) overlay.addEventListener('click', (e) => { if (e.target === overlay) closeModal('loginModal'); });

  const googleBtn = document.getElementById('googleLoginBtn');
  if (googleBtn) googleBtn.addEventListener('click', () => {
    simulateLoading(googleBtn, 'Connecting...', 1200).then(() => {
      login({ name: 'Deepan K', email: 'deepan@gmail.com', mobile: '9876543210', loginType: 'google' });
    });
  });

  const sendOtpBtn = document.getElementById('sendOtpBtn');
  if (sendOtpBtn) sendOtpBtn.addEventListener('click', () => {
    const mobile = document.getElementById('mobileInput').value.trim();
    if (!/^\d{10}$/.test(mobile)) { showToast('Enter a valid 10-digit mobile number.', 'error'); return; }
    simulateLoading(sendOtpBtn, 'Sending...', 900).then(() => {
      document.getElementById('otpVerify').classList.remove('hidden');
      showToast('OTP sent! Use 123456 for demo.', 'success');
    });
  });

  const verifyOtpBtn = document.getElementById('verifyOtpBtn');
  if (verifyOtpBtn) verifyOtpBtn.addEventListener('click', () => {
    const otp = document.getElementById('otpInput').value.trim();
    const mobile = document.getElementById('mobileInput').value.trim();
    if (otp !== '123456') { showToast('Invalid OTP. Try 123456.', 'error'); return; }
    simulateLoading(verifyOtpBtn, 'Verifying...', 800).then(() => {
      login({ name: 'Candidate User', email: '', mobile, loginType: 'otp' });
    });
  });
}

function simulateLoading(btn, text, ms) {
  const orig = btn.textContent;
  btn.textContent = text;
  btn.disabled = true;
  return new Promise(res => setTimeout(() => {
    btn.textContent = orig;
    btn.disabled = false;
    res();
  }, ms));
}

/* ============================================================
   DROPDOWN / PROFILE
   ============================================================ */
function closeDropdowns() {
  document.getElementById('profileDropdown')?.classList.remove('open');
}
window.closeDropdowns = closeDropdowns;

function initDropdowns() {
  const avatarWrap = document.getElementById('avatarWrap');
  if (avatarWrap) {
    avatarWrap.addEventListener('click', (e) => {
      e.stopPropagation();
      document.getElementById('profileDropdown')?.classList.toggle('open');
    });
  }
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) logoutBtn.addEventListener('click', logout);
  document.addEventListener('click', closeDropdowns);
}

/* ============================================================
   NOTIFICATION PANEL
   ============================================================ */
function renderNotifications() {
  const list = document.getElementById('notifList');
  if (!list) return;
  const tab = state.notifTab;
  const items = tab === 'all' ? state.notifications :
    tab === 'unread' ? state.notifications.filter(n => !n.read) :
      state.notifications.filter(n => n.read);
  list.innerHTML = items.length ? items.map(n => `
    <div class="notif-item ${n.read ? 'read' : 'unread'}" data-id="${n.id}">
      <div class="notif-icon-wrap">
        <i class="fa-solid ${n.read ? 'fa-bell-slash' : 'fa-bell'}"></i>
      </div>
      <div class="notif-content">
        <div class="notif-msg">${n.msg}</div>
        <div class="notif-time">${n.time}</div>
      </div>
    </div>
  `).join('') : '<p style="text-align:center;color:#9CA3AF;padding:24px;font-size:13px;">No notifications</p>';

  list.querySelectorAll('.notif-item').forEach(el => {
    el.addEventListener('click', () => {
      const n = state.notifications.find(x => x.id == el.dataset.id);
      if (n) { n.read = true; localStorage.setItem('tb_notifications', JSON.stringify(state.notifications)); updateNotifBadge(); renderNotifications(); }
    });
  });
}

function updateNotifBadge() {
  const unread = state.notifications.filter(n => !n.read).length;
  const badge = document.getElementById('notifBadge');
  if (badge) { badge.textContent = unread; badge.style.display = unread ? '' : 'none'; }
}

function initNotifications() {
  const notifBtn = document.getElementById('notifBtn');
  const notifPanel = document.getElementById('notifPanel');
  const notifClose = document.getElementById('notifClose');

  if (notifBtn) notifBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    notifPanel?.classList.toggle('open');
    closeDropdowns();
    renderNotifications();
  });
  if (notifClose) notifClose.addEventListener('click', () => notifPanel?.classList.remove('open'));

  document.querySelectorAll('.notif-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.notif-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      state.notifTab = tab.dataset.tab;
      renderNotifications();
    });
  });
  updateNotifBadge();
}

/* ============================================================
   SEARCH TOGGLE
   ============================================================ */
function initSearchToggle() {
  const btn = document.getElementById('searchToggleBtn');
  const bar = document.getElementById('inlineSearch');
  if (btn && bar) {
    btn.addEventListener('click', () => {
      bar.classList.toggle('open');
      if (bar.classList.contains('open')) document.getElementById('inlineSearchInput')?.focus();
    });
  }
  const inlineInput = document.getElementById('inlineSearchInput');
  if (inlineInput) {
    inlineInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const q = inlineInput.value.trim();
        if (q) { state.keyword = q; applyFiltersAndRender(); scrollToJobs(); }
      }
    });
  }
}

/* ============================================================
   HAMBURGER
   ============================================================ */
function initHamburger() {
  const ham = document.getElementById('hamburger');
  const nav = document.getElementById('mainNav');
  if (ham && nav) ham.addEventListener('click', () => nav.classList.toggle('mobile-open'));
}

/* ============================================================
   HERO SEARCH
   ============================================================ */
function initHeroSearch() {
  const btn = document.getElementById('heroSearchBtn');
  if (btn) btn.addEventListener('click', () => {
    state.keyword = document.getElementById('keywordInput').value.trim();
    applyFiltersAndRender();
    scrollToJobs();
  });
  const ki = document.getElementById('keywordInput');
  if (ki) ki.addEventListener('keydown', (e) => { if (e.key === 'Enter') btn?.click(); });
}

function quickSearch(term) {
  state.keyword = term;
  const ki = document.getElementById('keywordInput');
  if (ki) ki.value = term;
  applyFiltersAndRender();
  scrollToJobs();
}
window.quickSearch = quickSearch;

function scrollToJobs() {
  document.getElementById('jobs-section')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/* ============================================================
   CATEGORY PILLS
   ============================================================ */
function initCategoryPills() {
  document.querySelectorAll('.pill').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      state.activeCategory = pill.dataset.dept;
      state.currentPage = 1;
      applyFiltersAndRender();
    });
  });
}

/* ============================================================
   FILTERS
   ============================================================ */
function toggleFilter(el) {
  el.classList.toggle('collapsed');
  const body = el.nextElementSibling;
  if (body) body.classList.toggle('collapsed');
}
window.toggleFilter = toggleFilter;

function initFilters() {
  /* ── Experience range ── */
  const expRange = document.getElementById('expRange');
  if (expRange) expRange.addEventListener('input', () => {
    state.expFilter = +expRange.value;
    document.getElementById('expRangeLabel').textContent = `0 – ${state.expFilter} Yrs`;
    debouncedFilter();
  });

  /* ── Salary range — now max 10 LPA ── */
  const salRange = document.getElementById('salRange');
  if (salRange) {
    salRange.max = 10;          // cap at 10
    salRange.value = 10;
    salRange.step = 1;
    const salLabel = document.getElementById('salRangeLabel');
    if (salLabel) salLabel.textContent = 'Up to 10 LPA';

    salRange.addEventListener('input', () => {
      state.salFilter = +salRange.value;
      if (salLabel) salLabel.textContent = `Up to ${state.salFilter} LPA`;
      debouncedFilter();
    });
  }

  document.querySelectorAll('[data-filter]').forEach(cb => {
    cb.addEventListener('change', debouncedFilter);
  });

  const clearAll = document.getElementById('clearAllBtn');
  if (clearAll) clearAll.addEventListener('click', () => {
    document.querySelectorAll('[data-filter]').forEach(cb => cb.checked = false);
    if (expRange) { expRange.value = 30; state.expFilter = 30; document.getElementById('expRangeLabel').textContent = '0 – 30 Yrs'; }
    if (salRange) {
      salRange.value = 10; state.salFilter = 10;
      const salLabel = document.getElementById('salRangeLabel');
      if (salLabel) salLabel.textContent = 'Up to 10 LPA';
    }
    state.keyword = '';
    const ki = document.getElementById('keywordInput');
    if (ki) ki.value = '';
    applyFiltersAndRender();
    showToast('Filters cleared.', 'info');
  });

  const sort = document.getElementById('sortSelect');
  if (sort) sort.addEventListener('change', () => applyFiltersAndRender());

  const mob = document.getElementById('filterToggleMob');
  const sidebar = document.getElementById('filtersSidebar');
  if (mob && sidebar) mob.addEventListener('click', () => sidebar.classList.toggle('mobile-open'));

  /* ── Inject extra filter checkboxes into sidebar ── */
  injectExtraFilters();
}

/* ── Dynamically inject Education, School filter groups ── */
async function injectExtraFilters() {
  const sidebar = document.getElementById('filtersSidebar');
  if (!sidebar) return;

  /* Remove any previously injected groups to avoid duplicates on re-init */
  sidebar.querySelectorAll('.injected-filter-group').forEach(el => el.remove());

  /* Load education options from JSON */
  let eduOptions = ['B.E / B.Tech', 'B.Sc CS', 'BCA', 'M.Tech', 'MCA', 'M.Sc', 'MBA', 'Diploma'];
  try {
    const res = await fetch('education.json');
    const data = await res.json();
    if (Array.isArray(data.education)) {
      eduOptions = data.education.map(e => e.name);
    }
  } catch (_) { /* fallback to defaults */ }

  /* Load skills options from JSON */
  let skillsByCategory = {};
  try {
    const res = await fetch('skills.json');
    const data = await res.json();
    if (Array.isArray(data.skills)) {
      data.skills.forEach(s => {
        if (!skillsByCategory[s.category]) skillsByCategory[s.category] = [];
        skillsByCategory[s.category].push(s.skill_name);
      });
    }
  } catch (_) {
    skillsByCategory = {
      'Software Development': ['HTML', 'CSS', 'JavaScript', 'PHP', 'Python', 'MySQL', 'React', 'API Development'],
    };
  }

  const schoolOptions = ['Lady Andal', 'LAOS', 'TMSS', 'MSS Chennai', 'Sir Mutha', 'Sirmlady'];

  const deptOptions = [
    'Teaching', 'Administration', 'Human Resources', 'Accounts',
    'Information Technology', 'Front Office', 'Library', 'Healthcare',
    'Transport', 'Hostel', 'Marketing', 'Operations',
  ];

  /* ── Education filter with search + scroll ── */
  const eduWrap = document.createElement('div');
  eduWrap.className = 'filter-group injected-filter-group';
  eduWrap.innerHTML = `
    <div class="filter-group-title" onclick="toggleFilter(this)">
      <span>Education</span> <i class="fa-solid fa-chevron-down"></i>
    </div>
    <div class="filter-group-body">
      <div class="filter-search-wrap">
        <i class="fa-solid fa-magnifying-glass filter-search-icon"></i>
        <input type="text" class="filter-search-input" placeholder="Search education..." autocomplete="off" />
      </div>
      <div class="filter-scroll-list" id="eduScrollList">
        ${eduOptions.map(o => `
          <label class="filter-check">
            <input type="checkbox" data-filter="edu" value="${o}" />
            <span>${o}</span>
          </label>
        `).join('')}
      </div>
    </div>
  `;
  sidebar.appendChild(eduWrap);

  /* Search input filters visible options */
  const searchInput = eduWrap.querySelector('.filter-search-input');
  const scrollList = eduWrap.querySelector('#eduScrollList');
  searchInput.addEventListener('input', () => {
    const q = searchInput.value.toLowerCase().trim();
    scrollList.querySelectorAll('.filter-check').forEach(label => {
      const text = label.querySelector('span').textContent.toLowerCase();
      label.style.display = text.includes(q) ? '' : 'none';
    });
  });

  /* Bind change events */
  eduWrap.querySelectorAll('[data-filter]').forEach(cb => cb.addEventListener('change', debouncedFilter));

  /* ── Skills filter with search + scroll + category groups ── */
  const skillsWrap = document.createElement('div');
  skillsWrap.className = 'filter-group injected-filter-group';
  const skillItemsHtml = Object.entries(skillsByCategory).map(([cat, skills]) => `
    <div class="filter-category-label">${cat}</div>
    ${skills.map(s => `
      <label class="filter-check">
        <input type="checkbox" data-filter="skill" value="${s}" />
        <span>${s}</span>
      </label>
    `).join('')}
  `).join('');
  skillsWrap.innerHTML = `
    <div class="filter-group-title" onclick="toggleFilter(this)">
      <span>Skills</span> <i class="fa-solid fa-chevron-down"></i>
    </div>
    <div class="filter-group-body">
      <div class="filter-search-wrap">
        <i class="fa-solid fa-magnifying-glass filter-search-icon"></i>
        <input type="text" class="filter-search-input" placeholder="Search skills..." autocomplete="off" />
      </div>
      <div class="filter-scroll-list" id="skillScrollList">
        ${skillItemsHtml}
      </div>
    </div>
  `;
  sidebar.appendChild(skillsWrap);

  const skillSearchInput = skillsWrap.querySelector('.filter-search-input');
  const skillScrollList = skillsWrap.querySelector('#skillScrollList');
  skillSearchInput.addEventListener('input', () => {
    const q = skillSearchInput.value.toLowerCase().trim();
    skillScrollList.querySelectorAll('.filter-check').forEach(label => {
      const text = label.querySelector('span').textContent.toLowerCase();
      label.style.display = text.includes(q) ? '' : 'none';
    });
    /* hide category header when all its skill rows are hidden */
    skillScrollList.querySelectorAll('.filter-category-label').forEach(cat => {
      let sibling = cat.nextElementSibling;
      let anyVisible = false;
      while (sibling && !sibling.classList.contains('filter-category-label')) {
        if (sibling.style.display !== 'none') { anyVisible = true; break; }
        sibling = sibling.nextElementSibling;
      }
      cat.style.display = anyVisible ? '' : 'none';
    });
  });

  skillsWrap.querySelectorAll('[data-filter]').forEach(cb => cb.addEventListener('change', debouncedFilter));

  /* ── Department + School filters ── */
  [
    { title: 'Department', attr: 'dept', opts: deptOptions },
    { title: 'School', attr: 'school', opts: schoolOptions },
  ].forEach(g => {
    const wrap = document.createElement('div');
    wrap.className = 'filter-group injected-filter-group';
    wrap.innerHTML = `
      <div class="filter-group-title" onclick="toggleFilter(this)">
        <span>${g.title}</span> <i class="fa-solid fa-chevron-down"></i>
      </div>
      <div class="filter-group-body">
        ${g.opts.map(o => `
          <label class="filter-check">
            <input type="checkbox" data-filter="${g.attr}" value="${o}" />
            <span>${o}</span>
          </label>
        `).join('')}
      </div>
    `;
    sidebar.appendChild(wrap);
    wrap.querySelectorAll('[data-filter]').forEach(cb => cb.addEventListener('change', debouncedFilter));
  });
}

let filterTimer;
function debouncedFilter() {
  clearTimeout(filterTimer);
  filterTimer = setTimeout(() => { state.currentPage = 1; applyFiltersAndRender(); }, 180);
}

function applyFiltersAndRender() {
  let jobs = [...JOBS_DATA];

  /* keyword */
  if (state.keyword) {
    const kw = state.keyword.toLowerCase();
    jobs = jobs.filter(j =>
      j.title.toLowerCase().includes(kw) ||
      j.company.toLowerCase().includes(kw) ||
      (j.school || '').toLowerCase().includes(kw) ||
      j.skills.some(s => s.toLowerCase().includes(kw))
    );
  }

  /* experience range */
  jobs = jobs.filter(j => j.minExp <= state.expFilter);

  /* salary range — always active (max 10 LPA) */
  jobs = jobs.filter(j => j.minSal <= state.salFilter);

  /* checkbox filters */
  const checked = (attr) => [...document.querySelectorAll(`[data-filter="${attr}"]:checked`)].map(c => c.value);


  const depts = checked('dept');
  if (depts.length) jobs = jobs.filter(j => depts.includes(j.dept));

  const skills = checked('skill');
  if (skills.length) jobs = jobs.filter(j => skills.some(s => j.skills.includes(s)));

  const edus = checked('edu');
  if (edus.length) jobs = jobs.filter(j =>
    j.edu && edus.some(e => j.edu.toLowerCase().includes(e.toLowerCase()) || e.toLowerCase().includes(j.edu.toLowerCase()))
  );

  const schools = checked('school');
  if (schools.length) jobs = jobs.filter(j => schools.includes(j.school));

  /* sort */
  const sort = document.getElementById('sortSelect')?.value || 'relevance';
  if (sort === 'salary') jobs.sort((a, b) => b.minSal - a.minSal);
  else if (sort === 'date') jobs.sort((a, b) => a.id - b.id);

  state.filteredJobs = jobs;
  renderJobs();
  renderPagination();
}

/* ============================================================
   RENDER JOBS
   ============================================================ */

/* School badge colour map */
const SCHOOL_COLORS = {
  'Lady Andal':  { bg: '#FEF3C7', color: '#92400E', border: '#FDE68A' },
  'LAOS':        { bg: '#DCFCE7', color: '#166534', border: '#BBF7D0' },
  'Sirmlady':    { bg: '#FCE7F3', color: '#9D174D', border: '#FBCFE8' },
  'TMSS':        { bg: '#DBEAFE', color: '#1E40AF', border: '#BFDBFE' },
  'MSS Chennai': { bg: '#DBEAFE', color: '#1E40AF', border: '#BFDBFE' },
  'Sir Mutha':   { bg: '#EDE9FE', color: '#5B21B6', border: '#DDD6FE' },
};

function renderJobs() {
  const list = document.getElementById('jobList');
  const countEl = document.getElementById('jobsCount');
  if (!list) return;

  list.innerHTML = Array(3).fill(0).map(() => `
    <div class="skeleton-card">
      <div style="display:flex;gap:14px;">
        <div class="skeleton sk-logo"></div>
        <div style="flex:1;">
          <div class="skeleton sk-line sk-title" style="margin-bottom:10px;"></div>
          <div class="skeleton sk-line sk-comp"></div>
        </div>
      </div>
      <div style="display:flex;gap:8px;margin-top:14px;">
        <div class="skeleton sk-line sk-b1"></div>
        <div class="skeleton sk-line sk-b2"></div>
        <div class="skeleton sk-line sk-b3"></div>
      </div>
    </div>
  `).join('');

  setTimeout(() => {
    const start = (state.currentPage - 1) * state.jobsPerPage;
    const pageJobs = state.filteredJobs.slice(start, start + state.jobsPerPage);
    const total = state.filteredJobs.length;

    if (countEl) countEl.innerHTML = total
      ? `Showing <strong>${start + 1}–${Math.min(start + state.jobsPerPage, total)}</strong> of <strong>${total}</strong> jobs`
      : '0 jobs found';

    if (!pageJobs.length) {
      list.innerHTML = `<div class="empty-state" style="background:white;border-radius:12px;border:1px solid #E5E7EB;">
        <i class="fa-solid fa-briefcase" style="font-size:48px;opacity:.3;margin-bottom:12px;display:block;"></i>
        <h3>No jobs found</h3><p>Try adjusting your filters or search terms.</p>
      </div>`;
      return;
    }

    list.innerHTML = pageJobs.map(job => {
      const sc = SCHOOL_COLORS[job.school] || { bg: '#F3F4F6', color: '#374151', border: '#E5E7EB' };
      const schoolBadge = job.school
        ? `<span class="badge school-badge" style="background:${sc.bg};color:${sc.color};border-color:${sc.border};">
             <i class="fa-solid fa-school"></i> ${job.school}
           </span>`
        : '';
      const eduBadge = job.edu
        ? `<span class="badge"><i class="fa-solid fa-graduation-cap"></i> ${job.edu}</span>`
        : '';

      return `
      <div class="job-card" data-id="${job.id}">
        ${job.urgent ? '<span class="urgent-badge">Urgent</span>' : ''}
        <div class="job-card-top">
          <div class="job-logo" style="background:${job.logoColor}">${job.logo}</div>
          <div class="job-meta">
            <div class="job-title">${job.title}</div>
            <div class="job-company"><strong>${job.company}</strong></div>
            <div class="job-badges">
              <span class="badge"><i class="fa-solid fa-briefcase"></i> ${job.exp}</span>
              <span class="badge"><i class="fa-solid fa-indian-rupee-sign"></i> ${job.salary}</span>
              ${eduBadge}
              ${schoolBadge}
            </div>
            <div class="job-skills">
              ${job.skills.map(s => `<span class="skill-tag">${s}</span>`).join('')}
            </div>
          </div>
        </div>
        <div class="job-footer">
          <span class="job-posted"><i class="fa-regular fa-clock"></i> ${job.posted}</span>
          <div class="job-actions">
            <button class="btn-outline view-btn" data-id="${job.id}">View Details</button>
            <button class="btn-primary apply-btn" data-id="${job.id}"><i class="fa-solid fa-paper-plane"></i> Apply Now</button>
          </div>
        </div>
      </div>
    `}).join('');

    list.querySelectorAll('.apply-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const job = JOBS_DATA.find(j => j.id == btn.dataset.id);
        if (!job) return;
        if (!state.user) { state.pendingApplyJob = job; openModal('loginModal'); }
        else openApplyModal(job);
      });
    });

    list.querySelectorAll('.view-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        window.location.href = `candidate-job-details.html?id=${btn.dataset.id}`;
      });
    });
  }, 500);
}

function renderPagination() {
  const pag = document.getElementById('pagination');
  if (!pag) return;
  const total = state.filteredJobs.length;
  const pages = Math.ceil(total / state.jobsPerPage);
  if (pages <= 1) { pag.innerHTML = ''; return; }

  let html = '';
  if (state.currentPage > 1) html += `<button class="page-btn" data-p="${state.currentPage - 1}">‹</button>`;
  for (let i = 1; i <= pages; i++) html += `<button class="page-btn ${i === state.currentPage ? 'active' : ''}" data-p="${i}">${i}</button>`;
  if (state.currentPage < pages) html += `<button class="page-btn" data-p="${state.currentPage + 1}">›</button>`;
  pag.innerHTML = html;

  pag.querySelectorAll('.page-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      state.currentPage = +btn.dataset.p;
      renderJobs(); renderPagination(); scrollToJobs();
    });
  });
}

/* ============================================================
   APPLY MODAL
   ============================================================ */
window.openApplyModal = openApplyModal;
window.queuePendingApplyJob = function (job) { state.pendingApplyJob = job; };

function openApplyModal(job) {
  state.pendingApplyJob = job;
  state.applyStep = 1;
  document.getElementById('applyJobTitle').textContent = job.title;
  document.getElementById('applyCompanyName').textContent = job.company;
  const prof = JSON.parse(localStorage.getItem('tb_profile') || '{}');
  if (state.user?.name) document.getElementById('appName').value = state.user.name;
  if (state.user?.email) document.getElementById('appEmail').value = state.user.email;
  if (prof.education) document.getElementById('appEdu').value = prof.education;
  if (prof.experience) document.getElementById('appExp').value = prof.experience;
  if (prof.company) document.getElementById('appCurrComp').value = prof.company;
  if (prof.salary) document.getElementById('appCurrSal').value = prof.salary;
  if (prof.skills) document.getElementById('appSkills').value = prof.skills;
  updateStepper();
  openModal('applyModal');
}

function updateStepper() {
  const s = state.applyStep;
  document.querySelectorAll('.step').forEach((el, i) => {
    el.classList.remove('active', 'done');
    if (i + 1 < s) el.classList.add('done');
    else if (i + 1 === s) el.classList.add('active');
  });
  document.querySelectorAll('.step-line').forEach((el, i) => {
    el.classList.toggle('done', i + 1 < s);
  });
  document.querySelectorAll('.step-page').forEach((el, i) => {
    el.classList.toggle('active', i + 1 === s);
  });
  const prevBtn = document.getElementById('prevStepBtn');
  const nextBtn = document.getElementById('nextStepBtn');
  if (prevBtn) prevBtn.disabled = s === 1;
  if (nextBtn) nextBtn.textContent = s === 4 ? 'Submit Application' : 'Next →';
}

function initApplyModal() {
  const closeBtn = document.getElementById('applyModalClose');
  if (closeBtn) closeBtn.addEventListener('click', () => closeModal('applyModal'));

  const overlay = document.getElementById('applyModal');
  if (overlay) overlay.addEventListener('click', (e) => { if (e.target === overlay) closeModal('applyModal'); });

  const prevBtn = document.getElementById('prevStepBtn');
  const nextBtn = document.getElementById('nextStepBtn');

  if (prevBtn) prevBtn.addEventListener('click', () => {
    if (state.applyStep > 1) { state.applyStep--; updateStepper(); }
  });
  if (nextBtn) nextBtn.addEventListener('click', () => {
    if (state.applyStep < 4) {
      state.applyStep++;
      if (state.applyStep === 4) populateReview();
      updateStepper();
    } else {
      submitApplication();
    }
  });

  const resumeFile = document.getElementById('resumeFile');
  if (resumeFile) resumeFile.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;
    document.getElementById('uploadedFileName').textContent = file.name;
    document.getElementById('uploadSuccess').classList.remove('hidden');
    setTimeout(() => {
      document.querySelector('.parsing-text').textContent = '✓ Resume parsed';
      if (!document.getElementById('appName').value && state.user?.name)
        document.getElementById('appName').value = state.user.name;
      showToast('Resume parsed & fields auto-filled!', 'success');
    }, 1500);
  });
}

function populateReview() {
  const data = {
    'Full Name': document.getElementById('appName')?.value || '—',
    'Email': document.getElementById('appEmail')?.value || '—',
    'Education': document.getElementById('appEdu')?.value || '—',
    'Experience': document.getElementById('appExp')?.value || '—',
    'Current Company': document.getElementById('appCurrComp')?.value || '—',
    'Current Salary': document.getElementById('appCurrSal')?.value || '—',
    'Expected Salary': document.getElementById('appExpSal')?.value || '—',
    'Notice Period': document.getElementById('noticePeriod')?.value || '—',
    'Key Skills': document.getElementById('appSkills')?.value || '—',
  };
  document.getElementById('reviewCard').innerHTML = Object.entries(data).map(([k, v]) =>
    `<div class="review-row"><span class="review-key">${k}</span><span class="review-val">${v}</span></div>`
  ).join('');
}

function submitApplication() {
  if (!document.getElementById('agreeTerms')?.checked) {
    showToast('Please agree to the terms before submitting.', 'warning'); return;
  }
  const job = state.pendingApplyJob;
  if (!job) return;

  const existing = JSON.parse(localStorage.getItem('tb_applications') || '[]');
  if (existing.find(a => a.jobId === job.id)) {
    showToast('You have already applied for this job!', 'warning'); return;
  }

  const appId = 'TB' + Date.now().toString().slice(-8);
  const app = {
    id: appId,
    jobId: job.id,
    jobTitle: job.title,
    company: job.company,
    school: job.school || '',
    appliedDate: new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }),
    status: 'Under Review',
  };
  existing.push(app);
  localStorage.setItem('tb_applications', JSON.stringify(existing));

  closeModal('applyModal');
  showToast(`Application submitted! ID: ${appId}`, 'success');
  setTimeout(() => window.location.href = 'candidate-applied-jobs.html', 1600);
}

/* ============================================================
   INIT
   ============================================================ */
document.addEventListener('DOMContentLoaded', () => {
  updateAuthUI();
  initLoginModal();
  initDropdowns();
  initNotifications();
  initSearchToggle();
  initHamburger();
  initHeroSearch();
  initCategoryPills();
  initFilters();
  initApplyModal();

  if (document.getElementById('jobList')) applyFiltersAndRender();

  window.addEventListener('scroll', () => {
    const header = document.getElementById('mainHeader');
    if (header) header.style.boxShadow = window.scrollY > 10 ? '0 4px 20px rgba(0,0,0,.12)' : '';
  });
});