from nottingtable.crawler.text_spread_sheet import extract_text_spread_sheet
from nottingtable.crawler.ics_helper import get_cal
from nottingtable.crawler.ics_helper import add_whole_course


def get_plan_textspreadsheet(url, plan_id):
    """
    Get plan textspreadsheet and return a list of dicts
    :param url: base url of timetabling system
    :param plan_id: plan id
    :return: a list of timetable dicts and plan name
    """

    url = url + 'reporting/TextSpreadsheet;programme+of+study;id;{}%0D%0A?days=1-7&weeks=1-52' \
                '&periods=1-32&template=SWSCUST+programme+of+study+TextSpreadsheet'.format(plan_id)

    course_list, name = extract_text_spread_sheet(url, lambda _: False)

    return course_list, name


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
