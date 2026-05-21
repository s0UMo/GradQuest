// Search Bar Filtering Logic
const searchInput = document.getElementById('searchInput');
const cards = document.querySelectorAll('.card');

searchInput.addEventListener('input', (e) => {
  const searchTerm = e.target.value.toLowerCase();

  cards.forEach(card => {
    // Look for the company name inside the card
    const companyName = card.querySelector('.company-name').textContent.toLowerCase();
    
    // Toggle display based on whether it matches the search term
    if (companyName.includes(searchTerm)) {
      card.style.display = 'flex';
    } else {
      card.style.display = 'none';
    }
  });
});

// Optional: Extra CSS class logic from your original script
cards.forEach(card => {
  card.addEventListener('mouseenter', () => card.classList.add('hovered'));
  card.addEventListener('mouseleave', () => card.classList.remove('hovered'));
});

// ── Coming Soon Modal Interaction ──────────────────
document.addEventListener('DOMContentLoaded', () => {
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
});