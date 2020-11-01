import csv
import os
from datetime import date, datetime
from typing import List
from flix.adapters.repository import AbstractRepository, RepositoryException
from flix.domain.model import *
from werkzeug.security import generate_password_hash
from bisect import bisect, bisect_left, insort_left


class MemoryRepository(AbstractRepository):

    def __init__(self):
        self._movies = list()
        self.years = list()
        self.actors = list()
        self.directors = list()
        self._movies_index = dict()
        self._genres = list()
        self._users = list()
        self._comments = list()
        self._review = list()

    def add_user(self, user: User):
        self._users.append(user)

    def get_user(self, username) -> User:
        return next((user for user in self._users if user.username == username), None)

    def add_movie(self, movie: Movie):
        insort_left(self._movies, movie)
        self._movies_index[movie.rank] = movie

    def get_movie(self, rank: int) -> Movie:
        movie = None
        try:
            movie = self._movies_index[rank]
        except KeyError:
            pass  # Ignore exception and return None.

        return movie

    def get_movies_by_year(self, target_year: int) -> List[Movie]:
        matching_movies = list()

        try:
            for movie in self._movies:
                if movie.date == target_year:
                    matching_movies.append(movie)
                else:
                    break
        except ValueError:
            # No movies for specified date. Simply return an empty list.
            pass

        return matching_movies

    def get_number_of_movies(self):
        return len(self._movies)

    def get_first_movie(self):
        movie = None
        moviesort = list()
        for item in self._movies:
            moviesort.append(item)
            moviesort.sort(key=lambda x: x.rank, reverse=False)

        if len(moviesort) > 0:
            movie = moviesort[0]
        return movie

    def get_last_movie(self):
        movie = None
        moviesort = list()
        for item in self._movies:
            moviesort.append(item)
            moviesort.sort(key=lambda x: x.rank, reverse=False)

        if len(moviesort) > 0:
            movie = moviesort[-1]
        return movie

    def get_movies_by_rank(self, rank_list):
        # Strip out any ranks in rank_list that don't represent Movie ranks in the repository.
        existing_ranks = [rank for rank in rank_list if rank in self._movies_index]

        # Fetch the Movies.
        movies = [self._movies_index[rank] for rank in existing_ranks]
        return movies

    def get_movie_ranks_for_genre(self, genre_name: str):
        # Linear search, to find the first occurrence of a Genre with the name genre_name.
        genre = next((genre for genre in self._genres if genre.genre_name == genre_name), None)

        # Retrieve the ranks of movies associated with the Genre.
        if genre is not None:
            movie_ranks = [movie.rank for movie in genre.genre_asso_movies]
        else:
            # No Genre with name genre_name, so return an empty list.
            movie_ranks = list()

        return movie_ranks

    def get_movie_ranks_for_director(self, director_full_name: str):
        # Linear search, to find the first occurrence of a director with the name director_full_name.
        director = None
        for d in self.directors:
            if d.director_full_name == director_full_name:
                director = d
        print(director)

        # Retrieve the ranks of movies associated with the director.
        if director is not None:
            movie_ranks = [movie.rank for movie in director.director_asso_movies]
        else:
            # No director with name director_full_name, so return an empty list.
            movie_ranks = list()

        return movie_ranks

    def get_movie_ranks_for_actor(self, actor_full_name: str):
        # Linear search, to find the first occurrence of a actor with the name actor_full_name.
        actor = None
        for a in self.actors:
            if a.actor_name == actor_full_name:
                actor = a



        # Retrieve the ranks of movies associated with the actor.
        if actor is not None:

            movie_ranks = [movie.rank for movie in actor.actor_asso_movies]
        else:
            # No actor with name actor_full_name, so return an empty list.
            movie_ranks = list()

        return movie_ranks

    def get_movie_ranks_for_year(self, tgt_year: str):
        movie_ranks = list()
        for movie in self._movies:
            if str(movie.date) == tgt_year:
                movie_ranks.append(movie.rank)

        return movie_ranks

    def get_year_of_previous_movie(self, movie: Movie):
        previous_year = None

        try:
            index = self.movie_index(movie)
            for stored_movie in reversed(self._movies[0:index]):
                if stored_movie.date < movie.date:
                    previous_year = stored_movie.date
                    break
        except ValueError:
            # No earlier movies, so return None.
            pass

        return previous_year

    def get_year_of_next_movie(self, movie: Movie):
        next_year = None

        try:
            index = self.movie_index(movie)
            for stored_movie in self._movies[index + 1:len(self._movies)]:
                if stored_movie.date > movie.date:
                    next_year = stored_movie.date
                    break
        except ValueError:
            # No subsequent movies, so return None.
            pass

        return next_year

    def add_genre(self, genre: Genre):
        self._genres.append(genre)

    def get_genres(self) -> List[Genre]:
        return self._genres

    def add_director(self, director: Director):
        self.directors.append(director)

    def get_directors(self) -> List[Director]:
        return self.directors

    def add_actor(self, actor: Actor):
        self.actors.append(actor)

    def get_actors(self) -> List[Actor]:
        return self.actors

    def add_comment(self, comment: Comment):
        super().add_comment(comment)
        self._comments.append(comment)

    def get_comments(self):
        return self._comments

    # Helper method to return movie index.
    def movie_index(self, movie: Movie):
        index = bisect_left(self._movies, movie)
        if index != len(self._movies) and self._movies[index].date == movie.date:
            return index
        raise ValueError

    def set_rating(self, rating:int, user:User, movie:Movie):
        index = self._movies.index(movie)
        self._movies[index].set_rating(rating,user)

    def get_movies(self):
        return self._movies

    def add_year(self, year):
        if year not in self.years:
            self.years.append(year)

    def get_years(self):
        return self.years


