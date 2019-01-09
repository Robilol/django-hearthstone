from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register', views.register, name='register'),
    path('login', auth_views.LoginView.as_view(template_name='registration/login.html'), name='app_login'),
    path('logout', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='app_logout'),
    path('change-password', views.changePassword, name='changePassword'),

    path('game', views.game, name='game'),

    path('card/<int:card_id>', views.card, name='card'),
    path('sell-card/<int:card_id>', views.sellCard, name='sellCard'),
    path('buy-cards', views.buyCards, name='buyCards'),
    path('my-cards', views.myCards, name='myCards'),
    path('my-decks', views.myDecks, name='myDecks'),

    path('deck/<int:deck_id>', views.deck, name='deck'),
    path('deck/delete/<int:deck_id>', views.deleteDeck, name='deckDelete'),
    path('deck/update/<int:deck_id>', views.updateDeck, name='deckUpdate'),
    path('deck/create', views.createDeck, name='deckCreate'),

    path('player/all', views.playerAll, name='playerAll'),
    path('player/<int:user_id>', views.player, name='player'),

    path('follow/<int:user_id>', views.follow, name='follow'),
    path('unfollow/<int:user_id>', views.unfollow, name='unfollow'),

    path('forum', views.forum, name='forum'),
    path('create-topic', views.createTopic, name='createTopic'),
    path('topic/<int:topic_id>', views.topic, name='topic'),
]
