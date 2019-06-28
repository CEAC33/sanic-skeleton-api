import psycopg2
from sanic.log import logger

from local_settings import *
    
async def get_from_postgre(query):
    try:
        connect_str = "dbname='{dbname}' user='{user}' host='{host}' password='{password}'"
        db_config = DATABASES.get('default')
        connect_str = connect_str.format(dbname=db_config.get('NAME'), user=db_config.get('USER'), host=db_config.get('HOST'), password=db_config.get('PASSWORD'))

        conn = psycopg2.connect(connect_str)
        cursor = conn.cursor()

        cursor.execute(query)
        rows = cursor.fetchall()
        result = [x[0] for x in rows]

        # logger.info(rows)
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        logger.error("Uh oh, can't connect. Invalid dbname, user or password?")
        logger.error(e)