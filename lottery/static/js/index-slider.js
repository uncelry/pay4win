let first_slide_offset = 0;

$( document ).ready(function() {
    // Берем все слайды в слайдере
    let all_basic_slides = $('.slf-index-top-slider-body .slf-index-top-slider-slide');

    // После последнего слайда добавляем первый
    $(all_basic_slides[all_basic_slides.length - 1]).after($(all_basic_slides[0]).clone().removeClass('slf-index-top-slider-slide-active'));

    // Получаем новый набор слайдов
    let all_slides = $('.slf-index-top-slider-body .slf-index-top-slider-slide');

    // Анимация слайдера циклической функцией
    setTimeout(function(){
        animateTopSlider(all_slides);
    }, 1000);
});


function animateTopSlider(slides_arr){

    let curr_slide = $('.slf-index-top-slider-body .slf-index-top-slider-slide-active');
    let first_slide = $(slides_arr[0]);
    let curr_slide_number;
    // Ищем номер активного слайда
    for(let i = 0; i < slides_arr.length; i++){
        if($(slides_arr[i]).hasClass('slf-index-top-slider-slide-active')){
            curr_slide_number = i;
            break;
        }
    }

    // Если это последний слайд, то меняем его на самый первый и переключаем на второй
    if($(slides_arr[slides_arr.length - 1]).hasClass('slf-index-top-slider-slide-active')){
        $(first_slide).css('margin-left', '0');
        first_slide_offset = 0;
        $(curr_slide).removeClass('slf-index-top-slider-slide-active');
        $(slides_arr[0]).addClass('slf-index-top-slider-slide-active');

        $(first_slide).animate({
            marginLeft: String(first_slide_offset - 100) + '%'
        }, 6000, "swing", function(){
            // Перекидываем активный класс на следующий элемент
            first_slide_offset -= 100;
            $(slides_arr[0]).removeClass('slf-index-top-slider-slide-active');
            $(slides_arr[1]).addClass('slf-index-top-slider-slide-active');

            setTimeout(function(){
                animateTopSlider(slides_arr);
            }, 11000);
        });

    // Иначе просто переключаем на следующий
    }else{
        $(first_slide).animate({
            marginLeft: String(first_slide_offset - 100) + '%'
        }, 6000, "swing", function(){
            // Перекидываем активный класс на следующий элемент
            first_slide_offset -= 100;
            $(slides_arr[curr_slide_number]).removeClass('slf-index-top-slider-slide-active');
            $(slides_arr[curr_slide_number + 1]).addClass('slf-index-top-slider-slide-active');

            setTimeout(function(){
                animateTopSlider(slides_arr);
            }, 11000);
        });
    }


}