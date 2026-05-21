document.addEventListener('DOMContentLoaded', () => {
  // ── Search Bar Filtering Logic ─────────────────────
  const searchInput = document.getElementById('searchInput');
  const cards = document.querySelectorAll('.card');

  if (searchInput && cards.length > 0) {
    searchInput.addEventListener('input', (e) => {
      const searchTerm = e.target.value.toLowerCase();
      cards.forEach(card => {
        const nameEl = card.querySelector('.company-name');
        if (nameEl) {
          const companyName = nameEl.textContent.toLowerCase();
          if (companyName.includes(searchTerm)) {
            card.style.display = 'flex';
          } else {
            card.style.display = 'none';
          }
        }
      });
    });
  }

  // ── Card Hover Effects ─────────────────────────────
  if (cards.length > 0) {
    cards.forEach(card => {
      card.addEventListener('mouseenter', () => card.classList.add('hovered'));
      card.addEventListener('mouseleave', () => card.classList.remove('hovered'));
    });
  }

  // ── Coming Soon Modal Interaction ──────────────────
  const modal = document.getElementById('comingSoonModal');
  const openButtons = document.querySelectorAll('.pyq-coming-soon-btn');
  const closeButton = document.getElementById('closeModalBtn');
  const actionButton = document.getElementById('modalActionBtn');

  function openModal(e) {
    if (e) e.preventDefault();
    if (modal) {
      modal.classList.add('active');
    }
  }

  function closeModal() {
    if (modal) {
      modal.classList.remove('active');
    }
  }

  if (openButtons.length > 0) {
    openButtons.forEach(btn => btn.addEventListener('click', openModal));
  }

  if (closeButton) {
    closeButton.addEventListener('click', closeModal);
  }

  if (actionButton) {
    actionButton.addEventListener('click', closeModal);
  }

  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        closeModal();
      }
    });
  }

  // Check URL parameters for coming_soon=true
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('coming_soon') === 'true') {
    openModal();
    // Clean URL parameter without reloading
    urlParams.delete('coming_soon');
    const newQueryString = urlParams.toString();
    const newUrl = window.location.pathname + (newQueryString ? '?' + newQueryString : '') + window.location.hash;
    window.history.replaceState({}, document.title, newUrl);
  }

  // ── Mobile Hamburger Menu Toggle ───────────────────
  const navbarToggle = document.getElementById('navbarToggle');
  const navLinks = document.querySelector('.nav-links');

  if (navbarToggle && navLinks) {
    navbarToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      navbarToggle.classList.toggle('active');
      navLinks.classList.toggle('active');
    });

    // Close when clicking a link
    const links = navLinks.querySelectorAll('a');
    links.forEach(link => {
      link.addEventListener('click', () => {
        navbarToggle.classList.remove('active');
        navLinks.classList.remove('active');
      });
    });

    // Close when clicking outside
    document.addEventListener('click', (e) => {
      if (!navLinks.contains(e.target) && !navbarToggle.contains(e.target)) {
        navbarToggle.classList.remove('active');
        navLinks.classList.remove('active');
      }
    });
  }

  // ── Toast Dismissal ────────────────────────────────
  const alerts = document.querySelectorAll('#toastContainer .alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.classList.add('fade-out');
      setTimeout(() => {
        alert.remove();
      }, 500);
    }, 4000);
  });
});