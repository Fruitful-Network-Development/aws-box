// header/header.js
// Header-specific initialization logic

document.addEventListener('componentsLoaded', () => {
  // Header menu icon click handler
  const menuIcon = document.querySelector('.header-icon');
  if (menuIcon) {
    menuIcon.addEventListener('click', () => {
      console.log('Menu clicked');
      // TODO: Implement menu toggle functionality
    });
  }

  // Search form handler
  const searchForm = document.querySelector('.header-search');
  if (searchForm) {
    searchForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const searchInput = searchForm.querySelector('.search-input');
      const query = searchInput?.value;
      console.log('Search query:', query);
      // TODO: Implement search functionality
    });
  }

  // Basket icon click handler
  const basketIcon = document.querySelector('.basket-icon');
  if (basketIcon) {
    basketIcon.addEventListener('click', () => {
      console.log('Cart clicked');
      // TODO: Open shopping cart overlay / page
    });
  }
});
