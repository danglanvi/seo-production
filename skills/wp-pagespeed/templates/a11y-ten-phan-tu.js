/*
 * Gắn tên đọc được cho link, nút, ô select còn thiếu tên, kể cả phần tử slider tạo muộn (MutationObserver).
 * Bỏ phần tử focus được ra khỏi vòng Tab khi nằm trong vùng aria-hidden="true".
 *
 * Mẫu của skill wp-pagespeed (references/plugin-chong-cheo.md mục 7). Nguồn: nhật ký tối ưu site TMĐT mẫu 30/10/2026,
 * hạng mục Hỗ trợ tiếp cận của PSI. Đây là lớp vá ở trình duyệt: sửa tên phần tử trong template trước khi dùng file này.
 * Chèn vào footer bằng plugin chèn code hoặc wp_footer. Điền BRAND, SOCIAL. Nhãn theo <html lang>: vi hoặc en.
 */
(function () {
  var BRAND = 'Tên thương hiệu';
  var IMG_NO_ALT_DECORATIVE = false; // true: ảnh thiếu thuộc tính alt coi là ảnh trang trí. Ảnh nội dung cần alt thật (skill image-seo-optimize)
  var L = (document.documentElement.lang || '').slice(0, 2) === 'vi' ? {
    on: ' trên ', mail: 'Gửi email cho chúng tôi', call: 'Gọi cho chúng tôi', home: 'Trang chủ ' + BRAND,
    prev: 'Ảnh trước', next: 'Ảnh sau', close: 'Đóng', sub: 'Xem danh mục con của ', select: 'Chọn một mục', zalo: 'Chat Zalo với ' + BRAND, wa: 'Chat WhatsApp với ' + BRAND
  } : {
    on: ' on ', mail: 'Send us an email', call: 'Call us', home: BRAND + ' home',
    prev: 'Previous slide', next: 'Next slide', close: 'Close', sub: 'Show subcategories of ', select: 'Select an option', zalo: 'Chat on Zalo', wa: 'Chat on WhatsApp'
  };
  var SOCIAL = { 'facebook.com': 'Facebook', 'instagram.com': 'Instagram', 'linkedin.com': 'LinkedIn', 'pinterest.com': 'Pinterest', 'tiktok.com': 'TikTok', 'twitter.com': 'X', 'x.com': 'X', 'youtube.com': 'YouTube' };
  var FOCUSABLE = 'a[href],button,input,select,textarea,[tabindex]:not([tabindex="-1"])';

  function hasName(el) {
    if ((el.getAttribute('aria-label') || '').trim() || el.getAttribute('aria-labelledby') || (el.getAttribute('title') || '').trim()) return true;
    if (el.textContent.trim()) return true;
    var imgs = el.querySelectorAll('img');
    for (var i = 0; i < imgs.length; i++) { if ((imgs[i].getAttribute('alt') || '').trim()) return true; }
    return false;
  }
  function nameLink(a) {
    if (hasName(a)) return;
    var href = a.getAttribute('href') || '';
    if (/^mailto:/i.test(href)) { a.setAttribute('aria-label', L.mail); return; }
    if (/^tel:/i.test(href)) { a.setAttribute('aria-label', L.call); return; }
    var host = '';
    try { host = new URL(a.href).hostname.replace(/^www\./, ''); } catch (e) { return; }
    if (host === location.hostname.replace(/^www\./, '')) { if (/^\/?$/.test(new URL(a.href).pathname)) a.setAttribute('aria-label', L.home); return; }
    if (/(^|\.)zalo\.me$/.test(host)) { a.setAttribute('aria-label', L.zalo); return; }
    if (host === 'wa.me' || /(^|\.)whatsapp\.com$/.test(host)) { a.setAttribute('aria-label', L.wa); return; }
    for (var k in SOCIAL) { if (host === k || host.slice(-k.length - 1) === '.' + k) { a.setAttribute('aria-label', BRAND + L.on + SOCIAL[k]); return; } }
  }
  function nameButton(b) {
    if (hasName(b)) return;
    var c = (b.className || '').toString();
    var head = b.closest('.accordion-header'); // menu dạng accordion (Flatsome và theme tương tự)
    var link = head && head.querySelector('a');
    if (link && link.textContent.trim()) { b.setAttribute('aria-label', L.sub + link.textContent.trim()); return; }
    if (/prev/i.test(c)) b.setAttribute('aria-label', L.prev);
    else if (/next/i.test(c)) b.setAttribute('aria-label', L.next);
    else if (/close/i.test(c)) b.setAttribute('aria-label', L.close);
  }
  function fixHiddenFocus(el) {
    var hidden = el.getAttribute('aria-hidden') === 'true';
    el.querySelectorAll(FOCUSABLE + ',[data-gtvd-tab]').forEach(function (f) {
      if (hidden && !f.hasAttribute('data-gtvd-tab')) { f.setAttribute('data-gtvd-tab', f.getAttribute('tabindex') || ''); f.setAttribute('tabindex', '-1'); }
      else if (!hidden && f.hasAttribute('data-gtvd-tab')) { var t = f.getAttribute('data-gtvd-tab'); if (t) f.setAttribute('tabindex', t); else f.removeAttribute('tabindex'); f.removeAttribute('data-gtvd-tab'); }
    });
  }
  function fixAll(root) {
    if (IMG_NO_ALT_DECORATIVE) root.querySelectorAll('img:not([alt])').forEach(function (img) { img.setAttribute('alt', ''); });
    root.querySelectorAll('a[href]').forEach(nameLink);
    root.querySelectorAll('button').forEach(nameButton);
    root.querySelectorAll('select').forEach(function (s) {
      if (s.getAttribute('aria-label') || s.getAttribute('aria-labelledby') || (s.id && document.querySelector('label[for="' + s.id + '"]')) || s.closest('label')) return;
      s.setAttribute('aria-label', s.options[0] && s.options[0].text.trim() ? s.options[0].text.trim() : L.select);
    });
    root.querySelectorAll('[aria-hidden="true"]').forEach(fixHiddenFocus);
  }
  var pending = false;
  function schedule() { if (pending) return; pending = true; setTimeout(function () { pending = false; fixAll(document); }, 150); }
  function start() {
    fixAll(document);
    new MutationObserver(function (muts) {
      for (var i = 0; i < muts.length; i++) {
        var m = muts[i];
        if (m.type === 'attributes') { fixHiddenFocus(m.target); continue; }
        if (m.addedNodes.length) schedule();
      }
    }).observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['aria-hidden'] });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true }); else start();
})();
