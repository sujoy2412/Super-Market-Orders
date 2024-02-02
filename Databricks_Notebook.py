# Databricks notebook source
# MAGIC %md 
# MAGIC ***Mounting of Databricks Workspace on Data Lake***

# COMMAND ----------

mount_dict={'/mnt/staging':'supermarketdata'}
for i,j in mount_dict.items():
    if i not in dbutils.fs.mounts():
        try:
            dbutils.fs.mount(source=f'wasbs://{j}@supermarketdataingest.blob.core.windows.net',mount_point=i,extra_configs={"fs.azure.account.key.supermarketdataingest.blob.core.windows.net":dbutils.secrets.get('mounting','ADLSaccessKey')})
        except Exception:
            print("Already Mounted")

# COMMAND ----------

dbutils.fs.mounts()

# COMMAND ----------

# MAGIC %fs ls /mnt/staging
# MAGIC

# COMMAND ----------

schema_1 = 'ID long, Birth_Year Int, Education string, Marital_Status string, Income float'

# COMMAND ----------

# MAGIC %md
# MAGIC ***Cleaning of Customer Dataset***

# COMMAND ----------

customer_df = spark.read.format("csv").option("header", "true").schema(schema_1).load("dbfs:/mnt/staging/customer_data/")

# COMMAND ----------

customer_df.show(10)

# COMMAND ----------

customer_df.createOrReplaceTempView("Customer_table")


# COMMAND ----------

spark.sql("Select SUM(CASE WHEN ID is null then 1 else 0 end) as ID_count, SUM(CASE WHEN Birth_Year is null then 1 else 0 end) as Birthyear_count, SUM(CASE WHEN Education is null then 1 else 0 end) as Education_count, SUM(CASE WHEN Marital_Status is null then 1 else 0 end) as Marital_count, SUM(CASE WHEN Income is null then 1 else 0 end) as Income_count from Customer_table").show()

# COMMAND ----------

average_df=spark.sql("select avg(Income) from Customer_table where Income is not null").collect()

# COMMAND ----------

print(average_df[0][0])

# COMMAND ----------

customer_df=customer_df.fillna({"Income" : "52247"})

# COMMAND ----------

customer_df.filter("Income is null").show()

# COMMAND ----------

customer_df.show(5)

# COMMAND ----------

spark.sql("select distinct Marital_Status from Customer_table").show()

# COMMAND ----------

from pyspark.sql.functions import when, col, lit

# COMMAND ----------

customer_df2 = customer_df.withColumn("Marital_Status", when(col("Marital_Status") == 'Alone', lit('Single')).when((col("Marital_Status") == 'Absurd') | (col("Marital_Status") == 'YOLO'), lit('Complicated')).when(col("Marital_Status") == 'Together', lit('Married')).otherwise(col("Marital_Status")))

display(customer_df2)

# COMMAND ----------

customer_df2.write \
        .mode("overwrite") \
            .option("header","true") \
                .option("path","/mnt/staging/Final_Cleaned/Customer_Final") \
                    .save()

# COMMAND ----------

# MAGIC %md ***Cleaning of Order_Items Data***

# COMMAND ----------

schema = 'Order_Item_ID LONG, Order_ID LONG, Product_ID String, Item_Quantity INT, Item_SubTotal float, Product_Price float'

# COMMAND ----------

order_df = spark.read.format("csv").schema(schema).option("header", "true").load("dbfs:/mnt/staging/order_items_data/orderitems.csv")

# COMMAND ----------

order_df.display()

# COMMAND ----------

order_df.createOrReplaceTempView("Order_table")

# COMMAND ----------

spark.sql("Select SUM(CASE WHEN Order_Item_ID is null then 1 else 0 end) as Order_Item_ID, SUM(CASE WHEN Order_ID is null then 1 else 0 end) as Order_ID, SUM(CASE WHEN Product_ID is null then 1 else 0 end) as Product_ID, SUM(CASE WHEN Item_Quantity is null then 1 else 0 end) as Item_Quantity, SUM(CASE WHEN Item_Subtotal is null then 1 else 0 end) as Item_Subtotal, SUM(CASE WHEN Product_Price is null then 1 else 0 end) as Product_Price from Order_table").show()

# COMMAND ----------

from pyspark.sql.functions import col
order_df_1 = order_df.withColumn("Item_Subtotal",col("Product_Price")*col("Item_Quantity"))

# COMMAND ----------

order_df_1.createOrReplaceTempView("Sujoy")
spark.sql("Select * from Sujoy where Item_Subtotal<>(Product_Price*Item_Quantity)").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ***Cleaning of Sales_Order***

# COMMAND ----------

schema_sales = 'Index LONG, Order_ID STRING, Customer_ID LONG, Date DATE, Status STRING, Seller_Type STRING, Seller_Name STRING, Delivery_Type STRING, Courier_Status STRING, Quantity INT, Currency STRING, Net_Amount float, Destination_City STRING, Destination_State STRING, Destination_Country STRING, Promotion_ID STRING, B2B Boolean, Courier_Vendor STRING, Payment STRING, Payment_method STRING'

