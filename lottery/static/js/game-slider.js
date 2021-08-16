// Заставляем работать слайдер
$( document ).ready(function() {

    // 1) Выставляем активному по умолчанию элементу класс активности
    $(".slf-slider-main:first-of-type").addClass('slf-slider-main-active-el');

    // 2) Выставляем всем миниатюрам обработчик события нажатия

    let main_slides = $(".slf-slider-mini-pic-el");

    for(let i = 0; i < main_slides.length; i++){
        $(main_slides[i]).on("click", sliderSmallClicked);
    }

    // 3) Выставляем всем средним картинкам обработчик
    let actual_slides_pics = $("img.slf-slider-main");

    for(let i = 0; i < actual_slides_pics.length; i++){
        $(actual_slides_pics[i]).on("click", slidePictureClicked);
    }

    // 4) Выставляем обработчик крестику на закрытие модального окна
    $($('.slf-modal-close-btn')[0]).on("click", closeModalWindow);

    // 5) Выставляем обработчик фону на закрытие модального окна
    $($('.slf-modal-game-slider-window')[0]).on("click", closeModalWindow);

    // 6) Выставляем обработчик нажатия кнопки ESC для закрытия модального окна
    $(document).keydown(closeModalByEscape);
});


// Обработчик нажатия на миниатюры слайдера
function sliderSmallClicked(e){
    let clicked_el = e.target;

    let main_slides = $(".slf-slider-mini-pic-el");

    let videos = $('video');
    for(let i = 0; i < videos.length; i++){
        let media = $(videos[i]).get(0);
        media.pause();
        media.currentTime = 0;
    }

    for(let i = 0; i < main_slides.length; i++){
        if(main_slides[i] === clicked_el){
            $(".slf-slider-main-active-el").css({"display": "none"}).removeClass('slf-slider-main-active-el');
            $($(".slf-slider-main")[i]).css({"display": "unset"}).addClass('slf-slider-main-active-el');
        }
    }
}


// Обработчик нажатия на слайд-картинку
function slidePictureClicked(e){
    let modal = $('.slf-modal-game-slider-window')[0];

    $(modal).find('img.slf-modal-img').attr('src', $(e.target).attr('pic-to-show'));

    $(modal).removeClass('slf-modal-closed');
}


// Обработчик - закрытие модального окна
function closeModalWindow(e){
    $($('.slf-modal-game-slider-window')[0]).addClass('slf-modal-closed');
}


// Обработчик - нажатие ESC для закрытия модального окна
function closeModalByEscape(e){
    if (e.keyCode === 27) {
        if( !$($('.slf-modal-game-slider-window')[0]).hasClass('slf-modal-closed') ){
            $($('.slf-modal-game-slider-window')[0]).addClass('slf-modal-closed');
        }
    }
}