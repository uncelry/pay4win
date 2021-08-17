$( document ).ready(function() {
    let links = $('.slf-type-modal-link-opener');

    for(let i = 0; i < links.length; i++){
        $(links[i]).on("click", handleLinkPress);
    }

});

function handleLinkPress(e){
    if($(e.target).attr('type-open') === 'gold'){
        $($('.slf-types-modal-content-silver')[0]).css({'display': 'none'});
        $($('.slf-types-modal-content-bronze')[0]).css({'display': 'none'});
        $($('.slf-types-modal-content-gold')[0]).css({'display': 'unset'});
    }

    if($(e.target).attr('type-open') === 'silver'){
        $($('.slf-types-modal-content-silver')[0]).css({'display': 'unset'});
        $($('.slf-types-modal-content-bronze')[0]).css({'display': 'none'});
        $($('.slf-types-modal-content-gold')[0]).css({'display': 'none'});
    }

    if($(e.target).attr('type-open') === 'bronze'){
        $($('.slf-types-modal-content-silver')[0]).css({'display': 'none'});
        $($('.slf-types-modal-content-bronze')[0]).css({'display': 'unset'});
        $($('.slf-types-modal-content-gold')[0]).css({'display': 'none'});
    }
}