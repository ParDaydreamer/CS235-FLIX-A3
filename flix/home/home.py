from flask import Blueprint, render_template

import flix.utilities.utilities as utilities


home_blueprint = Blueprint(
    'home_bp', __name__)


@home_blueprint.route('/', methods=['GET'])
def home():
    return render_template(
        'home/home.html',
        genre_urls=utilities.get_genres_and_urls(),
        year_urls=utilities.get_year_and_urls(),
        director_urls=utilities.get_directors_and_urls(),
        actor_urls=utilities.get_actors_and_urls(),
        home_movies=utilities.get_selected_movies(6),
    )


