db_local_remove:
	psql -h localhost -p 5432 -w -f data/drop_db.sql

db_local_create: db_local_remove
	psql -h localhost -p 5432 -w -f data/create_db.sql
	PGPASSWORD=ai_product_catalog123 psql -h localhost -p 5432 -U ai_product_catalog -w -f data/create_tables.sql

db_local_load:
	jupyter nbconvert --to notebook --execute data/ingest_dataworld_nike_dataset.ipynb

lint:
	pylint data/ProductDataLib.py

