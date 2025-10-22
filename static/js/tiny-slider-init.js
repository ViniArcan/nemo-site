document.addEventListener('DOMContentLoaded', function () {
    // --- Initialize Awards Slider ---
    const sliderAwardsEl = document.querySelector('.tiny-slider-awards');
    if (sliderAwardsEl) {
        const sliderAwards = tns({
            container: sliderAwardsEl,
            items: 1, // Start with 1 item on mobile
            slideBy: 'page',
            autoplay: false,
            controls: false, // Disable default controls, we use custom
            nav: true, // Show dots navigation
            mouseDrag: true,
            gutter: 20, // Space between items
            responsive: {
                576: { // Bootstrap sm breakpoint
                    items: 2
                },
                768: { // Bootstrap md breakpoint
                    items: 3
                },
                992: { // Bootstrap lg breakpoint
                    items: 4
                },
                1200: { // Bootstrap xl breakpoint
                    items: 5
                }
            }
        });

        // Connect Custom Controls
        const prevAwardsBtn = document.querySelector('.slider-prev-awards');
        const nextAwardsBtn = document.querySelector('.slider-next-awards');
        if (prevAwardsBtn) prevAwardsBtn.onclick = () => sliderAwards.goTo('prev');
        if (nextAwardsBtn) nextAwardsBtn.onclick = () => sliderAwards.goTo('next');
    }

    // --- Initialize Other News Slider ---
    const sliderOtherEl = document.querySelector('.tiny-slider-other');
    if (sliderOtherEl) {
        const sliderOther = tns({
            container: sliderOtherEl,
            items: 1,
            slideBy: 'page',
            autoplay: false,
            controls: false,
            nav: true,
            mouseDrag: true,
            gutter: 20,
            responsive: {
                576: { items: 2 },
                768: { items: 3 },
                992: { items: 4 },
                1200: { items: 5 }
            }
        });

        // Connect Custom Controls
        const prevOtherBtn = document.querySelector('.slider-prev-other');
        const nextOtherBtn = document.querySelector('.slider-next-other');
        if (prevOtherBtn) prevOtherBtn.onclick = () => sliderOther.goTo('prev');
        if (nextOtherBtn) nextOtherBtn.onclick = () => sliderOther.goTo('next');
    }
});