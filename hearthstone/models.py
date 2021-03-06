from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.shortcuts import render, redirect, get_object_or_404


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credit = models.IntegerField(default=200)
    isFirstConnection = models.BooleanField(default=True)
    elo = models.IntegerField(default=1000)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Deck(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Card(models.Model):
    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, null=True, blank=True)
    cost = models.IntegerField(default=1)
    health = models.IntegerField(default=1)
    damage = models.IntegerField(default=1)
    deck = models.ManyToManyField(Deck, related_name="deck", through='CardsDeck')
    owner = models.ManyToManyField(User, related_name="cards", through='CardsUser')

    def __str__(self):
        return self.title


class CardsUser(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.IntegerField()


class CardsDeck(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    quantity = models.IntegerField()


@receiver(pre_save, sender=Card)
def slugify(sender, instance, *args, **kwargs):
    instance.slug = instance.title \
        .replace(' ', '-') \
        .replace('\'', '-') \
        .replace(',', '-') \
        .replace('!', '-') \
        .replace('-', '-')
    instance.slug = instance.slug.replace('__', '_')
    instance.slug = instance.slug.rstrip('_')


class Topic(models.Model):
    title = models.CharField(max_length=150)
    content = models.CharField(max_length=2000)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.title


@receiver(post_save, sender=Topic)
def actu_from_topic(sender, instance, **kwargs):
    user = get_object_or_404(User, pk=instance.author_id)
    Actu.objects.create(user=user,
                        content='Votre ami ' + user.username + ' a créer un topic sur le forum: ' + instance.title)


class Message(models.Model):
    content = models.CharField(max_length=1000)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)

    def __str__(self):
        return self.content


@receiver(post_save, sender=Message)
def actu_from_message(sender, instance, **kwargs):
    user = get_object_or_404(User, pk=instance.author_id)
    topic = get_object_or_404(Topic, pk=instance.topic_id)
    Actu.objects.create(user=user, content='Votre ami ' + user.username + ' a répondu au topic: ' + topic.title)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follow_user')
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed')
    created_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.content


@receiver(post_save, sender=Follow)
def actu_from_following(sender, instance, **kwargs):
    user = get_object_or_404(User, pk=instance.user_id)
    followed = get_object_or_404(User, pk=instance.followed_id)
    Actu.objects.create(user=user, content='Votre ami ' + user.username + ' a commencé à suivre: ' + followed.username)


@receiver(post_delete, sender=Follow)
def actu_from_unfollowing(sender, instance, **kwargs):
    user = get_object_or_404(User, pk=instance.user_id)
    followed = get_object_or_404(User, pk=instance.followed_id)
    Actu.objects.create(user=user, content='Votre ami ' + user.username + ' a arrêté de suivre: ' + followed.username)


class Actu(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actu_user')
    content = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.content


class Game(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player')
    opponent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='opponent')
    round = models.IntegerField(null=False, blank=True)
    result = models.IntegerField(null=False, blank=True)  # 1 player1 |  -1 player2
    date = models.DateTimeField(default=timezone.now)

@receiver(post_save, sender=Game)
def actu_from_game(sender, instance, **kwargs):
    user = get_object_or_404(User, pk=instance.player_id)
    opponent = get_object_or_404(User, pk=instance.opponent_id)
    if (instance.result == 1):
        Actu.objects.create(user=user, content='Votre ami ' + user.username + ' a gagné son match contre: ' + opponent.username)
    else:
        Actu.objects.create(user=user, content='Votre ami ' + user.username + ' a perdu son match contre: ' + opponent.username)
    if (instance.result == 1):
        Actu.objects.create(user=opponent, content='Votre ami ' + opponent.username + ' a perdu son match contre: ' + user.username)
    else:
        Actu.objects.create(user=opponent, content='Votre ami ' + opponent.username + ' a gagné son match contre: ' + user.username)


class ExchangeCard(models.Model):
    card1 = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='exchange_card1', null=True)
    card2 = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='exchange_card2')
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exchange_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exchange_user2')
    user1_status = models.IntegerField(null=True)
    user2_status = models.IntegerField(null=True)
    exchange_status = models.IntegerField(null=True)

    def __str__(self):
        return self.content
