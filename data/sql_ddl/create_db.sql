create user "ai-product-catalog" with password 'ai_product_catalog123';
ALTER USER "ai-product-catalog" WITH SUPERUSER;

create database ai_product_catalog with owner "ai-product-catalog";
