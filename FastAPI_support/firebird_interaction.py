import itertools
from typing import Any, List

import fdb

from config import hidden_vars as hv, category_goods_, menu_tuple

fdb_connection = fdb.connect(
    dsn=hv.fdb_dsn,
    user=hv.fdb_user,
    password=hv.fdb_password
)


def get_folders_from_fdb() -> list[dict[str, int | bool | Any]]:
    cur = fdb_connection.cursor()
    cur.execute('SELECT code, parent, name FROM DIR_GOODS dg WHERE ISPATH = 1 ORDER BY code')
    temp_data = cur.fetchall()
    result = list()
    for line in temp_data:
        if int(line[0]) in category_goods_ or int(line[0]) in menu_tuple:
            result.append(
                {
                    'code': int(line[0]),
                    'parent': int(line[1]),
                    'ispath': True,
                    'name': line[2],
                    'quantity': None,
                    'price': None
                }
            )
    return result


def get_full_stock_from_fdb(*args) -> list[dict[str, int | bool | Any]]:
    args = [item for item in itertools.chain(*args)]
    cur = fdb_connection.cursor()
    cur.execute(
        'SELECT SQ.CODE, SQ.PARENT, SQ.NAME, Sum(QUANTITY), SQ.PRICE_ FROM ('
        'SELECT dg.CODE, dg.parent, dg.NAME, dst.QUANTITY, dg.PRICE_ '
        'FROM DIR_GOODS dg, DOC_SESSION_TABLE dst '
        f'WHERE dg.CODE = dst.GOOD AND dg.PARENT IN {tuple(args)} '
        'UNION ALL '
        'SELECT dg.CODE, dg.parent, dg.NAME, -dst2.QUANTITY, dg.PRICE_ '
        'FROM DIR_GOODS dg, DOC_SALE_TABLE dst2 '
        f'WHERE dg.CODE = dst2.GOOD AND dg.PARENT IN {tuple(args)} '
        'UNION ALL '
        'SELECT dg.CODE, dg.parent, dg.NAME, -dbt.QUANTITY, dg.PRICE_ '
        'FROM DIR_GOODS dg, DOC_BALANCE_TABLE dbt '
        f'WHERE dg.CODE = dbt.GOOD AND dg.PARENT IN {tuple(args)} '
        'UNION ALL '
        'SELECT dg.CODE, dg.parent, dg.NAME, +drt.QUANTITY, dg.PRICE_ '
        'FROM DIR_GOODS dg, DOC_RETURN_TABLE drt '
        f'WHERE dg.CODE = drt.GOOD AND dg.PARENT IN {tuple(args)} '
        'UNION ALL '
        'SELECT dg.CODE, dg.parent, dg.NAME, -det.QUANTITY, dg.PRICE_ '
        'FROM DIR_GOODS dg, DOC_EXPSESSION_TABLE det '
        f'WHERE dg.CODE = det.GOOD AND dg.PARENT IN {tuple(args)}) SQ '
        'GROUP BY SQ.CODE, SQ.PARENT, SQ.NAME, SQ.PRICE_ '
        'HAVING SUM(SQ.QUANTITY) >= 1 '
        'ORDER BY SQ.PARENT, SQ.CODE'
    )
    temp_data = cur.fetchall()
    result = list()
    for line in temp_data:
        result.append(
            {
                'code': int(line[0]),
                'parent': int(line[1]),
                'ispath': False,
                'name': line[2],
                'quantity': int(line[3]) if line[3] else None,
                'price': int(line[4]) if line[4] else None,
            }
        )
    return result
