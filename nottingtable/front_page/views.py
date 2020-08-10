from flask import Blueprint
from flask import current_app
from flask import request
from flask import render_template

from nottingtable.api.views import add_or_update
from nottingtable.api.views import get_record
from nottingtable.crawler.individual import get_individual_timetable
from nottingtable.crawler.plans import get_plan_textspreadsheet
from nottingtable.crawler.models import Y1Group
from nottingtable.crawler.models import MasterPlan

bp = Blueprint('front', __name__, template_folder='templates')


@bp.route('/', methods=('GET',))
def index():
    return render_template('index.html')


@bp.route('/year-24', methods=('GET',))
def show_year_24():
    return render_template('year-24.html')


@bp.route('/year-1', methods=('GET',))
def show_year_1():
    """
    Render page for year1 selection page
    :return: rendered page with selection list
    """

    group_list = Y1Group.query.all()
    return render_template('year-1.html', group_list=group_list)


@bp.route('/plan', methods=('GET',))
def show_plan():
    """
    Render page for master students
    :return: rendered page with selection list
    """

    plan_list = MasterPlan.query.all()
    return render_template('plan.html', plan_list=plan_list)


@bp.route('/check', methods=('POST',))
def check_cal():
    """Show the list of all calendar events"""

    def get_link():
        """Generate download links"""
        if data['type'] == 'year-1':
            return '/api/individual/ical?group={}'.format(student_id)
        elif data['type'] == 'year-24':
            return '/api/individual/ical?id={}'.format(student_id)
        elif data['type'] == 'plan':
            return '/api/plan/ical?plan={}'.format(student_id)

    # Defense
    types = ['year-1', 'year-24', 'plan']
    data = request.form
    if not data.get('type') in types:
        return render_template('check.html', timetable=None)

    force_refresh = data.get('force-refresh')
    student_id = data.get('id') or data.get('group') or data.get('plan')
    record, force_refresh = get_record(student_id, force_refresh)
    fields = ['Activity', 'Module', 'Day', 'Staff', 'Start', 'End', 'Weeks']

    if force_refresh:
        url = current_app.config['BASE_URL']
        if data['type'] == 'year-1':
            try:
                timetable = get_individual_timetable(url, student_id, True)
            except NameError:
                return render_template('check.html', timetable=None)
        elif data['type'] == 'year-24':
            try:
                timetable = get_individual_timetable(url, student_id, False)
            except NameError:
                return render_template('check.html', timetable=None)
        elif data['type'] == 'plan':
            try:
                timetable = get_plan_textspreadsheet(url, student_id)
            except NameError:
                return render_template('check.html', timetable=None)
        else:
            return render_template('check.html', timetable=None)
        add_or_update(record, student_id, timetable, force_refresh)
        link = get_link()
        return render_template('check.html', fields=fields, timetable=timetable, link=link)
    else:
        return render_template('check.html', fields=fields, timetable=record.timetable, link=get_link())
