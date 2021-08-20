$( document ).ready(function() {

    let frm = $('#formTicketID');
    frm.submit(function() {
        $.ajax({
            type: frm.attr('method'),
            url: frm.attr('action'),
            data: frm.serialize(),

            success: function(response) {
                console.log(response); // УБРАТЬ!---------------------
                updateTicketForm(response);
            },

            error: function(response) {
                // Скрываем все сообщения
                let alerts = $('.slf-tickets-alert').attr({"style": "display: none!important"});
                $("#alert_res_error").css({"display": "unset"});
            }

        });
        return false;
    });

});


function updateTicketForm(data){

    // Скрываем все сообщения
    let alerts = $('.slf-tickets-alert').attr({"style": "display: none!important"});

    // Показываем актуальное сообщение
    $("#alert_" + String(data.result_code)).css({"display": "unset"});

    // Обновляем баланс пользователя
    $("#navbarNavAltMarkup .slf-steam-login-inv-wrapper .slf-nav-steam-user-links p.dropdown-item").html("Баланс: " + data.steam_user_new_balance + "<span>₽</span>");

    // Проверяем закончена ли игра
    if(data.is_lottery_finished){
        $('div.slf-game-ticket-info-wrapper').fadeOut(300, function(){
            $(this).remove();
        });
    }else{
        // Если не закончена, то обновляем поля в форме
        $(".slf-game-tickets-left").text("Осталось: " + data.tickets_left + "шт.");
        $(".slf-game-form-ticket-bought-amount .slf-form-span").html(data.total_bought_for_user + "<sup>шт.</sup>");
        $('#formAmountInput').val(1).attr('max', data.tickets_left);
    }

    // Если пользователь только вступил в розыгрыш, то показываем ему шанс выигрыша
    if(data.is_user_in_lottery && !$('.slf-participant-win-chance-user').length){
        $("#participatorMagic").after("<h3 class=\"slf-participant-win-chance-user\">Ваш шанс на победу: <span>" + data.user_win_chance + "%</span></h3>");
        $(".slf-participant-win-chance-user").hide().fadeIn(300);

    } else if($('.slf-participant-win-chance-user').length){
        // Если пользователь уже был в розыгрыше, то обновляем данные
        $(".slf-participant-win-chance-user").html("Ваш шанс на победу: <span>" + data.user_win_chance + "%</span>");
    }

}