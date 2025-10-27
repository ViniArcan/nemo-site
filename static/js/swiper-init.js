/* --- Master Swiper Initialization File --- */
/* This one file controls all sliders on the site. */

document.addEventListener('DOMContentLoaded', function () {

    // --- 1. Initialize Index Page Slider ---
    // This looks for the unique ID #indexSwiper
    const indexSwiperEl = document.querySelector('#indexSwiper');
    if (indexSwiperEl) {
        var indexSwiper = new Swiper("#indexSwiper", {
            slidesPerView: 1,
            spaceBetween: 25,
            loop: true,
            centeredSlides: true,
            grabCursor: true,
            pagination: {
              el: ".index-pagination", // Use unique class
              clickable: true,
              dynamicBullets: true,
            },
            navigation: {
              nextEl: ".index-next", // Use unique class
              prevEl: ".index-prev", // Use unique class
            },
            breakpoints: {
                576: { // Matches Bootstrap's 'sm' breakpoint
                    slidesPerView: 2,
                    centeredSlides: false,
                },
                992: { // Matches Bootstrap's 'lg' breakpoint
                    slidesPerView: 3,
                    centeredSlides: true,
                },
            },
        });
    }

    // --- 2. Initialize News Page (Awards) Slider ---
    // This looks for the unique ID #awardsSwiper
    const awardsSwiperEl = document.querySelector('#awardsSwiper');
    if (awardsSwiperEl) {
        var awardsSwiper = new Swiper("#awardsSwiper", {
            slidesPerView: 1,
            spaceBetween: 25,
            loop: true,
            centeredSlides: true,
            grabCursor: true,
            pagination: {
              el: ".awards-pagination", // Unique class
              clickable: true,
              dynamicBullets: true,
            },
            navigation: {
              nextEl: ".awards-next", // Unique class
              prevEl: ".awards-prev", // Unique class
            },
            breakpoints: {
                576: {
                    slidesPerView: 2,
                    centeredSlides: false
                },
                992: {
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

    // --- 3. Initialize News Page (Other News) Slider ---
    // This looks for the unique ID #otherNewsSwiper
    const otherNewsSwiperEl = document.querySelector('#otherNewsSwiper');
    if (otherNewsSwiperEl) {
         var otherNewsSwiper = new Swiper("#otherNewsSwiper", {
            slidesPerView: 1,
            spaceBetween: 25,
            loop: true,
            centeredSlides: true,
            grabCursor: true,
            pagination: {
              el: ".other-pagination", // Unique class
              clickable: true,
              dynamicBullets: true,
            },
            navigation: {
              nextEl: ".other-next", // Unique class
              prevEl: ".other-prev", // Unique class
            },
            breakpoints: {
                576: {
                    slidesPerView: 2,
                    centeredSlides: false
                 },
                992: {
                    slidesPerView: 3,
                    centeredSlides: true
                 },
                1200: {
                     slidesPerView: 4,
                     centeredSlides: false
                 },
            },
        });
    }
});