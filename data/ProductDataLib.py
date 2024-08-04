"""Library for importing product data from third party sources.
"""
import pandas as pd
import psycopg
import openai

class ProductDataSet:
    """Self contained class for managing the process associated with importing product data
    from third party sources.
    """

    class ProductColumns:
        """Enumeration of Product-Entity Data Frame
        """
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
        """Enumeration of Brand-Entity Data Frame
        """
        DESC = "Brand_Desc"
        ID = "Brand_ID"

    class CategoryColumns:
        """Enumeration of Category-Entity Data Frame
        """
        DESC = "Category_Desc"
        ID = "Category_ID"

    class EmbeddingColumns:
        """Enumeration of Embedding-Entity (Product-Embedding) Data Frame
        """
        PRODUCT_ID = "Product_ID"
        MODEL = "Model"
        TEXT_SEGMENT = "Text_Segment"
        EMBEDDING = "Embedding"

    data_source_description = None
    target_database_conn_str = None
    max_embeddings_allowed = -1
    products_df = None
    brands_df = None
    categories_df = None
    embeddings_df = None
    openai_client = None
    openai_model_name = None
    embeddings_counter = 0

    def __init__(self,
                 data_source_description,
                 target_database_conn_str,
                 openai_api_url,
                 openai_model_name,
                 max_embeddings_allowed = -1):
        """Initialize the product data set processing library.

        Keyword arguments:
        data_source_description -- short form description of the data source
        target_database_conn_str -- destination database connection string
        max_embeddings_allowed -- optional limit for the number of embeddings processed by the load.  
                                useful for managing costs during development and testing.
        """
        self.data_source_description = data_source_description
        self.target_database_conn_str = target_database_conn_str
        self.max_embeddings_allowed = max_embeddings_allowed
        self.openai_model_name = openai_model_name

        if self.target_database_conn_str is None or len(self.target_database_conn_str) == 0:
            raise RuntimeError("Database Connection String for Destination DB is required!")

        self.openai_client = openai.OpenAI()
        if openai_api_url not in (None, ""):
            print ("Overriding OpenAI Base URL:", openai_api_url)
            openai.base_url = openai_api_url


    def import_df(self, input_df, mapping):
        """Make a copy of the provided data frame and translate its data structure to the product
        library's canonical format based on the provided field mappings.  The master data frame
        is then stored within the class instance in self.products_df.  This process also involves 
        denormalizing the category and brand data into a separate look up table.

        Keyword arguments:
        input_df -- data frame containing product data loaded from third party source
        mapping -- translations from provided data frame to canonical format
        """
        self.products_df = input_df.copy(deep=True)
        self.products_df.rename(columns=mapping, inplace=True)

        self.products_df = self.products_df[self.products_df.columns.intersection(
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

        self.products_df.drop_duplicates(inplace = True)
        self.brands_df = pd.DataFrame({self.BrandColumns.DESC:
                                      self.products_df[self.ProductColumns.BRAND_DESC]
                                      .drop_duplicates() })
        self.categories_df = pd.DataFrame({self.CategoryColumns.DESC:
                                          self.products_df[self.ProductColumns.CATEGORY_DESC]
                                          .drop_duplicates() })

        return self.products_df


    def sql_execute(self, sql, values, fetch = True):
        """Utility function for executing SQL statements against the destination database.

        Keyword arguments:
        sql -- SQL statement to execute
        values -- values to substitute into parameterized sql
        fetch -- flag indicating whether the results are expected
        """
        with psycopg.connect(self.target_database_conn_str) as db_connection:
            with db_connection.cursor() as c:
                c.execute(sql, values)

                if fetch:
                    rows = c.fetchall()
                    return rows

        return None


    def sql_insert_dataframe_row(self, row, insert_sql, exists_sql, fetch=True):
        """Utility method that will insert a single row of a dataframe into the database.

        Keyword arguments:
        row -- values to substitute into parameterized sql
        insert_sql -- sql statement for the insert operation
        exists_sql -- sql statement used to determine if the row already exists in the database
        fetch -- flag indicating whether the results are expected from the insert statement (id?)
        """
        try:
            result = self.sql_execute(exists_sql, row, True)
        except Exception as e:
            print ("Caught Exception While Executing SQL!  ", e, "Impacting Values Were =", row)
            raise e

        if len(result) == 0:
#            print ("Not Found.  Creating....")
            result = self.sql_execute(insert_sql, row, fetch)

        if fetch:
            if len(result) == 0:
                print ("Unexpectedly NO RESULTS from neither INSERT or EXISTS statements...",
                       insert_sql, exists_sql)
                return None
            if len(result) > 1:
                print ("Unexpected MULTIPLE RESULTS from INSERT/EXISTS statements... Count=",
                       str(len(result)), insert_sql, exists_sql)
                raise RuntimeError("Unexpected MULTIPLE RESULTS from INSERT/EXISTS statements...",
                                   "Count=" + str(len(result)))

            result, = result[0]

    #        print("RESULT....  Type=", str(type(result)), "Value=", result)
            return result

        return None


    def sql_insert_dataframe(self, df, id_column, insert_sql, exists_sql, fetch=True):
        """Utility method that will insert complete dataframe into the database.

        Keyword arguments:
        df -- dataframe to be persisted into the database
        insert_sql -- sql statement for the insert operation
        exists_sql -- sql statement used to determine if the row already exists in the database
        fetch -- flag indicating whether the results are expected from the insert statement (id?)
        """
        result = df.apply(lambda row: self.sql_insert_dataframe_row(
                                row.to_dict(), insert_sql, exists_sql, fetch), axis=1)
        if fetch:
            df[id_column] = result
#        print(df.head())


    def get_brand_id_for_product(self, row):
        """Gets the brand ID that corresponds to the description contained in the provided 
        product record.

        Keyword arguments:
        row -- product record (row of a dataframe)
        """
        brand_desc = row[self.ProductColumns.BRAND_DESC]
        brand_ids = self.brands_df[self.brands_df[self.BrandColumns.DESC] ==
                                            brand_desc][self.BrandColumns.ID]
        if len(brand_ids) == 0:
            raise RuntimeError("No Brand IDs were found for the given brand descrption")
        if len(brand_ids) > 1:
            raise RuntimeError("Too many Brand IDs were found for the given brand descrption: " +
                                str(len(brand_ids)))
        return brand_ids.values[0]


    def get_category_id_for_product(self, row):
        """Gets the category ID that corresponds to the description contained in the provided
        product record.

        Keyword arguments:
        row -- product record (row of a dataframe)
        """
        category_desc = row[self.ProductColumns.CATEGORY_DESC]
        category_ids = self.categories_df[self.categories_df[self.CategoryColumns.DESC] ==
                                            category_desc][self.CategoryColumns.ID]
        if len(category_ids) == 0:
            raise RuntimeError("No Category IDs were found for the given brand descrption")
        if len(category_ids) > 1:
            raise RuntimeError("Too many Category IDs were found for the given brand descrption: " +
                                    str(len(category_ids)))
        return category_ids.values[0]


    def persist(self):
        """Save the assembled and cleaned product data set to the destination database.
        """
        self.persist_categories()
        self.products_df[self.ProductColumns.CATEGORY_ID] = self.products_df.apply(
                            lambda row: self.get_category_id_for_product(row), axis=1)

        self.persist_brands()
        self.products_df[self.ProductColumns.BRAND_ID] = self.products_df.apply(
                            lambda row: self.get_brand_id_for_product(row), axis=1)

        self.persist_products()


    def persist_categories(self):
        """Save the categories lookup table to the destination database.
        """
        insert_sql = f"""
                        INSERT INTO categories(category_desc) VALUES
                        (%({self.CategoryColumns.DESC})s)
                        RETURNING category_id;
                    """
        exists_sql = f"""
                        SELECT category_id
                        FROM categories
                        WHERE %({self.CategoryColumns.DESC})s = category_desc;
                    """
        self.sql_insert_dataframe(self.categories_df,
                                  self.CategoryColumns.ID,
                                  insert_sql,
                                  exists_sql)


    def persist_brands(self):
        """Save the brands lookup table to the destination database.
        """
        insert_sql = f"""
                        INSERT INTO brands(brand_desc)
                        VALUES (%({self.BrandColumns.DESC})s)
                        RETURNING brand_id;
                    """
        exists_sql = f"""
                        SELECT brand_id
                        FROM brands
                        WHERE %({self.BrandColumns.DESC})s = brand_desc;
                    """
        self.sql_insert_dataframe(self.brands_df, self.BrandColumns.ID, insert_sql, exists_sql)


    def persist_products(self):
        """Save the product entities to the destination database.
        """
        insert_sql = f"""
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
        exists_sql = f"""
                        SELECT product_id
                        FROM products
                        WHERE   sku = %({self.ProductColumns.SKU})s
                            AND brand_id = %({self.ProductColumns.BRAND_ID})s
                            AND product_name = %({self.ProductColumns.NAME})s
                            AND product_desc = %({self.ProductColumns.DESC})s
                            AND msrp = CAST(%({self.ProductColumns.PRICE})s as double precision)
                            AND category_id = %({self.ProductColumns.CATEGORY_ID})s
                    """
        self.sql_insert_dataframe(self.products_df, self.ProductColumns.ID, insert_sql, exists_sql)


    def load_embeddings(self):
        """Load all preconfigured embeddings from the database and into memory.
        """
        select_sql = """
                        SELECT  product_id,
                                model,
                                text_segment,
                                embedding
                        FROM product_embeddings
                    """
        rows = self.sql_execute(select_sql, {}, True)
        self.embeddings_df = pd.DataFrame(columns=(self.EmbeddingColumns.PRODUCT_ID,
                                                  self.EmbeddingColumns.MODEL,
                                                  self.EmbeddingColumns.TEXT_SEGMENT,
                                                  self.EmbeddingColumns.EMBEDDING))
        for row in rows:
            print (row)


    def refresh_embeddings(self):
        """Recreate all embeddings based on the master data frame.
        """
        self.products_df.apply(lambda row: self.append_embedding_for_product(
                                            row), axis=1, result_type='expand')
        print (self.embeddings_df.head())
        return self.embeddings_df


    def append_embedding_for_product(self, row):
        """Recreate the embedding for the provided product record.

        Keyword arguments:
        row -- product record
        """
        product_id = row[self.ProductColumns.ID]
        model = self.openai_model_name

        embedded_text = f"""'{row[self.ProductColumns.NAME]}',
                            '{row[self.ProductColumns.SKU]}',
                            {row[self.ProductColumns.PRICE]},
                            '{row[self.ProductColumns.BRAND_DESC]}',
                            '{row[self.ProductColumns.DESC]}'"""
        embedded_text = embedded_text.replace("\n", " ")

        print ("Preparing to create embedding....  Product_ID:", product_id,
                                                  "Model:", model,
                                                  "Text:\"", embedded_text, "\"")

        matching_df = self.embeddings_df[(self.embeddings_df[self.EmbeddingColumns.PRODUCT_ID]
                                                                == product_id) &
                                       (self.embeddings_df[self.EmbeddingColumns.MODEL]
                                                                == model) &
                                       (self.embeddings_df[self.EmbeddingColumns.TEXT_SEGMENT]
                                                                == embedded_text)]

        if len(matching_df) > 0:
            print ("... skipping - Some # of embeddings for product ALREADY EXIST ...",
                                matching_df.head())
            return None

        self.embeddings_counter = self.embeddings_counter + 1
        if (self.max_embeddings_allowed > 0) and (
                    self.embeddings_counter > self.max_embeddings_allowed):
            print("Maximum # of Embeddings Reached.  Skipping embedding invocation....",
                  "Limit:", self.max_embeddings_allowed, "Counter:", self.embeddings_counter)
            return None

        embedding = self.openai_client.embeddings.create(input = [embedded_text],
                                                        model=model).data[0].embedding
        print ("CREATED Embedding for ....  Text:", embedded_text)

        new_row = [ product_id, model, embedded_text, embedding ]
        self.embeddings_df.loc[len(self.embeddings_df)] = new_row
        return new_row


    def persist_embeddings(self):
        """Save the provided embeddings into the database.  The algorithm essentially merges
        what is provided with what is in the database.  
        """
        insert_sql = f"""
                        INSERT INTO product_embeddings
                        (
                            product_id,
                            model,
                            text_segment,
                            embedding
                        ) 
                        VALUES
                        (
                            %({self.EmbeddingColumns.PRODUCT_ID})s,
                            %({self.EmbeddingColumns.MODEL})s,
                            %({self.EmbeddingColumns.TEXT_SEGMENT})s,
                            %({self.EmbeddingColumns.EMBEDDING})s
                        )
                    """
        exists_sql = f"""
                        SELECT product_id, model, text_segment, embedding
                        FROM product_embeddings 
                        WHERE   product_id = %({self.EmbeddingColumns.PRODUCT_ID})s
                            AND model = %({self.EmbeddingColumns.MODEL})s
                            AND text_segment = %({self.EmbeddingColumns.TEXT_SEGMENT})s
                            AND embedding = cast(%({self.EmbeddingColumns.EMBEDDING})s
                                        as vector(1536))
                    """
        self.sql_insert_dataframe(self.embeddings_df, None, insert_sql, exists_sql, fetch=False)



if __name__ == "__main__":
    test_df = pd.DataFrame(columns=("test_sku", "test_name", "test_junk", "test_price",
                                    "test_desc", "test_brand", "test_category", "test junk2"),
                        data={
                            ("mySKUa", "myNAMEa", "myJUNKa", "1.00",
                                    "myDESCa", "myBRANDa", "myCATEGORYa", "myJUNK2a"),
                            ("mySKUb", "myNAMEb", "myJUNKb", "2.00",
                                    "myDESCb", "myBRANDa", "myCATEGORYb", "myJUNK2b"),
                            ("mySKUc", "myNAMEc", "myJUNKc", "3.00",
                                    "myDESCc", "myBRANDa", "myCATEGORYc", "myJUNK2c"),
                            ("mySKUd", "myNAMEd", "myJUNKd", "4.00",
                                    "myDESCd", "myBRANDb", "myCATEGORYa", "myJUNK2d"),
                            ("mySKUe", "myNAMEe", "myJUNKe", "5.00",
                                    "myDESCe", "myBRANDb", "myCATEGORYb", "myJUNK2e"),
                            ("mySKUf", "myNAMEf", "myJUNKf", "6.00",
                                    "myDESCf", "myBRANDb", "myCATEGORYc", "myJUNK2f")
                            }
                        )

    DB_CONNECTION_STRING = """  host=127.0.0.1
                                port=5432
                                dbname=ai_product_catalog
                                user=ai_product_catalog
                                password=ai_product_catalog123"""

    productDataSet = ProductDataSet("test_data", DB_CONNECTION_STRING,
                                    None, "text-embedding-ada-001")
    resultDF = productDataSet.import_df(test_df,
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
