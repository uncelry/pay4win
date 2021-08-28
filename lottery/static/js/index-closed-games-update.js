// Функция обновления закрытых розыгрышей на главной
function indexUpdateClosedGamesPrivate(games_arr, card_holder){

    // Скрываем прошлые розыгрыши
    $(card_holder).fadeOut(300, function(){

        // Если есть новые розыгрыши
        if(games_arr){

            // Удаляем старые розыгрыши
            let current_games = $(card_holder).find('.slf-lottery-card').remove();

            // Проходимся по массиву и создаем каждый новый розыгрыш
            games_arr.forEach(function(lottery) {

                // Создаем розыгрыш по json-объекту

            });
        }

        // Показываем обновленные розыгрыши
        $(card_holder).fadeIn(300);
    });
}