import csv
import os

from datetime import date
from typing import List

from sqlalchemy import desc, asc
from sqlalchemy.engine import Engine
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from werkzeug.security import generate_password_hash

from sqlalchemy.orm import scoped_session
from flask import _app_ctx_stack

from flix.domain.model import *
from flix.domain.model import Movie
from flix.adapters.repository import AbstractRepository

genres = None
directors = None
actors = None


class SessionContextManager:
    def __init__(self, session_factory):
        self.__session_factory = session_factory
        self.__session = scoped_session(self.__session_factory, scopefunc=_app_ctx_stack.__ident_func__)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @property
    def session(self):
        return self.__session

    def commit(self):
        self.__session.commit()

    def rollback(self):
        self.__session.rollback()

    def reset_session(self):
        # this method can be used e.g. to allow Flask to start a new session for each http request,
        # via the 'before_request' callback
        self.close_current_session()
        self.__session = scoped_session(self.__session_factory, scopefunc=_app_ctx_stack.__ident_func__)

    def close_current_session(self):
        if not self.__session is None:
            self.__session.close()


class SqlAlchemyRepository(AbstractRepository):

    def __init__(self, session_factory):
        self._session_cm = SessionContextManager(session_factory)


    def close_session(self):
        self._session_cm.close_current_session()

    def reset_session(self):
        self._session_cm.reset_session()

    def add_user(self, user: User):
        with self._session_cm as scm:
            scm.session.add(user)
            scm.commit()

    def add_director(self, director: Director):
        with self._session_cm as scm:
            scm.session.add(director)
            scm.commit()

    def add_actor(self, actor: Actor):
        with self._session_cm as scm:
            scm.session.add(actor)
            scm.commit()

    def get_user(self, username) -> User:
        user = None
        try:
            user = self._session_cm.session.query(User).filter_by(_User__username=username).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        return user

    def get_director(self, director_name) -> Director:
        director = None
        try:
            director = self._session_cm.session.query(Director).filter_by(_Director__director_name=director_name).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        return director

    def add_rating(self, rating: float, user: User, movie: Movie):
        the_movie = self._session_cm.session.query(Movie).filter_by(_Movie__title=movie.title).one()
        the_movie.add_rating(rating, user)
        print(the_movie.rating, the_movie.votes)
        #self._session_cm.session.query(Movie).filter_by(_Movie__title=movie.title).update({'rating':str(the_movie.rating)})
        #self._session_cm.session.query(Movie).filter_by(_Movie__title=movie.title).update({'votes':the_movie.votes})
        self._session_cm.session.commit()

    def get_directors(self):
        directors = []
        for d in self._session_cm.session.query(Director):
            directors.append(d)
        return directors

    def get_actor(self, actor_name) -> Actor:
        actor = None
        try:
            actor = self._session_cm.session.query(Actor).filter_by(_Actor__actor_name=actor_name).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        return actor

    def get_actors(self):
        actors = []
        for d in self._session_cm.session.query(Actor):
            actors.append(d)
        return actors

    def get_date(self, year) -> int:
        date = None
        try:
            date = self._session_cm.session.query(Date).filter_by(int=year).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        return date

    def get_dates(self):
        dates = []
        for d in self._session_cm.session.query(Movie).all():
            dates.append(d.date)
        return dates

    def add_movie(self, movie: Movie):
        with self._session_cm as scm:
            scm.session.add(movie)
            scm.commit()

    def get_movie(self, id: int) -> Movie:
        movie = None
        try:
            movies = self._session_cm.session.query(Movie).all()
            for m in movies:
                if m.id == id:
                    movie = m
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        return movie

    def get_movies(self):
        movies = self._session_cm.session.query(Movie).all()
        return movies

    def get_movies_by_date(self, target_date: date) -> List[Movie]:
        if target_date is None:
            movies = self._session_cm.session.query(Movie).all()
            return movies
        else:
            # Return movies matching target_date; return an empty list if there are no matches.
            movies = self._session_cm.session.query(Movie).filter_by(_Movie__year=target_date).all()
            return movies

    def get_number_of_movies(self):
        number_of_movies = self._session_cm.session.query(Movie).count()
        return number_of_movies

    def get_first_movie(self):
        movie = self._session_cm.session.query(Movie).first()
        return movie

    def get_last_movie(self):
        movie = self._session_cm.session.query(Movie).filter_by(_Movie__id=self.get_number_of_movies()).one()
        return movie

    def get_movies_by_id(self, id_list):
        movies = []
        movie = self._session_cm.session.query(Movie).all()
        for m in movie:
            if m.id in id_list:
                movies.append(m)
        return movies

    def get_movie_ids_for_genre(self, genre_name: str):
        movie_ids = []

        # Use native SQL to retrieve movie ids, since there is no mapped class for the movie_genres table.
        row1 = self._session_cm.session.execute('SELECT * FROM genres').fetchall()
        row = []
        for g in row1:
            if genre_name.lower() in g[1].lower():
                row.append(g[0])
        if row is None or row == []:
            # No genre with the name genre_name - create an empty list.
            movie_ids = list()
        else:
            genre_id = row[0]

            # Retrieve movie ids of movies associated with the genre.
            movie_ids = self._session_cm.session.execute(
                    'SELECT movie_id FROM movie_genres WHERE genre_id = :genre_id ORDER BY movie_id ASC',
                    {'genre_id': genre_id}
            ).fetchall()
            movie_ids = [id[0] for id in movie_ids]

        return movie_ids

    def get_movie_ids_for_director(self, director_name: str):
        movie_ids = []

        # Use native SQL to retrieve movie ids, since there is no mapped class for the movie_directors table.
        row1 = self._session_cm.session.execute('SELECT * FROM directors').fetchall()
        row = []
        for d in row1:
            if director_name.lower() in d[1].lower():
                row.append(d[0])
        if row is None or row == []:
            # No director with the name director_name - create an empty list.
            movie_ids = list()
        else:
            director_id = row[0]

            # Retrieve movie ids of movies associated with the director.
            movie_ids = self._session_cm.session.execute(
                    'SELECT movie_id FROM movie_directors WHERE director_id = :director_id ORDER BY movie_id ASC',
                    {'director_id': director_id}
            ).fetchall()
            movie_ids = [id[0] for id in movie_ids]

        return movie_ids

    def get_movie_ids_for_actor(self, actor_name: str):
        movie_ids = []

        # Use native SQL to retrieve movie ids, since there is no mapped class for the movie_actors table.
        row1 = self._session_cm.session.execute('SELECT * FROM actors').fetchall()
        row = []
        for a in row1:
            if actor_name.lower() in a[1].lower():
                row.append(a[0])

        if row is None or row == []:
            # No actor with the name actor_name - create an empty list.
            movie_ids = list()
        else:
            actor_id = row[0]

            # Retrieve movie ids of movies associated with the actor.
            movie_ids = self._session_cm.session.execute(
                    'SELECT movie_id FROM movie_actors WHERE actor_id = :actor_id ORDER BY movie_id ASC',
                    {'actor_id': actor_id}
            ).fetchall()
            movie_ids = [id[0] for id in movie_ids]

        return movie_ids

    def get_movie_ids_for_date(self, year: int):
        movie_ids = []

        # Use native SQL to retrieve movie ids, since there is no mapped class for the movie_dates table.
        movie_ids = self._session_cm.session.execute(
                    'SELECT id FROM movies WHERE movie_date = :the_date',
                    {'the_date': year}
            ).fetchall()
        movie_ids = [id[0] for id in movie_ids]

        return movie_ids

    def get_movie_ids_for_title(self, title_name: str):
        movie_ids = []

        # Use native SQL to retrieve movie ids, since there is no mapped class for the movie_dates table.
        movies = self._session_cm.session.execute(
            'SELECT * FROM movies'
        ).fetchall()
        for m in movies:
            if title_name.lower() in m[1].lower():
                movie_ids.append(m[0])

        return movie_ids

    def get_date_of_previous_movie(self, movie: Movie):
        result = None
        if movie.id == 1:
            return result
        prev = self._session_cm.session.query(Movie).filter_by(_Movie__id=movie.id-1).one()

        if prev is not None:
            result = prev.date

        return result

    def get_date_of_next_movie(self, movie: Movie):
        result = None
        if movie.id == self.get_number_of_movies():
            return result
        next = self._session_cm.session.query(Movie).filter_by(_Movie__id=movie.id + 1).one()

        if next is not None:
            result = next.date

        return result

    def get_genres(self) -> List[Genre]:
        genres = self._session_cm.session.query(Genre).all()
        return genres

    def add_genre(self, genre: Genre):
        with self._session_cm as scm:
            scm.session.add(genre)
            scm.commit()

    def get_comments(self) -> List[Comment]:
        comments = self._session_cm.session.query(Comment).all()
        return comments

    def add_comment(self, comment: Comment):
        super().add_comment(comment)
        with self._session_cm as scm:
            scm.session.add(comment)
            scm.commit()

