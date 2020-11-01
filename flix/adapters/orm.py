from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Date, DateTime,
    ForeignKey
)
from sqlalchemy.orm import mapper, relationship

from flix.domain import model

metadata = MetaData()

users = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('username', String(255), unique=True, nullable=False),
    Column('password', String(255), nullable=False)
)

comments = Table(
    'comments', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', ForeignKey('users.id')),
    Column('movie_rank', ForeignKey('movies.rank')),
    Column('comment', String(1024), nullable=False),
    Column('timestamp', DateTime, nullable=False)
)

movies = Table(
    'movies', metadata,
    Column('rank', Integer, primary_key=True, autoincrement=True),
    Column('title', String(255), nullable=False),
    Column('genre', String(255), nullable=True),
    Column('description', String(1024), nullable=True),
    Column('director', String(255), nullable=True),
    Column('actors', String, nullable=True),
    Column('year', Integer, nullable=True),
    Column('runtime', Integer, nullable=True),
    Column('rating', String, nullable=True),
    Column('votes', Integer, nullable=True),
    Column('revenue', String, nullable=True),
    Column('metascore', String, nullable=True),
    Column('hyperlink', String(255), nullable=True),
    Column('image_hyperlink', String(255), nullable=True)
)

genres = Table(
    'genres', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(64), nullable=False),
    Column('tagged_movies', String, nullable=True)
)

movie_genres = Table(
    'movie_genres', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('movie_rank', ForeignKey('movies.rank')),
    Column('genre_id', ForeignKey('genres.id'))
)

directors = Table(
    'directors', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(64), nullable=False)
)


actors = Table(
    'actors', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(64), nullable=False)
)

movie_directors = Table(
    'movie_directors', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('movie_rank', ForeignKey('movies.rank')),
    Column('director_id', ForeignKey('directors.id'))
)


movie_actors = Table(
    'movie_actors', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('movie_rank', ForeignKey('movies.rank')),
    Column('actor_id', ForeignKey('actors.id'))
)


def map_model_to_tables():
    mapper(model.User, users, properties={
        '_User__username': users.c.username,
        '_User__password': users.c.password,
        '_User__comments': relationship(model.Comment, backref='_Comment__user')
    })
    mapper(model.Director, directors, properties={
        '_Director__director_full_name': directors.c.name
    })
    mapper(model.Actor, actors, properties={
        '_Actor__actor_full_name': actors.c.name
    })
    mapper(model.Comment, comments, properties={
        '_Comment__comment': comments.c.comment,
        '_Comment__timestamp': comments.c.timestamp
    })
    movies_mapper = mapper(model.Movie, movies, properties={
        '_Movie__rank': movies.c.rank,
        '_Movie__title': movies.c.title,
        '_Movie__year': movies.c.year,
        '_Movie__genres': movies.c.genre,
        '_Movie__description': movies.c.description,
        '_Movie__director': movies.c.director,
        '_Movie__actors': movies.c.actors,
        '_Movie__votes': movies.c.votes,
        '_Movie__revenue': movies.c.revenue,
        '_Movie__metascore': movies.c.metascore,
        '_Movie__runtime_minutes': movies.c.runtime,
        '_Movie__rating': movies.c.rating,
        '_Movie__hyperlink': movies.c.hyperlink,
        '_Movie__image_hyperlink': movies.c.image_hyperlink,
        '_Movie__comments': relationship(model.Comment, backref='_Comment__movie'),
    })
    mapper(model.Genre, genres, properties={
        '_Genre__genre_name': genres.c.name,
        '_Genre__tagged_movies': genres.c.tagged_movies
    })
