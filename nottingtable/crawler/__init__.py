import click
from nottingtable import db
from flask import current_app


def update_course_db():
    """Re-get courses information"""
    from nottingtable.crawler.models import Course
    Course.__table__.drop(db.engine)
    Course.__table__.create(db.engine)
    url = current_app.config['BASE_URL']
    from nottingtable.crawler.courses import get_department_list
    from nottingtable.crawler.courses import get_department_courses
    name_to_id = get_department_list(url)
    for dept_name, dept_id in name_to_id.items():
        result = get_department_courses(url, dept_id, dept_name)
        click.echo(result)
    click.echo('Courses Updated!')


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


def update_module_list():
    """Re-get Module List"""
    from nottingtable.crawler.models import Module
    Module.__table__.drop(db.engine)
    Module.__table__.create(db.engine)
    from nottingtable.crawler.filter_parser import parse_modulearray
    url = current_app.config['BASE_URL']
    name_to_id = parse_modulearray(url)
    for name, m_id in name_to_id.items():
        db.session.add(Module(module_name=name, module_id=m_id))
    db.session.commit()
    click.echo('Module List Updated!')