from datetime import date

from flask import Blueprint
from flask import request, render_template, redirect, url_for, session

from better_profanity import profanity
from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

import flix.adapters.repository as repo
import flix.utilities.utilities as utilities
import flix.feed.services as services

from flix.authentication.authentication import login_required


# Configure Blueprint.
feed_blueprint = Blueprint(
    'feed_bp', __name__)


@feed_blueprint.route('/movies_by_year', methods=['GET'])
def movies_by_year():
    movies_per_page = 4

    # Read query parameters.
    year = request.args.get('year')
    cursor = request.args.get('cursor')
    movie_to_show_comments = request.args.get('view_comments_for')

    if movie_to_show_comments is None:
        # No view-comments query parameter, so set to a non-existent movie rank.
        movie_to_show_comments = -1
    else:
        # Convert movie_to_show_comments from string to int.
        movie_to_show_comments = int(movie_to_show_comments)

    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)

    # Retrieve movie ids for movies that are genreged with genre_name.
    movie_ranks = services.get_movie_ranks_for_year(year, repo.repo_instance)

    # Retrieve the batch of movies to display on the Web page.
    movies = services.get_movies_by_rank(movie_ranks[cursor:cursor + movies_per_page], repo.repo_instance)

    first_movie_url = None
    last_movie_url = None
    next_movie_url = None
    prev_movie_url = None

    if cursor > 0:
        # There are preceding movies, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_movie_url = url_for('feed_bp.movies_by_year', year=year, cursor=cursor - movies_per_page)
        first_movie_url = url_for('feed_bp.movies_by_year', year=year)

    if cursor + movies_per_page < len(movie_ranks):
        # There are further movies, so generate URLs for the 'next' and 'last' navigation buttons.
        next_movie_url = url_for('feed_bp.movies_by_year', year=year, cursor=cursor + movies_per_page)

        last_cursor = movies_per_page * int(len(movie_ranks) / movies_per_page)
        if len(movie_ranks) % movies_per_page == 0:
            last_cursor -= movies_per_page
        last_movie_url = url_for('feed_bp.movies_by_year', year=year, cursor=last_cursor)

    # Construct urls for viewing movie comments and adding comments.
    for movie in movies:
        movie['view_comment_url'] = url_for('feed_bp.movies_by_year', year=year, cursor=cursor, view_comments_for=movie['rank'])
        movie['add_comment_url'] = url_for('feed_bp.comment_on_movie', movie=movie['rank'])

    # Generate the webpage to display the movies.
    return render_template(
        'feed/movies.html',
        title='Movies',
        movies_title=f'movies in {year}',
        movies=movies,
        selected_movies=utilities.get_selected_movies(len(movies) * 2),
        genre_urls=utilities.get_genres_and_urls(),
        year_urls=utilities.get_year_and_urls(),
        director_urls=utilities.get_directors_and_urls(),
        actor_urls=utilities.get_actors_and_urls(),
        first_movie_url=first_movie_url,
        last_movie_url=last_movie_url,
        prev_movie_url=prev_movie_url,
        next_movie_url=next_movie_url,
        show_comments_for_movie=movie_to_show_comments
    )



@feed_blueprint.route('/movies_by_genre', methods=['GET'])
def movies_by_genre():
    movies_per_page = 4

    # Read query parameters.
    genre_name = request.args.get('genre')
    cursor = request.args.get('cursor')
    movie_to_show_comments = request.args.get('view_comments_for')

    if movie_to_show_comments is None:
        # No view-comments query parameter, so set to a non-existent movie rank.
        movie_to_show_comments = -1
    else:
        # Convert movie_to_show_comments from string to int.
        movie_to_show_comments = int(movie_to_show_comments)

    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)

    # Retrieve movie ids for movies that are genreged with genre_name.
    movie_ranks = services.get_movie_ranks_for_genre(genre_name, repo.repo_instance)

    # Retrieve the batch of movies to display on the Web page.
    movies = services.get_movies_by_rank(movie_ranks[cursor:cursor + movies_per_page], repo.repo_instance)

    first_movie_url = None
    last_movie_url = None
    next_movie_url = None
    prev_movie_url = None

    if cursor > 0:
        # There are preceding movies, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_movie_url = url_for('feed_bp.movies_by_genre', genre=genre_name, cursor=cursor - movies_per_page)
        first_movie_url = url_for('feed_bp.movies_by_genre', genre=genre_name)

    if cursor + movies_per_page < len(movie_ranks):
        # There are further movies, so generate URLs for the 'next' and 'last' navigation buttons.
        next_movie_url = url_for('feed_bp.movies_by_genre', genre=genre_name, cursor=cursor + movies_per_page)

        last_cursor = movies_per_page * int(len(movie_ranks) / movies_per_page)
        if len(movie_ranks) % movies_per_page == 0:
            last_cursor -= movies_per_page
        last_movie_url = url_for('feed_bp.movies_by_genre', genre=genre_name, cursor=last_cursor)

    # Construct urls for viewing movie comments and adding comments.
    for movie in movies:
        movie['view_comment_url'] = url_for('feed_bp.movies_by_genre', genre=genre_name, cursor=cursor, view_comments_for=movie['rank'])
        movie['add_comment_url'] = url_for('feed_bp.comment_on_movie', movie=movie['rank'])

    # Generate the webpage to display the movies.
    return render_template(
        'feed/movies.html',
        title='Movies',
        movies_title=genre_name + ' movies',
        movies=movies,
        selected_movies=utilities.get_selected_movies(len(movies) * 2),
        genre_urls=utilities.get_genres_and_urls(),
        year_urls=utilities.get_year_and_urls(),
        director_urls=utilities.get_directors_and_urls(),
        actor_urls=utilities.get_actors_and_urls(),
        first_movie_url=first_movie_url,
        last_movie_url=last_movie_url,
        prev_movie_url=prev_movie_url,
        next_movie_url=next_movie_url,
        show_comments_for_movie=movie_to_show_comments
    )


