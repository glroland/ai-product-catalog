import pandas as pd
import psycopg
import openai

class ProductDataSet:

    class ProductColumns:
        SKU = "SKU"
        PRICE = "Price"
        CATEGORY_DESC = "Category_Desc"
        CATEGORY_ID = "Category_ID"
        BRAND_DESC = "Brand_Desc"
        BRAND_ID = "Brand_ID"
        NAME = "Product_Name"
        DESC = "Product_Desc"
        ID = "Product_ID"

    class BrandColumns:
        DESC = "Brand_Desc"
        ID = "Brand_ID"

    class CategoryColumns:
        DESC = "Category_Desc"
        ID = "Category_ID"

    PROVIDER_OPENAI = "openai"
    PROVIDER_OPENAI_EMBEDDINGS_MODEL = "text-embedding-ada-002"

    dataSourceDescription = None
    targetDatabaseConnString = None
    productsDF = None
    brandsDF = None

    def __init__(self, dataSourceDescription, targetDatabaseConnString):
        self.dataSourceDescription = dataSourceDescription
        self.targetDatabaseConnString = targetDatabaseConnString

        if self.targetDatabaseConnString == None or len(self.targetDatabaseConnString) == 0:
            raise RuntimeError("Database Connection String for Destination DB is required!")

    def import_df(self, inputDF, mapping):
        self.productsDF = inputDF.copy(deep=True)    
        self.productsDF.rename(columns=mapping, inplace=True)

        self.productsDF = self.productsDF[self.productsDF.columns.intersection(
                { 
                    self.ProductColumns.SKU, 
                    self.ProductColumns.PRICE,
                    self.ProductColumns.CATEGORY_DESC, 
                    self.ProductColumns.CATEGORY_ID, 
                    self.ProductColumns.BRAND_DESC,
                    self.ProductColumns.BRAND_ID,
                    self.ProductColumns.NAME,
                    self.ProductColumns.DESC 
                }
            )]
        
        self.productsDF.drop_duplicates(inplace = True)
        self.brandsDF = pd.DataFrame({ self.BrandColumns.DESC: self.productsDF[self.ProductColumns.BRAND_DESC].drop_duplicates() })
        self.categoriesDF = pd.DataFrame({ self.CategoryColumns.DESC: self.productsDF[self.ProductColumns.CATEGORY_DESC].drop_duplicates() })

        return self.productsDF

    def sql_execute(self, sql, values, fetchOne = True):
        with psycopg.connect(self.targetDatabaseConnString) as db_connection:
            with db_connection.cursor() as c:
                c.execute(sql, values)

                if fetchOne:
                    rows = c.fetchone()
                    return rows

    def sql_insert_dataframe_row(self, row, insertSQL, existsSQL):
        try:
            result = self.sql_execute(existsSQL, row, True)
        except Exception as e:
            print ("Caught Exception While Executing SQL!  ", e, "Impacting Values Were =", row)
            raise e
        
        if (result == None):
#            print ("Not Found.  Creating....")
            result = self.sql_execute(insertSQL, row, True)
#        print("RESULT=", result[0])
        return result[0]
    
    def sql_insert_dataframe(self, df, idColumn, insertSQL, existsSQL):
        df[idColumn] = df.apply(lambda row: self.sql_insert_dataframe_row(row.to_dict(), insertSQL, existsSQL), axis=1)
