
    /* ── Init sidebar ──────────────────────────── */
    if (typeof initSidebar === 'function') initSidebar('offer-management');

    const API_BASE = window.API_BASE || window.AUTH_API_BASE || 'http://127.0.0.1:8000';
    const _token = () => localStorage.getItem('access_token') || '';

    /* ── Data ──────────────────────────────────── */
    let CANDIDATES = [];

    const STATUS_META = {
      awaiting: { label: 'Awaiting Offer', cls: 'badge-awaiting' },
      pending: { label: 'Offer Pending', cls: 'badge-pending' },
      sent: { label: 'Offer Sent', cls: 'badge-sent' },
      accepted: { label: 'Accepted', cls: 'badge-accepted' },
      draft: { label: 'Draft', cls: 'badge-draft' },
    };

    const TEMPLATES = {
      standard: {
        name: 'Standard Employment',
        body: `Dear <span class="ph">[Candidate Name]</span>,<br><br>
We are pleased to offer you the position of <span class="ph">[Job Title]</span> at <span class="ph">[School Name]</span>, under the <span class="ph">[Department]</span> department.<br><br>
This is a full-time position with a gross annual compensation of <span class="ph">[Offered Salary]</span> LPA. Your expected date of joining is <span class="ph">[Joining Date]</span>. You will be subject to a probationary period of <span class="ph">[Probation Period]</span>.<br><br>
Please confirm your acceptance by <span class="ph">[Expiry Date]</span>. If you have any questions, feel free to reach out to our HR team.<br><br>
We look forward to welcoming you to the team.<br><br>
Warm regards,<br><strong>School Admin — TMSS</strong>`
      },
      teaching: {
        name: 'Teaching Staff Offer',
        body: `Dear <span class="ph">[Candidate Name]</span>,<br><br>
Congratulations! We are delighted to extend this offer for the role of <span class="ph">[Job Title]</span> at <span class="ph">[School Name]</span>.<br><br>
As a member of our academic faculty under <span class="ph">[Department]</span>, your responsibilities will include curriculum delivery, student assessment, and participation in school events as per the academic calendar.<br><br>
Compensation: <span class="ph">[Offered Salary]</span> LPA | Joining: <span class="ph">[Joining Date]</span> | Probation: <span class="ph">[Probation Period]</span><br><br>
Kindly confirm your acceptance by <span class="ph">[Expiry Date]</span>.<br><br>
Regards,<br><strong>School Admin — TMSS</strong>`
      },
      admin: {
        name: 'Administrative Offer',
        body: `Dear <span class="ph">[Candidate Name]</span>,<br><br>
We are pleased to offer you the administrative role of <span class="ph">[Job Title]</span> within the <span class="ph">[Department]</span> at <span class="ph">[School Name]</span>.<br><br>
Your role will include coordination, reporting, and administrative support across departments. Compensation package: <span class="ph">[Offered Salary]</span> LPA.<br><br>
Date of Joining: <span class="ph">[Joining Date]</span> | Probation: <span class="ph">[Probation Period]</span> | Offer valid until: <span class="ph">[Expiry Date]</span>.<br><br>
Sincerely,<br><strong>School Admin — TMSS</strong>`
      },
      contract: {
        name: 'Contract / Part-time',
        body: `Dear <span class="ph">[Candidate Name]</span>,<br><br>
This letter confirms a fixed-term engagement for the role of <span class="ph">[Job Title]</span> at <span class="ph">[School Name]</span>.<br><br>
Nature: Contract / Part-time | Department: <span class="ph">[Department]</span> | Remuneration: <span class="ph">[Offered Salary]</span> LPA (pro-rated).<br><br>
Start Date: <span class="ph">[Joining Date]</span>. This offer expires on <span class="ph">[Expiry Date]</span>.<br><br>
Please sign and return this letter as acceptance.<br><br>
Best regards,<br><strong>School Admin — TMSS</strong>`
      }
    };

    /* ── State ─────────────────────────────────── */
    let currentCandidate = null;
    let selectedTemplate = null;
    let data = [...CANDIDATES];

    /* ── Render Table ──────────────────────────── */
    function renderTable(rows) {
      const tbody = document.getElementById('tableBody');
      const empty = document.getElementById('emptyState');
      document.getElementById('rowCount').textContent = rows.length + ' record' + (rows.length !== 1 ? 's' : '');
      if (!rows.length) { tbody.innerHTML = ''; empty.style.display = 'block'; return; }
      empty.style.display = 'none';
      tbody.innerHTML = rows.map(c => {
        const s = STATUS_META[c.status];
        const isAwaiting = c.status === 'awaiting';
        return `<tr data-id="${c.id}">
      <td>
        <div class="avatar-cell">
          <div class="avatar ${c.av}">${c.initials}</div>
          <div>
            <div class="cname">${c.name}</div>
            <div class="crole">${c.exp} experience</div>
          </div>
        </div>
      </td>
      <td>${c.role}</td>
      <td>${c.dept}</td>
      <td style="font-size:12.5px;">${c.school}</td>
      <td><span class="badge ${s.cls}">${s.label}</span></td>
      <td style="color:var(--text3);font-size:12.5px;">${c.updated}</td>
      <td>
        <div class="action-btns">
          ${isAwaiting ? `<button class="btn btn-issue btn-sm" onclick="openIssueModal(${c.id})">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
            Issue Offer
          </button>` : `
          <div class="icon-btn" title="View Offer" onclick="viewOffer(${c.id})">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
          </div>
          <div class="icon-btn" title="Download PDF" onclick="downloadOffer(${c.id})">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          </div>`}
        </div>
      </td>
    </tr>`;
      }).join('');
    }

    /* ── Filters ────────────────────────────────── */
    function applyFilters() {
      const q = document.getElementById('searchInput').value.toLowerCase();
      const statusCheck = document.getElementById('statusFilter').value;
      const roleCheck = document.getElementById('jobFilter').value;

      let res = CANDIDATES.filter(c => {
        let match = true;
        if (q) match = match && (c.name.toLowerCase().includes(q) || (c.school && c.school.toLowerCase().includes(q)));
        if (statusCheck) {
          if (statusCheck === 'pending' && !['pending', 'draft', 'awaiting'].includes(c.status)) match = false;
          else if (statusCheck !== 'pending' && c.status !== statusCheck) match = false;
        }
        if (roleCheck) match = match && c.role === roleCheck;
        return match;
      });
      data = res;
      renderTable(data);
    }

    function filterByStatus(status) {
      document.getElementById('statusFilter').value = status;
      document.querySelectorAll('.stat-card').forEach(el => el.classList.remove('active-filter'));
      applyFilters();
    }

    /* ── Open Issue Offer Modal ─────────────────── */
    function openIssueModal(id) {
      currentCandidate = CANDIDATES.find(c => c.id === id);
      selectedTemplate = null;
      if (!currentCandidate) return;

      document.getElementById('modalTitle').textContent = 'Issue Offer — ' + currentCandidate.name;
      document.getElementById('modalSub').textContent = currentCandidate.role + ' · ' + currentCandidate.school;

      // Auto-fill chips
      const chips = [
        { icon: personIcon(), text: currentCandidate.name },
        { icon: briefcaseIcon(), text: currentCandidate.role },
        { icon: deptIcon(), text: currentCandidate.dept },
        { icon: schoolIcon(), text: currentCandidate.school },
      ];
      document.getElementById('autofillRow').innerHTML = chips.map(ch =>
        `<span class="af-chip">${ch.icon}${ch.text}</span>`
      ).join('');

      // Reset fields
      ['offSalary', 'offProbation', 'offJoining', 'offExpiry', 'offNotes'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
      });

      // Set min date to today's local date to prevent past dates selection
      const today = new Date();
      const yyyy = today.getFullYear();
      const mm = String(today.getMonth() + 1).padStart(2, '0');
      const dd = String(today.getDate()).padStart(2, '0');
      const minDateStr = `${yyyy}-${mm}-${dd}`;
      const joiningInput = document.getElementById('offJoining');
      if (joiningInput) joiningInput.min = minDateStr;
      const expiryInput = document.getElementById('offExpiry');
      if (expiryInput) expiryInput.min = minDateStr;

      document.querySelectorAll('.template-card').forEach(el => el.classList.remove('selected'));
      document.getElementById('previewPanel').classList.remove('visible');
      document.getElementById('previewPanel').innerHTML = '';
      document.getElementById('previewBtn').innerHTML = previewBtnInner('Preview Letter');

      document.getElementById('offerModal').style.display = 'flex';
      document.body.style.overflow = 'hidden';
    }

    function closeModal() {
      document.getElementById('offerModal').style.display = 'none';
      document.body.style.overflow = '';
      currentCandidate = null;
      selectedTemplate = null;
    }

    /* ── Template Select ────────────────────────── */
    function selectTemplate(el) {
      document.querySelectorAll('.template-card').forEach(c => c.classList.remove('selected'));
      el.classList.add('selected');
      selectedTemplate = el.dataset.tpl;
      // auto-refresh preview if open
      if (document.getElementById('previewPanel').classList.contains('visible')) buildPreview();
    }

    /* ── Preview ────────────────────────────────── */
    function previewBtnInner(label) {
      return `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>${label}`;
    }

    function togglePreview() {
      const panel = document.getElementById('previewPanel');
      if (panel.classList.contains('visible')) {
        panel.classList.remove('visible');
        document.getElementById('previewBtn').innerHTML = previewBtnInner('Preview Letter');
      } else {
        buildPreview();
      }
    }

    function generateOfferLetterHTML() {
      if (!selectedTemplate) return "";
      const tpl = TEMPLATES[selectedTemplate];
      const c = currentCandidate;
      const sal = document.getElementById('offSalary').value || '[Offered Salary]';
      const prob = document.getElementById('offProbation').value || '[Probation Period]';
      const join = fmtDate(document.getElementById('offJoining').value) || '[Joining Date]';
      const exp = fmtDate(document.getElementById('offExpiry').value) || '[Expiry Date]';

      const adminEmail = localStorage.getItem('user_email') || 'admin@school.org';
      const regardsSignature = `School Admin - ${adminEmail}`;

      let body = tpl.body
        .replace(/\[Candidate Name\]/g, c.name)
        .replace(/\[Job Title\]/g, c.role)
        .replace(/\[School Name\]/g, c.school)
        .replace(/\[Department\]/g, c.dept)
        .replace(/\[Offered Salary\]/g, sal)
        .replace(/\[Probation Period\]/g, prob)
        .replace(/\[Joining Date\]/g, join)
        .replace(/\[Expiry Date\]/g, exp)
        .replace(/School Admin — TMSS/g, regardsSignature);

      const notes = document.getElementById('offNotes').value.trim();
      if (notes) body += `<br><br><em style="color:var(--text3);font-size:12px;">Additional terms: ${notes}</em>`;
      return body;
    }

    function buildPreview() {
      if (!selectedTemplate) { showToast('<i class="ti ti-alert-triangle" aria-hidden="true"></i> Please select a template first.'); return; }
      const tpl = TEMPLATES[selectedTemplate];
      const body = generateOfferLetterHTML();

      const panel = document.getElementById('previewPanel');
      panel.innerHTML = `
    <span class="preview-badge">Preview</span>
    <h4>${tpl.name}</h4>
    ${body}
  `;
      panel.classList.add('visible');
      document.getElementById('previewBtn').innerHTML = previewBtnInner('Hide Preview');
      panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /* ── Collect form data ──────────────────────── */
    function collectOfferData() {
      return {
        salary: document.getElementById('offSalary').value,
        probation: document.getElementById('offProbation').value,
        joining: document.getElementById('offJoining').value,
        expiry: document.getElementById('offExpiry').value,
        notes: document.getElementById('offNotes').value.trim(),
        template: selectedTemplate,
      };
    }

    /* ── Save Draft ─────────────────────────────── */
    async function saveOfferDraft() {
      if (!validateForm(false)) return;
      const d = collectOfferData();
      try {
        const payload = {
          offered_salary: d.salary || null,
          joining_date: d.joining || null,
          probation_period: d.probation || null,
          offer_expiry_date: d.expiry || null,
          offer_remarks: d.notes || null,
          offer_template: d.template || 'standard',
          offer_letter_doc: generateOfferLetterHTML()
        };
        const res = await fetch(`${API_BASE}/school/offers/${currentCandidate.id}/issue`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${_token()}` },
          body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error(res.status);
        const candidateName = currentCandidate ? currentCandidate.name : '';
        await loadCandidates();
        closeModal();
        showToast('<i class="ti ti-device-floppy" aria-hidden="true"></i> Offer saved for ' + candidateName);
      } catch (e) {
        console.warn('API error', e);
        showToast('<i class="ti ti-alert-triangle" aria-hidden="true"></i> Error saving offer', 'error');
      }
    }

    /* ── Send Offer ─────────────────────────────── */
    async function sendOffer() {
      if (!validateForm(true)) return;
      const d = collectOfferData();
      try {
        const payload = {
          offered_salary: d.salary || null,
          joining_date: d.joining || null,
          probation_period: d.probation || null,
          offer_expiry_date: d.expiry || null,
          offer_remarks: d.notes || null,
          offer_template: d.template || 'standard',
          offer_letter_doc: generateOfferLetterHTML()
        };
        const res = await fetch(`${API_BASE}/school/offers/${currentCandidate.id}/issue`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${_token()}` },
          body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error(res.status);
        const candidateName = currentCandidate ? currentCandidate.name : '';
        await loadCandidates();
        closeModal();
        showToast('<i class="ti ti-rocket" aria-hidden="true"></i> Offer issued to ' + candidateName + ' via system!');
      } catch (e) {
        console.warn('API error', e);
        showToast('<i class="ti ti-alert-triangle" aria-hidden="true"></i> Error issuing offer', 'error');
      }
    }

    function validateForm(requireTemplate) {
      const sal = document.getElementById('offSalary').value;
      const prob = document.getElementById('offProbation').value;
      const join = document.getElementById('offJoining').value;
      const exp = document.getElementById('offExpiry').value;
      if (!sal || !prob || !join || !exp) {
        showToast('<i class="ti ti-alert-triangle" aria-hidden="true"></i> Please fill in all required compensation fields.'); return false;
      }

      // Past date validation
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      const joinDate = new Date(join);
      joinDate.setHours(0, 0, 0, 0);
      if (joinDate < today) {
        showToast('<i class="ti ti-alert-triangle" aria-hidden="true"></i> Expected Joining Date cannot be in the past.', 'error');
        return false;
      }

      const expDate = new Date(exp);
      expDate.setHours(0, 0, 0, 0);
      if (expDate < today) {
        showToast('<i class="ti ti-alert-triangle" aria-hidden="true"></i> Offer Expiry Date cannot be in the past.', 'error');
        return false;
      }

      if (requireTemplate && !selectedTemplate) {
        showToast('<i class="ti ti-alert-triangle" aria-hidden="true"></i> Please select an offer letter template.'); return false;
      }
      return true;
    }

    /* ── Update status (local + API) ────────────── */
    async function updateCandidateStatus(id, newStatus) {
      try {
        const res = await fetch(`${API_BASE}/school/offers/${id}/update-status`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${_token()}` },
          body: JSON.stringify({ status: newStatus })
        });
        if (!res.ok) throw new Error(res.status);
        await loadCandidates();
        showToast('Offer status updated to ' + newStatus);
      } catch (e) {
        console.warn('API error', e);
        showToast('<i class="ti ti-alert-triangle" aria-hidden="true"></i> Error updating status', 'error');
      }
    }

    function recalcStats() {
      document.getElementById('sc-total').textContent = CANDIDATES.length;
      document.getElementById('sc-awaiting').textContent = CANDIDATES.filter(c => c.status === 'awaiting').length;
      document.getElementById('sc-pending').textContent = CANDIDATES.filter(c => c.status === 'pending' || c.status === 'draft' || c.status === 'sent').length;
      document.getElementById('sc-accepted').textContent = CANDIDATES.filter(c => c.status === 'accepted').length;
    }

    /* ── View Offer Modal ───────────────────────── */
    let _viewCandidateId = null;

    function viewOffer(id) {
      const c = CANDIDATES.find(c => c.id === id);
      if (!c) return;
      _viewCandidateId = id;

      // Auto-pick template by role
      const r = c.role.toLowerCase();
      const tplKey = r.includes('vice') || r.includes('principal') || r.includes('admin')
        ? 'admin'
        : r.includes('counsel') || r.includes('coordinator')
          ? 'admin'
          : r.includes('teacher')
            ? 'teaching'
            : 'standard';

      const tpl = TEMPLATES[tplKey];
      const s = STATUS_META[c.status];

      // Build offer body — replace placeholders with stored or indicated values
      const offerData = c.offerData || {};
      const sal = offerData.salary ? `₹ ${offerData.salary} LPA` : '<em style="color:var(--text3)">On file</em>';
      const prob = offerData.probation || 'Per terms';
      const join = offerData.joining ? fmtDate(offerData.joining) : '<em style="color:var(--text3)">As agreed</em>';
      const exp = offerData.expiry ? fmtDate(offerData.expiry) : '<em style="color:var(--text3)">As agreed</em>';

      let body = tpl.body
        .replace(/\[Candidate Name\]/g, c.name)
        .replace(/\[Job Title\]/g, c.role)
        .replace(/\[School Name\]/g, c.school)
        .replace(/\[Department\]/g, c.dept)
        .replace(/\[Offered Salary\]/g, sal)
        .replace(/\[Probation Period\]/g, prob)
        .replace(/\[Joining Date\]/g, join)
        .replace(/\[Expiry Date\]/g, exp);

      if (offerData.notes) {
        body += `<br><br><em style="color:var(--text3);font-size:12px;">Additional terms: ${offerData.notes}</em>`;
      }

      // Populate modal
      document.getElementById('viewModalTitle').textContent = 'Offer Letter — ' + c.name;
      document.getElementById('viewModalSub').textContent = c.role + ' · ' + c.school;

      const chips = [
        { icon: personIcon(), text: c.name },
        { icon: briefcaseIcon(), text: c.role },
        { icon: deptIcon(), text: c.dept },
        { icon: schoolIcon(), text: c.school },
      ];
      document.getElementById('viewAutofillRow').innerHTML = chips.map(ch =>
        `<span class="af-chip">${ch.icon}${ch.text}</span>`
      ).join('');

      const badge = document.getElementById('viewStatusBadge');
      badge.className = 'badge ' + s.cls;
      badge.textContent = s.label;

      document.getElementById('viewOfferBody').innerHTML =
        `<span class="preview-badge">Issued</span><h4>${tpl.name}</h4>${body}`;

      document.getElementById('viewOfferModal').style.display = 'flex';
      document.body.style.overflow = 'hidden';
    }

    function closeViewModal() {
      document.getElementById('viewOfferModal').style.display = 'none';
      document.body.style.overflow = '';
      _viewCandidateId = null;
    }

    function downloadOfferFromView() {
      if (_viewCandidateId === null) return;
      downloadOffer(_viewCandidateId);
    }

    /* ── Download ────────────────────────── */
    function downloadOffer(id) {
      const c = CANDIDATES.find(c => c.id === id);
      if (c && c.offer_letter_doc) {
        showToast('<i class="ti ti-file-text" aria-hidden="true"></i> Generating PDF for ' + c.name);

        const htmlContent = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Offer Letter - ${c.name}</title>
  <style>
    @page {
      size: letter;
      margin: 1in;
    }
    * {
      box-sizing: border-box;
    }
    body {
      font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
      font-size: 12pt;
      line-height: 1.6;
      color: #333333;
      margin: 0;
      padding: 0;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
    .offer-container {
      width: 100%;
      max-width: 100%;
    }
    h1, h2, h3, h4 {
      color: #111111;
      font-weight: 600;
      margin-top: 0;
    }
    p {
      margin-bottom: 1.2em;
      orphans: 3;
      widows: 3;
    }
    .no-break {
      page-break-inside: avoid;
      break-inside: avoid;
    }
    /* Hide everything except the document when printing */
    @media print {
      body { margin: 0; }
      .no-print { display: none !important; }
    }
  </style>
</head>
<body>
  <div class="offer-container">
    ${c.offer_letter_doc}
  </div>
  <script>
    /* Auto-trigger print dialog as soon as fonts/images are ready */
    window.addEventListener('load', function () {
      setTimeout(function () {
        window.print();
      }, 250); /* small delay lets fonts render before the dialog opens */
    });
  