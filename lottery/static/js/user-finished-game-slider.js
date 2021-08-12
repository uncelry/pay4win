const SET_MARGIN_LEFT = 10;
const SET_PIC_WIDTH = 115;

function setCarouselButtons(){
    let carousels = $("#slfClosedCardHolder .slf-closed-lottery-card .slf-user-closed-games-card-slider-wrapper");
    for (let i = 0; i < carousels.length; i++){

        let els = $(carousels[i]).find('.slf-user-closed-games-slider-element');

        let amount_of_els = els.length;
        let el_width = $(els[0]).width();
        let el_left_margin = $(els[els.length - 1]).css("margin-left");
        el_left_margin = Number(el_left_margin.substr(0, el_left_margin.length - 2));

        let total_els_width = (el_width * amount_of_els) + (el_left_margin * (amount_of_els - 1));

        if (total_els_width > $($(carousels[i]).find('.slf-user-closed-games-slider-body')[0]).width()){
            // Выставляем правую кнопку как активную
            let right_btn = $(carousels[i]).find('.slf-user-closed-games-card-slider-right-btn')[0];
            $(right_btn).removeClass('slf-btn-slider-inactive slf-btn-slider-active');
            $(right_btn).addClass('slf-btn-slider-active');

            // Выставляем левую кнопку как не активную
            let left_btn = $(carousels[i]).find('.slf-user-closed-games-card-slider-left-btn')[0];
            $(left_btn).removeClass('slf-btn-slider-inactive slf-btn-slider-active');
            $(left_btn).addClass('slf-btn-slider-inactive');

        } else {
            // Выставляем обе кнопки как неактивные
            let right_btn = $(carousels[i]).find('.slf-user-closed-games-card-slider-right-btn')[0];
            $(right_btn).removeClass('slf-btn-slider-inactive slf-btn-slider-active');
            $(right_btn).addClass('slf-btn-slider-inactive');

            let left_btn = $(carousels[i]).find('.slf-user-closed-games-card-slider-left-btn')[0];
            $(left_btn).removeClass('slf-btn-slider-inactive slf-btn-slider-active');
            $(left_btn).addClass('slf-btn-slider-inactive');
        }
    }
}

function buttonsHandler(e){

    // Получаем первый элемент (его будем двигать)
    let first_el = $($(e.target).siblings('.slf-user-closed-games-slider-body')[0]).find('.slf-user-closed-games-slider-element:first-of-type')[0];
    let carousel_width = $($(e.target).siblings('.slf-user-closed-games-slider-body')[0]).width();
    let els_amount = $($(e.target).siblings('.slf-user-closed-games-slider-body')[0]).find('.slf-user-closed-games-slider-element').length;
    let els_width_no_first_margin = (els_amount * SET_PIC_WIDTH) + (SET_MARGIN_LEFT * (els_amount - 1));

    // На время анимации убираем обработчик нажатия
    $(e.target).unbind('click');

    if( $(e.target).hasClass('slf-user-closed-games-card-slider-right-btn') ){
        // Если нажата правая кнопка

        // Двигаем всё влево
        $(first_el).animate({"marginLeft":
                (Number($(first_el).css("marginLeft").substr(0, $(first_el).css("marginLeft").length - 2)) + (-SET_MARGIN_LEFT + -SET_PIC_WIDTH)) + 'px'
        }, 500);

        $(first_el).promise().done(function (){

            // Проверяем надо ли блокировать кнопку
            let first_el_margin = -Number($(first_el).css("marginLeft").substr(0, $(first_el).css("marginLeft").length - 2));
            if( (els_width_no_first_margin - first_el_margin) <= carousel_width ){
                $(e.target).removeClass('slf-btn-slider-inactive slf-btn-slider-active').addClass('slf-btn-slider-inactive');
            }

            // Активируем левую кнопку
            let left_btn = $(e.target).siblings('.slf-user-closed-games-card-slider-left-btn')[0];
            $(left_btn).removeClass('slf-btn-slider-inactive slf-btn-slider-active').addClass('slf-btn-slider-active');

            // Обновляем события кнопок
            setEventListenersToButtons();
        })

    }else if( $(e.target).hasClass('slf-user-closed-games-card-slider-left-btn') ){
        // Если нажата левая кнопка

        // Двигаем всё вправо
        $(first_el).animate({"marginLeft":
                (Number($(first_el).css("marginLeft").substr(0, $(first_el).css("marginLeft").length - 2)) - (-SET_MARGIN_LEFT + -SET_PIC_WIDTH)) + 'px'
        }, 500);

        $(first_el).promise().done(function (){

           // Проверяем надо ли блокировать кнопку
            let first_el_margin = -Number($(first_el).css("marginLeft").substr(0, $(first_el).css("marginLeft").length - 2));
            if( first_el_margin === 0){
                $(e.target).removeClass('slf-btn-slider-inactive slf-btn-slider-active').addClass('slf-btn-slider-inactive');
            }

            // Активируем правую кнопку
            let right_btn = $(e.target).siblings('.slf-user-closed-games-card-slider-right-btn')[0];
            $(right_btn).removeClass('slf-btn-slider-inactive slf-btn-slider-active').addClass('slf-btn-slider-active');

            // Обновляем события кнопок
            setEventListenersToButtons();
        });

    }
}

function resetAllSliderElements(){
    let carousels_first_els = $("#slfClosedCardHolder .slf-closed-lottery-card .slf-user-closed-games-slider-body .slf-user-closed-games-slider-element:first-of-type");

    for (let i = 0; i < carousels_first_els.length; i++) {
        $(carousels_first_els[i]).stop().css('marginLeft', '0');
    }

}

function setEventListenersToButtons(){
    let listen_buttons_all = $("#slfClosedCardHolder .slf-closed-lottery-card .slf-user-closed-games-card-slider-wrapper .slf-slider-btn");
    for (let i = 0; i < listen_buttons_all.length; i++){
        $(listen_buttons_all[i]).unbind('click');
    }

    let listen_buttons = $("#slfClosedCardHolder .slf-closed-lottery-card .slf-user-closed-games-card-slider-wrapper .slf-btn-slider-active");
    for (let i = 0; i < listen_buttons.length; i++){
        $(listen_buttons[i]).bind('click', buttonsHandler);
    }
}

$( document ).ready(function() {
    resetAllSliderElements();
    setCarouselButtons();
    setEventListenersToButtons();
});

$(window).resize(function(){
  resetAllSliderElements();
  setCarouselButtons();
  setEventListenersToButtons();
});