# Super-Market-Orders

Microsoft Power BI link (https://app.powerbi.com/view?r=eyJrIjoiOTVjMzgwZDktNjc4Zi00OWY4LTllZTQtM2NhZDkwNGEzZTYxIiwidCI6IjEzZTNiMTg2LWM0NDYtNGFhYi05YzZkLTlhYjliYjc2ODE2YyIsImMiOjh9)

# Project Summary:

Built a comprehensive data pipeline for a supermarket's e-commerce operations, integrating diverse datasets on Azure and Amazon S3. Utilized Azure Data Lake, Azure Data Factory, Azure Databricks, and other tools to automate hourly data ingestion, cleaning, and processing. Leveraged Azure SQL for storing processed data and Power BI for dynamic visualizations.

# Key Highlights:

1. Automated hourly ingestion of Orders and order items via HTTP connection, followed by conditional ingestion of customer data from SQL Database and products data from Amazon S3.
2. Implemented data cleaning processes for Orders, customer data, and order_items, ensuring data integrity and consistency.
3. Conducted dataset joins to extract valuable insights:
4. Analyzed sales distribution across states for the fiscal year (2022).
5. Evaluated the overall preference for delivery modes and payment methods.
6. Identified best-selling products in different categories.
7. Explored the preferred modes of delivery in various states.
8. Calculated net sales over the year.
9. Presented the analytical results through a visually compelling Power BI dashboard.

# Tech Stack:

1. Azure Data Lake and Databricks for a robust landing zone and data processing.
2. Azure Data Factory for efficient orchestration and data ingestion.
3. Amazon S3 as a data source for additional datasets.
4. Azure Key Vault for secure credential storage.
5. Azure SQL for storing processed data, ensuring a scalable and reliable solution.
6. Power BI used for creating dynamic and insightful dashboards.

This project demonstrates expertise in end-to-end data engineering, employing a powerful tech stack to optimize data processing, storage, and visualization for informed business decisions in the e-commerce domain.
