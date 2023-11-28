from config import category_goods_, menu_tuple
from v2.day_activity_transfer_events import transfer_activity
from v2.firebird_db_func import get_folders_from_fdb, get_full_stock_from_fdb
from v2.postgres_db_func_crud import truncate_table, upload_data
from v2.tables import StockTable


def refresh_availability():
    print('Обновляют таблицу наличия на SSH сервере и на данном ПК')
    truncate_table([StockTable.__name__])
    truncate_table([StockTable.__name__], tunnel=True)
    data_ = get_folders_from_fdb() + get_full_stock_from_fdb(category_goods_ + menu_tuple)
    upload_data(table=StockTable, data=data_)
    upload_data(table=StockTable, data=data_, tunnel=True)


def main():
    refresh_availability()
    transfer_activity()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Script stopped')
