from datetime import date

from flix.domain.model import User, Movie, Genre, make_comment, make_genre_association, ModelException

import pytest


@pytest.fixture()
def movie():
    return Movie(None, 2016, 18)


@pytest.fixture()
def user():
    return User('dbowie', '1234567890')


@pytest.fixture()
def genre():
    return Genre('Action')


def test_user_construction(user):
    assert User is not None

    for comment in user.comments:
        # User should have an empty list of Comments after construction.
        assert False


def test_movie_construction(movie):
    assert movie.year == 2016
    assert movie is not None


    assert repr(
        movie) == '<Movie None, 2016>'


def test_movie_less_than_operator():
    movie_1 = Movie(None, 2016, None)

    movie_2 = Movie(None, 2019, None)

    assert movie_1 < movie_2


def test_genre_construction(genre):
    assert genre.genre_name == 'Action'

    for movie in genre.genre_asso_movies:
        assert False

    assert not genre.is_applied_to(Movie(None, None, None))


def test_make_comment_establishes_relationships(movie, user):
    comment_text = 'A nice movie!'
    comment = make_comment(comment_text, user, movie)

    # Check that the User object knows about the Comment.
    assert comment in user.comments

    # Check that the Comment knows about the User.
    assert comment.user is user

    # Check that Movie knows about the Comment.
    assert comment in movie.comments

    # Check that the Comment knows about the Movie.
    assert comment.movie is movie


def test_make_genre_associations(movie, genre):
    make_genre_association(movie, genre)

    # check that the Genre knows about the Movie.
    assert genre.is_applied_to(movie)
    assert movie in genre.genre_asso_movies


def test_make_genre_associations_with_movie_already_genre_asso(movie, genre):
    make_genre_association(movie, genre)

    with pytest.raises(ModelException):
        make_genre_association(movie, genre)
