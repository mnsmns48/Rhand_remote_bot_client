from typing import Type

from sqlalchemy import insert, create_engine
from sshtunnel import SSHTunnelForwarder

from config import hidden_vars as hv, category_test
from db_update.base import StockTable
from db_update.firebird_interaction import get_ispath_from_fdb, get_full_stock_from_fdb

engine_client = create_engine(f'postgresql+psycopg2://{hv.server_db_username_client}:{hv.server_db_password_client}'
                              f'@loc{hv.remote_bind_address_host}:{hv.remote_bind_address_port}/activity_server')


def write_data_in_client(table: Type, data: list) -> None:
    conn = engine_client.connect()
    conn.execute(insert(table), data)
    conn.commit()
    conn.close()


def write_data_in_ssh_server(table: Type, ispath_list: list, stock_data: list) -> None:
    with SSHTunnelForwarder(
            (hv.ssh_host, 22),
            ssh_username=hv.ssh_username,
            ssh_password=hv.ssh_password,
            remote_bind_address=(hv.remote_bind_address_host, hv.remote_bind_address_port)) as server:
        server.start()
        local_port = str(server.local_bind_port)
        print('Connection with DB success...')
        engine_server = create_engine(
            f"postgresql://{hv.server_db_username_server}:{hv.server_db_password_server}@"
            f"{hv.remote_bind_address_host}:{local_port}/activity_server",
            echo=True)
        conn = engine_server.connect()
        conn.execute(insert(table), ispath_list)
        conn.execute(insert(table), stock_data)
        conn.commit()
        conn.close()


path_ = get_ispath_from_fdb()
data_ = get_full_stock_from_fdb(category_test)
write_data_in_ssh_server(table=StockTable, ispath_list=path_, stock_data=data_)
