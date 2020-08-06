import os
import arrow


class Config(object):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BASE_URL = 'http://timetablingunnc.nottingham.ac.uk:8005/'
    FIRST_MONDAY = arrow.get('2019-09-16')  # YYYY-MM-DD
    YEAR1_PDF_URL = 'https://www.nottingham.edu.cn/en/academicservices/documents/year-1-student-timetable-1920-spring-semester-20200429v4.pdf'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user@localhost/foo'
    BASE_URL = 'http://timetablingunnc.nottingham.ac.uk:8005/'


class DevelopmentConfig(Config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

