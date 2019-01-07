from random import randint
from pprint import pprint
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from .forms import UserRegisterForm
from .forms import DeckForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .models import Card, Deck, Game
from django.contrib.auth.models import User


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

    if request.user.is_authenticated and request.user.profile.isFirstConnection is True:

        user = request.user
        # Ajouts cartes

        allCards = Card.objects.all()

        deck = Deck()
        deck.title = 'Deck de base'
        deck.owner = user
        deck.save()

        # card = get_object_or_404(Card, pk=cardId)

        for i in range(0, 30):
            card = allCards[randint(0, allCards.count() - 1)]
            user.cards.add(card)
            deck.cards.add(card)

        user.profile.isFirstConnection = False
        user.save()

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


def changePassword(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Votre mot de passe a bien été changé !')
            return redirect('changePassword')
        else:
            messages.error(request, 'Merci de corriger les erreurs ci-dessous')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change-password.html', {
        'form': form
    })


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

            user = request.user
            user.cards.add(card)

        request.user.profile.credit -= 100
        request.user.save()
    elif request.user.is_authenticated and request.user.profile.credit < 100:
        messages.warning(request, f'Vous n\'avez pas assez de crédit :(')
        return redirect('home')
    else:
        messages.warning(request, f'Vous devez être connecté pour accéder à cette page')
        return redirect('home')

    return render(request, 'hearthstone/buy-cards.html', {'cards': cards})


def sellCard(request, card_id):
    card = get_object_or_404(Card, pk=card_id)
    user = request.user
    decksUser = Deck.objects.all().filter(owner=user)
    for deckUser in decksUser:
        cardsDeck = deckUser.cards.all()
        for cardDeck in cardsDeck:
            if card == cardDeck:
                messages.warning(request, f'Vous ne pouvez pas vendre une carte faisant partie de l\'un de vos Deck')
                return redirect('myCards')

    user.cards.remove(card)
    user.profile.credit += 10
    user.save()
    messages.success(request, f'La carte a bien été vendu, elle vous a rapporté 10 poussières')
    return redirect('myCards')


def myCards(request):
    user = request.user
    cards = user.cards.all()

    return render(request, 'hearthstone/my-cards.html', {'cards': cards})


def myDecks(request):
    decksUser = Deck.objects.all().filter(owner=request.user)

    return render(request, 'hearthstone/my-decks.html', {'decks': decksUser})


def deck(request, deck_id):
    deck = get_object_or_404(Deck, pk=deck_id)

    cards = deck.cards.all()

    return render(request, 'hearthstone/deck.html', {'cards': cards, 'deck': deck})


def createDeck(request):
    if request.POST:
        form = DeckForm(request.POST)
        if form.is_valid():
            deck = Deck()
            deck = form.save(commit=False)
            deck.owner = request.user
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

        cardsDeck = deck.cards.all()

        for cardDeck in cardsDeck:
            deck.cards.remove(cardDeck)

        for key, value in cards:
            if key[:4] == 'card':
                cardId = key.split('_')[1]

                card = get_object_or_404(Card, pk=cardId)

                deck.cards.add(card)

        return redirect('deck', deck.pk)
    else:
        deck = get_object_or_404(Deck, pk=deck_id)

        user = request.user

        cardsUsed = deck.cards.all()

        cardsUsedId = []

        for card in cardsUsed:
            cardsUsedId.append(card.pk)

        cardsUser = user.cards.all()

        return render(request, 'hearthstone/update-deck.html',
                      {'cards': cardsUser, 'deck': deck, 'cardsUsed': cardsUsedId})


def playerAll(request):
    players = User.objects.all()

    return render(request, 'hearthstone/player-all.html', {'players': players})


def player(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    decks = user.decks.all()

    return render(request, 'hearthstone/player.html', {'player': user, 'decks': decks})
