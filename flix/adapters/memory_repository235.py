import csv
import os
from bisect import bisect_left, insort_left
from datetime import datetime
from typing import List

from flix.adapters.repository import AbstractRepository, RepositoryException
from flix.domain.model import Movie, Actor, User, Director, Genre, Comment, make_genre_association, \
    make_comment, make_director_association, make_actor_association
from werkzeug.security import generate_password_hash


class MemoryRepository(AbstractRepository):

    def __init__(self):
        self._movies = list()
        self._movies_index = dict()
        self._genres = list()
        self._users = list()
        self._comments = list()
        self._directors = list()
        self._actors = list()
        self._dates = list()

    def add_user(self, user: User):
        self._users.append(user)

    def get_user(self, username) -> User:
        return next((user for user in self._users if user.username == username), None)

    def get_users(self):
        return  self._users

    def add_movie(self, movie: Movie):
        insort_left(self._movies, movie)
        self._movies_index[movie.id] = movie

    def get_movie(self, movie_id: int) -> Movie:
        movie = None
        try:
            movie = self._movies_index[movie_id]
        except KeyError:
            pass  # Ignore exception and return None.

        return movie

    def get_number_of_movies(self):
        return len(self._movies)

    def get_first_movie(self):
        movie = None

        if len(self._movies) > 0:
            for mov in self._movies:
                if mov.id == 1:
                    movie = mov
        return movie

    def get_last_movie(self):
        movie = None

        if len(self._movies) > 0:
            for mov in self._movies:
                if mov.id == len(self._movies):
                    movie = mov
        return movie

    def get_movies_by_id(self, id_list):
        # Strip out any ids in id_list that don't represent Movie ids in the repository.
        existing_ids = [movie_id for movie_id in id_list if movie_id in self._movies_index]

        # Fetch the Movies.
        movies = [self._movies_index[the_id] for the_id in existing_ids]
        return movies

    def get_movie_ids_for_genre(self, genre_name: str):
        # Linear search, to find the first occurrence of a Genre with the name genre_name.
        genre = next((genre for genre in self._genres if genre.genre_name == genre_name), None)
        # Retrieve the ids of movies associated with the Genre.
        if genre is not None:
            movie_ids = [movie.id for movie in genre.tagged_movies]
        else:
            # No Genre with name genre_name, so return an empty list.
            movie_ids = list()

        return movie_ids

    def get_movie_ids_for_director(self, director_name: str):
        # Linear search, to find the first occurrence of a Director with the name director_name.
        director = next((director for director in self._directors if
                         director_name == director.director_full_name or
                         director_name in director.director_full_name.split()), None)

        # Retrieve the ids of movies associated with the Director.
        if director is not None:
            movie_ids = [movie.id for movie in director.directed_movies]
        else:
            # No Director with name director_name, so return an empty list.
            movie_ids = list()

        return movie_ids

    def get_movie_ids_for_actor(self, actor_name: str):
        # Linear search, to find the first occurrence of a actor with the name actor_name.
        actor = next((actor for actor in self._actors if
                      actor_name == actor.actor_full_name or actor_name in actor.actor_full_name.split()), None)

        # Retrieve the ids of movies associated with the Actor.
        if actor is not None:
            movie_ids = [movie.id for movie in actor.joined_movies]
        else:
            # No Actor with name actor_name, so return an empty list.
            movie_ids = list()

        return movie_ids

    def get_movie_ids_for_title(self, title_name: str):
        movie_ids = list()
        for movie in self._movies:
            if title_name == movie.title or title_name in movie.title.split():
                movie_ids.append(movie.id)

        return movie_ids

    def get_movie_ids_for_date(self, the_date: str):
        movie_ids = list()
        for movie in self._movies:
            if str(movie.date) == the_date:
                movie_ids.append(movie.id)

        return movie_ids

    def get_date_of_previous_movie(self, movie: Movie):
        previous_date = None

        try:
            index = 0
            for i in self._movies_index:
                if self._movies_index[i] == movie:
                    index = i
            if index == 1:
                return None
            previous_date = self._movies_index[index - 1].date
        except:
            # No earlier movies, so return None.
            pass

        return previous_date

    def get_date_of_next_movie(self, movie: Movie):
        next_date = None

        try:
            index = 0
            for i in self._movies_index:
                if self._movies_index[i] == movie:
                    index = i
            if index == 100:
                return None
            next_date = self._movies_index[index + 1].date
        except:
            # No subsequent movies, so return None.
            pass

        return next_date

    def add_genre(self, genre: Genre):
        self._genres.append(genre)

    def get_genres(self) -> List[Genre]:
        return self._genres

    def add_actor(self, actor: Actor):
        self._actors.append(actor)

    def get_actors(self) -> List[Actor]:
        return self._actors

    def add_date(self, the_date: int):
        self._dates.append(the_date)

    def get_dates(self) -> List[int]:
        return self._dates

    def add_director(self, director: Director):
        self._directors.append(director)

    def get_directors(self) -> List[Director]:
        return self._directors

    def add_comment(self, comment: Comment):
        super().add_comment(comment)
        self._comments.append(comment)

    def add_rating(self, rating: float, user: User, movie: Movie):
        index = self._movies.index(movie)
        self._movies[index].add_rating(rating, user)

    def add_image_link(self, link: str, movie: Movie):
        index = self._movies.index(movie)
        self._movies[index].image_hyperlink = link

    def get_comments(self):
        return self._comments

    def get_movies(self):
        return self._movies

    # Helper method to return movie index.
    def movie_index(self, movie: Movie):
        index = bisect_left(self._movies, movie)
        if index != len(self._movies) and self._movies[index].date == movie.date:
            return index
        raise ValueError


