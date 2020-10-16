from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from app.models import Actor, Movie
from app.utils import remove_accents


def search(request):
    if request.method == "GET":
        query = remove_accents(request.GET.get("q", ""))

        actors = None
        movies = None

        if query:
            actors = Actor.objects.filter(Q(name__icontains=query) | Q(name_unaccent__icontains=query))
            movies = Movie.objects.filter(Q(name__icontains=query) | Q(name_unaccent__icontains=query))

        return render(request, "search.html", {"q": query, "actors": actors, "movies": movies})

    return HttpResponse(status=403)


def actor_view(request, actor_id):
    if request.method == "GET":
        actor = get_object_or_404(Actor, pk=actor_id)
        movies = Movie.objects.filter(actors__id=actor.id)
        return render(request, "actor.html", {"actor": actor, "movies": movies})

    return HttpResponse(status=403)


def movie_view(request, movie_id):
    if request.method == "GET":
        movie = get_object_or_404(Movie, pk=movie_id)
        actors = movie.actors.all()
        return render(request, "movie.html", {"movie": movie, "actors": actors})

    return HttpResponse(status=403)
