// CareerCompass AI — shared interactions (landing page)

document.addEventListener('DOMContentLoaded', () => {

  // Mobile nav toggle
  const navToggle = document.getElementById('navToggle');
  const mobileMenu = document.getElementById('mobileMenu');
  if (navToggle && mobileMenu) {
    navToggle.addEventListener('click', () => {
      const isOpen = mobileMenu.style.display === 'flex';
      mobileMenu.style.display = isOpen ? 'none' : 'flex';
    });
    mobileMenu.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => { mobileMenu.style.display = 'none'; });
    });
  }

  // Reveal-on-scroll (single, restrained: fade + rise, once per element).
  // Elements are visible by default in CSS; only opt into the hidden
  // "pending" state here, right before we're sure we can reveal them again.
  const revealEls = document.querySelectorAll('.reveal');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if ('IntersectionObserver' in window && !reduceMotion) {
    revealEls.forEach(el => el.classList.add('reveal-pending'));
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    revealEls.forEach(el => io.observe(el));

    // Safety net: if anything is ever missed (odd layout, resize during
    // capture, etc.) make sure it becomes visible anyway.
    setTimeout(() => revealEls.forEach(el => el.classList.add('in')), 4000);
  }

  // Hero compass needle: one settle-into-place spin on load, then rest.
  const needle = document.getElementById('needle');
  if (needle && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    needle.style.transition = 'transform 1.4s cubic-bezier(.2,.8,.2,1)';
    needle.style.transform = 'rotate(-35deg)';
    requestAnimationFrame(() => {
      setTimeout(() => { needle.style.transform = 'rotate(24deg)'; }, 120);
      setTimeout(() => { needle.style.transform = 'rotate(0deg)'; }, 900);
    });
  }
});
