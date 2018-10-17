from random import randint

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from .forms import UserRegisterForm
from django.contrib import messages

from .models import Card, Deck, Game, CardUser, CardDeck


def home(request):
    title = 'Accueil'
    slugs = [
        'test',
        'tast',
        'tost',
    ]
    context = {
        'title': title,
        'games': Game.objects.all(),
        'cards': Card.objects.all(),
        'slugs': slugs,
    }
    return render(request, 'hearthstone/index.html', context)


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Le compte de {username} a bien été créé !')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})


def game(request):
    return render(request, 'hearthstone/game.html')


def card(request, card_id):
    card = get_object_or_404(Card, pk=card_id)
    return render(request, 'hearthstone/card.html', {'card': card})


def buyCards(request):
    cardCounter = Card.objects.all().count()
    cards = []
    if request.user.is_authenticated and request.user.profile.credit >= 100:
        for i in range(8):
            random_index = randint(0, cardCounter - 1)
            card = Card.objects.all()[random_index]
            cards.append(card)
            cardUser = CardUser(card=card, user=request.user)
            cardUser.save()
        request.user.profile.credit -= 100
        request.user.save()
    elif request.user.is_authenticated and request.user.profile.credit < 100:
        messages.warning(request, f'Vous n\'avez pas assez de crédit :(')
        return redirect('home')
    else:
        messages.warning(request, f'Vous devez être connecté pour accéder à cette page')
        return redirect('home')

    return render(request, 'hearthstone/buy-cards.html', {'cards': cards})


def myCards(request):
    cardsUser = CardUser.objects.all().filter(user_id=request.user.id)
    cards = []

    for cardUser in cardsUser:
        card = cardUser.card
        cards.append(card)

    return render(request, 'hearthstone/my-cards.html', {'cards': cards})


def myDecks(request):
    decks = []

    return render(request, 'hearthstone/my-decks.html', {'decks': decks})