def read_csv_file(filename: str):
    with open(filename, encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)

        # Read first line of the the CSV file.
        headers = next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:
            # Strip any leading/trailing white space from data read.
            row = [item.strip() for item in row]
            yield row




def load_movies_and_genres(data_path: str, repo: MemoryRepository):
    genres = dict()
    actors = dict()
    directors = dict()

    for data_row in read_csv_file(os.path.join(data_path, 'Data1000Movies.csv')):

        movie_key = int(data_row[0])
        number_of_genres = len(data_row[2].split(","))
        movie_genres = data_row[2].split(",")
        movie_actors = data_row[5].split(",")
        director = data_row[4]

        # Add any new genres; associate the current movie with genres.
        for genre in movie_genres:
            if genre not in genres.keys():
                genres[genre] = list()
            genres[genre].append(movie_key)

        if director not in directors.keys():
            directors[director] = list()
        directors[director].append(movie_key)

        for actor in movie_actors:
            if actor not in actors.keys():
                actors[actor] = list()
            actors[actor].append(movie_key)

        # Create Movie object.
        movie = Movie(
            title=data_row[1],
            year=int(data_row[6]),
            rank=int(data_row[0])
        )
        repo.add_year(movie.date)
        movie.description = data_row[3]
        movie.director = Director(data_row[4])
        repo.add_director(Director(data_row[4]))
        movie.actors = data_row[5].split(",")
        for actor in movie.actors:
            repo.add_actor(Actor(actor))
        movie.runtime_minutes = int(data_row[7])
        movie.rating = float(data_row[8])
        movie.votes = float(data_row[9])
        if data_row[10] != 'N/A':
            movie.revenue = f"{data_row[10]} Millions"
        if data_row[11] != 'N\A':
            movie.metascore = data_row[11]

        # Add the Movie to the repository.
        repo.add_movie(movie)


    # Create Genre objects, associate them with Movies and add them to the repository.
    for genre_name in genres.keys():
        genre = Genre(genre_name)
        for movie_rank in genres[genre_name]:
            movie = repo.get_movie(movie_rank)
            make_genre_association(movie, genre)
        repo.add_genre(genre)

    for actor_name in actors.keys():
        actor = Actor(actor_name)
        for movie_rank in actors[actor_name]:
            movie = repo.get_movie(movie_rank)
            make_actor_association(movie, actor)
        repo.add_actor(actor)

    for director_name in directors.keys():
        director = Director(director_name)
        for movie_rank in directors[director_name]:
            movie = repo.get_movie(movie_rank)
            make_director_association(movie, director)
        repo.add_director(director)

def load_movies_and_actors(data_path: str, repo: MemoryRepository):
    genres = dict()
    actors = dict()
    directors = dict()

    for data_row in read_csv_file(os.path.join(data_path, 'Data1000Movies.csv')):

        movie_key = int(data_row[0])
        number_of_actors = len(data_row[5].split(","))
        movie_genres = data_row[2].split(",")
        movie_actors = data_row[5].split(",")
        director = data_row[4]

        # Add any new genres; associate the current movie with genres.
        for genre in movie_genres:
            if genre not in genres.keys():
                genres[genre] = list()
            genres[genre].append(movie_key)

        if director not in directors.keys():
            directors[director] = list()
        directors[director].append(movie_key)

        # Add any new details; associate the current movie with details.
        for actor in movie_actors:
            if actor not in actors.keys():
                actors[actor] = list()
            actors[actor].append(movie_key)

        # Create Movie object.
        movie = Movie(
            title=data_row[1],
            year=int(data_row[6]),
            rank=int(data_row[0])
        )
        movie.description = data_row[3]
        movie.director = Director(data_row[4])
        repo.add_director(movie.director)
        movie.actors = data_row[5].split(",")
        for actor in movie.actors:
            repo.add_actor(Actor(actor))
        movie.genres = data_row[2].split(",")
        movie.runtime_minutes = int(data_row[7])
        movie.rating = float(data_row[8])
        movie.votes = float(data_row[9])
        if data_row[10] != 'N/A':
            movie.revenue = f"{data_row[10]} Millions"
        if data_row[11] != 'N\A':
            movie.metascore = data_row[11]

        # Add the Movie to the repository.
        repo.add_movie(movie)

        # Create Genre objects, associate them with Movies and add them to the repository.
        for genre_name in genres.keys():
            genre = Genre(genre_name)
            for movie_rank in genres[genre_name]:
                movie = repo.get_movie(movie_rank)
                make_genre_association(movie, genre)
            repo.add_genre(genre)

        for actor_name in actors.keys():
            actor = Actor(actor_name)
            for movie_rank in actors[actor_name]:
                movie = repo.get_movie(movie_rank)
                make_actor_association(movie, actor)
            repo.add_actor(actor)

        for director_name in directors.keys():
            director = Director(director_name)
            for movie_rank in directors[director_name]:
                movie = repo.get_movie(movie_rank)
                make_director_association(movie, director)
            repo.add_director(director)

