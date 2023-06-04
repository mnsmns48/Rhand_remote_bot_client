from retry import retry
from sqlalchemy import create_engine, insert, Table, text
from sshtunnel import SSHTunnelForwarder, BaseSSHTunnelForwarderError

from config import hidden_vars as hv


@retry(BaseSSHTunnelForwarderError, tries=5000, delay=30)
def write_data_in_server(table: Table, data: list, db_name: str) -> None:
    with SSHTunnelForwarder(
            (hv.ssh_host, 22),
            ssh_username=hv.ssh_username,
            ssh_password=hv.ssh_password,
            remote_bind_address=(hv.remote_bind_address_host, hv.remote_bind_address_port)) as server:
        server.start()
        local_port = str(server.local_bind_port)
        print('Connection with DB success...')
        engine = create_engine(
            f"postgresql://{hv.server_db_username_server}:{hv.server_db_password_server}@"
            f"{hv.remote_bind_address_host}:{local_port}/{db_name}",
            echo=False)
        conn = engine.connect()
        conn.execute(insert(table), data)
        conn.commit()
        conn.close()


def write_data_in_client(table: Table, data: list, db_name: str) -> None:
    engine = create_engine(f'postgresql://{hv.server_db_username_client}:{hv.server_db_password_client}'
                           f'@{hv.remote_bind_address_host}:{hv.remote_bind_address_port}/{db_name}',
                           echo=False)
    conn = engine.connect()
    conn.execute(insert(table), data)
    conn.commit()
    conn.close()


@retry(BaseSSHTunnelForwarderError, tries=5000, delay=30)
def truncate_table_in_server(table: Table, db_name: str) -> None:
    with SSHTunnelForwarder(
            (hv.ssh_host, 22),
            ssh_username=hv.ssh_username,
            ssh_password=hv.ssh_password,
            remote_bind_address=(hv.remote_bind_address_host, hv.remote_bind_address_port)) as server:
        server.start()
        local_port = str(server.local_bind_port)
        print('Connection with DB success...')
        engine = create_engine(
            f"postgresql://{hv.server_db_username_server}:{hv.server_db_password_server}@"
            f"{hv.remote_bind_address_host}:{local_port}/{db_name}",
            echo=False)
        conn = engine.connect()
        print('Очищаю таблицу наличия на сервере')
        conn.execute(text(f"TRUNCATE TABLE {table}"))
        conn.commit()
        conn.close()
