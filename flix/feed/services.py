from typing import List, Iterable
import requests
from flix.adapters.repository import AbstractRepository
from flix.domain.model import Movie, Actor, User, Review, Director, Genre, Comment, make_genre_association, make_comment


class NonExistentMovieException(Exception):
    pass


class UnknownUserException(Exception):
    pass


def add_comment(movie_rank: int, comment_text: str, username: str, repo: AbstractRepository):
    # Check that the movie exists.
    movie = repo.get_movie(movie_rank)
    if movie is None:
        raise NonExistentMovieException

    user = repo.get_user(username)
    if user is None:
        user = User("Guest account", "Abcd1234")

    # Create comment.
    comment = make_comment(comment_text, user, movie)

    # Update the repository.
    repo.add_comment(comment)


def get_movie(movie_rank: int, repo: AbstractRepository):
    movie = repo.get_movie(movie_rank)

    if movie is None:
        raise NonExistentMovieException

    return movie_to_dict(movie, repo)


def get_first_movie(repo: AbstractRepository):

    movie = repo.get_first_movie()

    return movie_to_dict(movie, repo)


def get_last_movie(repo: AbstractRepository):

    movie = repo.get_last_movie()
    return movie_to_dict(movie, repo)


def get_movies_by_year(date, repo: AbstractRepository):
    # Returns movies for the target date (empty if no matches), the date of the previous movie (might be null), the date of the next movie (might be null)

    movies = repo.get_movies_by_year(target_year=date)

    movies_dto = list()
    prev_year = next_year = None

    if len(movies) > 0:
        prev_year = repo.get_year_of_previous_movie(movies[0])
        next_year = repo.get_year_of_next_movie(movies[0])

        # Convert Movies to dictionary form.
        movies_dto = movies_to_dict(movies, repo)

    return movies_dto, prev_year, next_year


def get_movie_ranks_for_genre(genre_name, repo: AbstractRepository):
    movie_ranks = repo.get_movie_ranks_for_genre(genre_name)

    return movie_ranks

def get_movie_ranks_for_actor(actor_name, repo: AbstractRepository):
    movie_ranks = repo.get_movie_ranks_for_actor(actor_name)

    return movie_ranks

def get_movie_ranks_for_director(director_name, repo: AbstractRepository):
    movie_ranks = repo.get_movie_ranks_for_director(director_name)

    return movie_ranks


def get_movie_ranks_for_year(tgt_year, repo: AbstractRepository):
    movie_ranks = repo.get_movie_ranks_for_year(tgt_year)

    return movie_ranks


def get_movies_by_rank(rank_list, repo: AbstractRepository):
    movies = repo.get_movies_by_rank(rank_list)

    # Convert Movies to dictionary form.
    movies_as_dict = movies_to_dict(movies, repo)

    return movies_as_dict


def get_comments_for_movie(movie_rank, repo: AbstractRepository):
    movie = repo.get_movie(movie_rank)

    if movie is None:
        raise NonExistentMovieException

    return comments_to_dict(movie.comments)


# ============================================
# Functions to convert model entities to dicts
# ============================================

def movie_to_dict(movie: Movie, repo: AbstractRepository):
    '''actors = movie.actors[0]
    for i in movie.actors[1:]:
        actors += ","
        actors += str(i)'''
    actors = movie.actors

    movie_detail = requests.get(f"http://omdbapi.com?t={movie.title}&apikey=47f211b2").text
    #print(movie_detail)
    try:
        img_link = movie_detail.split('","')[13].split('":"')[1]
    except:
        img_link = "static/movie.png"
    movie.image_hyperlink = img_link
    try:
        d = movie.director.director_full_name
        director = movie.director
    except:
        director = Director(movie.director)
    try:
        genres = movie.genres.split(',')
    except:
        genres = movie.genres

    movie_dict = {
        'rank': movie.rank,
        'date': movie.date,
        'title': movie.title,
        'first_para': movie.description,
        'hyperlink': movie.hyperlink,
        'image_hyperlink': movie.image_hyperlink,
        'comments': comments_to_dict(movie.comments),
        'genres': genres_to_dict(genres, repo),
        'rating': movie.rating,
        'votes': movie.votes,
        'metascore': movie.metascore,
        'director': director,
        'actors': actors,
        'runtime_minutes': movie.runtime_minutes,
        'revenue': movie.revenue
    }
    return movie_dict


def movies_to_dict(movies: Iterable[Movie], repo:AbstractRepository):
    return [movie_to_dict(movie, repo) for movie in movies]


def comment_to_dict(comment: Comment):
    comment_dict = {
        'username': comment.user.username,
        'movie_rank': comment.movie.rank,
        'comment_text': comment.comment,
        'timestamp': comment.timestamp
    }
    return comment_dict


def comments_to_dict(comments: Iterable[Comment]):
    return [comment_to_dict(comment) for comment in comments]


def genre_to_dict(genre: Genre, repo: AbstractRepository):
    genre_dict = {
        'name': genre,
        'genre_asso_movies': [movie.rank for movie in repo.get_movies() if genre in movie.genres]
    }
    return genre_dict

def director_to_dict(director: Director):
    director_dict = {
        'name': director.director_full_name,
        'director_asso_movies': [movie.rank for movie in director.director_asso_movies]
    }
    return director_dict

def actor_to_dict(actor: Actor):
    actor_dict = {
        'name': actor,
        'actor_asso_movies': [movie.rank for movie in actor.actor_asso_movies]
    }
    return actor_dict


def genres_to_dict(genres: Iterable[Genre], repo:AbstractRepository):
    return [genre_to_dict(genre, repo) for genre in genres]

def directors_to_dict(directors: Iterable[Director]):
    return [director_to_dict(director) for director in directors]

def actors_to_dict(actors: Iterable[Actor]):
    return [actor_to_dict(actor) for actor in actors]

# ============================================
# Functions to convert dicts to model entities
# ============================================

def dict_to_movie(dict):
    movie = Movie(dict.rank, dict.date, dict.title, dict.first_para, dict.hyperlink)
    # Note there's no comments or genres.
    return movie

def set_rating(movie_id: int, rating: int, username: str, repo: AbstractRepository):
    user = repo.get_user(username)
    if user is None:
        user = User('Guest account', 'defaultpass')

    movie = repo.get_movie(movie_id)
    if movie is None:
        raise NonExistentMovieException

    repo.set_rating(rating, user, movie)