@feed_blueprint.route('/movies_by_director', methods=['GET'])
def movies_by_director():
    movies_per_page = 4

    # Read query parameters.
    director_name = request.args.get('director')
    cursor = request.args.get('cursor')
    movie_to_show_comments = request.args.get('view_comments_for')

    if movie_to_show_comments is None:
        # No view-comments query parameter, so set to a non-existent movie rank.
        movie_to_show_comments = -1
    else:
        # Convert movie_to_show_comments from string to int.
        movie_to_show_comments = int(movie_to_show_comments)

    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)

    # Retrieve movie ids for movies that are associated with director_name.
    movie_ranks = services.get_movie_ranks_for_director(director_name, repo.repo_instance)
    print(movie_ranks)

    # Retrieve the batch of movies to display on the Web page.
    movies = services.get_movies_by_rank(movie_ranks[cursor:cursor + movies_per_page], repo.repo_instance)

    first_movie_url = None
    last_movie_url = None
    next_movie_url = None
    prev_movie_url = None

    if cursor > 0:
        # There are preceding movies, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_movie_url = url_for('feed_bp.movies_by_director', director=director_name, cursor=cursor - movies_per_page)
        first_movie_url = url_for('feed_bp.movies_by_director', director=director_name)

    if cursor + movies_per_page < len(movie_ranks):
        # There are further movies, so generate URLs for the 'next' and 'last' navigation buttons.
        next_movie_url = url_for('feed_bp.movies_by_director', director=director_name, cursor=cursor + movies_per_page)

        last_cursor = movies_per_page * int(len(movie_ranks) / movies_per_page)
        if len(movie_ranks) % movies_per_page == 0:
            last_cursor -= movies_per_page
        last_movie_url = url_for('feed_bp.movies_by_director', director=director_name, cursor=last_cursor)

    # Construct urls for viewing movie comments and adding comments.
    for movie in movies:
        movie['view_comment_url'] = url_for('feed_bp.movies_by_director', director=director_name, cursor=cursor,
                                            view_comments_for=movie['rank'])
        movie['add_comment_url'] = url_for('feed_bp.comment_on_movie', movie=movie['rank'])

    # Generate the webpage to display the movies.

    return render_template(
        'feed/movies.html',
        title='Movies',
        movies_title=director_name + ' movies',
        movies=movies,
        selected_movies=utilities.get_selected_movies(len(movies) * 2),
        genre_urls=utilities.get_genres_and_urls(),
        year_urls=utilities.get_year_and_urls(),
        director_urls=utilities.get_directors_and_urls(),
        actor_urls=utilities.get_actors_and_urls(),
        first_movie_url=first_movie_url,
        last_movie_url=last_movie_url,
        prev_movie_url=prev_movie_url,
        next_movie_url=next_movie_url,
        show_comments_for_movie=movie_to_show_comments
    )

