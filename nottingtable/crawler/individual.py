import re
import requests
from bs4 import BeautifulSoup

from nottingtable import db
from nottingtable.crawler.ics_helper import get_cal
from nottingtable.crawler.ics_helper import add_whole_course
from nottingtable.crawler.courses import add_course
from nottingtable.crawler.modules import get_module_activity
from nottingtable.crawler.models import Course


def validate_student_id(student_id, is_year1=False):
    """
    Get and verify student id
    :param student_id:
    :param is_year1: whether the student is year 1 student
    :return: a boolean
    """
    if not is_year1:
        if not re.match(r'\d{8}', student_id):
            return False
        else:
            return True
    else:
        if not re.match(r'Year 1-.*-\d{2}.*', student_id):
            return False
        else:
            return True


def get_time_periods():
    """
    Generate time periods list from 8:00 to 22:00
    :return: time periods list
    """
    periods = []
    for h in range(8, 22):
        for m in range(2):
            periods.append(str(h) + ':' + ('00' if m == 0 else '30'))
    periods.append('22:00')
    return periods


def get_individual_timetable(url, student_id, is_year1=False):
    """
    Get individual timetable
    :param url: base url of timetabling server
    :param student_id: student id or group id for year 1
    :param is_year1: whether the student is year 1 student
    :return: timetable dict for the student
    """
    url = url + 'reporting/individual;Student+Sets;{};{}?template=Student+Set+Individual' \
                '&weeks=1-52&days=1-7&periods=1-32'.format("name" if is_year1 else "id", student_id)
    res = requests.get(url)
    if res.status_code != 200:
        raise NameError('Student ID Not Found.')
    soup = BeautifulSoup(res.text, 'lxml')
    name = soup.find('span', class_='header-1-1-1').get_text()
    if not is_year1:
        name = name.split('/')
        name = name[-2] + ' ' + name[-1]
    timetable = soup.find(class_='grid-border-args')
    periods = get_time_periods()
    timetable_list = []
    is_time_period = True
    weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    current_weekday = ''
    for tr in timetable('tr'):
        if is_time_period:
            is_time_period = False
            continue
        else:
            time_period_index = 0
            for td in tr.children:
                if td.name != 'td':
                    continue
                if not td.has_attr('rowspan'):
                    time_period_index = time_period_index + 1
                    continue
                if td.get_text() in weekdays:
                    current_weekday = td.get_text()
                    continue
                assert td['rowspan'] == '1'
                course_info = td.find_all('table')
                activity_id = course_info[0].tr.td.get_text().replace('  ', ' ')
                course_id = course_info[1].tr.td.get_text()
                third_row_info = course_info[2].tr.find_all('td')
                room = third_row_info[0].get_text()
                staff = third_row_info[1].get_text()
                weeks = third_row_info[2].get_text()
                start_time = periods[time_period_index]
                time_period_index = time_period_index + int(td['colspan'])
                end_time = periods[time_period_index]

                module = Course.query.filter_by(activity=activity_id).first()
                if not module:
                    # For a few newly added course, use hot update via Courses API
                    # But re-craw courses table is more recommended
                    new_course = get_module_activity(re.match(r'(https?://.*?/)', url).group(1), course_id, activity_id)
                    new_course_record = add_course(new_course)
                    db.session.commit()
                    module = new_course_record
                module = module.module

                timetable_list.append({
                    'Activity': activity_id,
                    'Course': course_id,
                    'Module': module,
                    'Room': room,
                    'Staff': staff,
                    'Start': start_time,
                    'End': end_time,
                    'Weeks': weeks,
                    'Day': current_weekday
                })
    return timetable_list, name


def generate_ics(record, start_week_monday):
    """
    Pair course activity and course info
    :param record: timetable list from individual web page
    :param start_week_monday: arrow object
    :return: ics_file
    """
    ics_file = get_cal()
    for course in record.timetable:
        # course is from individual webpage
        # course_info is from course page cached in the database
        course_info = Course.query.filter_by(activity=course['Activity']).first()
        course['Module'] = course_info.module
        course['Name of Type'] = course_info.type
        add_whole_course(course, ics_file, start_week_monday, record.timestamp)
    return ics_file.to_ical().decode('utf-8')