#        print(df.head())

    def reset_brand_id_for_product(self, row):
        brandDesc = row[self.ProductColumns.BRAND_DESC]
        brandIds = self.brandsDF[self.brandsDF[self.BrandColumns.DESC] == brandDesc][self.BrandColumns.ID]
        if (len(brandIds) == 0):
            raise RuntimeError("No Brand IDs were found for the given brand descrption");
        elif (len(brandIds) > 1):
            raise RuntimeError("Too many Brand IDs were found for the given brand descrption: " + str(len(brandIds)));
        return brandIds.values[0]

    def reset_category_id_for_product(self, row):
        categoryDesc = row[self.ProductColumns.CATEGORY_DESC]
        categoryIds = self.categoriesDF[self.categoriesDF[self.CategoryColumns.DESC] == categoryDesc][self.CategoryColumns.ID]
        if (len(categoryIds) == 0):
            raise RuntimeError("No Category IDs were found for the given brand descrption");
        elif (len(categoryIds) > 1):
            raise RuntimeError("Too many Category IDs were found for the given brand descrption: " + str(len(categoryIds)));
        return categoryIds.values[0]

    def persist(self):
        self.persist_categories()
        self.productsDF[self.ProductColumns.CATEGORY_ID] = self.productsDF.apply(lambda row: self.reset_category_id_for_product(row), axis=1)

        self.persist_brands()
        self.productsDF[self.ProductColumns.BRAND_ID] = self.productsDF.apply(lambda row: self.reset_brand_id_for_product(row), axis=1)

        self.persist_products()
        return
    
    def persist_categories(self):
        insertSQL = f"""
                        INSERT INTO categories(category_desc) VALUES (%({self.CategoryColumns.DESC})s) RETURNING category_id;
                    """
        existsSQL = f"""
                        SELECT category_id FROM categories WHERE %({self.CategoryColumns.DESC})s = category_desc;
                    """
        self.sql_insert_dataframe(self.categoriesDF, self.CategoryColumns.ID, insertSQL, existsSQL)

    def persist_brands(self):
        insertSQL = f"""
                        INSERT INTO brands(brand_desc) VALUES (%({self.BrandColumns.DESC})s) RETURNING brand_id;
                    """
        existsSQL = f"""
                        SELECT brand_id FROM brands WHERE %({self.BrandColumns.DESC})s = brand_desc;
                    """
        self.sql_insert_dataframe(self.brandsDF, self.BrandColumns.ID, insertSQL, existsSQL)
    
    def persist_products(self):
        insertSQL = f"""
                        INSERT INTO products
                        (
                            sku, 
                            brand_id,
                            product_name,
                            product_desc,
                            size,
                            msrp,
                            category_id
                        ) 
                        VALUES 
                        (
                            %({self.ProductColumns.SKU})s,
                            %({self.ProductColumns.BRAND_ID})s,
                            %({self.ProductColumns.NAME})s,
                            %({self.ProductColumns.DESC})s,
                            null,
                            CAST(%({self.ProductColumns.PRICE})s as double precision),
                            %({self.ProductColumns.CATEGORY_ID})s
                        )
                        RETURNING product_id
                    """
        existsSQL = f"""
                        SELECT product_id 
                        FROM products 
                        WHERE   sku = %({self.ProductColumns.SKU})s
                            AND brand_id = %({self.ProductColumns.BRAND_ID})s
                            AND product_name = %({self.ProductColumns.NAME})s
                            AND product_desc = %({self.ProductColumns.DESC})s
                            AND msrp = CAST(%({self.ProductColumns.PRICE})s as double precision)
                            AND category_id = %({self.ProductColumns.CATEGORY_ID})s
                    """
        self.sql_insert_dataframe(self.productsDF, self.ProductColumns.ID, insertSQL, existsSQL)







    def persist_embeddings(self):
        with psycopg.connect(db_conn_str) as db_connection:
            with db_connection.cursor() as c:
                c.executemany(
                    f"""
                        INSERT INTO product_embeddings
                        (
                            product_id,
                            engine,
                            model,
                            embedding
                        ) 
                        VALUES
                        (
                            (
                                select product_id 
                                from products 
                                where product_name=%(product_name)s
                                    and sku=%(product_id)s
                                    and brand_id=(select brand_id from brands where brand_desc=%(brand)s fetch first 1 rows only)
                                    and product_desc=%(description)s
                                fetch first 1 rows only
                            ),
                            '{PROVIDER_OPENAI}',
                            '{PROVIDER_OPENAI_EMBEDDINGS_MODEL}',
                            %(embeddingToStore)s
                        )
                    """,
                    embeddingsDF.to_dict(orient="records"),
                )


    def get_embedding_from_db(self, db_conn_str, productName, sku, price, brand, description, model):
        productName = productName.replace("'", "''")
        
        cleansedDescription = None
        if description != None and type(description) != float:
            cleansedDescription = description.replace("\n", " ").replace("'", "''")

        with psycopg.connect(db_conn_str) as db_connection:
            with db_connection.cursor() as c:
                sql = f"""
                                select embedding
                                from product_embeddings
                                where model = '{model}'
                                and engine = '{PROVIDER_OPENAI}'
                                and product_id = 
                                    (
                                        select product_id 
                                        from products 
                                        where product_name='{productName}'
                                        and sku='{sku}'
                                        and brand_id=(select brand_id from brands where brand_desc='{brand}' fetch first 1 rows only)
                                        and product_desc"""
                if cleansedDescription != None:
                    sql = sql + f"='{cleansedDescription}'"
                else:
                    sql = sql + " is null"
                    sql = sql + f"""
                                            fetch first 1 rows only
                                        )
                            """
        #            print(sql)
                
                c.execute(sql)
                record = c.fetchone()

                if record == None:
                    return None
                
                return record[0]
            

    def get_embedding_from_db(self, db_conn_str, productName, sku, price, brand, description, model):
        productName = productName.replace("'", "''")
        
        cleansedDescription = None
        if description != None and type(description) != float:
            cleansedDescription = description.replace("\n", " ").replace("'", "''")

        with psycopg.connect(db_conn_str) as db_connection:
            with db_connection.cursor() as c:
                sql = f"""
                                select embedding
                                from product_embeddings
                                where model = '{model}'
                                and engine = '{PROVIDER_OPENAI}'
                                and product_id = 
                                    (
                                        select product_id 
                                        from products 
                                        where product_name='{productName}'
                                        and sku='{sku}'
                                        and brand_id=(select brand_id from brands where brand_desc='{brand}' fetch first 1 rows only)
                                        and product_desc"""
                if cleansedDescription != None:
                    sql = sql + f"='{cleansedDescription}'"
                else:
                    sql = sql + " is null"
                    sql = sql + f"""
                                            fetch first 1 rows only
                                        )
                            """
    #            print(sql)
                
                c.execute(sql)
                record = c.fetchone()

                if record == None:
                    return None
                
                return record[0]
            


    def refresh_embeddings(self):
        client = openai.OpenAI()

