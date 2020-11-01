from sqlalchemy import select, inspect

from flix.adapters.orm import metadata

def test_database_populate_inspect_table_names(database_engine):

    # Get table information
    inspector = inspect(database_engine)
    assert inspector.get_table_names() == ['actors', 'comments', 'directors', 'genres', 'movie_actors',
                                           'movie_directors', 'movie_genres', 'movies', 'users']

def test_database_populate_select_all_genres(database_engine):

    # Get table information
    inspector = inspect(database_engine)
    name_of_genres_table = inspector.get_table_names()[3]

    with database_engine.connect() as connection:
        # query for records in table genres
        select_statement = select([metadata.tables[name_of_genres_table]])
        result = connection.execute(select_statement)

        all_genre_names = []
        for row in result:
            all_genre_names.append(row['name'])

        assert all_genre_names == ['Action', 'Adventure', 'Sci-Fi', 'Mystery', 'Horror', 'Thriller', 'Animation',
                                   'Comedy', 'Family', 'Fantasy', 'Drama', 'Music', 'Biography', 'Romance']

def test_database_populate_select_all_users(database_engine):

    # Get table information
    inspector = inspect(database_engine)
    name_of_users_table = inspector.get_table_names()[8]

    with database_engine.connect() as connection:
        # query for records in table users
        select_statement = select([metadata.tables[name_of_users_table]])
        result = connection.execute(select_statement)

        all_users = []
        for row in result:
            all_users.append(row['username'])

        assert all_users == ['thorke', 'fmercury', 'mjackson']

def test_database_populate_select_all_comments(database_engine):

    # Get table information
    inspector = inspect(database_engine)
    name_of_comments_table = inspector.get_table_names()[1]

    with database_engine.connect() as connection:
        # query for records in table comments
        select_statement = select([metadata.tables[name_of_comments_table]])
        result = connection.execute(select_statement)

        all_comments = []
        for row in result:
            all_comments.append((row['id'], row['user_id'], row['movie_rank'], row['comment']))

        assert all_comments == [(1, 2, 1, 'This movie is okay.'),
                                (2, 1, 1, 'Yeah Freddie, it is good.'),
                                (3, 3, 1, "I hope it worth the ticket!")]

def test_database_populate_select_all_movies(database_engine):

    # Get table information
    inspector = inspect(database_engine)
    name_of_movies_table = inspector.get_table_names()[7]

    with database_engine.connect() as connection:
        # query for records in table movies
        select_statement = select([metadata.tables[name_of_movies_table]])
        result = connection.execute(select_statement)

        all_movies = []
        for row in result:
            all_movies.append((row['rank'], row['title']))

        nr_movies = len(all_movies)

        assert all_movies[0] == (1, 'Guardians of the Galaxy')
        assert all_movies[nr_movies//2] == (6, 'The Great Wall')
        assert all_movies[nr_movies-1] == (10, 'Passengers')