# COMMAND ----------

sales_data = spark.read.format("csv").option("header",True) \
    .schema(schema_sales).option("dateFormat","MM-dd-yy").load("dbfs:/mnt/staging/sales_data/sales.csv")

# COMMAND ----------

display(sales_data)

# COMMAND ----------

sales_data.createOrReplaceTempView("Sales")

# COMMAND ----------

Final_salesorder = spark.sql("""Select A.Order_ID, A.Customer_ID, A.Date, B.Product_ID, B.Item_Quantity, A.Currency, B.Product_Price, B.Item_Subtotal, A.Status, A.Seller_Type, A.Seller_Name, A.Delivery_Type, A.Destination_City, A.Destination_State, A.Payment_method  from Sales A 
          left join Sujoy B 
          on A.Index=B.Order_ID""")

# COMMAND ----------

Final_salesorder.display()

# COMMAND ----------

Final_salesorder.createOrReplaceTempView("Final_SaleOrd")

# COMMAND ----------

spark.sql("""SELECT * FROM Final_SaleOrd 
          WHERE Product_ID IS NOT NULL""").display()

# COMMAND ----------

Cleaned_saleorder=spark.sql("SELECT Customer_ID, CASE WHEN Customer_ID IS NOT NULL THEN 'Member' ELSE 'Non-Member' end as Membership, Order_ID,Date,Product_ID,Item_Quantity,Currency,Product_Price,Item_Subtotal,Status,Seller_Type,Seller_Name,Delivery_Type,Destination_City,Destination_State,Payment_method FROM Final_SaleOrd WHERE Product_ID IS NOT NULL")

# COMMAND ----------

Uncleaned_saleorder=spark.sql("SELECT Customer_ID, CASE WHEN Customer_ID IS NOT NULL THEN 'Member' ELSE 'Non-Member' end as Membership, Order_ID,Date,Product_ID,Item_Quantity,Currency,Product_Price,Item_Subtotal,Status,Seller_Type,Seller_Name,Delivery_Type,Destination_City,Destination_State,Payment_method FROM Final_SaleOrd WHERE Product_ID IS NULL")

# COMMAND ----------

Cleaned_saleorder.createOrReplaceTempView("Saleorder_Table")

# COMMAND ----------

schema_prod='Product_ID int, Product string, Category String, Sub_Category String, Brand String, Sale_Price float,Market_Price float, Type String, Rating float, Product_ID2 String'

# COMMAND ----------

product_df = spark.read.format("csv").option("header", "true").schema(schema_prod).load("dbfs:/mnt/staging/productlist01/Product_List.csv")
product_df.display()

# COMMAND ----------

product_df2=product_df.drop("Product_ID")

# COMMAND ----------

product_df2.display()

# COMMAND ----------

product_df3=product_df2.withColumnRenamed("Product_ID2", "Product_ID")

# COMMAND ----------

product_df3.filter("Product like 'Snacks & Branded Foods'").show()

# COMMAND ----------

product_df3.createOrReplaceTempView("Product_table1")

# COMMAND ----------

# MAGIC %sql select * from Product_table1 where Product_ID is null

# COMMAND ----------

product_df4= product_df3.dropna(subset=["Product_ID"])
product_df4.createOrReplaceTempView("Product_T2")

# COMMAND ----------

spark.sql("SELECT SUM(CASE WHEN Product_ID IS NULL THEN 1 else 0 end) as productid_count, SUM(CASE WHEN Product IS NULL THEN 1 else 0 end)as productcount, SUM(case when category is null then 1 else 0 end) as category_count, SUM(case when sub_category is null then 1 else 0 end) as subcat_count, sum(case when brand is null then 1 else 0 end) as brand_count, sum(case when sale_price is null then 1 else 0 end) as price_count, sum(case when market_price is null then 1 else 0 end) as market_count, sum(case when type is null then 1 else 0 end) as type_count, sum(case when rating is null then 1 else 0 end) as rating_count, sum(case when Product_ID is null then 1 else 0 end) as productid_count from Product_T2").show()

# COMMAND ----------

Final_salesorder=spark.sql("""select A.Product_ID, B.Customer_ID, B.Order_ID, A.Product, A.brand, A.category, A.sub_category, A.market_price, A.sale_price, A.type, A.rating, B.Currency, B.Delivery_Type, B.Destination_City, B.Destination_State, B.Item_Quantity, B.Item_Subtotal, B.Membership, B.Payment_method 
                                from Product_T2 A JOIN Saleorder_Table B on A.Product_ID = B.Product_ID where Customer_ID is not null""")

# COMMAND ----------

Final_salesorder.write \
    .mode("overwrite") \
        .option("header","true") \
            .option("path","/mnt/staging/Final_Cleaned/Sales_Order_Final") \
                .save()

# COMMAND ----------

Final_salesorder.printSchema()
