import json
import re
import requests

from nottingtable import db
from nottingtable.crawler.models import HexID


def get_hex_id_list(url='http://unnc-app.scientia.com.cn/api/Resource/StudentSet'):
    """
    Write num id to hex id mapping relationship into database
    :param url: base url
    :return: None
    """
    res = requests.get(url, headers={'Referer': 'http://unnc-tcs.scientia.com.cn/'})
    list_res = json.loads(res.content)
    for id_entry in list_res:
        hex_id = id_entry['hostKey']
        description = id_entry['description'].split(' - ')
        num_id = description[-1]
        if not num_id or len(hex_id) < 32:
            continue
        record = HexID(num_id=num_id, hex_id=hex_id)
        db.session.add(record)
    db.session.commit()


def update_individual_hex_id(num_id, url='http://unnc-app.scientia.com.cn/'):
    """
    Update individual hex id from sws system
    :param num_id: the user id to be updated
    :param url: the unnc-scientia url
    :return: hexID record
    """
    url = url + f'sws/timetable/Index?id={num_id}' \
                '&days=1-5&weeks=1-52&periods=1-24&template=Student+Set+Individual&height=100&week=100'
    res = requests.head(url, headers={'Referer': 'http://unnc-sws.scientia.com.cn/'})
    next_url = res.next.path_url
    hex_id = re.search(r'id;([0-9A-F]{32}).*', next_url).group(1)
    record = HexID(num_id=num_id, hex_id=hex_id)
    db.session.add(record)
    db.session.commit()
    return record


def get_hex_id(num_id):
    """
    Get hex id from database mapping with num id
    :param num_id: number id
    :return: hex id
    """
    try:
        hex_id = HexID.query.filter_by(num_id=num_id).first().hex_id
    except AttributeError:
        try:
            hex_id = update_individual_hex_id(num_id).hex_id
        except AttributeError:
            hex_id = None
    return hex_id