'''def load_movies_and_directors(data_path: str, repo: MemoryRepository):
    genres = dict()
    actors = dict()
    directors = dict()

    for data_row in read_csv_file(os.path.join(data_path, 'Data1000Movies.csv')):

        movie_key = int(data_row[0])
        number_of_directors = len(data_row[5].split(","))
        movie_genres = data_row[2].split(",")
        movie_actors = data_row[5].split(",")
        director = data_row[4]

        # Add any new details; associate the current movie with details.
        for genre in movie_genres:
            if genre not in genres.keys():
                genres[genre] = list()
            genres[genre].append(movie_key)

        if director not in directors.keys():
            directors[director] = list()
        directors[director].append(movie_key)

        for actor in movie_actors:
            if actor not in actors.keys():
                actors[actor] = list()
            actors[actor].append(movie_key)


        # Create Movie object.
        movie = Movie(
            title=data_row[1],
            year=int(data_row[6]),
            rank=int(data_row[0])
        )
        movie.description = data_row[3]
        movie.director = Director(data_row[4])
        repo.add_director(movie.director)
        movie.actors = data_row[5].split(",")
        for actor in movie.actors:
            repo.add_actor(Actor(actor))
        movie.genres = data_row[2].split(",")
        movie.runtime_minutes = int(data_row[7])
        movie.rating = float(data_row[8])
        movie.votes = float(data_row[9])
        if data_row[10] != 'N/A':
            movie.revenue = f"{data_row[10]} Millions"
        if data_row[11] != 'N\A':
            movie.metascore = data_row[11]

        # Add the Movie to the repository.
        repo.add_movie(movie)

        # Create Genre objects, associate them with Movies and add them to the repository.
        for genre_name in genres.keys():
            genre = Genre(genre_name)
            for movie_rank in genres[genre_name]:
                movie = repo.get_movie(movie_rank)
                make_genre_association(movie, genre)
            repo.add_genre(genre)

        for actor_name in actors.keys():
            actor = Actor(actor_name)
            for movie_rank in actors[actor_name]:
                movie = repo.get_movie(movie_rank)
                make_actor_association(movie, actor)
            repo.add_actor(actor)

        for director_name in directors.keys():
            director = Director(director_name)
            for movie_rank in directors[director_name]:
                movie = repo.get_movie(movie_rank)
                make_director_association(movie, director)
            repo.add_director(director)



def load_movies_and_years(data_path: str, repo: MemoryRepository):
    years = dict()
    genres = dict()
    actors = dict()
    directors = dict()

    for data_row in read_csv_file(os.path.join(data_path, 'Data1000Movies.csv')):

        movie_key = int(data_row[0])
        number_of_years = len(data_row[2].split(","))
        movie_genres = data_row[2].split(",")
        year=int(data_row[6])

        if year not in years.keys():
            years[year] = list()
        years[year].append(movie_key)

        # Create Movie object.
        movie = Movie(
            title=data_row[1],
            year=int(data_row[6]),
            rank=int(data_row[0])
        )
        movie.description = data_row[3]
        movie.director = Director(data_row[4])
        repo.add_director(movie.director)
        movie.actors = data_row[5].split(",")
        for actor in movie.actors:
            repo.add_actor(Actor(actor))
        movie.runtime_minutes = int(data_row[7])
        movie.rating = float(data_row[8])
        movie.votes = float(data_row[9])
        if data_row[10] != 'N/A':
            movie.revenue = f"{data_row[10]} Millions"
        if data_row[11] != 'N\A':
            movie.metascore = data_row[11]

        # Add the Movie to the repository.
        repo.add_movie(movie)

        # Create Genre objects, associate them with Movies and add them to the repository.
        for genre_name in genres.keys():
            genre = Genre(genre_name)
            for movie_rank in genres[genre_name]:
                movie = repo.get_movie(movie_rank)
                make_genre_association(movie, genre)
            repo.add_genre(genre)

        for actor_name in actors.keys():
            actor = Actor(actor_name)
            for movie_rank in actors[actor_name]:
                movie = repo.get_movie(movie_rank)
                make_actor_association(movie, actor)
            repo.add_actor(actor)

        for director_name in directors.keys():
            director = Director(director_name)
            for movie_rank in directors[director_name]:
                movie = repo.get_movie(movie_rank)
                make_director_association(movie, director)
            repo.add_director(director)


    # Create year objects, associate them with Movies and add them to the repository.
    for year in years.keys():
        for movie_rank in years[year]:
            movie = repo.get_movie(movie_rank)
            make_year_association(movie, year)
        repo.add_year(year)'''


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
