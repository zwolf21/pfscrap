from collections import OrderedDict


def parse_xml_table_tag(soup, tag, column_mapping=None, many=True):
    if column_mapping is not None:
        records = [
            OrderedDict(
                (column_mapping.get(r.name, r.name), r.text)
                for r in r.children
                if r.name in column_mapping
            )
            for r in soup(tag)
        ]
    else:
        records = [
            OrderedDict((r.name, r.text))
            for r in r.children
            if r.name
        ]
    if many == True:
        return records
    if records:
        return records[0]
    return {}
