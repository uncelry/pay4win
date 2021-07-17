function faqArrowAnim(e){

    const target_arrow = e.querySelector('img');

    const arrow_rotate = Number(window.getComputedStyle(target_arrow).getPropertyValue('transform').split('(')[1].split(',')[0]);

    if((arrow_rotate === 1) || (arrow_rotate === -1)){
        if(target_arrow.classList.contains('slf-faq-arrow-anim-fwd') || target_arrow.classList.contains('slf-faq-arrow-starter')){
            target_arrow.classList.remove('slf-faq-arrow-starter-closed');
            target_arrow.classList.remove('slf-faq-arrow-starter');
            target_arrow.classList.remove('slf-faq-arrow-anim-fwd');
            target_arrow.classList.add('slf-faq-arrow-anim-bwd');
        }else{
            target_arrow.classList.remove('slf-faq-arrow-anim-bwd');
            target_arrow.classList.add('slf-faq-arrow-anim-fwd');
        }
    }
}

