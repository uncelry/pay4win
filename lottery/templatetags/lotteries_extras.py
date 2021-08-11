from django import template
from lottery.models import LotteryGame

register = template.Library()


@register.simple_tag
def get_ongoing_ticks_amount_of_participant(lottery_game, participant):
    return LotteryGame.calculate_ticks_for_user(lottery_game, participant)


@register.simple_tag
def get_ongoing_win_chance_of_participant(lottery_game, participant):
    return LotteryGame.calculate_win_chance_for_user(lottery_game, participant)
