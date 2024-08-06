import psycopg
import os

def main():    
    db_host = "tools.home.glroland.com"
    if "DB_HOST" in os.environ:
        db_host = os.environ["DB_HOST"]

    db_port = "5432"
    if "DB_PORT" in os.environ:
        db_host = os.environ["DB_PORT"]
    
    db_name = "ai_product_catalog"
    if "DB_NAME" in os.environ:
        db_name = os.environ["DB_NAME"]

    db_user = "ai_product_catalog"
    if "DB_USER" in os.environ:
        db_user = os.environ["DB_USER"]
    
    db_password = "ai_product_catalog123"
    if "DB_PASSWORD" in os.environ:
        db_password = os.environ["DB_PASSWORD"]

        
    db_conn_str = f"host={db_host} port={db_port} dbname={db_name} user={db_user} password={db_password}"
    print (db_conn_str)
    
    with psycopg.connect(db_conn_str, autocommit=True) as db_connection:
        with db_connection.cursor() as c:
            c.execute(open("create_tables.sql", "r").read())


if __name__ == "__main__":
    main()