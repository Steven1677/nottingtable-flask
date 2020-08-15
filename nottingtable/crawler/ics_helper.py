from hashlib import md5

import arrow
from icalendar import Alarm
from icalendar import Calendar
from icalendar import Event


def get_cal():
    """Get a Calendar object with basic meta information"""
    ics = Calendar()
    ics.add('version', '2.0')
    ics.add('prodid', 'Nottingtable')
    return ics


def get_alarm(description, minutes):
    """
    Get an Alarm object with description displayed
    :param description: description stirng
    :param minutes: the minutes before the event (int)
    :return: an alarm object
    """
    alarm = Alarm()
    alarm['trigger'] = '-PT{}M'.format(minutes)
    alarm['action'] = 'DISPLAY'
    alarm['description'] = description
    return alarm


def weeks_generator(week_str):
    """
    Generator function for (a-b, c-d, e) format
    :param week_str: week_str from individual page
    :return: week iterator
    """
    week_periods = week_str.split(', ')
    for week_period in week_periods:
        dash_index = week_period.find('-')
        if dash_index == -1:
            week_num = int(week_period)
            yield week_num
        else:
            week_start_num = int(week_period[:dash_index])
            week_end_num = int(week_period[dash_index + 1:])
            current_week = week_start_num
            while current_week <= week_end_num:
                yield current_week
                current_week = current_week + 1


def get_event(course, date, start_time, end_time, update_time):
    """
    Get an Event object
    :param update_time: last update time
    :param end_time: end time for that course
    :param start_time: start time that course
    :param course: course dict
    :param date: course date
    :return: an event object
    """
    e = Event()
    e.add('uid', md5((course['Activity'] + date.format()).encode('utf-8')).hexdigest())
    e.add('summary', course['Module'] + ' - ' + course['Activity'])
    e.add('dtstart', date.shift(hours=start_time.hour, minutes=start_time.minute).to('utc').datetime)
    e.add('dtend', date.shift(hours=end_time.hour, minutes=end_time.minute).to('utc').datetime)
    e.add('dtstamp', update_time)
    e.add('location', course['Room'])

    if course['Staff']:
        description = course['Name of Type'] + '\n' + 'Staff: ' + course['Staff']
    else:
        description = course['Name of Type']
    e.add('description', description)

    a = get_alarm(course['Module'], 15)
    e.add_component(a)
    return e


def add_whole_course(course, ics_file, start_week_monday, last_update):
    """
    Add whole course to ics_file
    :param last_update: utc timestamp
    :param start_week_monday: arrow object
    :param course: course dict
    :param ics_file: an ics_file object
    :return: None
    """
    weekday_to_day = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6,
                      'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6}

    week_iterator = weeks_generator(course['Weeks'])
    start_time = arrow.get(course['Start'], 'H:mm')
    end_time = arrow.get(course['End'], 'H:mm')
    for week in week_iterator:
        course_date = start_week_monday.replace(tzinfo='Asia/Shanghai') \
            .shift(weeks=+(week - 1), days=+weekday_to_day[course['Day']])
        e = get_event(course, course_date, start_time, end_time, last_update)
        ics_file.add_component(e)
