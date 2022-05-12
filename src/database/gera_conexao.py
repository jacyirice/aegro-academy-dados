from .postgres import PostgreSQL

def get_conn():
    aegro_db = PostgreSQL(
        database="aegroprojeto",
        host="localhost",
        user="postgres",
        password="postgres",
    )
    aegro_db.connect()
    return aegro_db