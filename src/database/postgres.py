import psycopg2
from psycopg2.extensions import connection
from psycopg2.extras import execute_values

class PostgreSQL:
    conn: connection = None

    def __init__(self, database: str, host: str, user: str, password: str, port: int = 5432) -> None:
        """This a construct method

        Args:
            database (str): Database name
            host (str): Database host 
            user (str): Database user
            password (str): Database password
            port (int, optional): Database port. Defaults to 5432.
        """
        self.database = database
        self.host = host
        self.user = user
        self.password = password
        self.port = port

    def connect(self) -> None:
        """This method makes the connection to the database"""
        try:
            conn = psycopg2.connect(
                database=self.database,
                host=self.host,
                user=self.user,
                password=self.password,
            )
            self.conn = conn
        except psycopg2.Error as e:
            print(f"Erro na conexão: {e}")

    def disconnect(self) -> None:
        """This method closes the connection to the database"""
        if self.conn:
            self.conn.close()

    def select_all(self, table: str) -> list:
        """This method queries all records in a database table

        Args:
            table (str): Table name

        Returns:
            list: List containing table records
        """
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        objs = cursor.fetchall()
        return objs

    def select_by_field(self, table: str, field: str, value: str, op: str = '=') -> list:
        """This method queries all records in a database table
        filtering by a column and a value


        Args:
            table (str): Table name
            field (str): Column name
            value (str): Value column
            op (str, optional): Operator. Defaults to '='.

        Returns:
            list: List containing table records
        """
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table} WHERE {field}{op}%s", (value,))
        objs = cursor.fetchall()
        return objs

    def insert(self, table: str, obj: dict) -> int:
        cursor = self.conn.cursor()
        campos = self.format_fields(obj.keys())
        valores = self.format_values(obj.values())

        cursor.execute(
            f"INSERT INTO {table} ({campos}) VALUES ({('%s, '*len(valores))[:-2]}) RETURNING id;", valores)
        self.conn.commit()

        return cursor.fetchone()[0]

    def insert_many(self, table: str, list_fields: list, list_objs: list) -> list:
        cursor = self.conn.cursor()

        campos = self.format_fields(list_fields)
        valores = self.format_many_values(list_objs)

        execute_values(cursor,
            f"INSERT INTO {table} ({campos}) VALUES %s RETURNING id;", valores)
        self.conn.commit()
        return cursor.fetchall()

    def select_id_or_insert(self, table: str, uk: str, obj: dict) -> int:
        objs = self.select_by_field(table, uk, obj[uk])

        if not objs:
            return self.insert(table, obj)
        else:
            return objs[0][0]

    def format_many_values(self, list_objs) -> list:
        return [self.format_values(obj.values()) for obj in list_objs]

    def format_values(self, values) -> tuple:
        return tuple(values)

    def format_fields(self, fields) -> str:
        return ', '.join(fields)
