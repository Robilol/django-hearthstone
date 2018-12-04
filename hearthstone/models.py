from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credit = models.IntegerField(default=200)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Card(models.Model):
    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, null=True, blank=True)
    cost = models.IntegerField(default=1)
    health = models.IntegerField(default=1)
    damage = models.IntegerField(default=1)
    owner = models.ManyToManyField(User, related_name="cards")

    def __str__(self):
        return self.title


class Deck(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='decks')
    title = models.CharField(max_length=100)
    cards = models.ManyToManyField(Card, related_name="decks")

    def __str__(self):
        return self.title


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
