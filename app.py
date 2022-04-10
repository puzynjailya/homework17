# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from utils.schemas import *
from apis import api

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

api.init_app(app)


# Добавляем объекты для сериализации
# movie_schema = MovieSchema()
# movies_schema = MovieSchema(many=True)
# genre_schema = GenreSchema()
# genres_schema = GenreSchema(many=True)
# director_schema = DirectorSchema()
# directors_schema = DirectorSchema(many=True)

if __name__ == '__main__':
    app.run(debug=True)
