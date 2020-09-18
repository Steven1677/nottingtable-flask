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

    # initialize Flask-SQLAlchemy and db related commands
    db.init_app(app)
    app.cli.add_command(init_db_command)
    app.cli.add_command(update_course_db)
    app.cli.add_command(update_department_list)
    app.cli.add_command(update_hex_id)
    app.cli.add_command(update_master_plan_list)
    app.cli.add_command(update_year1_group)
    app.cli.add_command(update_module)
    app.cli.add_command(init_all)

    # apply the blueprints to the app
    from nottingtable import api
    from nottingtable import front_page

    app.register_blueprint(front_page.bp)
    app.register_blueprint(api.bp)

    # make / to be handled by front_page.index
    app.add_url_rule("/", endpoint='index')

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


@click.command("update-courses")
@with_appcontext
def update_course_db():
    from nottingtable.crawler import update_course_db
    update_course_db()


@click.command("update-departments")
@with_appcontext
def update_department_list():
    from nottingtable.crawler import update_department_list
    update_department_list()


@click.command("update-year1-groups")
@with_appcontext
def update_year1_group():
    """Re-get year1 group list"""
    from nottingtable.crawler import update_year1_group
    update_year1_group()


@click.command("update-master-plans")
@with_appcontext
def update_master_plan_list():
    """Re-get master plans information"""
    from nottingtable.crawler import update_master_plan_list
    update_master_plan_list()


@click.command("update-modules")
@with_appcontext
def update_module():
    """Re-get Module List"""
    from nottingtable.crawler import update_module_list
    update_module_list()


@click.command("update-hex-id")
@with_appcontext
def update_hex_id():
    """Re-get hex id list"""
    from nottingtable.crawler import update_hex_id_list
    update_hex_id_list()


@click.command("init-all")
@with_appcontext
def init_all():
    """Init everything"""
    from nottingtable.crawler import update_course_db
    from nottingtable.crawler import update_department_list
    from nottingtable.crawler import update_year1_group
    from nottingtable.crawler import update_master_plan_list
    from nottingtable.crawler import update_module_list
    from nottingtable.crawler import update_hex_id_list
    init_db()
    update_department_list()
    update_course_db()
    update_hex_id_list()
    update_year1_group()
    update_master_plan_list()
    update_module_list()
