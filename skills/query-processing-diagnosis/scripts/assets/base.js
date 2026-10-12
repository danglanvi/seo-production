
/* ===========================================
   DECK CONTROLLER — scale stage, điều hướng, hash, QA mode
   =========================================== */
const QA = /[?&]qa\b/.test(location.search);
if (QA) document.documentElement.classList.add('qa');

class SlidePresentation {
  constructor() {
    this.stage = document.getElementById('deckStage');
    this.slides = [...document.querySelectorAll('.slide')];
    this.cur = 0;
    const total = String(this.slides.length).padStart(2, '0');
    this.slides.forEach((s, i) => { const p = s.querySelector('.pgn'); if (p) p.textContent = String(i + 1).padStart(2, '0') + ' / ' + total; });
    this.setupScale(); this.setupKeys(); this.setupTouch(); this.setupWheel();
    document.getElementById('prevBtn').onclick = () => this.go(this.cur - 1);
    document.getElementById('nextBtn').onclick = () => this.go(this.cur + 1);
    const h = parseInt(location.hash.slice(1), 10);
    this.go(Number.isFinite(h) ? h - 1 : 0);
  }
  setupScale() {
    const scale = () => {
      const f = Math.min(innerWidth / 1920, innerHeight / 1080);
      this.stage.style.transform = `translate(${(innerWidth - 1920 * f) / 2}px, ${(innerHeight - 1080 * f) / 2}px) scale(${f})`;
    };
    scale(); addEventListener('resize', scale);
  }
  isTyping(t) { return t.closest && t.closest('input,textarea,select,[contenteditable="true"]'); }
  setupKeys() {
    document.addEventListener('keydown', e => {
      if (this.isTyping(e.target)) return;
      if (['ArrowRight', 'PageDown', ' '].includes(e.key)) { e.preventDefault(); this.go(this.cur + 1); }
      if (['ArrowLeft', 'PageUp'].includes(e.key)) { e.preventDefault(); this.go(this.cur - 1); }
      if (e.key === 'Home') this.go(0);
      if (e.key === 'End') this.go(this.slides.length - 1);
    });
  }
  setupTouch() {
    let x0 = null;
    addEventListener('touchstart', e => { x0 = e.touches[0].clientX; }, { passive: true });
    addEventListener('touchend', e => {
      if (x0 === null) return; const dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 50) this.go(this.cur + (dx < 0 ? 1 : -1)); x0 = null;
    });
  }
  setupWheel() {
    let lock = false;
    addEventListener('wheel', e => {
      if (lock || Math.abs(e.deltaY) < 30 || this.isTyping(e.target)) return;
      lock = true; this.go(this.cur + (e.deltaY > 0 ? 1 : -1)); setTimeout(() => lock = false, 800);
    }, { passive: true });
  }
  go(i) {
    this.cur = Math.max(0, Math.min(i, this.slides.length - 1));
    this.slides.forEach((s, k) => { s.classList.toggle('active', k === this.cur); s.classList.toggle('visible', k === this.cur); });
    document.getElementById('counter').textContent = (this.cur + 1) + ' / ' + this.slides.length;
    document.getElementById('progress').style.width = ((this.cur + 1) / this.slides.length * 100) + '%';
    history.replaceState(null, '', location.pathname + location.search + '#' + (this.cur + 1));
    this.slides[this.cur].dispatchEvent(new CustomEvent('enter'));
  }
}

/* ===========================================
   S03 — đánh dấu ranh giới. Bản skill bỏ phần demo của deck training (S03–S19, có dữ liệu mẫu của dự án thật)
   vì qp_render.py chỉ nhúng phần điều khiển phía trên và phần SỬA CHỮ phía dưới. Bản đầy đủ nằm ở deck training.
   =========================================== */

/* ===========================================
   SỬA CHỮ TẠI CHỖ — bản local: nút "Sửa chữ" hoặc phím E; Ctrl/Cmd+S lưu file.
   Bản web: site.py ẩn nút và bỏ phím E.
   =========================================== */
const EDIT_SEL = '.slide h1,.slide h2,.slide h4,.slide p,.slide li,.slide td,.slide .v,.slide .t,.slide .cchip,.slide .c';
let editing = false;
function toggleEdit() {
  editing = !editing;
  document.body.classList.toggle('editing', editing);
  document.getElementById('edit').classList.toggle('on', editing);
  document.querySelectorAll(EDIT_SEL).forEach(el => { if (editing) el.setAttribute('contenteditable', 'true'); else el.removeAttribute('contenteditable'); });
}
function saveFile() {
  if (editing) toggleEdit();
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob(['<!DOCTYPE html>\n' + document.documentElement.outerHTML], { type: 'text/html' }));
  a.download = location.pathname.split('/').pop() || 'deck.html'; a.click();
}
document.getElementById('edit').onclick = toggleEdit;
document.addEventListener('keydown', e => {
  const typing = e.target.closest && e.target.closest('input,textarea,[contenteditable="true"]');
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 's' && location.protocol === 'file:') { e.preventDefault(); saveFile(); }
  else if (typing) return;
  else if(e.key.toLowerCase()==='e'&&!e.metaKey&&!e.ctrlKey)toggleEdit();
});

new SlidePresentation();
