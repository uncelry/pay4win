function indexUpdateOpenGamesLoggedIn(lottery, card_holder){

    // Скрываем прошлые розыгрыши
    $(card_holder).fadeOut(300, function(){

        // Проверяем появился ли новый розыгрыш или это просто обновление существующего
        let curr_lotteries = $(card_holder).find('.slf-active-lottery-card .slf-lottery-card-lottery-num-number');
        let curr_lotteries_ids = [];
        for(let i = 0; i < curr_lotteries.length; i++){
            curr_lotteries_ids[i] = $(curr_lotteries[i]).attr('title');
        }

        if(curr_lotteries_ids.indexOf(lottery.lottery_id) !== -1){
            // Обновление розыгрыша
        }else{
            // Новый розыгрыш
        }

        // Показываем обновленные розыгрыши
        $(card_holder).fadeIn(300);
    });
}