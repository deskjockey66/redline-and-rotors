(() => {
  const carousel = document.querySelector('[data-carousel]');
  if (!carousel) return;
  const slides = [...carousel.querySelectorAll('[data-slide]')];
  if (slides.length < 2) return;
  const controls = carousel.querySelector('[data-controls]');
  const dots = [...carousel.querySelectorAll('[data-slide-to]')];
  const toggle = carousel.querySelector('[data-toggle]');
  const status = carousel.querySelector('[data-status]');
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let index = 0;
  let playing = !motion.matches;
  let hovering = false;
  let focused = false;
  let timer;
  function schedule() {
    window.clearTimeout(timer);
    if (playing && !hovering && !focused && !document.hidden) {
      timer = window.setTimeout(() => show(index + 1), 8000);
    }
  }
  function updateToggle() {
    toggle.textContent = playing ? 'Pause' : 'Play';
    toggle.setAttribute('aria-label', playing ? 'Pause automatic story rotation' : 'Start automatic story rotation');
  }
  function show(next, announce = false) {
    index = (next + slides.length) % slides.length;
    slides.forEach((slide, i) => { slide.hidden = i !== index; });
    dots.forEach((dot, i) => { dot.setAttribute('aria-pressed', String(i === index)); });
    carousel.querySelector('[data-count]').textContent = `${index + 1} / ${slides.length}`;
    if (announce) status.textContent = `Story ${index + 1} of ${slides.length}: ${slides[index].dataset.title}`;
    schedule();
  }
  carousel.querySelector('[data-prev]').addEventListener('click', () => show(index - 1, true));
  carousel.querySelector('[data-next]').addEventListener('click', () => show(index + 1, true));
  dots.forEach(dot => dot.addEventListener('click', () => show(Number(dot.dataset.slideTo), true)));
  toggle.addEventListener('click', () => { playing = !playing; updateToggle(); schedule(); });
  carousel.addEventListener('mouseenter', () => { hovering = true; schedule(); });
  carousel.addEventListener('mouseleave', () => { hovering = false; schedule(); });
  carousel.addEventListener('focusin', () => { focused = true; schedule(); });
  carousel.addEventListener('focusout', event => {
    if (!carousel.contains(event.relatedTarget)) { focused = false; schedule(); }
  });
  carousel.addEventListener('keydown', event => {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault();
    show(index + (event.key === 'ArrowRight' ? 1 : -1), true);
  });
  document.addEventListener('visibilitychange', schedule);
  motion.addEventListener('change', () => { if (motion.matches) playing = false; updateToggle(); schedule(); });
  controls.hidden = false;
  updateToggle();
  show(0);
})();
