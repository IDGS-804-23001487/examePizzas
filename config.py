class Config(object):
    SECRET_KEY = "PizzaSecreta2024"
    SESSION_COOKIE_SECURE = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:3306/examPizzas'
    SQLALCHEMY_TRACK_MODIFICATIONS = False