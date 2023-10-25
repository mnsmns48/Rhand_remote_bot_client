from typing import Type

from sqlalchemy import create_engine, FromClause
from sshtunnel import SSHTunnelForwarder
from config import hidden_vars as hv
from db_update.base import Base, StockTable

engine_client = create_engine(
    url=f'postgresql+psycopg2://{hv.server_db_username_client}:{hv.server_db_password_client}'
        f'@{hv.remote_bind_address_host}:{hv.remote_bind_address_port}/activity_server',
    echo=True)


def create_new_remote_table_server() -> None:
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
        Base.metadata.create_all(engine_server)
        print('Table created')


def create_new_table_client(base: Type[Base]) -> None:
    base.metadata.create_all(engine_client)
    print('Table created')


def truncate_client_table(table: Type[FromClause]) -> None:
    Base.metadata.drop_all(engine_client, tables=[table.__table__])
    print('Truncate table', table.__table__)


# truncate_client_table(StockTable)  # удалить таблицу
# create_new_remote_table_ser   ver()  # создать таблицу на сервере
create_new_table_client(StockTable)  # создать таблицу на клиентской машине
