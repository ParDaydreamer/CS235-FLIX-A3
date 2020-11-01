import abc
from typing import List
from datetime import date

from flix.domain.model import *


repo_instance = None


class RepositoryException(Exception):

    def __init__(self, message=None):
        self.message = message


class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def add_user(self, user: User):
        """" Adds a User to the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_user(self, username) -> User:
        """ Returns the User named username from the repository.

        If there is no User with the given username, this method returns None.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_movie(self, movie: Movie):
        """ Adds an Movie to the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_movie(self, rank: int) -> Movie:
        """ Returns Movie with rank from the repository.

        If there is no Movie with the given rank, this method returns None.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_movies_by_year(self, target_year: int) -> List[Movie]:
        """ Returns a list of Movies that were published on target_year.

        If there are no Movies on the given date, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_number_of_movies(self):
        """ Returns the number of Movies in the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_first_movie(self) -> Movie:
        """ Returns the first Movie, ordered by date, from the repository.

        Returns None if the repository is empty.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_last_movie(self) -> Movie:
        """ Returns the last Movie, ordered by date, from the repository.

        Returns None if the repository is empty.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_movies_by_rank(self, rank_list):
        """ Returns a list of Movies, whose ranks match those in rank_list, from the repository.

        If there are no matches, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_movie_ranks_for_genre(self, genre_name: str):
        """ Returns a list of ranks representing Movies that are genre_asso by genre_name.

        If there are Movies that are genre_asso by genre_name, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_year_of_previous_movie(self, movie: Movie):
        """ Returns the date of an Movie that immediately precedes movie.

        If movie is the first Movie in the repository, this method returns None because there are no Movies
        on a previous date.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_year_of_next_movie(self, movie: Movie):
        """ Returns the date of an Movie that immediately follows movie.

        If movie is the last Movie in the repository, this method returns None because there are no Movies
        on a later date.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_genre(self, genre: Genre):
        """ Adds a Genre to the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_genres(self) -> List[Genre]:
        """ Returns the Genres stored in the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_directors(self) -> List[Director]:
        """ Returns the directors stored in the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_actors(self) -> List[Actor]:
        """ Returns the actors stored in the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def add_comment(self, comment: Comment):
        """ Adds a Comment to the repository.

        If the Comment doesn't have bidirectional links with an Movie and a User, this method raises a
        RepositoryException and doesn't update the repository.
        """
        if comment.user is None or comment not in comment.user.comments:
            raise RepositoryException('Comment not correctly attached to a User')
        if comment.movie is None or comment not in comment.movie.comments:
            raise RepositoryException('Comment not correctly attached to an Movie')

    @abc.abstractmethod
    def get_comments(self):
        """ Returns the Comments stored in the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def set_rating(self, rating:int, user:User, movie:Movie):
        raise NotImplementedError

    def get_movie_ranks_for_year(self, year):
        raise NotImplementedError

    def get_years(self):
        raise NotImplementedError

    def get_movie_ranks_for_director(self, director):
        raise NotImplementedError

    def get_movie_ranks_for_actor(self, actor):
        raise NotImplementedError

    @abc.abstractmethod
    def get_movies(self) -> List[Movie]:
        """ Returns the Genres stored in the repository. """
        raise NotImplementedError








