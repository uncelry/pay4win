$( document ).ready(function() {
    $("#formAmountInput").on('input keyup', function(e) {
        let ticket_price = Number($('.slf-game-form-ticket-price .slf-form-span').attr('ticket-price'));
        $('.slf-game-form-total-price span.slf-form-span').html(Number($(e.target).val()) * ticket_price + "<sup>руб</sup>");
    });
});