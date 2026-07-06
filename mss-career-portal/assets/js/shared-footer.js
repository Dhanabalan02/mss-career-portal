(function () {
  function getFooterElement() {
    return document.getElementById('mss-footer') || document.querySelector('#shared-footer #mss-footer');
  }

  function scrollToFooter() {
    var footer = getFooterElement();
    if (footer) {
      footer.scrollIntoView({ behavior: 'smooth', block: 'end' });
      return;
    }

    window.scrollTo({
      top: Math.max(document.body.scrollHeight, document.documentElement.scrollHeight),
      behavior: 'smooth'
    });
  }

  if (!window.scrollToFooter) {
    window.scrollToFooter = scrollToFooter;
  }

  document.addEventListener('click', function (e) {
    var footerTrigger = e.target.closest('.mss-scroll-footer');
    if (!footerTrigger) return;
    e.preventDefault();
    e.stopPropagation();
    window.scrollToFooter();

    var mobileNav = document.getElementById('mssNavMobile');
    if (mobileNav && typeof bootstrap !== 'undefined') {
      var bsCollapse = bootstrap.Collapse.getInstance(mobileNav);
      if (bsCollapse) bsCollapse.hide();
    }
  });

  var placeholders = Array.from(document.querySelectorAll('#shared-footer'));
  if (placeholders.length === 0) return;

  var footerPath = new URL('../../components/footer.html', document.baseURI || window.location.href).href;

  fetch(footerPath, { cache: 'no-cache' })
    .then(function (response) {
      if (!response.ok) throw new Error('Failed to load shared footer: ' + response.status);
      return response.text();
    })
    .then(function (html) {
      var parser = new DOMParser();
      var doc = parser.parseFromString(html, 'text/html');
      var footerEl = doc.querySelector('#mss-footer');
      if (!footerEl) throw new Error('Shared footer markup missing #mss-footer');

      var styleEl = doc.querySelector('style#shared-footer-styles');
      if (styleEl && !document.getElementById('shared-footer-styles')) {
        document.head.appendChild(styleEl.cloneNode(true));
      }

      placeholders.forEach(function (placeholder) {
        placeholder.innerHTML = footerEl.outerHTML;
      });
    })
    .catch(function (error) {
      console.error('shared-footer.js:', error);
    });
})();