def read_csv_file(filename: str):
    with open(filename, encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)

        # Read first line of the the CSV file.
        next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:
            # Strip any leading/trailing white space from data read.
            row = [item.strip() for item in row]
            yield row


def load_movies_and_genres(data_path: str, repo: MemoryRepository):
    genres = dict()
    directors = dict()
    actors = dict()

    for data_row in read_csv_file(os.path.join(data_path, 'Data1000Movies.csv')):

        movie_key = int(data_row[0])
        movie_genres = data_row[2].lower().split(",")
        movie_directors = data_row[4].lower().split(",")
        movie_actors = data_row[5].lower().split(",")

        # Add any new genres; associate the current movie with genres.
        for genre in movie_genres:
            if genre not in genres.keys():
                genres[genre] = list()
            genres[genre].append(movie_key)
        for director in movie_directors:
            if director not in directors.keys():
                directors[director] = list()
            directors[director].append(movie_key)
        for actor in movie_actors:
            if actor not in actors.keys():
                actors[actor] = list()
            actors[actor].append(movie_key)

        # Create Movie object.
        movie = Movie(
            title=data_row[1].lower(),
            year=int(data_row[6]),
            movie_id=int(data_row[0])
        )
        movie.description = data_row[3]
        movie.runtime_minutes = int(data_row[7])
        movie.rating = float(data_row[8])
        movie.votes = float(data_row[9])
        if data_row[10] != 'N/A':
            movie.revenue = f"{data_row[10]}Millions"
        if data_row[11] != 'N/A':
            movie.metascore = data_row[11]

        # Add the Movie to the repository.
        repo.add_movie(movie)

    # Create Genre objects, associate them with Movies and add them to the repository.
    for genre_name in genres.keys():
        genre = Genre(genre_name)
        for movie_id in genres[genre_name]:
            movie = repo.get_movie(movie_id)
            make_genre_association(movie, genre)
        repo.add_genre(genre)

    for director_name in directors.keys():
        director = Director(director_name)
        for movie_id in directors[director_name]:
            movie = repo.get_movie(movie_id)
            make_director_association(movie, director)
        repo.add_director(director)

    for actor_name in actors.keys():
        actor = Actor(actor_name)
        for movie_id in actors[actor_name]:
            movie = repo.get_movie(movie_id)
            make_actor_association(movie, actor)
        repo.add_actor(actor)


def load_users(data_path: str, repo: MemoryRepository):
    users = dict()

    for data_row in read_csv_file(os.path.join(data_path, 'users.csv')):
        user = User(
            username=data_row[1],
            password=generate_password_hash(data_row[2])
        )
        repo.add_user(user)
        users[data_row[0]] = user
    return users


def load_comments(data_path: str, repo: MemoryRepository, users):
    for data_row in read_csv_file(os.path.join(data_path, 'comments.csv')):
        comment = make_comment(
            comment_text=data_row[3],
            user=users[data_row[1]],
            movie=repo.get_movie(int(data_row[2])),
            timestamp=datetime.fromisoformat(data_row[4])
        )
        repo.add_comment(comment)


def populate(data_path: str, repo: MemoryRepository):
    # Load movies and genres into the repository.
    load_movies_and_genres(data_path, repo)

    # Load users into the repository.
    users = load_users(data_path, repo)

    # Load comments into the repository.
    load_comments(data_path, repo, users)
