from flask import Flask, render_template, redirect, url_for
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from config import DevelopmentConfig
from models import db
from pizzeria import pizzeria

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.register_blueprint(pizzeria)
db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect()
csrf.init_app(app)

@app.route("/")
def index():
    return redirect(url_for('pizzeria.index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()