import psycopg2

from config import config

structured = False


def create_tables():
    """ create tables in the PostgreSQL database"""
    conn = None
    command = """
        CREATE TABLE IF NOT EXISTS public.quotes (
            id SERIAL PRIMARY KEY,
            quote_id INTEGER NOT NULL,
            posting_date DATE NOT NULL DEFAULT CURRENT_DATE,
            quote TEXT NOT NULL,
            quote_length INTEGER NOT NULL,
            allowed BOOLEAN DEFAULT FALSE
        )
        """
    try:
        conn = get_conn()
        cur = conn.cursor()
        # create table one by one
        # for command in commands:
        cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return False
    finally:
        if conn is not None:
            conn.close()
            return True


def find(i):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('select exists(select 1 from public.quotes where quote_id=' + str(i) + ')')
        # command = """select exists(select 1 from quotes where id=)"""
        # record_to_insert = (i)
        # cursor.execute(command, record_to_insert)
        row = cursor.fetchone()
        return row[0]
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return False
    finally:
        if conn is not None:
            conn.close()


def store(i, d, q, l, v):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        postgres_insert_query = """INSERT INTO quotes (quote_id, posting_date, quote, quote_length, allowed) VALUES (%s,
        %s,%s,%s,%s) """
        record_to_insert = (i, d, q, l, v)
        cursor.execute(postgres_insert_query, record_to_insert)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return False
    finally:
        if conn is not None:
            conn.close()
            return True


def get_conn():
    # read the connection parameters
    params = config()
    # connect to the PostgreSQL server
    return psycopg2.connect(**params, keepalives=1,
                            keepalives_idle=30,
                            keepalives_interval=10,
                            keepalives_count=5)


if __name__ == '__main__':
    create_tables()