@feed_blueprint.route('/movies_by_actor', methods=['GET'])
def movies_by_actor():
    movies_per_page = 4

    # Read query parameters.
    actor_name = request.args.get('actor')
    cursor = request.args.get('cursor')
    movie_to_show_comments = request.args.get('view_comments_for')

    if movie_to_show_comments is None:
        # No view-comments query parameter, so set to a non-existent movie rank.
        movie_to_show_comments = -1
    else:
        # Convert movie_to_show_comments from string to int.
        movie_to_show_comments = int(movie_to_show_comments)

    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)

    # Retrieve movie ids for movies that are associated with actor_name.
    movie_ranks = services.get_movie_ranks_for_actor(actor_name, repo.repo_instance)

    # Retrieve the batch of movies to display on the Web page.
    movies = services.get_movies_by_rank(movie_ranks[cursor:cursor + movies_per_page], repo.repo_instance)

    first_movie_url = None
    last_movie_url = None
    next_movie_url = None
    prev_movie_url = None

    if cursor > 0:
        # There are preceding movies, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_movie_url = url_for('feed_bp.movies_by_actor', actor=actor_name, cursor=cursor - movies_per_page)
        first_movie_url = url_for('feed_bp.movies_by_actor', actor=actor_name)

    if cursor + movies_per_page < len(movie_ranks):
        # There are further movies, so generate URLs for the 'next' and 'last' navigation buttons.
        next_movie_url = url_for('feed_bp.movies_by_actor', actor=actor_name, cursor=cursor + movies_per_page)

        last_cursor = movies_per_page * int(len(movie_ranks) / movies_per_page)
        if len(movie_ranks) % movies_per_page == 0:
            last_cursor -= movies_per_page
        last_movie_url = url_for('feed_bp.movies_by_actor', actor=actor_name, cursor=last_cursor)

    # Construct urls for viewing movie comments and adding comments.
    for movie in movies:
        movie['view_comment_url'] = url_for('feed_bp.movies_by_actor', actor=actor_name, cursor=cursor,
                                            view_comments_for=movie['rank'])
        movie['add_comment_url'] = url_for('feed_bp.comment_on_movie', movie=movie['rank'])

    # Generate the webpage to display the movies.
    return render_template(
        'feed/movies.html',
        title='Movies',
        movies_title=actor_name + ' movies',
        movies=movies,
        selected_movies=utilities.get_selected_movies(len(movies) * 2),
        genre_urls=utilities.get_genres_and_urls(),
        year_urls=utilities.get_year_and_urls(),
        director_urls=utilities.get_directors_and_urls(),
        actor_urls=utilities.get_actors_and_urls(),
        first_movie_url=first_movie_url,
        last_movie_url=last_movie_url,
        prev_movie_url=prev_movie_url,
        next_movie_url=next_movie_url,
        show_comments_for_movie=movie_to_show_comments
    )


@feed_blueprint.route('/comment', methods=['GET', 'POST'])
@login_required
def comment_on_movie():
    # Obtain the username of the currently logged in user.
    username = session['username']

    # Create form. The form maintains state, e.g. when this method is called with a HTTP GET request and populates
    # the form with an movie rank, when subsequently called with a HTTP POST request, the movie rank remains in the
    # form.
    form = CommentForm()

    if form.validate_on_submit():
        # Successful POST, i.e. the comment text has passed data validation.
        # Extract the movie rank, representing the commented movie, from the form.
        movie_id = int(form.movie_id.data)

        # Use the service layer to store the new comment.
        services.add_comment(movie_id, form.comment.data, username, repo.repo_instance)

        # Retrieve the movie in dict form.
        movie = services.get_movie(movie_id, repo.repo_instance)

        # Retrieve rating from user.
        rating = form.rating.data
        services.set_rating(movie_id, int(rating), username, repo.repo_instance)

        # Cause the web browser to display the page of all movies that have the same date as the commented movie,
        # and display all comments, including the new comment.
        return redirect(url_for('feed_bp.movies_by_year', date=movie['date'], view_comments_for=movie_id))

    if request.method == 'GET':
        # Request is a HTTP GET to display the form.
        # Extract the movie rank, representing the movie to comment, from a query parameter of the GET request.
        movie_id = int(request.args.get('movie'))

        # Store the movie rank in the form.
        form.movie_id.data = movie_id
    else:
        # Request is a HTTP POST where form validation has failed.
        # Extract the movie rank of the movie being commented from the form.
        movie_id = int(form.movie_id.data)

    # For a GET or an unsuccessful POST, retrieve the movie to comment in dict form, and return a Web page that allows
    # the user to enter a comment. The generated Web page includes a form object.
    movie = services.get_movie(movie_id, repo.repo_instance)
    return render_template(
        'feed/comment_on_movie.html',
        title='Edit movie',
        movie=movie,
        form=form,
        handler_url=url_for('feed_bp.comment_on_movie'),
        selected_movies=utilities.get_selected_movies(),
        genre_urls=utilities.get_genres_and_urls()
    )


class ProfanityFree:
    def __init__(self, message=None):
        if not message:
            message = u'Field must not contain profanity'
        self.message = message

    def __call__(self, form, field):
        if profanity.contains_profanity(field.data):
            raise ValidationError(self.message)

class RatingNum:
    def __init__(self, message=None):
        if not message:
            message = 'Rating must be integer between 1 and 10'
        self.message = message

    def __call__(self, form, field):
        try:
            if int(field.data) > 10 or int(field.data) < 1:
                raise ValidationError(self.message)
        except:
            raise ValidationError(self.message)

class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', [
        DataRequired(),
        Length(min=4, message='Your comment is too short'),
        ProfanityFree(message='Your comment must not contain profanity')])
    rating = TextAreaField('Rating', [
        DataRequired(),
        Length(min=0, message='Rating must not be empty'),
        RatingNum(message='Your rating must be integer between 1 and 10')])
    movie_id = HiddenField("Movie rank")
    submit = SubmitField('Submit')
