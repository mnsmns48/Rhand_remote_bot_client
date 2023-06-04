from sqlalchemy import Table, MetaData, Integer, Column, Boolean, Float, SmallInteger, VARCHAR, TIMESTAMP

metadata = MetaData()

activity = Table('activity', metadata,
                 Column('operation_code', Integer),
                 Column('time_', TIMESTAMP(timezone=False)),
                 Column('product_code', Integer),
                 Column('product', VARCHAR),
                 Column('quantity', SmallInteger),
                 Column('price', Float),
                 Column('sum_', Float),
                 Column('noncash', Boolean),
                 Column('return_', Boolean),
                 )

avail = Table(
    'avail', metadata,
    Column('type_', VARCHAR),
    Column('brand', VARCHAR),
    Column('code', Integer),
    Column('product', VARCHAR),
    Column('quantity', Integer),
    Column('price', Integer)
)
