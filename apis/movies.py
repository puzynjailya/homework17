from flask_restx import Resource, Namespace
from flask import request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from utils.models import Movie
from utils.schemas import MovieSchema
import logging
from marshmallow.exceptions import ValidationError, MarshmallowError

db = SQLAlchemy()

api = Namespace('movies', description='Поиск по фильмам')

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

logging.basicConfig(filename="movies.log", level=logging.INFO)


@api.route('/')
class MoviesViewer(Resource):

    def get(self):

        # Ловим query параметры
        director = request.args.get('director_id')
        genre = request.args.get('genre_id')

        # Проверяем на заданный только по director_id
        if director and not genre:
            result = db.session.query(Movie).filter(Movie.director_id == director).all()
            # Если запрос к БД ничего не нашёл
            if not result:
                return f'По запросу фильмов с режиссером id {director} ничего не найдено!', 404

            # Логируем события
            logging.info(f'Запрошена страница фильмов с режиссером с id = {director}')

            # Возвращаем сериализованные данные
            return jsonify(movies_schema.dump(result))

        # Проверяем на заданный только по genre_id
        if genre and not director:
            result = db.session.query(Movie).filter(Movie.genre_id == genre).all()
            # Если запрос к БД ничего не нашёл
            if not result:
                logging.warning('Страница не найдена')
                return f'По запросу фильмов с режиссером id {director} ничего не найдено!', 404

            # Логируем события
            logging.info(f'Запрошена страница фильмов с жанром с id = {genre}')

            # Возвращаем сериализованные данные
            return jsonify(movies_schema.dump(result))

        # Проверяем на заданные оба параметра
        if director and genre:
            result = db.session.query(Movie).filter(and_(Movie.director_id == director,
                                                         Movie.genre_id == genre)).all()
            if not result:
                return 'Ищите лучше', 404

            # Логируем события
            logging.info(f'Запрошена страница фильмов с genre_id = {genre} и director_id = {director}')

            return jsonify(movies_schema.dump(result))

        # Если query параметров нет, то делаем обычный простой запрос
        result = db.session.query(Movie).all()
        logging.info('Запрошена страница со всеми фильмами')
        return jsonify(movies_schema.dump(result))

    def post(self):
        data = request.json
        try:
            serialized_data = movie_schema.load(data)
            movie = Movie(**serialized_data)
            db.session.add(movie)
            db.session.commit()
            return '', 201
        except (MarshmallowError, ValidationError) as e:
            logging.warning(msg=f'Ошибка сериализации при загрузке: {e}')
            return 'Ошибка сериализации', 500


@api.route('/<int:mid>')
class MovieViewer(Resource):

    def get_id_data(self, mid):

        # Выполняем запрос к БД
        query = db.session.query(Movie).get(mid)
        # Если нет такого id
        if not query:
            abort(404)
        return query

    def get(self, mid):
        # Выполняем запрос к БД
        result = self.get_id_data(mid)

        # Логируем события
        logging.info(f'Запрошена страница со фильмом с id = {mid}')
        return jsonify(movie_schema.dump(result))

    def delete(self, mid):
        # Выполняем запрос к БД
        result = db.session.query(Movie).get(mid)

        # Если нет такого id
        if not result:
            return f"Запись с таким id : {mid} не найдена!", 404

        db.session.delete(result)
        db.session.commit()
        return '', 204

    def put(self, mid):
        # Получаем данные по id
        movie = self.get_id_data(mid)

        # Получаем данные json и проводим сериализацию
        data = request.json
        data = movie_schema.dump(data)

        # Заменяем данные
        movie.title = data['title']
        movie.description = data['description']
        movie.trailer = data['trailer']
        movie.year = data['year']
        movie.rating = data['rating']
        movie.genre_id = data['genre_id']
        movie.director_id = data['director_id']

        # Добавляем в БД
        db.session.add(movie)
        db.session.commit()
        return "", 204