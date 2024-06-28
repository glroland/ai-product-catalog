create user ai_product_catalog with password 'ai_product_catalog123';

drop database ai_product_catalog;
create database ai_product_catalog with owner ai_product_catalog;

CREATE EXTENSION if not exists vector;
