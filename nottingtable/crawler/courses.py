import requests
from bs4 import BeautifulSoup

from nottingtable import db
from nottingtable.crawler.models import Course
from nottingtable.crawler.models import Department


def get_department_list(url):
    """
    Get department List
    :param url: base url
    :return: name to id dict
    """

    if not Department.query.first():
        from nottingtable.crawler.filter_parser import parse_department_list
        name_to_id = parse_department_list(url)
        for dept_name, dept_id in name_to_id.items():
            db.session.add(Department(department_id=dept_id, department_name=dept_name))
        db.session.commit()
        return name_to_id
    else:
        depts = Department.query.all()
        name_to_id = {}
        for dept in depts:
            name_to_id[dept.department_name] = dept.department_id
        return name_to_id


def get_textspreadsheet(url, dept_id, dept_name):
    """
    Get department course table
    :param url: base url
    :param dept_id: department id str
    :param dept_name: department name str
    :return: None
    """
    exec_dept_list = ['Central']
    if dept_name in exec_dept_list:
        return dept_name + ' is excluded!'
    exec_type_list = ['booking', 'wrb-web bookings', 'wrb-provisional', 'booking']
    url = url + 'reporting/TextSpreadsheet;department;id;{}%0D%0A?days=1-7&weeks=1-52&periods=1-32' \
                '&template=SWSCUST+department+TextSpreadsheet&height=100&week=100'.format(dept_id)
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception('Course not Found')
    courses = resp.text
    courses_soup = BeautifulSoup(courses, 'lxml')
    courses_tables = courses_soup.find_all(border='1')
    fields = []
    course_list = []
    for courses_table in courses_tables:
        is_header = True
        for tr in courses_table('tr'):
            if is_header and not fields:
                for td in tr('td'):
                    fields.append(td.get_text())
                is_header = False
            elif is_header:
                is_header = False
                continue
            else:
                course_info = []
                for td in tr('td'):
                    content = td.get_text().replace('\xa0', '').replace('  ', ' ')
                    course_info.append(content)
                temp_dict = dict(zip(fields, course_info))
                if temp_dict['Name of Type'].lower() in exec_type_list:
                    continue
                course_list.append(temp_dict)
        if not course_list:
            return dept_name + ' is empty!'
    for course in course_list:
        course_record = Course(activity=course['Activity'],
                               module=course['Module'],
                               type=course['Size'],
                               day=course['Day'],
                               start=course['Start'],
                               end=course['End'],
                               duration=course['Duration'],
                               staff=course['Staff'],
                               room=course['Room'],
                               weeks=course['Weeks'])
        db.session.add(course_record)
    db.session.commit()
    return dept_name + ' is finished.'
