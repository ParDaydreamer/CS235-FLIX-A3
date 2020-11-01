from typing import Iterable
import random
import requests

from flix.adapters.repository import AbstractRepository
from flix.domain.model import *


def get_genre_names(repo: AbstractRepository):
    genres = repo.get_genres()
    genre_names = [genre.genre_name for genre in genres]
    return genre_names


def get_year(repo: AbstractRepository):
    years = repo.get_years()
    return years


def get_actor_names(repo: AbstractRepository):
    actors = repo.get_actors()
    actor_names = [actor.actor_full_name for actor in actors]

    return actor_names


def get_director_names(repo: AbstractRepository):
    directors = repo.get_directors()
    director_names = [director.director_full_name for director in directors]

    return director_names




def get_random_movies(quantity, repo: AbstractRepository):
    movie_count = repo.get_number_of_movies()

    if quantity >= movie_count:
        # Reduce the quantity of ids to generate if the repository has an insufficient number of movies.
        quantity = movie_count - 1

    # Pick distinct and random movies.
    random_ranks = random.sample(range(1, movie_count), quantity)
    movies = repo.get_movies_by_rank(random_ranks)

    return movies_to_dict(movies)


# ============================================
# Functions to convert dicts to model entities
# ============================================

def movie_to_dict(movie: Movie):
    movie_detail = requests.get(f"http://omdbapi.com?t={movie.title}&apikey=47f211b2").text
    try:
        img_link = movie_detail.split('","')[13].split('":"')[1]
    except:
        img_link = "static/movie.png"
    movie.image_hyperlink = img_link
    movie_dict = {
        'date': movie.date,
        'title': movie.title,
        'description': movie.description,
        'image_hyperlink': movie.image_hyperlink
    }
    return movie_dict


def movies_to_dict(movies: Iterable[Movie]):
    return [movie_to_dict(movie) for movie in movies]
