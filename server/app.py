from flask import Blueprint

main = Blueprint('main', __name__)

import json
from engine import RecommendationEngine

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from flask import Flask, request


@main.route("/products/<int:product_id>/associations", methods=["GET"])
def top_ratings(product_id):
    associations = recommendation_engine.get_association_rules(product_id)
    return (
        '[{}]'.format(','.join(associations)),
        200,
        {'Content-Type': 'application/json; charset=utf-8'}
    )


@main.route("/users/<string:phone_number>/recommendations", methods=["GET"])
def movie_ratings(phone_number):
    recommendations = recommendation_engine.get_items_for_user(phone_number)
    return (
        '[{}]'.format(','.join(recommendations)),
        200,
        {'Content-Type': 'application/json; charset=utf-8'}
    )


def create_app(spark_context, model_dir):
    global recommendation_engine

    recommendation_engine = RecommendationEngine(spark_context, model_dir)

    app = Flask(__name__)
    app.register_blueprint(main)
    return app
