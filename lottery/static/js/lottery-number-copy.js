$( document ).ready(function() {
    let ids = $('.slf-lottery-card-lottery-num-number');

    for(let i = 0; i < ids.length; i++){
        $(ids[i]).on("click", idClickHandler);
    }
});


function idClickHandler(e) {
    let code = e.target;
    let selection = window.getSelection();
    let range = document.createRange();
    range.selectNodeContents(code);
    selection.removeAllRanges();
    selection.addRange(range);

    try {
        document.execCommand('copy');
    } catch (err) {

    }
    window.getSelection().removeAllRanges();
}