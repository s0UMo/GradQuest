const searchInput = document.getElementById("searchInput");
const cards = document.querySelectorAll(".card");
if (searchInput) {
  searchInput.addEventListener("input", (e) => {
    const searchTerm = e.target.value.toLowerCase();
    cards.forEach((card) => {
      const companyName = card
        .querySelector(".company-name")
        .textContent.toLowerCase();
      if (companyName.includes(searchTerm)) {
        card.style.display = "flex";
      } else {
        card.style.display = "none";
      }
    });
  });
}
cards.forEach((card) => {
  card.addEventListener("mouseenter", () => card.classList.add("hovered"));
  card.addEventListener("mouseleave", () => card.classList.remove("hovered"));
});
document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("comingSoonModal");
  const openButtons = document.querySelectorAll(".pyq-coming-soon-btn");
  const closeButton = document.getElementById("closeModalBtn");
  const actionButton = document.getElementById("modalActionBtn");
  function openModal(e) {
    if (e) e.preventDefault();
    if (modal) {
      modal.classList.add("active");
    }
  }
  function closeModal() {
    if (modal) {
      modal.classList.remove("active");
    }
  }
  if (openButtons.length > 0) {
    openButtons.forEach((btn) => btn.addEventListener("click", openModal));
  }
  if (closeButton) {
    closeButton.addEventListener("click", closeModal);
  }
  if (actionButton) {
    actionButton.addEventListener("click", closeModal);
  }
  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) {
        closeModal();
      }
    });
  }
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get("coming_soon") === "true") {
    openModal();
    urlParams.delete("coming_soon");
    const newQueryString = urlParams.toString();
    const newUrl =
      window.location.pathname +
      (newQueryString ? "?" + newQueryString : "") +
      window.location.hash;
    window.history.replaceState({}, document.title, newUrl);
  }
  const hamburger = document.getElementById("hamburgerBtn");
  const navLinks = document.getElementById("navLinks");
  if (hamburger && navLinks) {
    hamburger.addEventListener("click", (e) => {
      e.stopPropagation();
      hamburger.classList.toggle("active");
      navLinks.classList.toggle("active");
      if (navLinks.classList.contains("active")) {
        document.body.style.overflow = "hidden";
      } else {
        document.body.style.overflow = "";
      }
    });
    document.addEventListener("click", (e) => {
      if (
        navLinks.classList.contains("active") &&
        !navLinks.contains(e.target) &&
        !hamburger.contains(e.target)
      ) {
        hamburger.classList.remove("active");
        navLinks.classList.remove("active");
        document.body.style.overflow = "";
      }
    });
  }
});
