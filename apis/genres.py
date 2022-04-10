from flask_restx import Resource, Namespace
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort
from utils.schemas import GenreSchema
from utils.models import Genre
import logging
from marshmallow.exceptions import MarshmallowError, ValidationError

db = SQLAlchemy()

api = Namespace('genres', description='Эндпойнт жанров')

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

logging.basicConfig(filename='genres.log', level=logging.INFO)

@api.route('/')
class GenresViewer(Resource):

    def get(self):
        genres = db.session.query(Genre).all()
        serialized_genres = genres_schema.dump(genres)
        logging.info('Запрошена страница со всеми жанрами')
        return jsonify(serialized_genres)

    def post(self):
        data = request.json
        try:
            serialized_data = genre_schema.dump(data)
            genre = Genre(**serialized_data)
            db.session.add(genre)
            db.session.commit()
        except (MarshmallowError, ValidationError) as e:
            logging.warning(msg=f'Ошибка сериализации при загрузке: {e}')
            return 'Ошибка сериализации', 500

        return '', 201

@api.route('/<int:gid>')
class GenreViewer(Resource):

    def get_id_data(self, gid):

        # Выполняем запрос к БД
        query = db.session.query(Genre).get(gid)
        # Если нет такого id
        if not query:
            abort(404)
        return query

    def get(self, gid):
        result = self.get_id_data(gid)
        serialized_data = genre_schema.dump(result)
        return jsonify(serialized_data)

    def put(self, gid):
        # Получаем данные по id
        result = self.get_id_data(gid)

        # Получаем данные json и сериализуем их (на всякий случай)
        data = request.json
        serialized_data = genre_schema.dump(data)

        # Заменяем их и сохраняем в БД
        result.name = serialized_data['name']
        db.session.add(result)
        db.session.commit()
        return '', 204

    def delete(self, gid):
        # Получаем данные по id
        result = self.get_id_data(gid)
        # Удаляем данные
        db.session.delete(result)
        db.session.commit()
        return '', 204



