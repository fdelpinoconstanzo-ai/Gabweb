document.addEventListener('DOMContentLoaded', () => {
  // Footer year
  const yearEl = document.getElementById('year');
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }

  // Active nav
  const currentPath = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.main-nav a').forEach(link => {
    const linkPath = link.getAttribute('href');
    if (linkPath === currentPath || (currentPath === '' && linkPath === 'index.html')) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });

  // Header scroll effect
  const header = document.querySelector('.site-header');
  if (header) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 20) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
    });
  }

  // Project filters
  const filterBtns = document.querySelectorAll('.filter-btn');
  const projectCards = document.querySelectorAll('.project-card');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (reducedMotion || !('IntersectionObserver' in window)) {
    projectCards.forEach(card => card.classList.add('is-visible'));
  } else {
    const revealObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });

    projectCards.forEach(card => revealObserver.observe(card));

    let parallaxFrame = null;
    const updateParallax = () => {
      projectCards.forEach(card => {
        if (card.classList.contains('hidden')) return;
        const image = card.querySelector('.project-image');
        const rect = card.getBoundingClientRect();
        if (!image || rect.bottom < 0 || rect.top > window.innerHeight) return;
        const distance = window.innerHeight / 2 - (rect.top + rect.height / 2);
        const offset = Math.max(-14, Math.min(14, distance * 0.035));
        image.style.setProperty('--parallax-y', `${offset}px`);
      });
      parallaxFrame = null;
    };

    window.addEventListener('scroll', () => {
      if (!parallaxFrame) {
        parallaxFrame = window.requestAnimationFrame(updateParallax);
      }
    }, { passive: true });
    updateParallax();
  }

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filter = btn.dataset.filter;

      projectCards.forEach(card => {
        const categories = card.dataset.category || '';
        if (filter === 'all' || categories.split(/\s+/).includes(filter)) {
          card.classList.remove('hidden');
        } else {
          card.classList.add('hidden');
        }
      });
    });
  });

  // Contact form placeholder
  const form = document.querySelector('.contact-form');
  if (form) {
    form.addEventListener('submit', event => {
      event.preventDefault();
      const btn = form.querySelector('button');
      const originalText = btn.textContent;
      btn.textContent = 'Sent';
      btn.disabled = true;
      setTimeout(() => {
        form.reset();
        btn.textContent = originalText;
        btn.disabled = false;
      }, 2000);
    });
  }
});