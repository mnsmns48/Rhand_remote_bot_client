from fdb.schema import Table
from sqlalchemy import create_engine
from sshtunnel import SSHTunnelForwarder
from config import hidden_vars as hv
from db_update.base import Base


def create_new_remote_table_server() -> None:
    with SSHTunnelForwarder(
            (hv.ssh_host, 22),
            ssh_username=hv.ssh_username,
            ssh_password=hv.ssh_password,
            remote_bind_address=(hv.remote_bind_address_host, hv.remote_bind_address_port)) as server:
        server.start()
        local_port = str(server.local_bind_port)
        print('Connection with DB success...')
        print('Port:', server.local_bind_port)
        engine_server = create_engine(
            f"postgresql://{hv.server_db_username_server}:{hv.server_db_password_server}@"
            f"{hv.remote_bind_address_host}:{local_port}/activity_server",
            echo=True)
        Base.metadata.create_all(engine_server)
        print('Table created')


def create_new_table_client() -> None:
    engine_client = create_engine(
        url=f'postgresql+psycopg2://{hv.server_db_username_client}:{hv.server_db_password_client}'
            f'@{hv.remote_bind_address_host}:{hv.remote_bind_address_port}/activity_client',
        echo=True)
    Base.metadata.create_all(engine_client)
    print('Table created')


create_new_remote_table_server()  # создать таблицу на сервере
create_new_table_client()  # создать таблицу на клиентской машине
