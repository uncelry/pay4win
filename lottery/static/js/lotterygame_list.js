// Функционал кнопки подгрузки розыгрышей

let cards_arr;
let i;
const AMOUNT_FOR_ONE_TIME = 10;
let shown_now;

document.addEventListener('DOMContentLoaded', function(){
    cards_arr = document.querySelectorAll('#slfSearchCardHolder > .slf-lottery-card');

    for(i = AMOUNT_FOR_ONE_TIME; i < cards_arr.length; i++){
        cards_arr[i].classList.add('slf-lottery-card-hidden');
    }

    shown_now = AMOUNT_FOR_ONE_TIME;
});

function showMore(e, btn){
    e.preventDefault();

    if ((cards_arr.length - shown_now) >= AMOUNT_FOR_ONE_TIME){
        for(i = shown_now; i < shown_now + AMOUNT_FOR_ONE_TIME; i++){
            cards_arr[i].classList.remove('slf-lottery-card-hidden');
        }

        shown_now += AMOUNT_FOR_ONE_TIME;
    } else {
        for(i = shown_now; i < cards_arr.length; i++){
            cards_arr[i].classList.remove('slf-lottery-card-hidden');
        }

        shown_now = cards_arr.length;
    }


    if (shown_now === cards_arr.length){
        btn.setAttribute('onclick', '');
        btn.classList.add('slf-lottery-card-hidden');
    }

    btn.blur();
}
