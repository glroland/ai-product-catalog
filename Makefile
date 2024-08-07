db_host ?= localhost
db_port ?= 5432
db_user ?= ai_product_catalog
db_password ?= ai_product_catalog123
db_dba_user ?= postgres
db_dba_password ?= r3dh@t123

data.lint:
	pylint data/*.py

data.install:
	cd data && pip install -r requirements.txt

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


chatbot.lint:
	cd ai-product-catalog-chatbot && pylint src/*.py

chatbot.install:
	cd ai-product-catalog-chatbot && pip install -r requirements.txt

chatbot.run:
	cd ai-product-catalog-chatbot/src && streamlit run ui.py --server.headless true --server.address 0.0.0.0 --server.port 8081

chatbot.build: chatbot.lint
	cd ai-product-catalog-chatbot && podman build -t registry.home.glroland.com/ai-product-catalog/chatbot:latest . --platform linux/amd64


service.run:
	cd ai-product-catalog-svc && mvn spring-boot:run

service.build:
	cd ai-product-catalog-svc && mvn clean package
	cd ai-product-catalog-svc && podman build -t registry.home.glroland.com/ai-product-catalog/svc:latest . --platform linux/amd64

publish:
	podman push registry.home.glroland.com/ai-product-catalog/svc:latest --tls-verify=false
	podman push registry.home.glroland.com/ai-product-catalog/chatbot:latest --tls-verify=false


install: data.install chatbot.install
