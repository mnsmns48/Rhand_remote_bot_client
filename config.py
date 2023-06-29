from dataclasses import dataclass
from environs import Env


@dataclass
class Hidden:
    ssh_host: str
    ssh_username: str
    ssh_password: str
    remote_bind_address_host: str
    remote_bind_address_port: str
    server_db_username_server: str
    server_db_password_server: str
    server_db_username_client: str
    server_db_password_client: str
    fdb_dsn: str
    fdb_user: str
    fdb_password: str


def load_config(path: str = None):
    env = Env()
    env.read_env()
    return Hidden(
        ssh_host=env.str("SSH_HOST"),
        ssh_username=env.str("SSH_USERNAME"),
        ssh_password=env.str("SSH_PASSWORD"),
        remote_bind_address_host=env.str("REMOTE_BIND_ADDRESS_HOST"),
        remote_bind_address_port=env.int("REMOTE_BIND_ADDRESS_PORT"),
        server_db_username_server=env.str("SERVER_DB_USERNAME_SERVER"),
        server_db_password_server=env.str("SERVER_DB_PASSWORD_SERVER"),
        server_db_username_client=env.str("SERVER_DB_USERNAME_CLIENT"),
        server_db_password_client=env.str("SERVER_DB_PASSWORD_CLIENT"),
        fdb_dsn=env.str("FDB_DSN"),
        fdb_user=env.str("FDB_USER"),
        fdb_password=env.str("FDB_PASSWORD")

    )


hidden_vars = load_config('..env')

category = {
    80: ['Смартфоны', 'Samsung'],
    81: ['Смартфоны', 'Realme'],
    82: ['Смартфоны', 'Xiaomi'],
    83: ['Смартфоны', 'Tecno/Infinix'],
    84: ['Смартфоны', 'TCL'],
    87: ['Смартфоны', 'Honor'],
    28: ['Кнопочные телефоны', 'NoBrand'],
    29: ['Планшеты', 'NoBrand'],
    36: ['Умные часы', 'NoBrand'],
    54: ['PowerBanks', 'NoBrand'],
    3: ['Замена аккумулятора', 'NoBrand'],
    86: ['Замена дисплея', 'NoBrand']
}
