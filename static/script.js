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