import time

from config import category
from db_fdb_func import get_day_activity_from_fdb_client, get_avail_from_fdb
from db_pg_func import \
    write_data_in_server, \
    write_data_in_client, \
    get_data_from_client_activity
from v2.tables import activity, avail


def transfer_avail() -> None:
    temp_category_list = list()
    for key, value in category.items():
        temp_category_list.append(key)
    insert_data = get_avail_from_fdb(tuple(temp_category_list))
    write_data_in_server(avail, insert_data)
    print('Передача ассортимента на сервер завершена')


def transfer_sales() -> None:
    while True:
        data_client = get_data_from_client_activity()
        data_fdb = get_day_activity_from_fdb_client()
        difference = len(data_fdb) - len(data_client)
        if difference:
            print(f"Новых записей {difference}\nВыгружаю данные на сервер")
            insert_data = data_fdb[-difference:]
            write_data_in_server(activity, insert_data)
            write_data_in_client(activity, insert_data)
            print('Данные выгружены')
            time.sleep(100)
        else:
            time.sleep(100)


def old_main() -> None:
    truncate_table_in_server(avail.name, StockTable.__tablename__)
    transfer_avail() # отправка на сервер наличия в тадлицу avail

    # transfer_sales()


if __name__ == '__main__':
    try:
        old_main()
    except KeyboardInterrupt:
        print('Script stopped')
