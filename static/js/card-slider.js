// static/js/card-slider.js

function initializeCardSlider(sliderWrapper) {
    const slider = sliderWrapper.querySelector('.card-slider');
    const track = sliderWrapper.querySelector('.card-track');
    const slides = Array.from(track.children);
    const nextButton = sliderWrapper.querySelector('.slider-arrow.next');
    const prevButton = sliderWrapper.querySelector('.slider-arrow.prev');

    if (slides.length === 0 || !nextButton || !prevButton || !slider || !track) return;

    let isDown = false;
    let startX;
    let scrollLeftStart; // Renamed for clarity
    let slideWidth = calculateSlideWidth();
    let currentIndex = 0;
    let slidesToShow = calculateSlidesToShow();

    // --- Helper Functions ---
    function calculateSlidesToShow() {
        if (window.innerWidth <= 768) return 1;
        if (window.innerWidth <= 992) return 2;
        return 3;
    }

    function calculateSlideWidth() {
         // Include gap in width calculation
        const gap = parseInt(getComputedStyle(track).gap) || 0;
        return slides.length > 0 ? slides[0].offsetWidth + gap : 300; // Use offsetWidth + gap
    }

    function updateLayoutMetrics() {
        slidesToShow = calculateSlidesToShow();
        slideWidth = calculateSlideWidth();
        // Recalculate max scroll and button states without moving
        updateButtonStates();
    }

     function smoothScrollTo(targetScrollLeft) {
        slider.scrollTo({
            left: targetScrollLeft,
            behavior: 'smooth'
        });
        // We will let the 'scroll' event listener update buttons
    }

    function updateButtonStates() {
        const currentScroll = Math.round(slider.scrollLeft); // Round for precision
        const maxScrollLeft = slider.scrollWidth - slider.clientWidth;
        prevButton.disabled = currentScroll <= 0;
        nextButton.disabled = currentScroll >= maxScrollLeft - 1; // Tolerance
        // Update currentIndex based on current scroll position
        currentIndex = Math.round(currentScroll / slideWidth);
    }

    // --- Snap Logic ---
    function snapScroll() {
        const currentScroll = slider.scrollLeft;
        const nearestIndex = Math.round(currentScroll / slideWidth);
        const maxIndex = slides.length - slidesToShow;
        const targetIndex = Math.min(Math.max(nearestIndex, 0), maxIndex); // Clamp index
        const targetScrollLeft = targetIndex * slideWidth;
        smoothScrollTo(targetScrollLeft);
    }

    // --- Drag/Swipe Event Listeners ---
    slider.addEventListener('mousedown', (e) => {
        isDown = true;
        slider.classList.add('active-drag');
        startX = e.pageX - slider.offsetLeft;
        scrollLeftStart = slider.scrollLeft;
        slider.style.scrollBehavior = 'auto'; // Disable smooth scroll during drag
        e.preventDefault();
    });

    slider.addEventListener('mouseleave', () => {
        if (!isDown) return; // Only snap if dragging was in progress
        isDown = false;
        slider.classList.remove('active-drag');
        slider.style.scrollBehavior = 'smooth'; // Re-enable smooth scroll
        snapScroll(); // Snap when mouse leaves while dragging
    });

    slider.addEventListener('mouseup', () => {
        if (!isDown) return; // Prevent snapping if not dragging
        isDown = false;
        slider.classList.remove('active-drag');
        slider.style.scrollBehavior = 'smooth'; // Re-enable smooth scroll
        snapScroll(); // Snap on mouse up
    });

    slider.addEventListener('mousemove', (e) => {
        if (!isDown) return;
        e.preventDefault();
        const x = e.pageX - slider.offsetLeft;
        const walk = (x - startX) * 2;
        slider.scrollLeft = scrollLeftStart - walk;
    });

    // --- Touch Events ---
    slider.addEventListener('touchstart', (e) => {
        isDown = true;
        startX = e.touches[0].pageX - slider.offsetLeft;
        scrollLeftStart = slider.scrollLeft;
        slider.style.scrollBehavior = 'auto';
    }, { passive: true });

    slider.addEventListener('touchend', () => {
        if (!isDown) return;
        isDown = false;
        slider.style.scrollBehavior = 'smooth';
        snapScroll(); // Snap on touch end
    });

    slider.addEventListener('touchmove', (e) => {
        if (!isDown) return;
        const x = e.touches[0].pageX - slider.offsetLeft;
        const walk = (x - startX) * 1.5;
        slider.scrollLeft = scrollLeftStart - walk;
    }, { passive: true });


    // --- Button Click Logic ---
    nextButton.addEventListener('click', () => {
        const targetIndex = Math.min(currentIndex + 1, slides.length - slidesToShow);
        smoothScrollTo(targetIndex * slideWidth);
    });

    prevButton.addEventListener('click', () => {
        const targetIndex = Math.max(currentIndex - 1, 0);
        smoothScrollTo(targetIndex * slideWidth);
    });

    // --- Update buttons on scroll end ---
    let scrollEndTimeout;
    slider.addEventListener('scroll', () => {
        clearTimeout(scrollEndTimeout);
        scrollEndTimeout = setTimeout(updateButtonStates, 150); // Update after scroll settles
    });

    // --- Recalculate on window resize ---
    window.addEventListener('resize', () => {
        // Use a timeout to avoid excessive calculations during resize
        clearTimeout(scrollEndTimeout); // Reuse timeout
        scrollEndTimeout = setTimeout(() => {
             updateLayoutMetrics();
             // Optionally snap to current index after resize
             smoothScrollTo(currentIndex * slideWidth);
        }, 250);
    });

    // --- Initial setup ---
    updateButtonStates();
    // Ensure initial smooth scrolling is enabled
    slider.style.scrollBehavior = 'smooth';

}

// Initialize all sliders on the page
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.card-slider-wrapper').forEach(initializeCardSlider);
});