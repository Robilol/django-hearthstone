from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


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


class Game(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player_one')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player_two')
    winner = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.winner.username


class Topic(models.Model):
    title = models.CharField(max_length=150)
    content = models.CharField(max_length=2000)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.title


class Message(models.Model):
    content = models.CharField(max_length=1000)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)

    def __str__(self):
        return self.content


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follow_user')
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed')

    def __str__(self):
        return self.content


class Actu(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actu_user')
    content = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.content
