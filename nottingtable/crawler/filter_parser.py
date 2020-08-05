import requests
import re


def get_filterjs(url):
    """
    Get filter.js file
    :param url: base url for timetabling system
    :return: filter.js text
    """
    url = url + 'js/filter.js'
    source = requests.get(url).text
    return source


def parse_department_list(url):
    """
    Parse filter.js deptarray information to Python dict
    :param url: base url for timetabling system
    :return: department name to id dict
    """

    # get filter.js file
    source = get_filterjs(url)

    dept_name = []
    dept_id = []

    # e.g. deptarray[0] [0] = "Language Centre";
    matches = re.findall(r'deptarray\[(\d{1,2})\] \[([01])\] = "(.*)"', source)
    for match in matches:
        # match e.g. ('0', '0', 'Language Centre'), ('0', '1', 'CSC-LANG')
        if match[1] == '0':
            dept_name.append(match[2])
        elif match[1] == '1':
            dept_id.append(match[2])

    return dict(zip(dept_name, dept_id))


def parse_pgt_programmearray(url):
    """
    Parse filter.js programmearray for pgt information
    :param url: base url for timetabling system
    :return: pgt programme name to id dict
    """

    # get filter.js file
    source = get_filterjs(url)

    name_to_id = {}

    # e.g. programmearray[340] [0] = "MSc Finance and Investment (Business Analytics)/F/02 - MSc Finance and
    # Investment (Business Analytics)";
    matches = re.findall(r'programmearray\[(\d{1,3})\] \[0\] = "(.*)";\s+'
                         r'programmearray\[\1\] \[1\] = ".*";\s+'
                         r'programmearray\[\1\] \[2\] = "(PGT/.*)"', source)
    for match in matches:
        # match e.g. ('0', 'MA Applied Linguistics/F/01 - EG04 Applied Linguistics', 'PGT/C1014/C7PAPLST/F/01')
        name_to_id[match[1]] = match[2]

    return name_to_id


def parse_modulearray(url):
    """
    Parse filter.js modulearray
    :param url: base url for timetabling system
    :return: module name to module id dict
    """

    # get filter.js file
    source = get_filterjs(url)

    name_to_id = {}

    # e.g. modulearray[0] [0] = "ABEE/3029/01";
    matches = re.findall(r'modulearray\[(\d{1,4})\] \[0\] = "(.*)";\s+'
                         r'modulearray\[\1\] \[1\] = ".*";\s+'
                         r'modulearray\[\1\] \[2\] = "(.*)"', source)
    for match in matches:
        name_to_id[match[1]] = match[2]

    return name_to_id