def movie_record_generator(filename: str):
    with open(filename, mode='r', encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)

        # Read first line of the CSV file.
        headers = next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:

            movie_data = row
            movie_key = movie_data[0]

            # Strip any leading/trailing white space from data read.
            movie_data = [item.strip() for item in movie_data]

            movie_genres = movie_data[2].split(',')
            movie_director = movie_data[4]
            movie_actors = movie_data[5].split(',')

            # Add any new genres; associate the current movie with genres.
            for genre in movie_genres:
                if genre not in genres.keys():
                    genres[genre] = list()
                genres[genre].append(movie_key)

            if movie_director not in directors.keys():
                directors[movie_director] = list()
            directors[movie_director].append(movie_key)

            for actor in movie_actors:
                if actor.strip() not in actors.keys():
                    actors[actor.strip()] = list()
                actors[actor.strip()].append(movie_key)

            yield movie_data


def get_genre_records():
    genre_records = list()
    genre_key = 0

    for genre in genres.keys():
        genre_key = genre_key + 1
        genre_records.append((genre_key, genre))
    return genre_records

def get_director_records():
    director_records = list()
    director_key = 0

    for director in directors.keys():
        director_key = director_key + 1
        director_records.append((director_key, director))
    return director_records

def get_actor_records():
    actor_records = list()
    actor_key = 0

    for actor in actors.keys():
        actor_key = actor_key + 1
        actor_records.append((actor_key, actor))
    return actor_records

