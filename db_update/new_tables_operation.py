from typing import Type

from sqlalchemy import create_engine, FromClause
from sqlalchemy.orm import Session
from sshtunnel import SSHTunnelForwarder

from config import Launch_Engine, hidden_vars as hv, create_ssh_tunnel
from db_update.base import Base, StockTable


def truncate_table(tunnel: SSHTunnelForwarder | None, table: Type[FromClause]) -> None:
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
        Base.metadata.drop_all(bind=connect.bind, tables=[table.__table__])
    print('Truncate table -', table.__table__)


def create_table(tunnel: SSHTunnelForwarder | None, base: Type[Base]) -> None:
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
        base.metadata.create_all(bind=connect.bind)
    print('Table created -', base.__table__)


ssh_tunnel = create_ssh_tunnel()
truncate_table(table=StockTable, tunnel=None)  # удалить таблицу
create_table(base=StockTable, tunnel=None)  # создать таблицу
# if tunnel = None,
#   write_data on client,
#       else write_data on server
