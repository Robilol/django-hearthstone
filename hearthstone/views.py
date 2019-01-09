from random import randint
from pprint import pprint
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from .forms import UserRegisterForm, DeckForm, TopicCreationForm, MessageCreationForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .models import Card, Deck, Game, Topic, Message, CardsUser, CardsDeck, Profile, Follow
from django.contrib.auth.models import User
from django.db.models import Count


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

    # ajout cartes first co

    if request.user.is_authenticated and request.user.profile.isFirstConnection is True:

        deck = Deck()
        deck.title = 'Deck de base'
        deck.owner = request.user
        deck.save()

        number_of_card = Card.objects.count()
        for i in range(30):
            random_card = Card.objects.all()[randint(0, number_of_card - 1)]
            card, created = CardsUser.objects.get_or_create(user=request.user, card=random_card,
                                                            defaults={'quantity': 1})
            if created:
                card.save()
            else:
                card.quantity += 1
                card.save()

            cardDeck, created = CardsDeck.objects.get_or_create(deck=deck, card=random_card,
                                                                defaults={'quantity': 1})
            if created:
                cardDeck.save()
            else:
                cardDeck.quantity += 1
                cardDeck.save()

        request.user.profile.isFirstConnection = False
        request.user.save()

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
    nb_cards = Card.objects.all().count()
    cards = []
    credit = request.user.profile.credit
    if request.user.is_authenticated and request.user.profile.credit >= 100:

        for i in range(8):
            random_index = randint(0, nb_cards - 1)
            random_card = Card.objects.all()[random_index]

            card, created = CardsUser.objects.get_or_create(user=request.user, card=random_card,
                                                            defaults={'quantity': 1})
            if created:
                card.save()
            else:
                card.quantity += 1
                card.save()

            cards.append(random_card)

        credit -= 100
        request.user.profile.credit = credit
        request.user.save()
    elif request.user.is_authenticated and request.user.profile.credit < 100:
        messages.warning(request, f'Vous n\'avez pas assez de crédit :(')
        return redirect('home')
    else:
        messages.warning(request, f'Vous devez être connecté pour accéder à cette page')
        return redirect('home')

    return render(request, 'hearthstone/buy-cards.html', {'cards': cards})


def follow(request, user_id):
    followed = get_object_or_404(User, pk=user_id)
    Follow.objects.get_or_create(user=request.user, followed=followed)
    messages.success(request, f'Vous commencez à suivre ce joueur')

    return redirect('player', followed.pk)


def unfollow(request, user_id):
    followed = get_object_or_404(User, pk=user_id)
    following = get_object_or_404(Follow, user=request.user.id, followed=followed.id)
    following.delete()
    messages.success(request, f'Vous ne suivez plus ce joueur')

    return redirect('player', followed.pk)


def sellCard(request, card_id):
    card = get_object_or_404(Card, pk=card_id)
    user = request.user
    decksUser = Deck.objects.all().filter(owner=user)
    for deckUser in decksUser:
        for cardsdeck in CardsDeck.objects.all().filter(deck=deckUser):
            if card == cardsdeck.card:
                messages.warning(request, f'Vous ne pouvez pas vendre une carte faisant partie de l\'un de vos Deck')
                return redirect('myCards')

    cardUser = get_object_or_404(CardsUser, user=user, card=card)

    if cardUser.quantity > 1:
        cardUser.quantity -= 1
        cardUser.save()
    else:
        cardUser.delete()

    user.profile.credit += 10
    user.save()
    messages.success(request, f'La carte a bien été vendu, elle vous a rapporté 10 poussières')
    return redirect('myCards')


def myCards(request):
    return render(request, 'hearthstone/my-cards.html', {})


def myDecks(request):
    decksUser = Deck.objects.all().filter(owner=request.user)

    return render(request, 'hearthstone/my-decks.html', {'decks': decksUser})


def deck(request, deck_id):
    deck = get_object_or_404(Deck, pk=deck_id)

    return render(request, 'hearthstone/deck.html', {'deck': deck})


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

        cardsUsed = deck.cardsdeck_set.all()

        cardsUsedId = []

        for card in cardsUsed:
            cardsUsedId.append(card.pk)

        cardsUser = user.cards.all()

        return render(request, 'hearthstone/update-deck.html',
                      {'deck': deck, 'cardsUsed': cardsUsedId})


def playerAll(request):
    players = User.objects.exclude(id=request.user.pk)

    return render(request, 'hearthstone/player-all.html', {'players': players})


def player(request, user_id):
    profile = get_object_or_404(Profile, pk=user_id)

    followeds = Follow.objects.all().filter(user=request.user)
    show_follow_button = 1
    for followed in followeds:
        if followed.followed_id == user_id:
            show_follow_button = 0

    return render(request, 'hearthstone/player.html', {'profile': profile, 'player_connected': request.user, 'show_follow_button': show_follow_button})


def forum(request):
    topics = Topic.objects.order_by('-created_at').annotate(number_of_messages=Count('message'))

    context = {
        'topics': topics,
    }

    return render(request, 'forum/index.html', context)


def createTopic(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TopicCreationForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            topic = form.save(commit=False)
            topic.author = request.user
            topic.save()
            messages.success(request, f'Votre sujet a bien été créé !')
            return redirect('topic', topic_id=topic.id)
    else:
        form = TopicCreationForm()
    return render(request, 'forum/create.html', {'form': form})


def topic(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = MessageCreationForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.author = request.user
            new_message.topic = topic
            new_message.save()
            messages.success(request, f'Votre message a bien été ajouté au sujet !')
    else:
        form = MessageCreationForm()

    msgs = Message.objects.all().filter(topic=topic)

    context = {
        'topic': topic,
        'msgs': msgs,
        'form': form,
    }

    return render(request, 'forum/topic.html', context)
