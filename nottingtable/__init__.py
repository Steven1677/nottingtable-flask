import click
from flask import Flask
from flask import current_app
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
    app.cli.add_command(update_master_plan_list)
    app.cli.add_command(update_year1_group)

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
    """Re-get courses information"""
    from nottingtable.crawler.models import Course
    Course.__table__.drop(db.engine)
    Course.__table__.create(db.engine)
    url = current_app.config['BASE_URL']
    from nottingtable.crawler.courses import get_department_list
    from nottingtable.crawler.courses import get_textspreadsheet
    name_to_id = get_department_list(url)
    for dept_name, dept_id in name_to_id.items():
        result = get_textspreadsheet(url, dept_id, dept_name)
        click.echo(result)
    click.echo('Courses Updated!')


@click.command("update-departments")
@with_appcontext
def update_department_list():
    """Re-get departments information"""
    from nottingtable.crawler.models import Department
    Department.__table__.drop(db.engine)
    Department.__table__.create(db.engine)
    url = current_app.config['BASE_URL']
    from nottingtable.crawler.courses import get_department_list
    name_to_id = get_department_list(url)
    for k, v in name_to_id.items():
        click.echo(k + ': ' + v)
    click.echo('Department List Updated!')


@click.command("update-master-plans")
@with_appcontext
def update_master_plan_list():
    """Re-get master plans information"""
    from nottingtable.crawler.models import MasterPlan
    MasterPlan.__table__.drop(db.engine)
    MasterPlan.__table__.create(db.engine)
    url = current_app.config['BASE_URL']
    from nottingtable.crawler.filter_parser import parse_pgt_programmearray
    name_to_id = parse_pgt_programmearray(url)
    for plan_name, plan_id in name_to_id.items():
        db.session.add(MasterPlan(plan_id=plan_id, plan_name=plan_name))
        click.echo(plan_name + ': ' + plan_id)
    db.session.commit()
    click.echo('Master Plan List Updated!')


@click.command("update-year1-groups")
@with_appcontext
def update_year1_group():
    """Re-get Year 1 group names"""
    from nottingtable.crawler.models import Y1Group
    Y1Group.__table__.drop(db.engine)
    Y1Group.__table__.create(db.engine)
    from nottingtable.crawler.year1_group import get_year1_group_list
    group_names = get_year1_group_list()
    for group_name in group_names:
        db.session.add(Y1Group(group=group_name))
    db.session.commit()
    click.echo('Y1 Group List Updated!')
