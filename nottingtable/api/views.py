import re
from datetime import timedelta
import arrow
import requests

from flask import Blueprint
from flask import current_app
from flask import jsonify
from flask import request
from flask import make_response

from nottingtable import db
from nottingtable.crawler.ics_helper import weeks_generator
from nottingtable.crawler.individual import validate_student_id
from nottingtable.crawler.individual import get_individual_timetable
from nottingtable.crawler.individual import generate_ics as get_ics_individual
from nottingtable.crawler.plans import get_plan_textspreadsheet
from nottingtable.crawler.plans import generate_ics as get_ics
from nottingtable.crawler.staff import get_staff_timetable
from nottingtable.crawler.hexid import get_hex_id
from nottingtable.crawler.models import User
from nottingtable.crawler.models import Course
from nottingtable.crawler.models import Y1Group
from nottingtable.crawler.models import MasterPlan

bp = Blueprint('api', __name__, url_prefix='/api')


def add_or_update(record, key, timetable, name, force_refresh):
    """
    Insert a new user record or update exist one
    :param name: user name identifier
    :param timetable: timetable list
    :param force_refresh: if refresh is required
    :param key: the key in database
    :param record: a User record
    :return: updated record
    """

    if not record:
        db.session.add(User(sid=key, timetable=timetable, sname=name))
        db.session.commit()
    elif force_refresh:
        record.timetable = timetable
        record.timestamp = arrow.utcnow().datetime
        record.sname = name
        db.session.commit()
    record = User.query.filter_by(sid=key).first()
    return record


def _get_record(student_id, force_refresh):
    """
    Get record from cache database
    :param student_id: cache identifier
    :param force_refresh: force_refresh flag
    :return: student_record and force_refresh
    """
    student_record = User.query.filter_by(sid=student_id).first()

    # cache life time check
    if student_record:
        last_update_time = arrow.get(student_record.timestamp)
        if arrow.utcnow() - last_update_time > timedelta(days=current_app.config['CACHE_LIFE']):
            force_refresh = 1
    else:
        force_refresh = 1

    return student_record, force_refresh


def output_timetable(format_type, record, ics_func, ics_name):
    """
    Return the timetable
    :param format_type: output format json/ical
    :param record: cached user record
    :param ics_func: the function to get ics file
    :param ics_name: ics filename
    :return: ics file or json response
    """
    if format_type == 'json':
        return jsonify(timetable=record.timetable, last_update=record.timestamp, name=record.sname), 200
    elif format_type == 'ical':
        response = make_response((ics_func(record, current_app.config['FIRST_MONDAY']), 200))
        response.headers['Content-Disposition'] = 'attachment; filename={}'.format('"' + ics_name + '.ics"')
        response.headers['Content-Type'] = 'text/calendar charset=utf-8'
        return response


def get_record(sid, force_refresh, crawler_func, crawler_args):
    """
    Get proper record
    :param sid: id
    :param force_refresh: force_refresh flag
    :param crawler_func: the function the extract information form the crawler part
    :param crawler_args: args for crawler func
    :return: record
    """
    s_record, force_refresh = _get_record(sid, force_refresh)

    if not s_record or force_refresh:
        url = current_app.config['BASE_URL']
        crawler_args['url'] = url
        list_timetable, name = crawler_func(**crawler_args)

        s_record = add_or_update(s_record, sid, list_timetable, name, force_refresh)

    return s_record


def get_current_semester():
    """
    Get the current semester via month
    :return 1 or 2
    """
    month = arrow.utcnow().date().month
    return 2 if 2 <= month <= 8 else 1


def get_max_week_number(course):
    """
    Get the max week number from a course object
    :param course: course object
    :return: last week number included in the course
    """
    weeks = course.get("Weeks")
    last_period = weeks.split(', ')[-1]
    if '-' not in last_period:
        return int(last_period)
    else:
        return int(last_period.split('-')[-1])


def filter_semester(semester, record):
    """
    Filter record timetable via semester
    :param semester: 1 or 2 or other (treated as all)
    :param record: a timetable list
    :return: a timetable list
    """
    def filter_func(course_obj):
        if semester == 1:
            return get_max_week_number(course_obj) < 20
        elif semester == 2:
            return get_max_week_number(course_obj) > 20
        else:
            return True

    return list(filter(filter_func, record))


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

    if not validate_student_id(student_id, is_year1=is_year1):
        return jsonify(error='Group Name Invalid'), 400

    force_refresh = request.args.get('force-refresh') or 0

    student_hex_id = get_hex_id(student_id)

    semester = request.args.get('semester') or get_current_semester()
    if semester != 1 and semester != 2 and semester != 3:
        semester = get_current_semester()

    try:
        student_record = get_record(student_id, force_refresh,
                                    get_individual_timetable, {'student_id': student_hex_id, 'is_year1': is_year1})
    except (NameError, AttributeError):
        return jsonify(error='Student ID/Group Not Found'), 404

    student_record.timetable = filter_semester(semester, student_record.timetable)
    return output_timetable(format_type, student_record, get_ics_individual, student_id)


