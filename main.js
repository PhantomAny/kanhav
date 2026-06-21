// ── Custom Cursor ────────────────────────────────────────────────────────────
const cursor    = document.getElementById('cursor');
const cursorRing = document.getElementById('cursorRing');
let mx = 0, my = 0, rx = 0, ry = 0;

document.addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY; });

(function animCursor() {
  cursor.style.left = mx + 'px';
  cursor.style.top  = my + 'px';
  rx += (mx - rx) * 0.12;
  ry += (my - ry) * 0.12;
  cursorRing.style.left = rx + 'px';
  cursorRing.style.top  = ry + 'px';
  requestAnimationFrame(animCursor);
})();

document.querySelectorAll('a, button, .project-card, .aim-item, .skill-pill').forEach(el => {
  el.addEventListener('mouseenter', () => {
    cursor.style.transform    = 'translate(-50%,-50%) scale(2)';
    cursorRing.style.transform = 'translate(-50%,-50%) scale(0.5)';
    cursorRing.style.opacity  = '1';
  });
  el.addEventListener('mouseleave', () => {
    cursor.style.transform    = 'translate(-50%,-50%) scale(1)';
    cursorRing.style.transform = 'translate(-50%,-50%) scale(1)';
    cursorRing.style.opacity  = '0.5';
  });
});

// ── Navbar scroll frost ───────────────────────────────────────────────────────
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 40);
});

// ── Scroll-reveal ─────────────────────────────────────────────────────────────
const reveals = document.querySelectorAll('.reveal');
const revealObs = new IntersectionObserver((entries) => {
  entries.forEach((entry, i) => {
    if (entry.isIntersecting) {
      setTimeout(() => entry.target.classList.add('visible'), i * 80);
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -60px 0px' });

reveals.forEach(el => revealObs.observe(el));
