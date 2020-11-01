from datetime import date

import pytest

from flix.authentication.services import AuthenticationException
from flix.feed import services as feed_services
from flix.authentication import services as auth_services
from flix.feed.services import NonExistentMovieException
from flix.domain.model import *


def test_can_add_user(in_memory_repo):
    new_username = 'jz'
    new_password = 'abcd1A23'

    auth_services.add_user(new_username, new_password, in_memory_repo)

    user_as_dict = auth_services.get_user(new_username, in_memory_repo)
    assert user_as_dict['username'] == new_username

    # Check that password has been encrypted.
    assert user_as_dict['password'].startswith('pbkdf2:sha256:')


def test_cannot_add_user_with_existing_name(in_memory_repo):
    username = 'thorke'
    password = 'abcd1A23'

    with pytest.raises(auth_services.NameNotUniqueException):
        auth_services.add_user(username, password, in_memory_repo)


def test_authentication_with_valid_credentials(in_memory_repo):
    new_username = 'pmccartney'
    new_password = 'abcd1A23'

    auth_services.add_user(new_username, new_password, in_memory_repo)

    try:
        auth_services.authenticate_user(new_username, new_password, in_memory_repo)
    except AuthenticationException:
        assert False


def test_authentication_with_invalid_credentials(in_memory_repo):
    new_username = 'pmccartney'
    new_password = 'abcd1A23'

    auth_services.add_user(new_username, new_password, in_memory_repo)

    with pytest.raises(auth_services.AuthenticationException):
        auth_services.authenticate_user(new_username, '0987654321', in_memory_repo)


def test_can_add_comment(in_memory_repo):
    movie_rank = 3
    comment_text = 'The loonies are stripping the supermarkets bare!'
    username = 'fmercury'

    # Call the service layer to add the comment.
    feed_services.add_comment(movie_rank, comment_text, username, in_memory_repo)

    # Retrieve the comments for the movie from the repository.
    comments_as_dict = feed_services.get_comments_for_movie(movie_rank, in_memory_repo)

    # Check that the comments include a comment with the new comment text.
    assert next(
        (dictionary['comment_text'] for dictionary in comments_as_dict if dictionary['comment_text'] == comment_text),
        None) is not None


def test_cannot_add_comment_for_non_existent_movie(in_memory_repo):
    movie_rank = 17
    comment_text = "This movie - what's that?"
    username = 'fmercury'

    # Call the service layer to attempt to add the comment.
    with pytest.raises(feed_services.NonExistentMovieException):
        feed_services.add_comment(movie_rank, comment_text, username, in_memory_repo)



def test_can_get_movie(in_memory_repo):
    movie_rank = 2

    movie_as_dict = feed_services.get_movie(movie_rank, in_memory_repo)

    assert movie_as_dict['rank'] == movie_rank
    assert movie_as_dict['date'] == 2012
    assert movie_as_dict['title'] == 'Prometheus'
    assert len(movie_as_dict['comments']) == 0

    genre_names = [dictionary['name'] for dictionary in movie_as_dict['genres']]
    assert Genre('Adventure') in genre_names
    assert Genre('Sci-Fi') in genre_names
    assert Genre('Mystery') in genre_names



def test_cannot_get_movie_with_non_existent_id(in_memory_repo):
    movie_rank = 17

    # Call the service layer to attempt to retrieve the Movie.
    with pytest.raises(feed_services.NonExistentMovieException):
        feed_services.get_movie(movie_rank, in_memory_repo)


def test_get_first_movie(in_memory_repo):
    movie_as_dict = feed_services.get_first_movie(in_memory_repo)

    assert movie_as_dict['rank'] == 1


def test_get_last_movie(in_memory_repo):
    movie_as_dict = feed_services.get_last_movie(in_memory_repo)

    assert movie_as_dict['rank'] == 10


def test_get_movies_by_date(in_memory_repo):
    target_date = 2014

    movies_as_dict, prev_date, next_date = feed_services.get_movies_by_year(target_date, in_memory_repo)

    assert len(movies_as_dict) == 1
    assert movies_as_dict[0]['rank'] == 1

    assert prev_date is None
    assert next_date == 2016





def test_get_movies_by_date_with_non_existent_date(in_memory_repo):
    target_date = 2020

    movies_as_dict, prev_date, next_date = feed_services.get_movies_by_year(target_date, in_memory_repo)

    # Check that there are no movies dated 2020-03-06.
    assert len(movies_as_dict) == 0


def test_get_movies_by_id(in_memory_repo):
    target_movie_ranks = [5, 6, 17, 19]
    movies_as_dict = feed_services.get_movies_by_rank(target_movie_ranks, in_memory_repo)

    # Check that 2 movies were returned from the query.
    assert len(movies_as_dict) == 2

    # Check that the movie ids returned were 5 and 6.
    movie_ranks = [movie['rank'] for movie in movies_as_dict]
    assert set([5, 6]).issubset(movie_ranks)


def test_get_comments_for_movie(in_memory_repo):
    comments_as_dict = feed_services.get_comments_for_movie(1, in_memory_repo)

    # Check that 2 comments were returned for movie with rank 1.
    assert len(comments_as_dict) == 3

    # Check that the comments relate to the movie whose rank is 1.
    movie_ranks = [comment['movie_rank'] for comment in comments_as_dict]
    movie_ranks = set(movie_ranks)
    assert 1 in movie_ranks and len(movie_ranks) == 1


def test_get_comments_for_non_existent_movie(in_memory_repo):
    with pytest.raises(NonExistentMovieException):
        comments_as_dict = feed_services.get_comments_for_movie(17, in_memory_repo)


def test_get_comments_for_movie_without_comments(in_memory_repo):
    comments_as_dict = feed_services.get_comments_for_movie(2, in_memory_repo)
    assert len(comments_as_dict) == 0

