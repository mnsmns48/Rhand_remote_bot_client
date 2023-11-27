from v2.postgres_db_func_crud import truncate_table, create_ssh_tunnel
from v2.tables import avail, StockTable

ssh_connect = create_ssh_tunnel()


def refresh():
    truncate_table([avail, StockTable.__name__], tunnel=None)
    truncate_table([avail, StockTable.__name__], tunnel=ssh_connect)


def main():
    refresh()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Script stopped')
