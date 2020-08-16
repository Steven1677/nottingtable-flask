from nottingtable.crawler.text_spread_sheet import extract_text_spread_sheet
from nottingtable.crawler.models import Module


def get_module_activity(url, module_name, activity):
    """
    Get one activity via module name
    :param url: base url
    :param module_name: module name string
    :param activity: activity string
    :return: one activity information dict and name
    """

    module = Module.query.filter_by(module_name=module_name).first()
    if module is None:
        raise NameError('Module Name Not Found')

    module_id = module.module_id
    url = url + 'reporting/TextSpreadsheet;module;id;{}%0D%0A?days=1-7&weeks=1-52&periods=1-32&' \
                'template=SWSCUST+module+TextSpreadsheet&height=100&week=100'.format(module_id)

    def activity_filter(course_dict):
        return course_dict['Activity'] != activity

    target_course, name = extract_text_spread_sheet(url, activity_filter)[0]

    return target_course, name
