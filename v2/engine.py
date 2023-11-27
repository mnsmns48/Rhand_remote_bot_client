import fdb
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
