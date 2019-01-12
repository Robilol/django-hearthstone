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
from .models import Card, Deck, Game, Topic, Message, CardsUser, CardsDeck, Profile, Follow, Actu
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models import Q


def home(request):
    title = 'Accueil'
    slugs = [
        'test',
        'tast',
        'tost',
    ]
    context = {
        'title': title,
        'games': Game.objects.all()[10::-1],
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
    if request.POST:
        playerId = request.POST.get("player")
        deckId = request.POST.get('deck')
        playerAdeck = get_object_or_404(Deck, pk=deckId)
        playerBdeck = None
        results = 0

        player = get_object_or_404(User, pk=playerId)

        decks = Deck.objects.all().filter(owner=player)

        for deck in decks:
            count = 0

            cardsDeck = deck.cardsdeck_set.all()

            for cardDeck in cardsDeck:
                count += cardDeck.quantity

            if count == 30:
                playerBdeck = deck

        firstPlayer = randint(0, 1)

        turn = 0
        actions = []

        playerAhp = 30
        playerBhp = 30

        playerAmana = 1
        playerBmana = 1

        playerAcards = playerAdeck.cardsdeck_set.all()
        playerBcards = playerBdeck.cardsdeck_set.all()

        while results == 0:
            turn += 1
            availableCards = []
            playerAcard = None
            playerBcard = None

            # joueur A
            availableCards = [x for x in playerAcards if x.card.cost <= playerAmana]
            availableCards.sort(key=lambda x: x.card.cost, reverse=True)

            if availableCards:
                playerAcard = availableCards[randint(0, len(availableCards) - 1)].card

                actions.append(
                    {playerAcard.slug: request.user.username + " a joué la carte " + playerAcard.title})
            else:
                actions.append({0: request.user.username + " n'a pas assez de mana pour jouer une carte "})

            # joueur B
            availableCards = [x for x in playerBcards if x.card.cost <= playerBmana]
            availableCards.sort(key=lambda x: x.card.cost, reverse=True)

            if availableCards:
                playerBcard = availableCards[randint(0, len(availableCards) - 1)].card

                actions.append({playerBcard.slug: player.username + " a joué la carte " + playerBcard.title})
            else:
                actions.append({0: player.username + " n'a pas assez de mana pour jouer une carte "})

            Acalc = playerAcard.damage + playerAcard.health + playerAcard.cost
            Bcalc = playerBcard.damage + playerBcard.health + playerBcard.cost

            if Acalc > Bcalc:
                playerBhp -= playerAcard.damage
                actions.append({0: player.username + " a perdu " + str(
                    playerAcard.damage) + " points de vie"})
            elif Acalc == Bcalc:
                rand = randint(0, 1)
                if rand == 0:
                    playerBhp -= playerAcard.damage
                    actions.append({0: player.username + " a perdu " + str(
                        playerAcard.damage) + " points de vie"})
                else:
                    playerAhp -= playerBcard.damage
                    actions.append({0: request.user.username + " a perdu " + str(
                        playerBcard.damage) + " points de vie"})
            else:
                playerAhp -= playerBcard.damage
                actions.append({0: request.user.username + " a perdu " + str(
                    playerBcard.damage) + " points de vie"})

            if playerAmana < 9:
                playerAmana += 1
            if playerBmana < 9:
                playerBmana += 1

            if playerAhp <= 0:
                results = -1
                game = Game.objects.create(player=request.user, opponent=player, result=-1, round=turn)

            if playerBhp <= 0:
                results = 1
                game = Game.objects.create(player=request.user, opponent=player, result=1, round=turn)

        return render(request, 'hearthstone/game-results.html',
                      {'game': game, 'actions': actions})

    else:
        allPlayers = Profile.objects.exclude(user=request.user.pk)

        playablePlayers = []

        for player in allPlayers:
            playable = False

            decks = Deck.objects.all().filter(owner=player.user)

            for deck in decks:
                count = 0

                cardsDeck = deck.cardsdeck_set.all()

                for cardDeck in cardsDeck:
                    count += cardDeck.quantity

                if count == 30:
                    playable = True

            if playable:
                playablePlayers.append(player)

        myDecks = Deck.objects.all().filter(owner=request.user)

        playableDecks = []

        for deck in myDecks:
            count = 0
            cardsDeck = deck.cardsdeck_set.all()

            for cardDeck in cardsDeck:
                count += cardDeck.quantity

            if count == 30:
                playableDecks.append(deck)

        return render(request, 'hearthstone/game.html',
                      {'playablePlayers': playablePlayers, 'playableDecks': playableDecks})


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
        cards = request.POST.getlist('cards')

        cardsDeck = deck.cardsdeck_set.all()

        for cardDeck in cardsDeck:
            cardDeck.delete()

        for card_id in cards:
            card = get_object_or_404(Card, pk=card_id)

            cardDeck, created = CardsDeck.objects.get_or_create(deck=deck, card=card,
                                                                defaults={'quantity': 1})
            if created:
                cardDeck.save()
            else:
                cardDeck.quantity += 1
                cardDeck.save()

        return redirect('deck', deck.pk)
    else:
        deck = get_object_or_404(Deck, pk=deck_id)

        cardsUsed = deck.cardsdeck_set.all()

        cardsUsedId = []

        for card in cardsUsed:
            for i in range(card.quantity):
                cardsUsedId.append(card.card.id)

        cardsUsedId = cardsUsedId[::-1]

        return render(request, 'hearthstone/update-deck.html',
                      {'deck': deck, 'cardsUsedId': cardsUsedId})


def playerAll(request):
    players = Profile.objects.exclude(user=request.user.pk)

    follows = Follow.objects.filter(user=request.user.pk)

    followsId = []

    for follow in follows:
        followsId.append(follow.pk)

    return render(request, 'hearthstone/player-all.html', {'players': players, 'followsId': followsId})


def player(request, user_id):
    profile = get_object_or_404(Profile, pk=user_id)

    followeds = Follow.objects.all().filter(user=request.user)
    show_follow_button = 1
    for followed in followeds:
        if followed.followed_id == user_id:
            show_follow_button = 0

    return render(request, 'hearthstone/player.html',
                  {'profile': profile, 'player_connected': request.user, 'show_follow_button': show_follow_button})


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


def actu(request):
    followeds = Follow.objects.filter(user_id=request.user.id)
    actus = []
    for followed in followeds:
        actu_of_friend = Actu.objects.all().filter(user_id=followed.followed_id).filter(
            Q(created_at__gte=followed.created_at) | Q(created_at=None))
        actus.append(actu_of_friend)

    # import pdb; pdb.set_trace()
    return render(request, 'hearthstone/actu.html', {'actus': actus, 'followeds': followeds})