@bp.route('/plan/<format_type>', methods=('GET',))
def get_plan_data(format_type):
    if format_type != 'json' and format_type != 'ical':
        return jsonify(error='Not Found'), 404

    plan_id = request.args.get('plan')
    if not plan_id:
        return jsonify(error='Plan not Provided'), 400

    force_refresh = request.args.get('force-refresh') or 0

    semester = request.args.get('semester') or get_current_semester()
    if semester != 1 and semester != 2 and semester != 3:
        semester = get_current_semester()

    try:
        student_record = get_record(plan_id, force_refresh,
                                    get_plan_textspreadsheet, {'plan_id': plan_id})
    except NameError:
        return jsonify(error='Plan ID Not Found'), 404

    student_record.timetable = filter_semester(semester, student_record.timetable)

    return output_timetable(format_type, student_record, get_ics, plan_id)


@bp.route('/staff/<format_type>', methods=('GET',))
def get_staff_data(format_type):
    if format_type != 'json' and format_type != 'ical':
        return jsonify(error='Not Found'), 404

    name = request.args.get('name')
    if not name:
        return jsonify(error='Staff Name not Provided'), 400

    force_refresh = request.args.get('force-refresh') or 0

    semester = request.args.get('semester') or get_current_semester()
    if semester != 1 and semester != 2 and semester != 3:
        semester = get_current_semester()

    try:
        staff_record = get_record(name, force_refresh,
                                  get_staff_timetable, {'name': name})
    except NameError:
        return jsonify(error='Staff Name Not Found'), 404

    staff_record.timetable = filter_semester(semester, staff_record.timetable)
    return output_timetable(format_type, staff_record, get_ics, name)


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
    code = request.args.get('code')

    if not name and not code:
        return jsonify(error='Module Name/Code Not Provided'), 400

    if code and not re.match(r'[a-zA-Z0-9]{8}', code):
        return jsonify(error='Invalid Module Code'), 400

    if name:
        module_records = Course.query.filter_by(module=name).all()
    else:
        module_records = Course.query \
            .filter(Course.activity.contains(code[:3]), Course.activity.contains(code[4:])).all()

    if not module_records:
        return jsonify(error='Module Not Found'), 404

    return jsonify([i.serialize for i in module_records]), 200


@bp.route('/multiple-schedule', methods=('GET',))
def multiple_schedule():
    str_participants = request.args.get('people')
    date = request.args.get('date')

    list_participants = str_participants.split(',')
    if not list_participants or len(list_participants) > 10:
        return jsonify(error='Number of participants exceeds the maximum.'), 400

    try:
        date = arrow.get(date, 'YYYY-MM-DD')
    except arrow.ParserError:
        return jsonify(error='Invalid date format.'), 400

    first_week = current_app.config['FIRST_MONDAY'].isocalendar()[1]
    date_week = date.isocalendar()[1]
    semester_week = date_week - first_week + 1
    week_day = arrow.locales.EnglishLocale.day_abbreviations[date.isocalendar()[2]]

    # From 8:00 to 22:00, 30 minutes per period
    time_period = [True] * 28

    for participant in list_participants:
        if 'Year 1' in participant:
            is_year1 = True
        else:
            is_year1 = False
        try:
            record = get_record(participant, 0,
                                get_individual_timetable, {'is_year1': is_year1, 'student_id': participant})
        except NameError:
            return jsonify(error='{} is Invalid'.format(participant)), 400

        timetable = record.timetable
        for course in timetable:
            if course['Day'] != week_day:
                continue
            if semester_week not in list(weeks_generator(course['Weeks'])):
                continue
            start_time = arrow.get(course['Start'], 'H:mm')
            start_time_index = (start_time.hour - 8) * 2 + int(start_time.minute / 30)
            end_time = arrow.get(course['End'], 'H:mm')
            end_time_index = (end_time.hour - 8) * 2 + int(end_time.minute / 30)
            for i in range(start_time_index, end_time_index):
                time_period[i] = False

    def time_index_to_time(x):
        return str(x // 2 + 8) + ':00' if x % 2 == 0 else str(x // 2 + 8) + ':30'

    res_time_period = []
    cur_start = -1
    for index, flag in enumerate(time_period):
        if flag and cur_start == -1:
            cur_start = index
        elif not flag and cur_start != -1:
            res_time_period.append(time_index_to_time(cur_start) + '-' + time_index_to_time(index))
            cur_start = -1
    if cur_start != -1:
        res_time_period.append(time_index_to_time(cur_start) + '-' + time_index_to_time(28))

    return jsonify(free_time=res_time_period)


@bp.route('/year1-list', methods=('GET',))
def show_year1_list():
    year1_list = Y1Group.query.all()
    return jsonify([i.group for i in year1_list]), 200


@bp.route('/master-plan-list', methods=('GET',))
def show_master_plan_list():
    master_list = MasterPlan.query.all()
    return jsonify({i.plan_name: i.plan_id for i in master_list})


@bp.errorhandler(requests.exceptions.ConnectionError)
def handle_origin_site_down(e):
    return jsonify(error='Official Website is closed.'), 404
