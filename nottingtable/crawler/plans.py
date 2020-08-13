import requests
from bs4 import BeautifulSoup

from nottingtable.crawler.ics_helper import get_cal
from nottingtable.crawler.ics_helper import add_whole_course


def get_plan_textspreadsheet(url, plan_id):
    """
    Get textspreadsheet and return a dict
    :param url: base url of timetabling system
    :param plan_id: plan id
    :return: a list of timetable dicts
    """

    url = url + 'reporting/TextSpreadsheet;programme+of+study;id;{}%0D%0A?days=1-7&weeks=1-52' \
                '&periods=1-32&template=SWSCUST+programme+of+study+TextSpreadsheet'.format(plan_id)

    res = requests.get(url)
    if res.status_code != 200:
        raise NameError('Plan ID Not Found.')
    soup = BeautifulSoup(res.text, 'lxml')

    # find course table from Mon to Sun
    timetables = soup.find_all(border='1')

    # field list for storing table headers
    fields = []

    # course list for storing course dicts
    course_list = []

    for timetable in timetables:
        # mark table header
        is_header = True
        for tr in timetable('tr'):
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
                course_list.append(temp_dict)

    return course_list


def generate_ics(record, start_week_monday):
    """
    Generate ics file for plans
    :param start_week_monday: the date of first monday in the academic year
    :param record:
    :return: ics file
    """

    ics_file = get_cal()

    for course in record.timetable:
        add_whole_course(course, ics_file, start_week_monday, record.timestamp)

    return ics_file.to_ical().decode('utf-8')