#    df['embeddingToStore'] = df.apply(lambda row: create_embedding(row["product_name"], row["product_id"], row["msrp"], row["brand"], row["description"], model=PROVIDER_OPENAI_EMBEDDINGS_MODEL), axis=1)

#    embeddingsDF = df[df['embeddingToStore'].notnull()]
#    print("Shape:", embeddingsDF.shape)
#    #print ("Vector Length:", str(len(embeddingsDF[0])))
#    embeddingsDF.head()

#        return df









    # counter = 0

    def create_embedding(self, openai_client, db_conn_str, productName, sku, price, brand, description, model):
        global counter

        text = f"""'{productName}', '{sku}', {price}, '{brand}', '{description}'"""
        text = text.replace("\n", " ")

        embedding = get_embedding_from_db(db_conn_str, productName, sku, price, brand, description, model)
        
        if embedding != None:
            print ("... skipping - ALREADY EXISTS ...", text, "Embedding from DB =", embedding)
            return None

        #   counter = counter + 1
        #   if counter > 10:
        #      return None

        response = openai_client.embeddings.create(input = [text], model=model).data[0].embedding
        print ("CREATING Embedding for ....  ", text, "Response =", response)
        return response


if __name__ == "__main__":
    testDF = pd.DataFrame(columns=("test_sku", "test_name", "test_junk", "test_price", "test_desc", "test_brand", "test_category", "test junk2"),
                        data={ 
                            ("mySKUa", "myNAMEa", "myJUNKa", "1.00", "myDESCa", "myBRANDa", "myCATEGORYa", "myJUNK2a"),
                            ("mySKUb", "myNAMEb", "myJUNKb", "2.00", "myDESCb", "myBRANDa", "myCATEGORYb", "myJUNK2b"),
                            ("mySKUc", "myNAMEc", "myJUNKc", "3.00", "myDESCc", "myBRANDa", "myCATEGORYc", "myJUNK2c"),
                            ("mySKUd", "myNAMEd", "myJUNKd", "4.00", "myDESCd", "myBRANDb", "myCATEGORYa", "myJUNK2d"),
                            ("mySKUe", "myNAMEe", "myJUNKe", "5.00", "myDESCe", "myBRANDb", "myCATEGORYb", "myJUNK2e"),
                            ("mySKUf", "myNAMEf", "myJUNKf", "6.00", "myDESCf", "myBRANDb", "myCATEGORYc", "myJUNK2f")
                            }
                        )

    DB_CONNECTION_STRING = f"host=127.0.0.1 port=5432 dbname=ai_product_catalog user=ai_product_catalog password=ai_product_catalog123"
    
    productDataSet = ProductDataSet("test_data", DB_CONNECTION_STRING)
    resultDF = productDataSet.import_df(testDF,
                        {
                            "test_sku": productDataSet.ProductColumns.SKU, 
                            "test_price": productDataSet.ProductColumns.PRICE,
                            "test_brand": productDataSet.ProductColumns.BRAND_DESC,
                            "test_category": productDataSet.ProductColumns.CATEGORY_DESC,
                            "test_name": productDataSet.ProductColumns.NAME,
                            "test_desc": productDataSet.ProductColumns.DESC
                        }
                    )
    productDataSet.persist()
    
    print(resultDF.head())
