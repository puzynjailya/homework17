from flask_restx import Api
from apis.movies import api as movie_ns
from apis.genres import api as genre_ns
from apis.directors import api as director_ns

api = Api(title='Апи для ДЗ17', version=1.0, description='API для выдачи данных по запросам к БД')

api.add_namespace(movie_ns)
api.add_namespace(genre_ns)
api.add_namespace(director_ns)
