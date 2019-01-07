from django import forms
from django.contrib.auth.models import User
from hearthstone.models import Deck, Topic, Message
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.shortcuts import render, redirect, get_object_or_404


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class DeckForm(ModelForm):
    title = forms.CharField()

    class Meta:
        model = Deck
        fields = ['title']


class TopicCreationForm(ModelForm):
    class Meta:
        model = Topic
        fields = ['title', 'content']


class MessageCreationForm(ModelForm):
    content = forms.CharField(label="Message")

    class Meta:
        model = Message
        fields = ['content']
