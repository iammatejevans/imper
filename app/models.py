from django.db import models
from django.urls import reverse


class Actor(models.Model):
    name = models.CharField(max_length=255)
    name_unaccent = models.CharField(max_length=255)
    url = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    def get_actor_url(self):
        return reverse('actor_view', kwargs={'actor_id': self.id})


class Movie(models.Model):
    name = models.CharField(max_length=255)
    name_unaccent = models.CharField(max_length=255)
    url = models.CharField(max_length=255, unique=True)
    actors = models.ManyToManyField(Actor)

    def __str__(self):
        return self.name

    def get_movie_url(self):
        return reverse('movie_view', kwargs={'movie_id': self.id})
