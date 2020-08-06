from flask import Blueprint
from flask import current_app
from flask import jsonify
from flask import request
from flask import make_response

from nottingtable import db
from nottingtable.crawler.individual import validate_student_id
from nottingtable.crawler.individual import get_individual_timetable
from nottingtable.crawler.individual import generate_ics as get_ics_individual
from nottingtable.crawler.plans import get_plan_textspreadsheet
from nottingtable.crawler.plans import generate_ics as get_ics_plan
from nottingtable.crawler.models import User
from nottingtable.crawler.models import Course

bp = Blueprint('api', __name__, url_prefix='/api')


def add_or_update(record, key, value, force_refresh):
    """
    Insert a new user record or update exist one
    :param force_refresh: if refresh is required
    :param value: the value ready for insertion and update
    :param key: the key in database
    :param record: a User record
    :return: updated record
    """
    if not record:
        db.session.add(User(student_id=key, timetable=value))
        db.session.commit()
    elif force_refresh != 0:
        record.timetable = value
        db.session.commit()
    record = User.query.filter_by(student_id=key).first()
    return record


def output_timetable(format_type, timetable, ics_func, ics_name):
    """
    Return the timetable
    :param format_type: output format json/ical
    :param timetable: timetable dicts list
    :param ics_func: the function to get ics file
    :param ics_name: ics filename
    :return: ics file or json response
    """
    if format_type == 'json':
        return jsonify(timetable=timetable), 200
    elif format_type == 'ical':
        response = make_response((ics_func(timetable, current_app.config['FIRST_MONDAY']), 200))
        response.headers['Content-Disposition'] = 'attachment; filename={}'.format('"' + ics_name + '.ics"')
        return response


@bp.route('/individual/<format_type>', methods=('GET',))
def get_individual_data(format_type):
    if format_type != 'json' and format_type != 'ical':
        return jsonify(error='Not Found'), 404
    if request.args.get('id'):
        student_id = request.args.get('id')
        is_year1 = False
    elif request.args.get('group'):
        student_id = request.args.get('group')
        is_year1 = True
    else:
        return jsonify(error='Student ID or Group Name Not Provided'), 400

    if not is_year1:
        if not validate_student_id(student_id, is_year1=is_year1):
            return jsonify(error='Student ID Invalid'), 400
    else:
        if not validate_student_id(student_id, is_year1=is_year1):
            return jsonify(error='Group Name Invalid'), 400

    force_refresh = request.args.get('force-refresh') or 0

    student_record = User.query.filter_by(student_id=student_id).first()

    if not student_record or force_refresh != 0:
        url = current_app.config['BASE_URL']
        try:
            timetable_list = get_individual_timetable(url, student_id, is_year1)
        except NameError:
            return jsonify(error='Student ID/Group Invalid'), 400

        student_record = add_or_update(student_record, student_id, timetable_list, force_refresh)

    return output_timetable(format_type, student_record.timetable, get_ics_individual, student_id)


@bp.route('/plan/<format_type>', methods=('GET',))
def get_plan_data(format_type):

    if format_type != 'json' and format_type != 'ical':
        return jsonify(error='Not Found'), 404

    plan_id = request.args.get('plan')
    if not plan_id:
        return jsonify(error='Plan not Provided'), 400

    force_refresh = request.args.get('force-refresh') or 0

    student_record = User.query.filter_by(student_id=plan_id).first()

    if not student_record or force_refresh != 0:
        url = current_app.config['BASE_URL']
        try:
            timetable_list = get_plan_textspreadsheet(url, plan_id)
        except NameError:
            return jsonify(error='Plan ID Invalid'), 400

        student_record = add_or_update(student_record, plan_id, timetable_list, force_refresh)

    return output_timetable(format_type, student_record.timetable, get_ics_plan, plan_id)


@bp.route('/activity', methods=('GET',))
def show_activity():
    name = request.args.get('name')

    if not name:
        return jsonify(error='Activity Name Not Provided'), 400

    activity_records = Course.query.filter_by(activity=name).all()

    return jsonify([i.serialize for i in activity_records]), 200


@bp.route('/module', methods=('GET',))
def show_module():
    name = request.args.get('name')

    if not name:
        return jsonify(error='Module Name Not Provided'), 400

    module_records = Course.query.filter_by(module=name).all()

    return jsonify([i.serialize for i in module_records]), 200