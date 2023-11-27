from v2.engine import fdb_connection


def get_avail_from_fdb(args: tuple) -> list:
    return_temp_list = list()
    cur = fdb_connection.cursor()
    cur.execute(
        'SELECT SQ.CODE, SQ.PARENT, SQ.NAME, Sum(QUANTITY), SQ.PRICE_ FROM ('
        'SELECT dg.CODE, dg.parent, dg.NAME, dst.QUANTITY, dg.PRICE_ '
        'FROM DIR_GOODS dg, DOC_SESSION_TABLE dst '
        f'WHERE dg.CODE = dst.GOOD AND dg.PARENT IN {args} '
        'UNION ALL '
        'SELECT dg.CODE, dg.parent, dg.NAME, -dst2.QUANTITY, dg.PRICE_ '
        'FROM DIR_GOODS dg, DOC_SALE_TABLE dst2 '
        f'WHERE dg.CODE = dst2.GOOD AND dg.PARENT IN {args} '
        'UNION ALL '
        'SELECT dg.CODE, dg.parent, dg.NAME, -dbt.QUANTITY, dg.PRICE_ '
        'FROM DIR_GOODS dg, DOC_BALANCE_TABLE dbt '
        f'WHERE dg.CODE = dbt.GOOD AND dg.PARENT IN {args} '
        'UNION ALL '
        'SELECT dg.CODE, dg.parent, dg.NAME, +drt.QUANTITY, dg.PRICE_ '
        'FROM DIR_GOODS dg, DOC_RETURN_TABLE drt '
        f'WHERE dg.CODE = drt.GOOD AND dg.PARENT IN {args} '
        'UNION ALL '
        'SELECT dg.CODE, dg.parent, dg.NAME, -det.QUANTITY, dg.PRICE_ '
        'FROM DIR_GOODS dg, DOC_EXPSESSION_TABLE det '
        f'WHERE dg.CODE = det.GOOD AND dg.PARENT IN {args}) SQ '
        'GROUP BY SQ.CODE, SQ.PARENT, SQ.NAME, SQ.PRICE_ '
        'HAVING SUM(SQ.QUANTITY) >= 1 '
        'ORDER BY SQ.PARENT, SQ.CODE'
    )
    for line in cur.fetchall():
        return_temp_list.append({
            'type_': category.get(line[1])[0],
            'brand': line[2].split(' ')[1],
            'code': line[0],
            'product': line[2].split(' ', maxsplit=1)[1] if category.get(line[1])[0] == 'Смартфон' else line[2],
            'quantity': int(line[3]),
            'price': int(line[4]) if line[4] is not None else None,
        })
    return return_temp_list
