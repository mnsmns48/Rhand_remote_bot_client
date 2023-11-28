import time
from datetime import datetime

from sqlalchemy import select, func, create_engine
from sqlalchemy.orm import Session


from v2.firebird_db_func import get_day_activity_from_fdb_client
from v2.engine import check_connection
from v2.postgres_db_func_crud import upload_data, update_data
from v2.tables import activity, StockTable


def transfer_activity():
    while True:
        data_client = get_data_from_client_activity()
        data_fdb = get_day_activity_from_fdb_client()
        difference = len(data_fdb) - len(data_client)
        if difference:
            insert_data = data_fdb[-difference:]
            upload_data(activity, insert_data, tunnel=True)
            upload_data(activity, insert_data)
            update_data(StockTable, insert_data, tunnel=True)
            update_data(StockTable, insert_data)
            print('--- Данные успешно выгружены ---\n')
            time.sleep(60)
        else:
            time.sleep(60)


@check_connection
def get_data_from_client_activity(**kwargs):
    engine = create_engine(url=kwargs.get('bind').engine, echo=False)
    with Session(engine) as connect:
        today = datetime.today().date()
        response = connect.execute(select(activity).filter(func.DATE(activity.c.time_) == today)).fetchall()
    return response

