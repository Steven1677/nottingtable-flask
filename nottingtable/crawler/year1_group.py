from flask import current_app
import requests
import io
import re
from pdfminer.high_level import extract_text
from nottingtable.crawler.models import HexID


def get_year1_group_list():
    """
    Get year 1 group list from hex_id table
    :return: year 1 group name list
    """
    if not current_app.config['YEAR1_PDF_URL']:
        year1_groups = HexID.query.filter(HexID.num_id.op('regexp')(r'^[ABC]\d{1,2}[-$]?.*')).all()
        year1_group_name_list = [x.num_id for x in year1_groups]
        return year1_group_name_list
    else:
        return get_year1_group_list_pdf()


def get_year1_group_list_pdf():
    """
    Get year 1 group list from PDF file
    :return: year 1 group name list
    """
    pdf_url = current_app.config['YEAR1_PDF_URL']
    pdf = requests.get(pdf_url, stream=True)
    pdf = io.BytesIO(pdf.content)

    text = extract_text(pdf)
    group_list = re.findall(r'Student Set timetable: (.*)', text)

    return group_list
