import click
from flask import Flask
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy

from nottingtable import config

db = SQLAlchemy()


def create_app(development_config=True):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # use development config or production config
    if development_config:
        app.config.from_object(config.DevelopmentConfig)
    else:
        app.config.from_object(config.ProductionConfig)

    # initialize Flask-SQLAlchemy and the init-db command
    db.init_app(app)
    app.cli.add_command(init_db_command)

    # apply the blueprints to the app
    from nottingtable import api

    app.register_blueprint(api.bp)

    return app


def init_db():
    import nottingtable.crawler.models
    db.drop_all()
    db.create_all()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")
