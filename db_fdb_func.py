import fdb

from config import hidden_vars as hv

from config import category

fdb_connection = fdb.connect(
    dsn=hv.fdb_dsn,
    user=hv.fdb_user,
    password=hv.fdb_password
)


def get_day_activity_from_fdb_client() -> list:
    temp_list_ = list()
    cur = fdb_connection.cursor()
    cur.execute(
        """
        SELECT ds.CODE, ds.DOC_DATE, dst.GOOD, dg.NAME, dst.QUANTITY, dst.PRICE2, dst.SUMMA2, ds.NONCASH
        FROM DOC_SALE ds, DOC_SALE_TABLE dst, DIR_GOODS dg
        WHERE CAST(ds.DOC_DATE AS DATE) = CAST('now' AS DATE) 
        AND (ds.CODE = dst.CODE)
        AND (dst.GOOD = dg.CODE)
        UNION ALL
        SELECT dr.CODE AS RCODE, dr.DOC_DATE, drt.GOOD, dg.NAME, drt.QUANTITY, drt.PRICE2, drt.SUMMA2, dr.NONCASH
        FROM DOC_RETURN dr, DOC_RETURN_TABLE drt, DIR_GOODS dg
        WHERE CAST(dr.DOC_DATE AS DATE) = CAST('now' AS DATE) 
        AND (dr.CODE = drt.CODE)
        AND (drt.GOOD = dg.CODE)
        ORDER BY 2
        """
    )
    for line in cur.fetchall():
        temp_list_.append(
            {
                'operation_code': int(line[0]),
                'time_': str(line[1]),
                'product_code': int(line[2]),
                'product': line[3],
                'quantity': int(line[4]),
                'price': float(line[5]),
                'sum_': float(line[6]),
                'noncash': True if int(line[7]) == 1 else False,
                'return_': True if int(line[0]) <= 30000 else False
            }
        )
    return temp_list_


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
