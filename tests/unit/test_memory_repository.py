from datetime import date, datetime
from typing import List

import pytest

from flix.domain.model import User, Movie, Genre, Comment, make_comment
from flix.adapters.repository import RepositoryException


def test_repository_can_add_a_user(in_memory_repo):
    user = User('Dave', '123456789')
    in_memory_repo.add_user(user)

    assert in_memory_repo.get_user('Dave') is user


def test_repository_can_retrieve_a_user(in_memory_repo):
    user = in_memory_repo.get_user('fmercury')
    assert user == User('fmercury', '8734gfe2058v')


def test_repository_does_not_retrieve_a_non_existent_user(in_memory_repo):
    user = in_memory_repo.get_user('prince')
    assert user is None


def test_repository_can_retrieve_movie_count(in_memory_repo):
    number_of_movies = in_memory_repo.get_number_of_movies()

    # Check that the query returned 6 Movies.
    assert number_of_movies == 10


def test_repository_can_add_movie(in_memory_repo):
    movie = Movie('Wild Goose Lake',2019, 11)
    in_memory_repo.add_movie(movie)

    assert in_memory_repo.get_movie(11) is movie


def test_repository_can_retrieve_movie(in_memory_repo):
    movie = in_memory_repo.get_movie(1)

    # Check that the Movie has the expected title.
    assert movie.title == 'Guardians of the Galaxy'

    # Check that the Movie is commented as expected.
    comment_one = [comment for comment in movie.comments if comment.comment == 'This movie is okay.'][
        0]
    comment_two = [comment for comment in movie.comments if comment.comment == 'Yeah Freddie, it is good.'][0]

    assert comment_one.user.username == 'fmercury'
    assert comment_two.user.username == "thorke"

    # Check that the Movie is tagged as expected.
    assert movie.is_of_genre(Genre('Action'))
    assert movie.is_of_genre(Genre('Adventure'))
    assert movie.is_of_genre(Genre('Sci-Fi'))


def test_repository_does_not_retrieve_a_non_existent_movie(in_memory_repo):
    movie = in_memory_repo.get_movie(1011)
    assert movie is None


def test_repository_can_retrieve_movies_by_year(in_memory_repo):
    movies = in_memory_repo.get_movies_by_year(2014)

    # Check that the query returned 3 Movies.
    assert len(movies) == 1


def test_repository_does_not_retrieve_an_movie_when_there_are_no_movies_for_a_given_year(in_memory_repo):
    movies = in_memory_repo.get_movies_by_year(2020)
    assert len(movies) == 0

def test_repository_does_not_retrieve_an_movie_when_there_are_no_movies_for_a_given_actor(in_memory_repo):
    movies = in_memory_repo.get_movie_ranks_for_actor('John Doe')
    assert len(movies) == 0

def test_repository_does_not_retrieve_an_movie_when_there_are_no_movies_for_a_given_director(in_memory_repo):
    movies = in_memory_repo.get_movie_ranks_for_director('Jane Doe')
    assert len(movies) == 0

def test_repository_can_retrieve_movies_for_a_given_actor(in_memory_repo):
    movies = in_memory_repo.get_movie_ranks_for_actor('Vin Diesel')
    assert len(movies) == 1

def test_repository_can_retrieve_movies_for_a_given_director(in_memory_repo):
    movies = in_memory_repo.get_movie_ranks_for_director('Yimou Zhang')
    assert len(movies) == 1

def test_repository_can_retrieve_movies_for_a_given_genre(in_memory_repo):
    movies = in_memory_repo.get_movie_ranks_for_genre('Thriller')
    assert len(movies) == 1

def test_repository_does_not_retrieve_an_movie_when_there_are_no_movies_for_a_given_genre(in_memory_repo):
    movies = in_memory_repo.get_movie_ranks_for_genre('Politics')
    assert len(movies) == 0

def test_repository_can_retrieve_genres(in_memory_repo):
    genres: List[Genre] = in_memory_repo.get_genres()

    assert len(genres) == 14

    tag_one = [genre for genre in genres if genre.genre_name == 'Sci-Fi'][0]
    tag_two = [genre for genre in genres if genre.genre_name == 'Adventure'][0]
    tag_three = [genre for genre in genres if genre.genre_name == 'Comedy'][0]
    tag_four = [genre for genre in genres if genre.genre_name == 'Thriller'][0]

    assert tag_one.number_of_tagged_movies == 2
    assert tag_two.number_of_tagged_movies == 6
    assert tag_three.number_of_tagged_movies == 3
    assert tag_four.number_of_tagged_movies == 1


