from dataclasses import dataclass
from environs import Env
from sshtunnel import SSHTunnelForwarder


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
    # 3: ['Замена аккумулятора', 'NoBrand'],
    # 86: ['Замена дисплея', 'NoBrand'],
    67: ['Bluetooth колонки', 'NoBrand'],
    77: ['Наушники Bluetooth TWS', 'NoBrand']
}

category_goods_ = (3, 4, 5, 9, 10, 21, 24, 32, 38, 39, 40, 41, 42, 43, 45, 49, 51, 53, 55, 57, 60, 61, 62, 63, 69, 77,
                   78, 79, 80, 81, 82, 83, 84, 87, 90, 92, 93, 94, 95, 96, 97, 98, 99, 100, 117, 118, 119, 120, 121,
                   122, 123, 125, 126, 127, 128)

menu_tuple = (
    12,  # Смартфоны
    36,  # Смарт часы, фитнес трекеры)
    29,  # Планшеты
    28,  # Кнопочные телефоны
    76,  # Умные товары Xiaomi
    23,  # Наушники
    67,  # Портативная аккустика
    27,  # Хранение информации(флешки, карты памяти, диски)
    6,  # Зарядные устройства
    54,  # Внешние аккумуляторы (POWERBANK)
    31,  # Кабеля и адаптеры
    25,  # Аксессуары для компьютера
    26,  # Сетевое оборудование
    33,  # Авто товары
    8,  # Батареи и аккумуляторы
)


class Launch_Engine:
    def __init__(self,
                 username: str,
                 password: str,
                 port: str):
        self.engine = f'postgresql+psycopg2://' \
                      f'{username}:{password}@{hidden_vars.remote_bind_address_host}:{port}/activity_server'


def create_ssh_tunnel() -> SSHTunnelForwarder:
    tunnel = SSHTunnelForwarder(
        (hidden_vars.ssh_host, 22),
        ssh_username=hidden_vars.ssh_username,
        ssh_password=hidden_vars.ssh_password,
        remote_bind_address=(hidden_vars.remote_bind_address_host, hidden_vars.remote_bind_address_port))
    tunnel.start()
    return tunnel
