/* doc-kit: tương tác của format bài blog (pages.dev) trên WordPress. Chỉ chạy trong .doc-kit.
   Khối: .btabs, .bquiz, .bchk, .bcmd (blog.js); .tabs, .cmd, [data-quiz], .calc (mag.js); .shot, .chk (doc.js);
   figure.zoom img (phóng ảnh), [data-embed] (khung xem trước Google Docs/Sheets/Drive/Looker Studio nạp khi bấm).
   .calc chỉ tính công thức gồm tên thanh trượt, số, + - * / ( ) và round(): bài do Người đăng bài viết không chạy được JS tuỳ ý. */
(function () {
  var root = document.querySelector('.doc-kit');
  if (!root) return;
  var doc = root.getAttribute('data-doc') || location.pathname;
  function $$(s, el) { return Array.prototype.slice.call((el || root).querySelectorAll(s)); }
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) { return null; } }
  function copy(text, done) {
    if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(text).then(done, function () {}); return; }
    var a = document.createElement('textarea'); a.value = text; document.body.appendChild(a); a.select();
    try { document.execCommand('copy'); done(); } catch (e) {} a.remove();
  }

  $$('.btabs').forEach(function (box) {
    var btns = $$('.btab-bar button', box), panes = $$('.btab-pane', box);
    function show(i) {
      btns.forEach(function (b, j) { b.setAttribute('aria-selected', i === j ? 'true' : 'false'); });
      panes.forEach(function (p, j) { p.hidden = i !== j; });
    }
    btns.forEach(function (b, i) { b.addEventListener('click', function () { show(i); }); });
    show(0);
  });

  $$('.bquiz .qz').forEach(function (q) {
    var fb = q.querySelector('.fb');
    $$('.opts button', q).forEach(function (b) {
      b.addEventListener('click', function () {
        $$('.opts button', q).forEach(function (x) { x.classList.remove('ok', 'no'); });
        var right = b.hasAttribute('data-ok');
        b.classList.add(right ? 'ok' : 'no');
        if (fb) { fb.hidden = false; var r = fb.querySelector('.res'); if (r) r.textContent = right ? 'Đúng. ' : 'Chưa đúng. '; }
      });
    });
  });

  $$('.bchk').forEach(function (box) {
    var key = 'doc-kit:' + doc + ':' + box.getAttribute('data-key');
    var boxes = $$('input[type=checkbox]', box), n = box.querySelector('.bchk-n');
    var saved = (store(key) || '').split(',');
    boxes.forEach(function (c, i) { c.checked = saved[i] === '1'; });
    function count() {
      var k = 0; boxes.forEach(function (c) { if (c.checked) k++; });
      if (n) n.textContent = k + '/' + boxes.length;
      store(key, boxes.map(function (c) { return c.checked ? '1' : '0'; }).join(','));
    }
    boxes.forEach(function (c) { c.addEventListener('change', count); });
    var reset = box.querySelector('.bchk-reset');
    if (reset) reset.addEventListener('click', function () { boxes.forEach(function (c) { c.checked = false; }); count(); store(key, null); });
    count();
  });

  $$('.bcmd').forEach(function (c) {
    var b = c.querySelector('button'), t = c.querySelector('code');
    if (b && t) b.addEventListener('click', function () { copy(t.textContent, function () { b.textContent = 'Đã chép'; setTimeout(function () { b.textContent = 'Chép'; }, 1500); }); });
  });

  $$('.tabs').forEach(function (t) {
    var bs = $$('.tb button', t), ps = $$('.tp', t);
    bs.forEach(function (b) { b.addEventListener('click', function () {
      bs.forEach(function (x) { x.classList.toggle('on', x === b); });
      ps.forEach(function (p) { p.classList.toggle('on', p.dataset.t === b.dataset.t); });
    }); });
  });

  $$('.cmd').forEach(function (c) {
    var b = document.createElement('button'); b.type = 'button'; b.className = 'cp'; b.textContent = 'Chép'; c.appendChild(b);
    b.addEventListener('click', function () {
      var k = c.cloneNode(true), x = k.querySelector('.cp'); if (x) x.remove();
      copy(k.textContent.trim(), function () { b.textContent = 'Đã chép'; setTimeout(function () { b.textContent = 'Chép'; }, 1300); });
    });
  });

  $$('[data-quiz]').forEach(function (z) {
    var qs = $$('.q', z), sc = z.querySelector('.sc'), n = 0;
    qs.forEach(function (q) { $$('.qo button', q).forEach(function (b) { b.addEventListener('click', function () {
      if (q.classList.contains('done')) return;
      q.classList.add('done');
      if (b.textContent === q.dataset.ans) { n++; if (sc) sc.textContent = n; } else b.classList.add('wrong');
      $$('.qo button', q).forEach(function (x) { if (x.textContent === q.dataset.ans) x.classList.add('right'); });
    }); }); });
    var rs = z.querySelector('.rs');
    if (rs) rs.addEventListener('click', function () {
      n = 0; if (sc) sc.textContent = 0;
      qs.forEach(function (q) { q.classList.remove('done'); $$('button', q).forEach(function (x) { x.classList.remove('right', 'wrong'); }); });
    });
  });

  $$('.calc').forEach(function (c) {
    var ins = $$('[data-i]', c), outs = $$('[data-f]', c);
    var names = ins.map(function (x) { return x.dataset.i; });
    var ok = /^[\s\d.+\-*\/(),]*$/;
    var fs = outs.map(function (o) {
      var f = o.dataset.f, rest = f.replace(/round|[A-Za-z_]\w*/g, function (w) { return w === 'round' || names.indexOf(w) >= 0 ? '' : '#'; });
      return ok.test(rest) ? new Function(names.concat('round'), 'return ' + f) : null;
    });
    function up() {
      var v = ins.map(function (x) { x.style.setProperty('--p', (x.value - x.min) / (x.max - x.min) * 100 + '%'); return +x.value; }).concat(Math.round);
      outs.forEach(function (o, i) { if (!fs[i]) return; var r = fs[i].apply(null, v); o.textContent = (typeof r === 'number' ? r.toLocaleString('vi-VN') : r) + (o.dataset.u || ''); });
    }
    ins.forEach(function (x) { x.addEventListener('input', up); }); up();
  });

  $$('.shot').forEach(function (f) {
    var pins = $$('.pin', f), items = $$('ol.sn li', f);
    function on(i) { pins.forEach(function (p, j) { p.classList.toggle('on', j === i); }); items.forEach(function (li, j) { li.classList.toggle('on', j === i); }); }
    pins.forEach(function (p, i) { p.addEventListener('mouseenter', function () { on(i); }); p.addEventListener('click', function () { on(i); }); });
    items.forEach(function (li, i) { li.addEventListener('mouseenter', function () { on(i); }); });
    f.addEventListener('mouseleave', function () { on(-1); });
  });

  // Phóng ảnh: lớp phủ đặt trong .doc-kit, style inline vì doc-kit.css sinh từ blog.css của site tài liệu.
  $$('figure.zoom img').forEach(function (im) {
    im.style.cursor = 'zoom-in';
    im.addEventListener('click', function () {
      var o = document.createElement('div'), big = new Image();
      o.className = 'lbx'; o.setAttribute('role', 'dialog'); o.setAttribute('aria-label', im.alt || 'Ảnh cỡ lớn');
      o.style.cssText = 'position:fixed;inset:0;z-index:99999;background:rgba(20,20,19,.86);overflow:auto;padding:16px;cursor:zoom-out';
      big.src = im.currentSrc || im.src; big.alt = im.alt;
      big.style.cssText = 'display:block;width:auto;max-width:none;margin:0 auto;border-radius:6px';
      function close() { o.remove(); document.removeEventListener('keydown', esc); }
      function esc(e) { if (e.key === 'Escape') close(); }
      o.appendChild(big); o.addEventListener('click', close); document.addEventListener('keydown', esc);
      root.appendChild(o);
    });
  });

  // Khung xem trước: chỉ nhận link https của Google Docs, Sheets, Drive, Looker Studio. Link mở thường nằm sẵn trong HTML cho crawler.
  var EMBED = /^https:\/\/(docs|drive|lookerstudio)\.google\.com\//;
  $$('[data-embed]').forEach(function (b) {
    var box = document.getElementById(b.getAttribute('data-embed')), src = b.getAttribute('data-src') || '', label = b.textContent;
    if (!box || !EMBED.test(src)) return;
    b.setAttribute('aria-expanded', 'false');
    b.addEventListener('click', function () {
      if (!box.querySelector('iframe')) {
        var f = document.createElement('iframe');
        f.src = src; f.title = b.getAttribute('data-title') || label; f.loading = 'lazy';
        f.style.cssText = 'display:block;width:100%;height:' + (parseInt(box.getAttribute('data-h'), 10) || 520) + 'px;border:1px solid var(--line);border-radius:10px;background:#fff';
        box.insertBefore(f, box.firstChild);
      }
      box.hidden = !box.hidden;
      b.setAttribute('aria-expanded', box.hidden ? 'false' : 'true');
      b.textContent = box.hidden ? label : (b.getAttribute('data-hide') || 'Ẩn khung');
    });
  });

  var chk = $$('.chk input[type=checkbox]'), saved = {};
  try { saved = JSON.parse(store('doc-kit-chk:' + doc) || '{}'); } catch (e) {}
  chk.forEach(function (b, i) { if (saved[i]) b.checked = true; b.addEventListener('change', function () { saved[i] = b.checked; store('doc-kit-chk:' + doc, JSON.stringify(saved)); }); });
})();
