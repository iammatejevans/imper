import time

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from bs4 import BeautifulSoup
import requests
from requests.exceptions import ConnectionError

from app.models import Movie, Actor
from app.utils import remove_accents


def actors_for_failed_urls(urls):
    if urls:
        failed_urls = []
        for movie_url, movie in urls:
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0'}
                movie_detail = requests.get(url=movie_url, headers=headers)
                actors_soup = BeautifulSoup(movie_detail.text, 'html.parser')

                for actor in actors_soup.find("h4", text="Hrají:").find_next("span").find_all("a"):
                    actor_name = actor.text
                    actor_name_unaccent = remove_accents(actor_name)
                    actor_url = actor['href']

                    try:
                        actor = Actor.objects.create(name=actor_name, name_unaccent=actor_name_unaccent, url=actor_url)
                    except IntegrityError:
                        actor = Actor.objects.get(name=actor_name, url=actor_url)

                    actor.save()
                    movie.actors.add(actor)
                    movie.save()

            except ConnectionError:
                failed_urls.append(f"https://www.csfd.cz{movie_url}")

        if failed_urls:
            return actors_for_failed_urls(failed_urls)


class Command(BaseCommand):
    help = 'Gets list of top 300 movies on CSFD and its actors'

    def handle(self, *args, **options):
        failed_urls = []

        session = requests.Session()
        session.headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0"}

        movies_page = session.get(url="https://www.csfd.cz/zebricky/nejlepsi-filmy/?show=complete")
        movie_soup = BeautifulSoup(movies_page.text, 'html.parser')

        for movie in movie_soup.find_all(class_="film"):
            movie_name = movie.find("a").text
            movie_name_unaccent = remove_accents(movie_name)
            movie_url = movie.find("a")['href']

            try:
                movie = Movie.objects.create(name=movie_name, name_unaccent=movie_name_unaccent, url=movie_url)
            except IntegrityError:
                movie = Movie.objects.get(name=movie_name, url=movie_url)

            try:
                movie_detail = session.get(url=f"https://www.csfd.cz{movie_url}")
                actors_soup = BeautifulSoup(movie_detail.text, 'html.parser')

                for actor in actors_soup.find("h4", text="Hrají:").find_next("span").find_all("a"):
                    actor_name = actor.text
                    actor_name_unaccent = remove_accents(actor_name)
                    actor_url = actor['href']

                    try:
                        actor = Actor.objects.create(name=actor_name, name_unaccent=actor_name_unaccent, url=actor_url)
                    except IntegrityError:
                        actor = Actor.objects.get(name=actor_name, url=actor_url)

                    actor.save()
                    movie.actors.add(actor)
                    movie.save()

            except ConnectionError:
                failed_urls.append(tuple([f"https://www.csfd.cz{movie_url}", movie]))

        if failed_urls:
            actors_for_failed_urls(failed_urls)
