import requests
from bs4 import BeautifulSoup


def extract_text_spread_sheet(url, exclude_filter):
    """
    Extract information from a text spread sheet
    :param exclude_filter: a function takes a dict and return True if the data should be ignored
    :param url: the url for text spread sheet
    :return: course list and name
    """

    resp = requests.get(url)
    if resp.status_code != 200:
        raise NameError('Course not Found')
    courses = resp.text
    courses_soup = BeautifulSoup(courses, 'lxml')
    name = courses_soup.find('span', class_='header-5-0-0').get_text()
    courses_tables = courses_soup.find_all(border='t')
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
                if exclude_filter(temp_dict):
                    continue
                course_list.append(temp_dict)
    return course_list, name
