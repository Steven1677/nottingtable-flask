import os
import arrow


class Config(object):
    DEBUG = False
    # DATABASE_URI=mysql+pymysql://database_user:database_password@database_address/database_name
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Default url for timetabling service
    BASE_URL = 'http://timetablingunnc.nottingham.ac.uk:8005/'  # Last '/' cannot be omitted
    FIRST_MONDAY = arrow.get('2021-09-13')  # YYYY-MM-DD format

    # Default url for year1 group list
    YEAR1_PDF_URL = 'https://www.nottingham.edu.cn/en/academicservices/documents/2020-2021-s2-year-1-student-timetable.pdf'

    # integer, the cache lifetime in database, unit: day
    CACHE_LIFE = 365

    # Server domain
    SERVER_NAME = os.environ.get('SERVER_NAME')


class ProductionConfig(Config):
    BASE_URL = 'http://timetablingunnc.nottingham.ac.uk:8005/'


class DevelopmentConfig(Config):
    DEBUG = True
