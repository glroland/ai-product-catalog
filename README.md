# ai-product-catalog-service
AI Enabled Product Catalog Service



Products Similar to a specified item - using RAG:

select * 
from products, product_embeddings
where products.product_id = product_embeddings.product_id
and products.product_id != 1
order by embedding <-> (select embedding from product_embeddings where product_id=1)
limit 5
