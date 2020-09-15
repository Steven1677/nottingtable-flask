import json
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
