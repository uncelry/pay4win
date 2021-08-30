function indexUpdateOpenGamesLoggedIn(data, card_holder, g_img, s_img, b_img){

    // Проверяем появился ли новый розыгрыш или это просто обновление существующего
    if(data.change_type === 'lottery_update'){
        // Если просто обновление одного розыгрыша

        let lottery = data

        // Ищем на странице розыгрыш, который надо обновить
        let curr_lotteries = $(card_holder).find('.slf-active-lottery-card .slf-lottery-card-lottery-num-number');
        let curr_lotteries_ids = [];
        for(let i = 0; i < curr_lotteries.length; i++){
            curr_lotteries_ids[i] = $(curr_lotteries[i]).attr('title');
        }
        let current_lotteries_cards = $(card_holder).find('.slf-active-lottery-card');

        let lottery_pos = curr_lotteries_ids.indexOf(lottery.lottery_id);

        if(lottery_pos !== -1){
            //Меняем розыгрыш, по которому пришли обновленные данные
            let lot = $(current_lotteries_cards[lottery_pos]);

            // Меняем прогресс
            $(lot).find('.slf-lottery-card-progress-tickets').html(
                lottery.lottery_tickets_bought + '/' + lottery.lottery_tickets_total + '<br><span>БИЛЕТОВ</span>'
            );
            $(lot).find('.slf-lottery-card-progress > div').attr('style', 'width: ' + lottery.lottery_progress + '%');

            // Если пользователь участвует в обновленном розыгрыше, то проверяем участвовал ли он до этого
            if(lottery.is_participant){
                if($(lot).hasClass('slf-active-lottery-card-ongoing')){

                    // Пользователь уже участвовал в нем - просто обновляем данные
                    $(lot).find('.slf-lottery-card-ticket-price-user-logged-in').fadeOut(300, function(){
                        $(this).html(
                            'Цена билета: <strong>' + lottery.lottery_ticket_price + '&#8381;</strong>' +
                                    ((lottery.is_participant) ? ' (приобретено <strong>x' + lottery.lottery_ticks_for_user + '</strong>)' : '') +
                                    ((lottery.is_participant) ? ' Шанс на победу: <strong>' + lottery.lottery_win_chance_for_user + '%</strong>' : '')
                        );
                        $(this).fadeIn(300);
                    });

                }else{

                    // Пользователь только принял участие - добавляем новые классы и элементы
                    $(lot).fadeOut(300, function(){

                        $(this).addClass('slf-active-lottery-card-ongoing');
                        $(this).find('.slf-lottery-card-participate').text('Перейти');
                        $(this).find('.slf-lottery-card-ticket-price-user-logged-in').html(
                            'Цена билета: <strong>' + lottery.lottery_ticket_price + '&#8381;</strong>' +
                                    ((lottery.is_participant) ? ' (приобретено <strong>x' + lottery.lottery_ticks_for_user + '</strong>)' : '') +
                                    ((lottery.is_participant) ? ' Шанс на победу: <strong>' + lottery.lottery_win_chance_for_user + '%</strong>' : '')
                        );

                        $(this).fadeIn(300);
                    });
                }
            }
        }
    }else if(data.change_type === 'new_lottery') {
        // Если новая игра (то есть, надо обновить все розыгрыши на странице)

        // Скрываем прошлые розыгрыши
        $(card_holder).fadeOut(300, function(){

            // Убираем все текущие розыгрыши
            $(card_holder).find('.slf-active-lottery-card').remove();

            // В цикле добавляем новые розыгрыши
            data.lotteries_array.forEach(function (lottery){

                // Делаем строку жанров
                let genres_str = '';
                for(let i = 0; i < lottery.game_genres.length; i++){
                    genres_str += lottery.game_genres[i];
                    if(i !== lottery.game_genres.length - 1){
                        genres_str += ', ';
                    }
                }

                // Добавляем новый розыгрыш первым
                $(card_holder).find('#slfSearchShowMoreBtn').before(
                    '<div class="slf-lottery-card slf-active-lottery-card ' + ((lottery.is_participant) ? 'slf-active-lottery-card-ongoing ' : '') + ((lottery.lottery_type === "g") ? 'slf-lottery-card-gold' : ((lottery.lottery_type === "s") ? 'slf-lottery-card-silver' : ((lottery.lottery_type === "b") ? 'slf-lottery-card-bronze' : ''))) + '">' +
                        '<img src="' + lottery.game_img + '" alt="" class="slf-lottery-card-img">' +
                        '<div class="slf-lottery-card-inner">' +
                            '<div class="slf-lottery-card-info-wrapper">'+

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
                                        'Тип:' +
                                        '<span class="slf-lottery-card-lottery-type">' +
                                            ((lottery.lottery_type === "g") ? '<img class="slf-lottery-card-lottery-type-pic" alt="" src="' + g_img + '"> Золото' : ((lottery.lottery_type === "s") ? '<img class="slf-lottery-card-lottery-type-pic" alt="" src="' + s_img + '"> Серебро' : ((lottery.lottery_type === "b") ? '<img class="slf-lottery-card-lottery-type-pic" alt="" src="' + b_img + '"> Бронза' : ''))) +
                                        '</span>' +
                                    '</p>' +
                                '</div>' +

                                '<a class="btn btn-primary slf-lottery-card-participate" href="' + lottery.lottery_link + '">' + ((lottery.is_participant) ? 'Перейти' : 'Участвовать') + '</a>' +
                            '</div>' +

                            '<div class="slf-lottery-card-progress">' +
                                '<div class="progress-bar stripes animated slower" style="width: ' + lottery.lottery_progress + '%"></div>' +
                                '<p class="slf-lottery-card-progress-tickets">' +
                                    lottery.lottery_tickets_bought + '/' + lottery.lottery_tickets_total + '<br><span>БИЛЕТОВ</span>' +
                                '</p>' +
                            '</div>' +

                            '<p class="slf-lottery-card-game-desc slf-lottery-card-game-desc-user-logged-in">' +
                                lottery.lottery_desc_480 +
                            '</p>' +

                            '<p class="slf-lottery-card-ticket-price slf-lottery-card-ticket-price-user-logged-in">' +
                                'Цена билета: <strong>' + lottery.lottery_ticket_price + '&#8381;</strong>' +
                                ((lottery.is_participant) ? ' (приобретено <strong>x' + lottery.lottery_ticks_for_user + '</strong>)' : '') +
                                ((lottery.is_participant) ? ' Шанс на победу: <strong>' + lottery.lottery_win_chance_for_user + '%</strong>' : '') +
                            '</p>' +

                        '</div>' +
                    '</div>'
                );

            });

            // Показываем обновленные розыгрыши
            $(card_holder).fadeIn(300);
        });
    }
}