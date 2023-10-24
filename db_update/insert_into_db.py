from typing import Type

from sqlalchemy import Table, insert, create_engine
from sqlalchemy.orm import DeclarativeBase

from config import hidden_vars as hv, category_test
from db_update.base import StockTable
from db_update.firebird_interaction import get_ispath_from_fdb, get_full_stock_from_fdb

engine_client = create_engine(f'postgresql+psycopg2://{hv.server_db_username_client}:{hv.server_db_password_client}'
                              f'@{hv.remote_bind_address_host}:{hv.remote_bind_address_port}/activity_client')


def write_data_in_client(table: Type, data: list) -> None:
    conn = engine_client.connect()
    conn.execute(insert(table), data)
    conn.commit()
    conn.close()


# data_list = get_ispath_from_fdb()
# for line in data_list:
#     temp_data.append({
#         'code': int(line[0]),
#         'parent': int(line[1]),
#         'ispath': True,
#         'name': line[2],
#         'quantity': int(line[4]) if line[4] else None,
#         'price': int(line[5]) if line[4] else None,
#     })

# write_data_in_client(data=temp_data, table=StockTable)


if __name__ == '__main__':
    temp_data = list()
    temp_result = get_full_stock_from_fdb(category_test)
    for line in temp_result:
        temp_data.append({
            'code': int(line[0]),
            'parent': int(line[1]),
            'ispath': True,
            'name': line[2],
            'quantity': int(line[4]) if line[4] else None,
            'price': int(line[5]) if line[5] else None,
        })
    write_data_in_client(data=temp_result, table=StockTable)
