from typing import Callable

import fdb
from sshtunnel import SSHTunnelForwarder

from config import hidden_vars as hv


class Launch_Engine:
    def __init__(self,
                 username: str,
                 password: str,
                 host: str,
                 port: str,
                 db_name: str):
        self.tunnel = None
        self.engine = f'postgresql+psycopg2://' \
                      f'{username}:{password}@{host}:{port}/{db_name}'


fdb_connection = fdb.connect(
    dsn=hv.fdb_dsn,
    user=hv.fdb_user,
    password=hv.fdb_password
)


def create_ssh_tunnel() -> SSHTunnelForwarder:
    tunnel = SSHTunnelForwarder(
        (hv.ssh_host, 22),
        ssh_username=hv.ssh_username,
        ssh_password=hv.ssh_password,
        remote_bind_address=(hv.remote_bind_address_host, hv.remote_bind_address_port))
    tunnel.start()
    return tunnel


def check_connection(function: Callable) -> Callable:
    def wrapped(*args, **kwargs):
        if kwargs.get('tunnel'):
            tunnel = create_ssh_tunnel()
            start = Launch_Engine(
                username=hv.server_db_username_server,
                password=hv.server_db_password_server,
                host=hv.remote_bind_address_host,
                port=str(tunnel.local_bind_port),
                db_name=hv.server_db_name
            )
        else:
            start = Launch_Engine(
                username=hv.server_db_username_client,
                password=hv.server_db_password_client,
                host=hv.remote_bind_address_host,
                port=hv.remote_bind_address_port,
                db_name=hv.local_db_name
            )
        return function(bind=start, *args, **kwargs)
    return wrapped