def movie_genres_generator():
    movie_genres_key = 0
    genre_key = 0

    for genre in genres.keys():
        genre_key = genre_key + 1
        for movie_key in genres[genre]:
            movie_genres_key = movie_genres_key + 1
            yield movie_genres_key, movie_key, genre_key

def movie_directors_generator():
    movie_directors_key = 0
    director_key = 0

    for director in directors.keys():
        director_key = director_key + 1
        for movie_key in directors[director]:
            movie_directors_key = movie_directors_key + 1
            yield movie_directors_key, movie_key, director_key


def movie_actors_generator():
    movie_actors_key = 0
    actor_key = 0

    for actor in actors.keys():
        actor_key = actor_key + 1
        for movie_key in actors[actor]:
            movie_actors_key = movie_actors_key + 1
            yield movie_actors_key, movie_key, actor_key


def generic_generator(filename, post_process=None):
    with open(filename) as infile:
        reader = csv.reader(infile)

        # Read first line of the CSV file.
        next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:
            # Strip any leading/trailing white space from data read.
            row = [item.strip() for item in row]

            if post_process is not None:
                row = post_process(row)
            yield row


def process_user(user_row):
    user_row[2] = generate_password_hash(user_row[2])
    return user_row


def populate(engine: Engine, data_path: str):
    conn = engine.raw_connection()
    cursor = conn.cursor()

    global genres
    genres = dict()

    global directors
    directors = dict()

    global actors
    actors = dict()

    insert_movies = """
        INSERT INTO movies (
        id,title,genre,description,director,actors,movie_date,runtime,rating,votes,revenue,metascore)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    cursor.executemany(insert_movies, movie_record_generator(os.path.join(data_path, 'Data1000Movies.csv')))

    insert_genres = """
        INSERT INTO genres (
        id, name)
        VALUES (?, ?)"""
    cursor.executemany(insert_genres, get_genre_records())

    insert_directors = """
            INSERT INTO directors (
            id, name)
            VALUES (?, ?)"""
    cursor.executemany(insert_directors, get_director_records())

    insert_actors = """
                INSERT INTO actors (
                id, name)
                VALUES (?, ?)"""
    cursor.executemany(insert_actors, get_actor_records())

    insert_movie_genres = """
        INSERT INTO movie_genres (
        id, movie_id, genre_id)
        VALUES (?, ?, ?)"""
    cursor.executemany(insert_movie_genres, movie_genres_generator())

    insert_movie_directors = """
            INSERT INTO movie_directors (
            id, movie_id, director_id)
            VALUES (?, ?, ?)"""
    cursor.executemany(insert_movie_directors, movie_directors_generator())

    insert_movie_actors = """
                INSERT INTO movie_actors (
                id, movie_id, actor_id)
                VALUES (?, ?, ?)"""
    cursor.executemany(insert_movie_actors, movie_actors_generator())

    insert_users = """
        INSERT INTO users (
        id, username, password)
        VALUES (?, ?, ?)"""
    cursor.executemany(insert_users, generic_generator(os.path.join(data_path, 'users.csv'), process_user))

    insert_comments = """
        INSERT INTO comments (
        id, user_id, movie_id, comment, timestamp)
        VALUES (?, ?, ?, ?, ?)"""
    cursor.executemany(insert_comments, generic_generator(os.path.join(data_path, 'comments.csv')))

    conn.commit()
    conn.close()