def test_repository_can_get_first_movie(in_memory_repo):
    movie = in_memory_repo.get_first_movie()
    assert movie.title == 'Guardians of the Galaxy'


def test_repository_can_get_last_movie(in_memory_repo):
    movie = in_memory_repo.get_last_movie()
    for m in in_memory_repo.get_movies():
        print(m)
    assert movie.title == 'Passengers'


def test_repository_can_get_movies_by_ranks(in_memory_repo):
    movies = in_memory_repo.get_movies_by_rank([2, 5, 6])

    assert len(movies) == 3
    assert movies[0].title == 'Prometheus'
    assert movies[1].title == "Suicide Squad"
    assert movies[2].title == 'The Great Wall'


def test_repository_does_not_retrieve_movie_for_non_existent_id(in_memory_repo):
    movies = in_memory_repo.get_movies_by_rank([2, 17])

    assert len(movies) == 1
    assert movies[0].title == 'Prometheus'


def test_repository_returns_an_empty_list_for_non_existent_ids(in_memory_repo):
    movies = in_memory_repo.get_movies_by_rank([0, 21])

    assert len(movies) == 0


def test_repository_returns_movie_ids_for_existing_tag(in_memory_repo):
    movie_ids = in_memory_repo.get_movie_ranks_for_genre('Sci-Fi')

    assert movie_ids == [1, 2]


def test_repository_returns_an_empty_list_for_non_existent_tag(in_memory_repo):
    movie_ids = in_memory_repo.get_movie_ranks_for_genre('United States')

    assert len(movie_ids) == 0


def test_repository_returns_year_of_previous_movie(in_memory_repo):
    movie = in_memory_repo.get_movie(3)
    previous_year = in_memory_repo.get_year_of_previous_movie(movie)

    assert previous_year == 2012


def test_repository_returns_none_when_there_are_no_previous_movies(in_memory_repo):
    movie = in_memory_repo.get_movie(1)
    previous_year = in_memory_repo.get_year_of_previous_movie(movie)

    assert previous_year is None


def test_repository_returns_year_of_next_movie(in_memory_repo):
    movie = in_memory_repo.get_movie(2)
    next_year = in_memory_repo.get_year_of_next_movie(movie)

    assert next_year == 2016


def test_repository_returns_none_when_there_are_no_subsequent_movies(in_memory_repo):
    movie = in_memory_repo.get_movie(6)
    next_year = in_memory_repo.get_year_of_next_movie(movie)

    assert next_year is None


def test_repository_can_add_a_tag(in_memory_repo):
    genre = Genre('Motoring')
    in_memory_repo.add_genre(genre)

    assert genre in in_memory_repo.get_genres()


def test_repository_can_add_a_comment(in_memory_repo):
    user = in_memory_repo.get_user('thorke')
    movie = in_memory_repo.get_movie(2)
    comment = make_comment("Trump's onto it!", user, movie)

    in_memory_repo.add_comment(comment)

    assert comment in in_memory_repo.get_comments()


def test_repository_does_not_add_a_comment_without_a_user(in_memory_repo):
    movie = in_memory_repo.get_movie(2)
    comment = Comment(None, movie, "Trump's onto it!", datetime.today())

    with pytest.raises(RepositoryException):
        in_memory_repo.add_comment(comment)


def test_repository_does_not_add_a_comment_without_an_movie_properly_attached(in_memory_repo):
    user = in_memory_repo.get_user('thorke')
    movie = in_memory_repo.get_movie(2)
    comment = Comment(None, movie, "Trump's onto it!", datetime.today())

    user.add_comment(comment)

    with pytest.raises(RepositoryException):
        # Exception expected because the Movie doesn't refer to the Comment.
        in_memory_repo.add_comment(comment)


def test_repository_can_retrieve_comments(in_memory_repo):
    assert len(in_memory_repo.get_comments()) == 3



