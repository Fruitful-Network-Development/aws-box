// Mobile navigation toggle
document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.querySelector('.nav-toggle');
    const navList = document.querySelector('.nav-list');

    if (toggle && navList) {
        toggle.addEventListener('click', () => {
            navList.classList.toggle('is-open');
        });

        navList.addEventListener('click', (event) => {
            if (event.target.tagName.toLowerCase() === 'a') {
                navList.classList.remove('is-open');
            }
        });
    }
});
