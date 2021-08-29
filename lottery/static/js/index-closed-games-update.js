// Функция обновления закрытых розыгрышей на главной
function indexUpdateClosedGamesPrivate(games_arr, card_holder){

    // Скрываем прошлые розыгрыши
    $(card_holder).fadeOut(300, function(){

        // Если есть новые розыгрыши
        if(games_arr){

            // Удаляем старые розыгрыши
            $(card_holder).find('.slf-lottery-card').remove();
            $(card_holder).find('#indexClosedNoTextPID').remove();

            // Проходимся по массиву и создаем каждый новый розыгрыш
            games_arr.forEach(function(lottery) {

                // Делаем строку жанров
                let genres_str = '';
                for(let i = 0; i < lottery.game_genres.length; i++){
                    genres_str += lottery.game_genres[i];
                    if(i !== lottery.game_genres.length - 1){
                        genres_str += ', ';
                    }
                }

                // Делаем строку участников
                let participators_cards = '';
                for(let i = 0; i < lottery.lottery_participants.length; i++){
                    participators_cards += '<a class="slf-user-closed-games-slider-element" style="background-image: url(' + lottery.lottery_participants[i].avatar + ')" title="' + lottery.lottery_participants[i].name + '" href="' + lottery.lottery_participants[i].link + '" target="_blank">' +
                        '<p class="slf-user-closed-games-slider-element-win-chance">' + lottery.lottery_participants[i].chance + '%</p>' +
                        '</a>';
                }

                // Создаем розыгрыш по json-объекту
                $(card_holder).append(
                    '<div class="slf-lottery-card slf-closed-lottery-card ' + ((lottery.is_winner) ? 'slf-closed-lottery-current-winner ' : '') + ((lottery.is_participant) ? 'slf-closed-lottery-card-participated ' : '') + ((lottery.lottery_type === "g") ? 'slf-lottery-card-gold' : ((lottery.lottery_type === "s") ? 'slf-lottery-card-silver' : ((lottery.lottery_type === "b") ? 'slf-lottery-card-bronze' : ''))) + '">' +
                        '<img src="' + lottery.game_img + '" alt="" class="slf-lottery-card-img">' +
                        '<div class="slf-lottery-card-inner">' +
                            '<div class="slf-lottery-card-info-wrapper">' +

                                '<div class="slf-lottery-card-info-name-wrapper">' +
                                    '<h2 class="slf-lottery-card-name" title="' + lottery.game_name + '">' + lottery.game_name + '</h2>' +
                                    '<p class="slf-lottery-card-genres">' +
                                        genres_str +
                                    '</p>' +
                                '</div>' +

                                '<div class="slf-lottery-card-lottery-info-wrapper">' +
                                    '<p class="slf-lottery-card-lottery-num">' +
                                        'Игра: <span class="slf-lottery-card-lottery-num-number" title="' + lottery.lottery_id + '">' + lottery.lottery_id + '</span>' +
                                    '</p>' +
                                    '<p class="slf-lottery-card-lottery-type-wrapper">' +
                                        'Победитель:' +
                                        '<span class="slf-lottery-card-lottery-num-number" title="' + lottery.lottery_winner_name + '">' +
                                            lottery.lottery_winner_name +
                                        '</span>' +
                                    '</p>' +
                                '</div>' +

                                '<p class="btn btn-primary slf-lottery-card-participate slf-closed-game-not-btn">Закрыто</p>' +

                            '</div>' +

                            '<div class="slf-user-closed-games-card-slider-wrapper">' +
                                '<i class="bi bi-caret-left-fill slf-user-closed-games-card-slider-left-btn slf-btn-slider-inactive slf-slider-btn"></i>' +
                                '<div class="slf-user-closed-games-card-slider-left-btn-under"></div>' +
                                '<div class="slf-user-closed-games-slider-body">' +
                                    participators_cards +
                                '</div>' +
                                '<div class="slf-user-closed-games-card-slider-right-btn-under"></div>' +
                                '<i class="bi bi-caret-right-fill slf-user-closed-games-card-slider-right-btn slf-btn-slider-inactive slf-slider-btn"></i>' +
                            '</div>' +

                            '<p class="slf-lottery-card-game-desc">' +
                                lottery.game_desc +
                            '</p>' +

                            '<p class="slf-lottery-card-ticket-price ' + (lottery.is_authenticated ? 'slf-lottery-card-ticket-price-user-logged-in' : '') + '">' +
                                'Цена билета: <strong>' + lottery.lottery_ticket_price + '&#8381;</strong>' +
                                (lottery.is_participant ? '(<strong>x' + lottery.lottery_amount_of_bought_tickets_for_user + '</strong>)' : '') +
                            '</p>' +
                        '</div>' +
                    '</div>'
                );
            });

            // Активируем стрелочки на новых карточках
            resetAllSliderElements();
            setCarouselButtons();
            setEventListenersToButtons();

        }else{
            // Удаляем старые розыгрыши
            $(card_holder).find('.slf-lottery-card').remove();
            $(card_holder).find('#indexClosedNoTextPID').remove();

            // Добавляем новость о том, что сейчас таких розыгрышей нет
            $(card_holder).append('<p id="indexClosedNoTextPID">В данный момент история игр по данному запросу пуста</p>')
        }

        // Показываем обновленные розыгрыши
        $(card_holder).fadeIn(300);
    });
}