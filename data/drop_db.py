import psycopg
import os

def main():
    db_host = "tools.home.glroland.com"
    if "DB_HOST" in os.environ:
        db_host = os.environ["DB_HOST"]

    db_port = "5432"
    if "DB_PORT" in os.environ:
        db_host = os.environ["DB_PORT"]
    
    db_user = "postgres"
    if "DB_DBA_USER" in os.environ:
        db_user = os.environ["DB_DBA_USER"]

    db_password = "r3dh@t123"
    if "DB_DBA_PASSWORD" in os.environ:
        db_password = os.environ["DB_DBA_PASSWORD"]
    
    db_conn_str = f"host={db_host} port={db_port} user={db_user} password={db_password}"
    print (db_conn_str)

    with psycopg.connect(db_conn_str, autocommit=True) as db_connection:
        with db_connection.cursor() as c:
            try:
                c.execute("drop database ai_product_catalog")
            except Exception as e:
                print ("Ignoring psycopg.errors.InvalidCatalogName")
            try:
                c.execute("drop user ai_product_catalog")
            except Exception as e:
                print ("Ignoring psycopg.errors.InvalidCatalogName")



if __name__ == "__main__":
    main()