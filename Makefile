db_host ?= 127.0.0.1
db_port ?= 5432
db_user ?= ai_product_catalog
db_password ?= ai_product_catalog123
db_dba_user ?= postgres
db_dba_password ?=

install:
	cd data && pip install -r requirements.txt

localdb:
ifneq "$(db_dba_password)" "" 
	PGPASSWORD=$(db_dba_password) psql -h $(db_host) -p $(db_port) -U $(db_dba_user) -f data/drop_db.sql
	PGPASSWORD=$(db_dba_password) psql -h $(db_host) -p $(db_port) -U $(db_dba_user) -f data/create_db.sql
else
	psql -h $(db_host) -p $(db_port) -w -f data/drop_db.sql
	psql -h $(db_host) -p $(db_port) -w -f data/create_db.sql
endif
	PGPASSWORD=$(db_password) psql -h $(db_host) -p $(db_port) -U $(db_user) -w -f data/create_tables.sql
	cd data && jupyter nbconvert --to python ingest_dataworld_nike_dataset.ipynb --stdout  | DB_HOST=$(db_host) DB_PORT=$(db_port) DB_USER=$(db_user) DB_PASSWORD=$(db_password) python

lint:
	pylint data/ProductDataLib.py
