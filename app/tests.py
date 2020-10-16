from django.db import transaction, IntegrityError
from django.test import TestCase
from faker import Faker
from django.test import Client

from app.models import Actor, Movie
from app.utils import remove_accents

fake = Faker()
client = Client()


class TestMovieModel(TestCase):
    def test_movie(self):
        self.assertEqual(Movie.objects.all().count(), 0)

        url = fake.url()
        movie = Movie.objects.create(name=fake.name(), url=url)

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Movie.objects.create(url=url)

        self.assertEqual(Movie.objects.all().count(), 1)
        self.assertEqual(Movie.objects.all().get().name, movie.name)

    def test_actor(self):
        self.assertEqual(Actor.objects.all().count(), 0)

        url = fake.url()
        actor = Actor.objects.create(name=fake.name(), url=url)

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Actor.objects.create(url=url)

        self.assertEqual(Actor.objects.all().count(), 1)
        self.assertEqual(Actor.objects.all().get().name, actor.name)

    def test_movie_has_actors(self):
        movie = Movie.objects.create(name=fake.name())
        actor = Actor.objects.create(name=fake.name())

        movie.actors.add(actor)
        movie.save()

        self.assertEqual(movie.actors.all().count(), 1)
        self.assertEqual(Movie.objects.filter(actors__id=actor.id).count(), 1)

        with self.assertRaises(TypeError):
            movie.actors.add(Movie.objects.create(name=fake.name()))


class TestSearch(TestCase):
    def setUp(self):
        actor1 = Actor.objects.create(name="Morgan Freeman")
        actor2 = Actor.objects.create(name="Mojmír Podržtužka")
        actor2.name_unaccent = remove_accents(actor2.name)
        actor2.save()

        movie1 = Movie.objects.create(name="Finding Nemo")
        movie1.actors.add(actor1)
        movie1.save()

        movie2 = Movie.objects.create(name="Návštěvníci")
        movie2.name_unaccent = remove_accents(movie2.name)
        movie2.actors.add(actor1, actor2)
        movie2.save()

    def testNoQuery(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No movies match your search")
        self.assertContains(response, "No actors match your search")

    def testQuery(self):
        response = client.get("/?q=mo")
        self.assertEqual(response.status_code, 200)
        for item in ("Morgan Freeman", "Mojmír Podržtužka", "Finding Nemo"):
            self.assertContains(response, item)

        for item in ("Návštěvníci", "No movies match your search", "No actors match your search"):
            self.assertNotIn(item, response)

    def testAccent(self):
        response = client.get("/?q=podržtužka")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mojmír Podržtužka")

        response = client.get("/?q=podrztuzka")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mojmír Podržtužka")


class TestDetail(TestCase):
    def setUp(self):
        actor1 = Actor.objects.create(name="Morgan Freeman")
        actor2 = Actor.objects.create(name="Emma Watson")

        movie1 = Movie.objects.create(name="Finding Nemo")
        movie1.actors.add(actor1)
        movie1.save()

        movie2 = Movie.objects.create(name="Arrival")
        movie2.actors.add(actor1, actor2)
        movie2.save()

    def testMovieDetail(self):
        movie = Movie.objects.get(name="Arrival")

        response = client.get(movie.get_movie_url(), follow=True)
        self.assertEqual(response.status_code, 200)

        for item in ("Morgan Freeman", "Emma Watson"):
            self.assertContains(response, item)
            self.assertContains(response, Actor.objects.get(name=item).get_actor_url())

        self.assertContains(response, "Arrival")

    def testActorDetail(self):
        actor = Actor.objects.get(name="Emma Watson")

        response = client.get(actor.get_actor_url(), follor=True)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Arrival")
        self.assertContains(response, Movie.objects.get(name="Arrival").get_movie_url())
        self.assertNotIn("Finding Nemo", response)