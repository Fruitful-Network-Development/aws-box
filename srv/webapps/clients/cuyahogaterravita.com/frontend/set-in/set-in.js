// set-in/set-in.js
// Set-in section specific initialization logic

document.addEventListener('componentsLoaded', () => {
  const csaSignupBtn2 = document.getElementById('csa-signup-btn-2');
  
  if (csaSignupBtn2) {
    csaSignupBtn2.addEventListener('click', () => {
      console.log('CSA Sign-Up clicked (program intro)');
      // TODO: open CSA sign-up form / modal
    });
  }
});
