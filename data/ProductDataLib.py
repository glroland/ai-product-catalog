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

    class EmbeddingColumns:
        PRODUCT_ID = "Product_ID"
        ENGINE = "Engine"
        MODEL = "Model"
        EMBEDDING = "Embedding"

    PROVIDER_OPENAI = "openai"
    PROVIDER_OPENAI_EMBEDDINGS_MODEL = "text-embedding-ada-002"

    dataSourceDescription = None
    targetDatabaseConnString = None
    maxEmbeddingsAllowed = -1
    productsDF = None
    brandsDF = None
    categoriesDF = None
    embeddingsDF = None
    openaiClient = None
    embeddingsCounter = 0

    def __init__(self, dataSourceDescription, targetDatabaseConnString, maxEmbeddingsAllowed = -1):
        self.dataSourceDescription = dataSourceDescription
        self.targetDatabaseConnString = targetDatabaseConnString
        self.maxEmbeddingsAllowed = maxEmbeddingsAllowed

        if self.targetDatabaseConnString == None or len(self.targetDatabaseConnString) == 0:
            raise RuntimeError("Database Connection String for Destination DB is required!")
        
        self.openaiClient = openai.OpenAI()


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


    def sql_execute(self, sql, values, fetch = True):
        with psycopg.connect(self.targetDatabaseConnString) as db_connection:
            with db_connection.cursor() as c:
                c.execute(sql, values)

                if fetch:
                    rows = c.fetchall()
                    return rows


    def sql_insert_dataframe_row(self, row, insertSQL, existsSQL, fetch=True):
        try:
            result = self.sql_execute(existsSQL, row, True)
        except Exception as e:
            print ("Caught Exception While Executing SQL!  ", e, "Impacting Values Were =", row)
            raise e
        
        if (len(result) == 0):
#            print ("Not Found.  Creating....")
            result = self.sql_execute(insertSQL, row, fetch)

        if fetch:
            if len(result) == 0:
                print ("Unexpectedly NO RESULTS from neither INSERT or EXISTS statements...", insertSQL, existsSQL)
                return None
            elif len(result) > 1:
                print ("Unexpectedly MULTIPLE RESULTS from INSERT or EXISTS statements... Count=", str(len(result)), insertSQL, existsSQL)
                raise RuntimeError("Unexpectedly MULTIPLE RESULTS from INSERT or EXISTS statements... Count=" + str(len(result)))

            result, = result[0]

    #        print("RESULT....  Type=", str(type(result)), "Value=", result)
            return result
    

    def sql_insert_dataframe(self, df, idColumn, insertSQL, existsSQL, fetch=True):
        result = df.apply(lambda row: self.sql_insert_dataframe_row(row.to_dict(), insertSQL, existsSQL, fetch), axis=1)
        if fetch:
            df[idColumn] = result
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


    def load_embeddings(self):
        selectSQL = f"""
                        SELECT  product_id,
                                engine,
                                model,
                                embedding
                        FROM product_embeddings
                    """
        rows = self.sql_execute(selectSQL, {}, True)
        self.embeddingsDF = pd.DataFrame(columns=(self.EmbeddingColumns.PRODUCT_ID,
                                                  self.EmbeddingColumns.ENGINE,
                                                  self.EmbeddingColumns.MODEL,
                                                  self.EmbeddingColumns.EMBEDDING))
        for row in rows:
            print (row)


    def refresh_embeddings(self):
        self.productsDF.apply(lambda row: self.append_embedding_for_product(row), axis=1, result_type='expand')
        print (self.embeddingsDF.head())
        return self.embeddingsDF


    def append_embedding_for_product(self, row):
        productId = row[self.ProductColumns.ID]
        engine = self.PROVIDER_OPENAI
        model = self.PROVIDER_OPENAI_EMBEDDINGS_MODEL
        
        embedded_text = f"""'{row[self.ProductColumns.NAME]}', '{row[self.ProductColumns.SKU]}', {row[self.ProductColumns.PRICE]}, '{row[self.ProductColumns.BRAND_DESC]}', '{row[self.ProductColumns.DESC]}'"""
        embedded_text = embedded_text.replace("\n", " ")

        print ("Preparing to create embedding....  Product_ID:", productId, "Engine:", engine, "Model:", model, "Text:\"", embedded_text, "\"")

        matchingDF = self.embeddingsDF[(self.embeddingsDF[self.EmbeddingColumns.PRODUCT_ID] == productId) &
                                       (self.embeddingsDF[self.EmbeddingColumns.ENGINE] == engine) &
                                       (self.embeddingsDF[self.EmbeddingColumns.MODEL] == model)]
        
        if len(matchingDF) > 0:
            print ("... skipping - Some # of embeddings for product ALREADY EXIST ...", matchingDF.head())
            return None

        self.embeddingsCounter = self.embeddingsCounter + 1
        if (self.maxEmbeddingsAllowed > 0) and (self.embeddingsCounter > self.maxEmbeddingsAllowed):
            print("Maximum # of Embeddings Reached.  Skipping embedding invocation....  Limit:", self.maxEmbeddingsAllowed, "Counter:", self.embeddingsCounter)
            return

        embedding = self.openaiClient.embeddings.create(input = [embedded_text], model=model).data[0].embedding
        print ("CREATED Embedding for ....  Text:", embedded_text)

        newRow = [ productId, engine, model, embedding ]
        self.embeddingsDF.loc[len(self.embeddingsDF)] = newRow
        return newRow

    def persist_embeddings(self):
        insertSQL = f"""
                        INSERT INTO product_embeddings
                        (
                            product_id,
                            engine,
                            model,
                            embedding
                        ) 
                        VALUES
                        (
                            %({self.EmbeddingColumns.PRODUCT_ID})s,
                            %({self.EmbeddingColumns.ENGINE})s,
                            %({self.EmbeddingColumns.MODEL})s,
                            %({self.EmbeddingColumns.EMBEDDING})s
                        )
                    """
        existsSQL = f"""
                        SELECT product_id, engine, model, embedding
                        FROM product_embeddings 
                        WHERE   product_id = %({self.EmbeddingColumns.PRODUCT_ID})s
                            AND engine = %({self.EmbeddingColumns.ENGINE})s
                            AND model = %({self.EmbeddingColumns.MODEL})s
                            AND embedding = cast(%({self.EmbeddingColumns.EMBEDDING})s as vector(1536))
                    """
        self.sql_insert_dataframe(self.embeddingsDF, None, insertSQL, existsSQL, fetch=False)



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
    productDataSet.load_embeddings()
    productDataSet.refresh_embeddings()
    productDataSet.persist_embeddings()
    
    print(resultDF.head())
