document.addEventListener('DOMContentLoaded', function () {

    // --- Initialize Awards Slider ---
    const awardsSwiperEl = document.querySelector('#awardsSwiper');
    if (awardsSwiperEl) {
        var awardsSwiper = new Swiper("#awardsSwiper", {
            // effect: 'slide', // 'slide' is the default
            slidesPerView: 1, // Start with 1 on mobile
            spaceBetween: 25,
            loop: true, // Loop might be desirable here
            centeredSlides: true,
            grabCursor: true,
            pagination: {
              el: ".awards-pagination", // Unique class for awards pagination
              clickable: true,
              dynamicBullets: true,
            },
            navigation: {
              nextEl: ".awards-next", // Unique class for awards next button
              prevEl: ".awards-prev", // Unique class for awards prev button
            },
            breakpoints: {
                576: { // Bootstrap sm breakpoint
                    slidesPerView: 2,
                    centeredSlides: false // Often looks better not centered with even numbers
                },
                992: { // Bootstrap lg breakpoint
                    slidesPerView: 3,
                    centeredSlides: true // Centering looks good with odd numbers
                },
                 1200: { // Bootstrap xl breakpoint
                    slidesPerView: 4,
                    centeredSlides: false // Can show more on very wide screens
                 },
            },
        });
    }

    // --- Initialize Other News Slider ---
    const otherNewsSwiperEl = document.querySelector('#otherNewsSwiper');
    if (otherNewsSwiperEl) {
         var otherNewsSwiper = new Swiper("#otherNewsSwiper", {
            // effect: 'slide',
            slidesPerView: 1,
            spaceBetween: 25,
            loop: true, // Loop might be desirable here
            centeredSlides: true,
            grabCursor: true,
            pagination: {
              el: ".other-pagination", // Unique class for other news pagination
              clickable: true,
              dynamicBullets: true,
            },
            navigation: {
              nextEl: ".other-next", // Unique class for other news next button
              prevEl: ".other-prev", // Unique class for other news prev button
            },
            breakpoints: {
                576: { // Bootstrap sm breakpoint
                    slidesPerView: 2,
                    centeredSlides: false
                 },
                992: { // Bootstrap lg breakpoint
                    slidesPerView: 3,
                    centeredSlides: true
                 },
                1200: { // Bootstrap xl breakpoint
                     slidesPerView: 4,
                     centeredSlides: false
                 },
            },
        });
    }
});