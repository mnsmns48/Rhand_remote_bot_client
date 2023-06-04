import time

from config import category
from db_fdb_func import get_data_from_client_activity, get_day_activity_from_fdb_client, get_avail_from_fdb
from db_pg_func import write_data_in_server, write_data_in_client, truncate_table_in_server
from db_sql_tables import activity, avail


def transfer_avail() -> None:
    temp_category_list = list()
    for key, value in category.items():
        temp_category_list.append(key)
    insert_data = get_avail_from_fdb(tuple(temp_category_list))
    write_data_in_server(avail, insert_data, 'activity_server')
    print('Передача ассортимента на сервер завершена')


def transfer_sales() -> None:
    while True:
        data_client = get_data_from_client_activity()
        data_fdb = get_day_activity_from_fdb_client()
        difference = len(data_fdb) - len(data_client)
        if difference:
            print(f"Новых записей {difference}\nВыгружаю данные на сервер")
            insert_data = data_fdb[-difference:]
            write_data_in_server(activity, insert_data, 'activity_server')
            write_data_in_client(activity, insert_data, 'activity_client')
            print('Данные выгружены')
            time.sleep(100)
        else:
            time.sleep(100)


def main():
    truncate_table_in_server(avail, 'activity_server')
    transfer_avail()
    transfer_sales()


if __name__ == '__main__':
    main()
