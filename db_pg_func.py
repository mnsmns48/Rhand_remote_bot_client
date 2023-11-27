from datetime import datetime

from retry import retry
from sqlalchemy import create_engine, insert, Table, text, select, func, delete, update
from sshtunnel import SSHTunnelForwarder, BaseSSHTunnelForwarderError
from config import hidden_vars as hv
from v2.tables import activity, avail

engine_client = create_engine(f'postgresql+psycopg2://{hv.server_db_username_client}:{hv.server_db_password_client}'
                              f'@{hv.remote_bind_address_host}:{hv.remote_bind_address_port}/activity_client')


@retry(BaseSSHTunnelForwarderError, tries=5000, delay=30)
def write_data_in_server(table: Table, data: list) -> None:
    server = SSHTunnelForwarder(
        (hv.ssh_host, 22),
        ssh_username=hv.ssh_username,
        ssh_password=hv.ssh_password,
        remote_bind_address=(hv.remote_bind_address_host, hv.remote_bind_address_port))
    server.start()
    local_port = str(server.local_bind_port)
    print('Connection with DB success...')
    engine = create_engine(
        f"postgresql://{hv.server_db_username_server}:{hv.server_db_password_server}@"
        f"{hv.remote_bind_address_host}:{local_port}/activity_server",
        echo=False)
    conn = engine.connect()
    conn.execute(insert(table), data)
    temp_list_ = dict()
    for sale in data:
        temp_list_.update({sale.get('product_code'): int(sale.get('quantity'))})
    response = conn.execute(select(avail).filter(avail.c.code.in_(temp_list_.keys()))).fetchall()
    for line in response:
        if line[4] - temp_list_.get(line[2]) == 0:
            conn.execute(delete(avail).where(avail.c.code == int(line[2])))
            print('Удаляю проданную позицию из наличия:', int(line[2]))
        else:
            conn.execute(update(avail).where(avail.c.code == int(line[2])).values(quantity=
                                                                                  line[4] - temp_list_.get(line[2])))
            print(f"Меняю количество проданого товара: "
                  f"позиция {line[2]} было {line[4]} стало {line[4] - temp_list_.get(line[2])}")
    conn.commit()
    conn.close()
    server.stop()


def write_data_in_client(table: Table, data: list) -> None:
    conn = engine_client.connect()
    conn.execute(insert(table), data)
    conn.commit()
    conn.close()


@retry(BaseSSHTunnelForwarderError, tries=5000, delay=30)
def truncate_table_in_server(*tables: str) -> None:
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
            f"{hv.remote_bind_address_host}:{local_port}/activity_server",
            echo=False)
        conn = engine.connect()
        print('Очищаю таблицу наличия на сервере')
        for table in tables:
            conn.execute(text(f"TRUNCATE TABLE {table}"))
            print(f'Очищаю таблицу {table} на сервере')
        conn.commit()
        conn.close()
        server.stop()


def get_data_from_client_activity():
    conn = engine_client.connect()
    today = datetime.today().date()
    response = conn.execute(select(activity).filter(func.DATE(activity.c.time_) == today)).fetchall()
    conn.close()
    return response
