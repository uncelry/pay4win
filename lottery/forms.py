from django import forms


class UserPrivacyForm(forms.Form):
    is_private = forms.BooleanField(label='Сделать профиль приватным', required=False)
    is_private.widget.attrs.update({
        'class': 'form-check-input slf-user-form-check-box',
        'type': 'checkbox',
        'id': 'flexSwitchCheckChecked'
    })


class BuyTicketForm(forms.Form):
    amount = forms.IntegerField(label='Количество', required=True)
    amount.widget.attrs.update({
        'class': 'form-control slf-game-amount-input',
        'type': 'text',
        'id': 'formAmountInput',
        'min': 1,
        'max': 5
    })
