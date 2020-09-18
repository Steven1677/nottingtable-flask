from nottingtable.crawler.models import HexID


def get_year1_group_list():
    """
    Get year 1 group list from hex_id table
    :return: year 1 group name list
    """
    year1_groups = HexID.query.filter(HexID.num_id.op('regexp')(r'^[ABC]\d{1,2}[-$]?.*')).all()
    year1_group_name_list = [x.num_id for x in year1_groups]
    return year1_group_name_list
