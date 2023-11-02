from typing import Type, List
from sqlalchemy import insert, create_engine
from sqlalchemy.orm import Session
from sshtunnel import SSHTunnelForwarder

from config import hidden_vars as hv, category_goods_, menu_tuple, Launch_Engine, create_ssh_tunnel
from db_update.base import StockTable
from db_update.firebird_interaction import get_folders_from_fdb, get_full_stock_from_fdb


def write_data(tunnel: SSHTunnelForwarder | None, table: Type, data: List) -> None:
    if tunnel:
        start = Launch_Engine(
            username=hv.server_db_username_server,
            password=hv.server_db_password_server,
            port=str(tunnel.local_bind_port),
        )
    else:
        start = Launch_Engine(
            username=hv.server_db_username_client,
            password=hv.server_db_password_client,
            port=hv.remote_bind_address_port,
        )
    engine = create_engine(url=start.engine, echo=True)
    with Session(engine) as connect:
        connect.execute(insert(table), data)
        connect.commit()
    print('success')


ssh_tunnel = create_ssh_tunnel()
folders_ = get_folders_from_fdb()
data_ = get_full_stock_from_fdb(category_goods_ + menu_tuple)

write_data(table=StockTable, data=folders_ + data_, tunnel=ssh_tunnel)
# if tunnel = None,
#   write_data on client,
#       else write_data on server
