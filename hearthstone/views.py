from random import randint
from pprint import pprint
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from .forms import UserRegisterForm
from .forms import DeckForm
from django.contrib import messages

from pprint import pprint

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
    cardUser = CardUser.objects.all().filter(user_id=request.user.id, card_id=card_id).first()
    return render(request, 'hearthstone/card.html', {'card': card, 'cardUser':cardUser})


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

def sellCard(request, carduser_id):
    card = get_object_or_404(CardUser, pk=carduser_id)
    card.delete()
    request.user.profile.credit += 10
    request.user.save()
    return redirect('myCards')


def myCards(request):
    cardsUser = CardUser.objects.all().filter(user_id=request.user.id)
    cards = []

    for cardUser in cardsUser:
        card = cardUser.card
        cards.append(card)

    return render(request, 'hearthstone/my-cards.html', {'cards': cards})


def myDecks(request):
    decksUser = Deck.objects.all().filter(user_id=request.user.id)

    return render(request, 'hearthstone/my-decks.html', {'decks': decksUser})


def deck(request, deck_id):
    deck = get_object_or_404(Deck, pk=deck_id)

    cardsDeck = CardDeck.objects.all().filter(deck_id=deck_id)
    cards = []

    for card in cardsDeck:
        cards.append(card.card)

    return render(request, 'hearthstone/deck.html', {'cards': cards, 'deck': deck})


def createDeck(request):
    if request.POST:
        form = DeckForm(request.POST)
        if form.is_valid():
            deck = Deck()
            deck = form.save(commit=False)
            deck.user = request.user
            deck.save()

            title = form.cleaned_data.get('title')
            messages.success(request, f'Le deck {title} a bien été créé !')

            return redirect('deck', deck.pk)
    else:
        form = DeckForm()
    return render(request, 'hearthstone/create-deck.html', {'form': form})


def deleteDeck(request, deck_id):
    deck = get_object_or_404(Deck, pk=deck_id)

    deck.delete()

    return redirect('myDecks')


def updateDeck(request, deck_id):
    if request.POST:
        deck = get_object_or_404(Deck, pk=deck_id)
        cards = request.POST.items()

        cardDeck = CardDeck.objects.all().filter(deck_id=deck_id)

        for cardDeck in cardDeck:
            cardDeck.delete()

        for key, value in cards:
            if key[:4] == 'card':
                cardId = key.split('_')[1]

                card = get_object_or_404(Card, pk=cardId)

                cardDeck = CardDeck(card=card, deck=deck)
                cardDeck.save()

        return redirect('deck', deck.pk)
    else:
        deck = get_object_or_404(Deck, pk=deck_id)

        cardsUser = CardUser.objects.all().filter(user_id=request.user.id)
        cards = []

        cardsDeck = CardDeck.objects.all().filter(deck_id=deck_id)
        cardsUsed = []

        for card in cardsDeck:
            cardsUsed.append(card.card.pk)

        for cardUser in cardsUser:
            card = cardUser.card
            cards.append(card)

        return render(request, 'hearthstone/update-deck.html', {'cards': cards, 'deck': deck, 'cardsUsed' : cardsUsed})
