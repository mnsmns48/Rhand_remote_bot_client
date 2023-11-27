from typing import List, Callable

from sqlalchemy import create_engine, text, Table, insert
from sqlalchemy.orm import Session
from sshtunnel import SSHTunnelForwarder

from config import hidden_vars as hv
from v2.engine import Launch_Engine


def create_ssh_tunnel() -> SSHTunnelForwarder:
    tunnel = SSHTunnelForwarder(
        (hv.ssh_host, 22),
        ssh_username=hv.ssh_username,
        ssh_password=hv.ssh_password,
        remote_bind_address=(hv.remote_bind_address_host, hv.remote_bind_address_port))
    tunnel.start()
    return tunnel


def ssh_connection_check(function: Callable) -> Callable:
    def wrapped(*args, **kwargs):
        if kwargs['tunnel']:
            tunnel = create_ssh_tunnel()
            start = Launch_Engine(
                username=hv.server_db_username_server,
                password=hv.server_db_password_server,
                host=hv.remote_bind_address_host,
                port=str(tunnel.local_bind_port),
                db_name=hv.server_db_name
            )
            function(bind=start, *args, **kwargs)
            tunnel.close()
        else:
            start = Launch_Engine(
                username=hv.server_db_username_client,
                password=hv.server_db_password_client,
                host=hv.remote_bind_address_host,
                port=hv.remote_bind_address_port,
                db_name=hv.local_db_name
            )
            function(bind=start, *args, **kwargs)

    return wrapped


@ssh_connection_check
def truncate_table(tables: List[str], **kwargs) -> None:
    engine = create_engine(url=kwargs['bind'].engine, echo=False)
    with Session(engine) as connect:
        for table in tables:
            connect.execute(text(f"TRUNCATE TABLE {table}"))
            connect.commit()
        print(f'Данные в {table} обновлены на {engine.url.host} {engine.url.port}')


@ssh_connection_check
def upload_data(table: Table, data: List, **kwargs) -> None:
    engine = create_engine(url=kwargs['bind'].engine, echo=False)
    with Session(engine) as connect:
        connect.execute(insert(table), data)
        connect.commit()
        print(f'Очищаю таблицу {table} на {engine.url.host} {engine.url.port}')


