#
# Configuration
#
db_host ?= db
db_port ?= 5432
db_user ?= ai-product-catalog
db_name ?= ai_product_catalog
db_password ?= ai_product_catalog123
db_dba_user ?= postgres
db_dba_password ?= d8nnyr0cks
openai_url ?= http://envision:11434/v1
run_chatbot_port ?= 8080
run_storefront_port ?= 8081
run_greeter_port ?= 8082
run_service_port ?= 8083


#
# Data Processing Actions
#
data.lint:
	pylint data/*.py data/python_ddl/*

data.install:
	cd data && pip install -r requirements.txt

data.db:
ifneq "$(db_dba_password)" "" 
	PGPASSWORD="$(db_dba_password)" psql -h "$(db_host)" -p "$(db_port)" -U "$(db_dba_user)" -f data/sql_ddl/drop_db.sql
	PGPASSWORD="$(db_dba_password)" psql -h "$(db_host)" -p "$(db_port)" -U "$(db_dba_user)" -f data/sql_ddl/create_db.sql
else
	psql -h "$(db_host)" -p "$(db_port)" -w -f data/sql_ddl/drop_db.sql
	psql -h "$(db_host)" -p "$(db_port)" -w -f data/sql_ddl/create_db.sql
endif
	PGPASSWORD="$(db_password)" psql -h "$(db_host)" -p "$(db_port)" -U "$(db_user)" -d "$(db_name)" -w -f data/sql_ddl/create_tables.sql
	cd data && jupyter nbconvert --to python ingest_dataworld_nike_dataset.ipynb --stdout  | DB_HOST="$(db_host)" DB_PORT="$(db_port)" DB_USER="$(db_user)" DB_PASSWORD="$(db_password)" DB_NAME="$(db_name)" OPENAI_API_URL="${openai_url}" python


#
# Chatbot Application Lifecycle Actions
#
chatbot.lint:
	cd customer-chatbot && pylint src/*.py

chatbot.install:
	cd customer-chatbot && pip install -r requirements.txt

chatbot.run: #chatbot.lint
	cd customer-chatbot/src && AI_BACKEND_ENDPOINT=http://localhost:$(run_storefront_port) streamlit run app.py --server.headless true --server.address 0.0.0.0 --server.port $(run_chatbot_port)

chatbot.build: chatbot.lint
	cd customer-chatbot && podman build -t registry.home.glroland.com/ai-product-catalog/chatbot:latest . --platform linux/amd64


#
# Storefront API Lifecycle Actions
#
storefront.lint:
	pylint --recursive y storefront-svc/src

storefront.install:
	cd storefront-svc && pip install -r requirements.txt

storefront.run: #storefront.lint
	cd storefront-svc/src && fastapi dev app.py  --host 0.0.0.0 --port $(run_storefront_port) --reload

storefront.run.supervisor:
	cd storefront-svc/src && ENV_PRODUCT_SERVICE_ADDRESS=http://localhost:8083 python supervisor.py --show-options

storefront.run.adapter:
	cd storefront-svc/src && ENV_PRODUCT_SERVICE_ADDRESS=http://localhost:8083 python service_adapter.py

storefront.test:
	cd storefront-svc && pytest

storefront.build: #storefront.lint
	cd storefront-svc && podman build -t registry.home.glroland.com/ai-product-catalog/storefront:latest . --platform linux/amd64


#
# Customer Greeter Agent Lifecycle Actions
#
customer-greeter-agent.lint:
	cd customer-greeter-agent && pylint src/*.py

customer-greeter-agent.install:
	cd customer-greeter-agent && pip install -r requirements.txt

customer-greeter-agent.run:
	cd customer-greeter-agent/src && PORT=$(run_greeter_port) python app.py

customer-greeter-agent.build: customer-greeter-agent.lint
	cd customer-greeter-agent && podman build -t registry.home.glroland.com/ai-product-catalog/customer-greeter-agent:latest . --platform linux/amd64


#
# AI Product Catalog Service Lifecycle Actions
#
service.run:
	cd ai-product-catalog-svc && mvn spring-boot:run -Dspring-boot.run.jvmArguments="-Dserver.port=$(run_service_port)"

service.build:
	cd ai-product-catalog-svc && mvn clean package
	cd ai-product-catalog-svc && podman build -t registry.home.glroland.com/ai-product-catalog/svc:latest . --platform linux/amd64


#
# Full Application Lifecycle Actions
#
build: service.build chatbot.build storefront.build #customer-greeter-agent.build

publish:
	podman push registry.home.glroland.com/ai-product-catalog/svc:latest --tls-verify=false
	podman push registry.home.glroland.com/ai-product-catalog/chatbot:latest --tls-verify=false
	podman push registry.home.glroland.com/ai-product-catalog/storefront:latest --tls-verify=false
	#podman push registry.home.glroland.com/ai-product-catalog/customer-greeter-agent:latest --tls-verify=false

install: data.install chatbot.install customer-greeter-agent.install storefront.install

lint: chatbot.lint storefront.lint data.lint
