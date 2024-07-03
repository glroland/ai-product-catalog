create user ai_product_catalog with password 'ai_product_catalog123';
ALTER USER ai_product_catalog WITH SUPERUSER;

drop database ai_product_catalog;
create database ai_product_catalog with owner ai_product_catalog;

