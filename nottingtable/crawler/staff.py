from nottingtable.crawler.text_spread_sheet import extract_text_spread_sheet


def get_staff_timetable(url, staff_name):
    """
    Get Staff timetable via staff name
    :param url: base url
    :param staff_name: staff name string
    :return: a list of dicts
    """

    url = url + 'TextSpreadsheet;Staff;name;{}?template=SWSCUST+Staff+TextSpreadsheet&weeks=1-52' \
                '&days=1-7&periods=1-32&Width=0&Height=0'.format(staff_name)

    course_list, name = extract_text_spread_sheet(url, lambda _: False)

    for course in course_list:
        course['Name of Type'] = course['Module']
        course['Module'] = course['Description']
    return course_list, name
