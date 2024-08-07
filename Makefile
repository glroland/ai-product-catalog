db_host ?= localhost
db_port ?= 5432
db_user ?= ai_product_catalog
db_password ?= ai_product_catalog123
db_dba_user ?= postgres
db_dba_password ?= r3dh@t123

lint:
	pylint data/*.py
	pylint chatbot/*.py

install: data.install chatbot.install

data.install:
	cd data && pip install -r requirements.txt
	cd chatbot && pip install -r requirements.txt

data.db:
ifneq "$(db_dba_password)" "" 
	PGPASSWORD=$(db_dba_password) psql -h $(db_host) -p $(db_port) -U $(db_dba_user) -f data/drop_db.sql
	PGPASSWORD=$(db_dba_password) psql -h $(db_host) -p $(db_port) -U $(db_dba_user) -f data/create_db.sql
else
	psql -h $(db_host) -p $(db_port) -w -f data/drop_db.sql
	psql -h $(db_host) -p $(db_port) -w -f data/create_db.sql
endif
	PGPASSWORD=$(db_password) psql -h $(db_host) -p $(db_port) -U $(db_user) -w -f data/create_tables.sql
	cd data && jupyter nbconvert --to python ingest_dataworld_nike_dataset.ipynb --stdout  | DB_HOST=$(db_host) DB_PORT=$(db_port) DB_USER=$(db_user) DB_PASSWORD=$(db_password) python

chatbot.install:
	cd chatbot && pip install -r requirements.txt

chatbot.run:
	cd chatbot/src && streamlit run ui.py --server.headless true --server.address 0.0.0.0 --server.port 8081

service.build:
	mvn clean package
	podman build -t registry.home.glroland.com/ai-product-catalog/svc:latest . --platform linux/amd64

service.run:
	mvn spring-boot:run
