/* Lớp sửa chữ trực tiếp (nút E): bật bằng phím E, đánh dấu khối đã sửa, nháp tự lưu, tải HTML hoặc chép ED-JSON. */
(function () {
  'use strict';
  var D = document, H = D.documentElement, src = JSON.parse(D.getElementById('ed-src').textContent);
  var KEY = 'sua:' + src.page + ':' + src.builtAt;
  var SKIP = {script: 1, style: 1, svg: 1, template: 1, noscript: 1};
  var blocks = [].slice.call(D.querySelectorAll('[data-b]')), on = false, dirty = false, timer = null;
  function $(id) { return D.getElementById(id); }
  function raw(n) {
    if (n.nodeType === 3) return n.nodeValue;
    if (n.nodeType !== 1) return '';
    var t = n.tagName.toLowerCase(), s = '';
    if (SKIP[t]) return '';
    if (t === 'br') return ' ';
    for (var k = n.firstChild; k; k = k.nextSibling) s += raw(k);
    return s;
  }
  function decor(n) { return /^(\d{1,2}|\*)$/.test(raw(n).replace(/\s+/g, ' ').trim()); }
  // Chữ của khối, cùng cách tính với review_blocks.py (bỏ icon, số bước, dấu *)
  function textOf(el) {
    var s = '';
    (function go(x) {
      for (var k = x.firstChild; k; k = k.nextSibling) {
        if (k.nodeType === 3) s += k.nodeValue;
        else if (k.nodeType === 1) {
          var t = k.tagName.toLowerCase();
          if (t === 'br') { s += ' '; continue; }
          if (SKIP[t] || decor(k)) continue;
          go(k);
        }
      }
    })(el);
    return s.replace(/\s+/g, ' ').trim().normalize('NFC');
  }
  function changed() { return blocks.filter(function (el) { return textOf(el) !== el.getAttribute('data-t'); }); }
  function cut(s, n) { return s.length > n ? s.slice(0, n) + '…' : s; }
  function esc(s) { return s.replace(/[&<>]/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;'}[c]; }); }
  function clean(v) { return v.replace(/\s+/g, ' ').trim(); }
  function metaEdits() {
    var out = {};
    ['title', 'desc'].forEach(function (k) {
      var v = clean($('ed-m-' + k).value);
      if (v !== src.meta[k]) out[k] = {before: src.meta[k], text: v};
    });
    return out;
  }
  function collect() {
    return {page: src.page, builtAt: src.builtAt, savedAt: new Date().toISOString(),
      edits: changed().map(function (el) { return {b: el.getAttribute('data-b'), before: el.getAttribute('data-t'), text: textOf(el)}; }),
      meta: metaEdits(), note: $('ed-note').value.trim()};
  }
  function total(c) { return c.edits.length + Object.keys(c.meta).length + (c.note ? 1 : 0); }
  function msg(t, err) { var m = $('ed-msg'); m.textContent = t; m.className = 'ed-msg' + (err ? ' err' : ''); }
  function count(k, max) { var v = clean($('ed-m-' + k).value), c = $('ed-c-' + k); c.textContent = v.length + '/' + max; c.classList.toggle('over', v.length > max); }
  function refresh() {
    var list = changed(), n = list.length + Object.keys(metaEdits()).length;
    blocks.forEach(function (el) { el.classList.toggle('ed-done', list.indexOf(el) >= 0); });
    $('ed-n').textContent = n;
    $('ed-badge').textContent = n || '';
    $('ed-list').innerHTML = list.map(function (el) {
      return '<li data-go="' + el.getAttribute('data-b') + '"><del>' + esc(cut(el.getAttribute('data-t'), 120)) + '</del><br><ins>' + esc(cut(textOf(el), 160)) + '</ins></li>';
    }).join('') || '<li>Chưa có chỗ sửa.</li>';
  }
  // Nháp tự lưu trong trình duyệt: đóng file rồi mở lại vẫn còn chỗ đã sửa
  function stash() {
    try {
      var d = {};
      changed().forEach(function (el) { d[el.getAttribute('data-b')] = el.innerHTML; });
      localStorage.setItem(KEY, JSON.stringify({blocks: d, title: $('ed-m-title').value, desc: $('ed-m-desc').value, note: $('ed-note').value}));
    } catch (e) {}
  }
  function unstash() {
    var s = null, n = 0;
    try { s = JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (e) {}
    if (!s) return 0;
    Object.keys(s.blocks || {}).forEach(function (b) {
      var el = D.querySelector('[data-b="' + b + '"]');
      if (el && textOf(el) === el.getAttribute('data-t')) { el.innerHTML = s.blocks[b]; n++; }
    });
    if (typeof s.title === 'string') $('ed-m-title').value = s.title;
    if (typeof s.desc === 'string') $('ed-m-desc').value = s.desc;
    if (s.note && !$('ed-note').value) $('ed-note').value = s.note;
    return n;
  }
  // Icon, số bước, dấu * trong khối giữ nguyên: không cho sửa
  function lock() {
    blocks.forEach(function (el) {
      [].forEach.call(el.querySelectorAll('*'), function (k) { if (k.tagName.toLowerCase() === 'svg' || decor(k)) k.setAttribute('contenteditable', 'false'); });
    });
  }
  function setOn(v) {
    on = v;
    H.classList.toggle('ed-on', on);
    blocks.forEach(function (el) {
      if (on) { el.setAttribute('contenteditable', 'plaintext-only'); el.setAttribute('spellcheck', 'false'); }
      else { el.removeAttribute('contenteditable'); el.removeAttribute('spellcheck'); }
    });
    [].forEach.call(D.querySelectorAll('details'), function (d) {
      if (d.closest('.ed-panel')) return;
      if (on) { if (d.dataset.eopen === undefined) d.dataset.eopen = d.open ? '1' : ''; d.open = true; }
      else if (d.dataset.eopen !== undefined) { d.open = d.dataset.eopen === '1'; delete d.dataset.eopen; }
    });
    $('ed-panel').hidden = !on;
    $('ed-hint').hidden = true;
    $('ed-btn').setAttribute('aria-pressed', String(on));
    if (on) refresh();
  }
  function stamp() {
    var d = new Date(), p = function (n) { return (n < 10 ? '0' : '') + n; };
    return d.getFullYear() + p(d.getMonth() + 1) + p(d.getDate()) + '-' + p(d.getHours()) + p(d.getMinutes());
  }
  function serialize() {
    $('ed-edits').textContent = JSON.stringify(collect()).replace(/</g, '\\u003c');
    var d = H.cloneNode(true);
    d.classList.remove('ed-on', 'ed-show');
    [].forEach.call(d.querySelectorAll('[data-b]'), function (x) { x.removeAttribute('contenteditable'); x.removeAttribute('spellcheck'); x.classList.remove('ed-done', 'ed-flash'); });
    [].forEach.call(d.querySelectorAll('details[data-eopen]'), function (x) { if (x.getAttribute('data-eopen') !== '1') x.removeAttribute('open'); x.removeAttribute('data-eopen'); });
    d.querySelector('#ed-panel').setAttribute('hidden', '');
    d.querySelector('#ed-btn').setAttribute('aria-pressed', 'false');
    d.querySelector('#ed-m-title').setAttribute('value', $('ed-m-title').value);
    d.querySelector('#ed-m-desc').textContent = $('ed-m-desc').value;
    d.querySelector('#ed-note').textContent = $('ed-note').value;
    return '<!doctype html>\n' + d.outerHTML;
  }
  // Link tải không gắn vào trang: lớp chặn click bên dưới không chặn được nó (lỗi của bản trước)
  function download(name, text, type) {
    var u = URL.createObjectURL(new Blob([text], {type: type})), a = D.createElement('a');
    a.href = u; a.download = name; a.click();
    setTimeout(function () { URL.revokeObjectURL(u); }, 5000);
  }
  function saveHtml() {
    if (!total(collect())) return msg('Chưa có chỗ nào được sửa.', true);
    var name = src.page + '-ban-sua-' + stamp() + '.html';
    download(name, serialize(), 'text/html');
    dirty = false;
    msg('Đã tải ' + name + ' về Downloads. Nhắn Claude tên file này. Không thấy file thì bấm "Sao chép cho Claude" rồi dán vào chat.');
  }
  function where(b) {
    var el = D.querySelector('[data-b="' + b + '"]'), sec = el && el.closest('section,header,footer,dialog'), h = sec && sec.querySelector('h1,h2');
    return h ? cut(textOf(h), 60) : '';
  }
  function report(c) {
    var out = 'SỬA NỘI DUNG · ' + src.title + ' (' + src.page + ') · ' + total(c) + ' chỗ\n';
    c.edits.forEach(function (e, i) { out += '\n[' + (i + 1) + '] ' + e.b + ' · ' + where(e.b) + '\nCŨ: ' + e.before + '\nMỚI: ' + e.text + '\n'; });
    Object.keys(c.meta).forEach(function (k) { out += '\n[meta ' + k + ']\nCŨ: ' + c.meta[k].before + '\nMỚI: ' + c.meta[k].text + '\n'; });
    if (c.note) out += '\nGHI CHÚ: ' + c.note + '\n';
    return out + '\nED-JSON: ' + JSON.stringify(c) + '\n';
  }
  function copy() {
    var c = collect();
    if (!total(c)) return msg('Chưa có chỗ nào được sửa.', true);
    var t = report(c);
    (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject()).then(function () {
      msg('Đã chép ' + total(c) + ' chỗ sửa. Dán vào chat với Claude.');
    }, function () {
      download(src.page + '-ban-sua-' + stamp() + '.txt', t, 'text/plain');
      msg('Không chép được, đã tải file .txt về Downloads.');
    });
  }
  function reset() {
    if (!confirm('Bỏ hết chỗ đã sửa trên file này?')) return;
    try { localStorage.removeItem(KEY); } catch (e) {}
    blocks.forEach(function (el) { if (textOf(el) !== el.getAttribute('data-t')) el.innerHTML = el.getAttribute('data-o'); });
    $('ed-m-title').value = src.meta.title; $('ed-m-desc').value = src.meta.desc; $('ed-note').value = '';
    $('ed-edits').textContent = '{}';
    lock(); dirty = false; count('title', 60); count('desc', 160); refresh();
    msg('Đã bỏ hết bản sửa.');
  }
  function jump(b) {
    var el = D.querySelector('[data-b="' + b + '"]');
    if (!el) return;
    el.scrollIntoView({block: 'center'}); el.classList.add('ed-flash');
    setTimeout(function () { el.classList.remove('ed-flash'); }, 1200);
  }
  window.__ed = {collect: collect, serialize: serialize, textOf: textOf};
  D.addEventListener('input', function (e) {
    var t = e.target;
    if (!t.closest || !(t.closest('[data-b]') || t.closest('.ed-panel'))) return;
    dirty = true;
    if (t.id === 'ed-m-title') count('title', 60);
    if (t.id === 'ed-m-desc') count('desc', 160);
    clearTimeout(timer);
    timer = setTimeout(function () { stash(); refresh(); }, 300);
  }, true);
  D.addEventListener('keydown', function (e) {
    var t = e.target;
    if (e.key === 'Enter' && t.closest && t.closest('[data-b]')) { e.preventDefault(); t.closest('[data-b]').blur(); return; }
    if ((e.metaKey || e.ctrlKey) && (e.key === 's' || e.key === 'S')) { e.preventDefault(); saveHtml(); return; }
    if ((e.key === 'e' || e.key === 'E') && !e.metaKey && !e.ctrlKey && !e.altKey) {
      if (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName)) return;
      e.preventDefault(); setOn(!on);
    }
  }, true);
  D.addEventListener('click', function (e) {
    var t = e.target, go = t.closest('[data-go]');
    if (go) { jump(go.getAttribute('data-go')); return; }
    if (t.closest('.ed-panel,.ed-btn')) return;
    // Link trong trang không mở được khi xem file trên máy: chặn để không rời trang
    if (t.closest('a[href]:not([download])')) { e.preventDefault(); return; }
    if (on && t.closest('summary,[data-ed=label],[data-ed=button]')) e.preventDefault();
  }, true);
  D.addEventListener('submit', function (e) { e.preventDefault(); }, true);
  D.addEventListener('toggle', function (e) {
    if (on && e.target.tagName === 'DETAILS' && !e.target.open && !e.target.closest('.ed-panel')) e.target.open = true;
  }, true);
  window.addEventListener('beforeunload', function (e) { if (dirty) { e.preventDefault(); e.returnValue = ''; } });
  $('ed-btn').addEventListener('click', function () { setOn(!on); });
  $('ed-panel').addEventListener('click', function (e) {
    var b = e.target.closest('[data-a]');
    if (!b) return;
    var a = b.getAttribute('data-a');
    if (a === 'html') saveHtml();
    else if (a === 'copy') copy();
    else if (a === 'reset') reset();
    else if (a === 'off') setOn(false);
    else if (a === 'show') H.classList.toggle('ed-show', b.checked);
  });
  // Lần mở đầu: chữ gốc lấy theo cách trình duyệt tính (textOf), để khối chưa sửa không bị coi là đã sửa. data-tj giữ qua các lần lưu.
  blocks.forEach(function (el) { if (!el.hasAttribute('data-tj')) { el.setAttribute('data-t', textOf(el)); el.setAttribute('data-tj', '1'); } });
  lock();
  var restored = unstash(), before = changed().length;
  count('title', 60); count('desc', 160); refresh();
  if (restored) { setOn(true); dirty = true; msg('Đã khôi phục ' + restored + ' chỗ sửa chưa tải về từ lần mở trước.'); }
  else if (before) { setOn(true); msg('File này có ' + before + ' chỗ đã sửa từ lần trước.'); }
  else setTimeout(function () { $('ed-hint').hidden = true; }, 9000);
})();
