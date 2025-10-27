 
var swiper = new Swiper(".slide-container", {
    // effect: 'slide', // 'slide' is the default, so this line is optional
    slidesPerView: 1, // Start with 1 on mobile
    spaceBetween: 25,
    loop: true,
    centeredSlides: true, // Correct parameter name and boolean value
    grabCursor: true,
    pagination: {
      el: ".swiper-pagination",
      clickable: true,
      dynamicBullets: true,
    },
    navigation: { // Ensure this is configured
      nextEl: ".swiper-button-next", // Swiper's default class
      prevEl: ".swiper-button-prev", // Swiper's default class
    },
    breakpoints: { // Keep your responsive settings
        // If showing 2 slides, start slightly wider than 520
        576: { // Matches Bootstrap's 'sm' breakpoint
            slidesPerView: 2,
            centeredSlides: false, // Often looks better not centered with even numbers
        },
        // If showing 3 slides, start slightly wider than 950
        992: { // Matches Bootstrap's 'lg' breakpoint
            slidesPerView: 3,
            centeredSlides: true, // Centering looks good with odd numbers
        },
    },
});