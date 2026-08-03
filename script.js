// =========================
// MOBILE MENU TOGGLE
// =========================
document.addEventListener('DOMContentLoaded', function() {
    const menu = document.querySelector('.menu');
    const navLinks = document.querySelector('.nav-links');
    const buttons = document.querySelector('.buttons');

    if (menu) {
        menu.addEventListener('click', function() {
            if (navLinks) {
                navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
            }
            if (buttons) {
                buttons.style.display = buttons.style.display === 'flex' ? 'none' : 'flex';
            }
        });
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});