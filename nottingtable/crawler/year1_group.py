import io
import re
import requests
from flask import current_app
from pdfminer.high_level import extract_text


def get_year1_group_list():
    """
    Get year 1 group list from year 1 group pdf timetable
    :return: year 1 group name list
    """
    pdf_url = current_app.config['YEAR1_PDF_URL']
    pdf = requests.get(pdf_url, stream=True)
    pdf = io.BytesIO(pdf.content)

    text = extract_text(pdf)
    group_list = re.findall(r'Student Set timetable: (.*)', text)

    return group_list
