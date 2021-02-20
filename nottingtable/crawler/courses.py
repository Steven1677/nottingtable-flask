from nottingtable import db
from nottingtable.crawler.text_spread_sheet import extract_text_spread_sheet
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


def add_course(course_dict):
    course_record = Course(activity=course_dict['Activity'],
                           module=course_dict['Module'],
                           type=course_dict['Name of Type'],
                           day=course_dict['Day'],
                           start=course_dict['Start'],
                           end=course_dict['End'],
                           duration=course_dict['Duration'],
                           staff=course_dict['Staff'],
                           room=course_dict['Room'],
                           weeks=course_dict['Weeks'])
    db.session.add(course_record)
    return course_record


def get_department_courses(url, dept_id, dept_name):
    """
    Get department course table
    :param url: base url
    :param dept_id: department id str
    :param dept_name: department name str
    :return: department collection status string
    """
    exec_dept_list = ['Central']
    if dept_name in exec_dept_list:
        return dept_name + ' is excluded!'
    exec_type_list = ['booking', 'wrb-web bookings', 'wrb-provisional', 'booking']
    url = url + 'reporting/TextSpreadsheet;department;id;{}%0D%0A?days=1-7&weeks=1-52&periods=1-32' \
                '&template=SWSCUST+department+TextSpreadsheet&height=100&week=100'.format(dept_id)

    def exclude_filter(course_dict):
        return course_dict['Name of Type'].lower() in exec_type_list
    try:
        course_list, _ = extract_text_spread_sheet(url, exclude_filter)
    except NameError:
        return dept_name + ' CRAWLING FAILED !!!'

    if not course_list:
        return dept_name + ' is empty!'

    duplicated = list()
    for course in course_list:
        if ',' in course['Day']:
            if all([ele["Activity"] != course["Activity"] for ele in duplicated]):
                days = course['Day'].split(',')
                for day in days:
                    course_tmp = course
                    course_tmp['Day'] = day
                    add_course(course_tmp)
                duplicated.append(course)
        else:
            add_course(course)
    db.session.commit()
    return dept_name + ' is finished.'
