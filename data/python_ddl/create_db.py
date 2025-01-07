"""Create Database Script
"""
import os
import psycopg

def main():
    db_host = "tools.home.glroland.com"
    if "DB_HOST" in os.environ:
        db_host = os.environ["DB_HOST"]

    db_port = "5432"
    if "DB_PORT" in os.environ:
        db_host = os.environ["DB_PORT"]

    db_dba_user = "postgres"
    if "DB_DBA_USER" in os.environ:
        db_dba_user = os.environ["DB_DBA_USER"]

    db_dba_password = "r3dh@t123"
    if "DB_DBA_PASSWORD" in os.environ:
        db_dba_password = os.environ["DB_DBA_PASSWORD"]

    db_name = "ai_product_catalog"
    if "DB_NAME" in os.environ:
        db_name = os.environ["DB_NAME"]

    db_user = "ai-product-catalog"
    if "DB_USER" in os.environ:
        db_user = os.environ["DB_USER"]

    db_password = "ai_product_catalog123"
    if "DB_PASSWORD" in os.environ:
        db_password = os.environ["DB_PASSWORD"]

    db_conn_str = f"host={db_host} port={db_port} user={db_dba_user} password={db_dba_password}"
    print (db_conn_str)

    with psycopg.connect(db_conn_str, autocommit=True) as db_connection:
        with db_connection.cursor() as c:
            c.execute(f"create user '{db_user}' with password '{db_password}'")
            c.execute(f"ALTER USER '{db_user}' WITH SUPERUSER")
            c.execute(f"create database {db_name} with owner {db_user}")


if __name__ == "__main__":
    main()
