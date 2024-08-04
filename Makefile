localdb:
	psql -h localhost -p 5432 -w -f data/drop_db.sql
	psql -h localhost -p 5432 -w -f data/create_db.sql
	PGPASSWORD=ai_product_catalog123 psql -h localhost -p 5432 -U ai_product_catalog -w -f data/create_tables.sql
	cd data && jupyter nbconvert --to python ingest_dataworld_nike_dataset.ipynb --stdout  | python

lint:
	pylint data/ProductDataLib.py

