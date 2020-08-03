from flask import Blueprint
from flask import current_app
from flask import jsonify
from flask import request
from flask import make_response

from nottingtable import db
from nottingtable.crawler.individual import validate_student_id
from nottingtable.crawler.individual import get_individual_timetable
from nottingtable.crawler.individual import generate_ics
from nottingtable.crawler.models import User
from nottingtable.crawler.models import Course

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/base_url', methods=('GET',))
def base_url():
    return jsonify(base_url=current_app.config['BASE_URL']), 200


@bp.route('/courses', methods=('PATCH',))
def update_courses():
    url = current_app.config['BASE_URL']
    from nottingtable.crawler.courses import get_department_list
    from nottingtable.crawler.courses import get_textspreadsheet
    name_to_id = get_department_list(url)
    results = []
    for dept_name, dept_id in name_to_id.items():
        result = get_textspreadsheet(url, dept_id, dept_name)
        results.append(result)
    return jsonify(results=results), 201


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
        timetable_list = get_individual_timetable(url, student_id, is_year1)
        if not student_record:
            db.session.add(User(student_id=student_id, timetable=timetable_list))
            db.session.commit()
        elif force_refresh != 0:
            student_record.timetable = timetable_list
            db.session.commit()

    if format_type == 'json':
        return jsonify(timetable=student_record.timetable), 200
    elif format_type == 'ical':
        response = make_response((generate_ics(student_record.timetable, current_app.config['FIRST_MONDAY']), 200))
        response.headers['Content-Disposition'] = 'attachment; filename={}.ics'.format(student_id)
        return response


@bp.route('/activity', methods=('GET',))
def show_activity():

    name = request.args.get('name')

    if not name:
        return jsonify(error='Activity Name Not Provided'), 400

    activity_records = Course.query.filter_by(activity=name).all()

    return jsonify([i.serialize for i in activity_records]), 200
