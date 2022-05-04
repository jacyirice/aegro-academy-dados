from .postgres import PostgreSQL

aegro_db = PostgreSQL(database='aegroprojeto',
                      host='localhost',
                      user='postgres',
                      password='postgres',
                      )
aegro_db.connect()