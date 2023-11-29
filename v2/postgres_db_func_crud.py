from typing import List, Type

from retry import retry
from sqlalchemy import create_engine, text, Table, insert, select, delete, update
from sqlalchemy.orm import Session
from sshtunnel import BaseSSHTunnelForwarderError

from v2.engine import check_connection
from v2.tables import StockTable


@retry(BaseSSHTunnelForwarderError, tries=5000, delay=30)
@check_connection
def truncate_table(tables: List[str], **kwargs) -> bool:
    engine = create_engine(url=kwargs['bind'].engine, echo=False)
    with Session(engine) as connect:
        for table in tables:
            connect.execute(text(f"TRUNCATE TABLE {table}"))
            connect.commit()
        print(f'Таблица {table} очищена на {engine.url.host} {engine.url.port}')
    return True


@retry(BaseSSHTunnelForwarderError, tries=5000, delay=30)
@check_connection
def upload_data(table: Type[StockTable], data: List, **kwargs) -> bool:
    engine = create_engine(url=kwargs['bind'].engine, echo=False)
    with Session(engine) as connect:
        connect.execute(insert(table), data)
        connect.commit()
        print(f'Загрузка данных в {table} на {engine.url.host} {engine.url.port} завершена')
    return True


@retry(BaseSSHTunnelForwarderError, tries=5000, delay=30)
@check_connection
def update_data(table: Type[StockTable], data: List, **kwargs) -> bool:
    temp_list_ = dict()
    for line in data:
        temp_list_.update({line.get('product_code'): int(line.get('quantity'))})
    engine = create_engine(url=kwargs['bind'].engine, echo=False)
    with Session(engine) as connect:
        response = connect.execute(select(table).filter(table.code.in_(temp_list_.keys()))).fetchall()
        for line in response:
            current_amount = line[0].quantity - temp_list_.get(line[0].code)
            if current_amount == 0:
                connect.execute(delete(table).where(table.code == line[0].code))
                print(f"\nУдаляю проданную позицию из наличия: {line[0].code} {line[0].name}\n")
            else:
                connect.execute(update(table).where(table.code == line[0].code)
                                .values(quantity=current_amount))
                print(f"\nМеняю количество товара на сайте:\n"
                      f"{line[0].name}\nБыло {temp_list_.get(line[0].code)} шт. -> стало {current_amount} шт.\n")
    return True
