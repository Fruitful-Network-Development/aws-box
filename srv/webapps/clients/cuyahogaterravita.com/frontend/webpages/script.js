// script.js

document.addEventListener('DOMContentLoaded', function() {
  const menuToggle = document.querySelector('.menu-toggle');
  const searchBtn = document.querySelector('.search-btn');
  const cartBtn = document.querySelector('.cart-btn');
  const learnMoreBtn = document.getElementById('learn-more-btn');
  const csaSignupBtn = document.getElementById('csa-signup-btn');
  const csaSignupBtn2 = document.getElementById('csa-signup-btn-2');
  const newsletterForm = document.getElementById('newsletter-form');

  menuToggle && menuToggle.addEventListener('click', () => {
    // TODO: toggle mobile nav menu
    // e.g. open/close side or dropdown menu
    console.log("Menu toggle clicked");
  });

  searchBtn && searchBtn.addEventListener('click', () => {
    // TODO: open search input
    console.log("Search button clicked");
  });

  cartBtn && cartBtn.addEventListener('click', () => {
    // TODO: open shopping cart overlay / page
    console.log("Cart button clicked");
  });

  learnMoreBtn && learnMoreBtn.addEventListener('click', () => {
    // TODO: scroll or navigate to more info section
    console.log("Learn More clicked");
  });

  csaSignupBtn && csaSignupBtn.addEventListener('click', () => {
    // TODO: open CSA sign-up form / modal
    console.log("CSA Sign-Up clicked (hero)");
  });

  csaSignupBtn2 && csaSignupBtn2.addEventListener('click', () => {
    // TODO: open CSA sign-up form / modal
    console.log("CSA Sign-Up clicked (program intro)");
  });

  newsletterForm && newsletterForm.addEventListener('submit', (e) => {
    e.preventDefault();
    // TODO: handle newsletter form submission (e.g. send AJAX)
    console.log("Newsletter form submitted");
  });
});

// WEATHER WIDGET DEMO
document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("weather-btn");
  if (!btn) return; // widget not on page

  btn.addEventListener("click", () => {
    const lat = document.getElementById("weather-lat").value;
    const lon = document.getElementById("weather-lon").value;

    fetch(`/api/weather/daily?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}&days=3&past_days=2`)
      .then(r => r.json())
      .then(data => {
        document.getElementById("weather-output").textContent =
          JSON.stringify(data, null, 2);
      })
      .catch(err => {
        document.getElementById("weather-output").textContent =
          "Error:\n" + err;
      });
  });
});

