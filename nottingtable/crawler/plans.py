import requests
from hashlib import md5
from bs4 import BeautifulSoup
from icalendar import Calendar, Event, Alarm
import arrow

from nottingtable.crawler.individual import weeks_generator


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

    weekday_to_day = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6}

    ics_file = Calendar()
    ics_file.add('version', '2.0')
    ics_file.add('prodid', 'Nottingtable')
    for course in record.timetable:

        week_iterator = weeks_generator(course['Weeks'])
        start_time = arrow.get(course['Start'], 'H:mm')
        end_time = arrow.get(course['End'], 'H:mm')

        for week in week_iterator:
            course_date = start_week_monday.replace(tzinfo='Asia/Shanghai') \
                .shift(weeks=+(week - 1), days=+weekday_to_day[course['Day']])
            e = Event()
            e.add('uid', md5((course['Activity']+course_date.format()).encode('utf-8')).hexdigest())
            e.add('summary', course['Module'] + ' - ' + course['Activity'])
            e.add('dtstart', course_date.shift(hours=start_time.hour, minutes=start_time.minute).to('utc').datetime)
            e.add('dtend', course_date.shift(hours=end_time.hour, minutes=end_time.minute).to('utc').datetime)
            e.add('dtstamp', record.timestamp)
            e.add('location', course['Room'])
            e.add('description', course['Name of Type'] + '\r\n' + 'Staff: ' + course['Staff'])
            a = Alarm()
            a['trigger'] = '-PT15M'
            a['action'] = 'DISPLAY'
            a['description'] = course['Module']
            e.add_component(a)
            ics_file.add_component(e)

    return ics_file.to_ical().decode('utf-8')
