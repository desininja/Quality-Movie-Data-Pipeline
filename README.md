---

# Quality Movie Data Pipeline

## Overview

The **Quality Movie Data Pipeline** project automates the ingestion, processing, and storage of movie data using AWS services. It leverages AWS Glue, Amazon S3, Amazon Redshift, AWS Step Functions, and AWS EventBridge to create a robust ETL (Extract, Transform, Load) pipeline with built-in data quality checks. This pipeline filters movies based on IMDb ratings and stores the processed data in Amazon Redshift for analytical purposes.

### Architectural Diagram

![Quality-Movie-Data-Ingestion-Architecture](https://github.com/desininja/Quality-Movie-Data-Pipeline/blob/main/Project%20Related%20Screenshots/Quality-Movie-Data-Ingestion-Architecture.png)

## Objective

The primary goal is to develop a reliable ETL pipeline on AWS that:

1. **Stores raw data** in Amazon S3.
2. **Triggers the data pipeline** using AWS EventBridge and Step Functions.
3. **Processes data with AWS Glue**, applying data quality checks.
4. **Stores cleaned data in Amazon Redshift** for analytics.
5. **Saves bad records and rule outcomes** back to S3 for review.

## Components

1. **Amazon S3**: Stores input data, bad records, and rule outcomes.
2. **AWS Glue Crawler**: Scans the input data in S3 to create or update the metadata in the Glue Data Catalog.
3. **AWS Glue ETL Job**: Processes the data, applies data quality rules, and loads it into Amazon Redshift.
4. **AWS Step Functions**: Manages and orchestrates the Glue ETL pipeline workflow.
5. **AWS EventBridge**: Triggers the Step Function based on predefined events.

## Bucket Structure

- `quality-movie-bucket/input_data/`: Contains input data in CSV format.
- `quality-movie-bucket/bad-records/`: Stores records that failed data quality checks.
- `quality-movie-bucket/rule_outcome_from_etl/`: Holds the outcomes of the data quality checks applied during the ETL process.

## Permissions Required

To ensure seamless interaction among services, appropriate IAM roles and permissions must be set up:

1. **AWS Glue IAM Role**: Permissions to read/write to S3, run Glue jobs, access the Glue Data Catalog, Redshift, and log to CloudWatch.
2. **Amazon S3 Bucket Policy**: Grants access to AWS Glue and Redshift.
3. **Redshift IAM Role**: Permissions to load data from Glue.
4. **VPC Endpoints**: S3, Glue, and monitoring endpoints must be added to the VPC associated with the Glue job.
5. **Redshift Security Group**: Modify inbound rules to allow access from the VPC where the Glue job is running.

Ensure all interacting services have the necessary IAM policies attached.

## ETL Pipeline Workflow

### AWS Glue ETL Process
- [Glue Job Code](https://github.com/desininja/Quality-Movie-Data-Pipeline/blob/main/Glue_Script.py)

1. **Start AWS Glue Crawler**: Scans input data in `quality-movie-bucket/input_data/` and updates the Glue Data Catalog.
2. **Check Crawler Status**: Step Function monitors if the crawler is running and waits 15 seconds before rechecking.
3. **Run AWS Glue ETL Job**: After the crawler completes, the Glue ETL job is triggered to process the data.
4. **Apply Data Quality Checks**: Filters movies based on IMDb ratings (e.g., between 8.5 and 10.3); non-conforming movies are labeled as "bad records."
5. **Save Bad Records**: Failing records are stored in `quality-movie-bucket/bad-records/`.
6. **Store Rule Outcomes**: Data quality rule results are saved in `quality-movie-bucket/rule_outcome_from_etl/`.
7. **Transform Data Schema and Load to Redshift**: The job alters the schema and loads the filtered data into the `redshiftdev_movies_imdb_movies_rating` table in Amazon Redshift.
8. **Send Notification**: On successful job completion, an SNS notification is sent; otherwise, a failure notification is triggered.

![Glue-Visual-ETL-Diagram](https://github.com/desininja/Quality-Movie-Data-Pipeline/blob/main/Project%20Related%20Screenshots/Glue%20Visual%20ETL.png)

## AWS Step Function Workflow
- [Step Function Code](https://github.com/desininja/Quality-Movie-Data-Pipeline/blob/main/Step_function.json)

1. **Start the Crawler**: Initiates the scanning process.
2. **Check Crawler Status**: Monitors the crawler's status.
3. **Wait Until Crawler Completes**: Waits for the crawler to finish, checking every 15 seconds.
4. **Run Glue Job**: Triggers the Glue ETL job post-crawler completion.
5. **Check Glue Job Status**: Ensures the Glue job has completed successfully.
6. **Send Success Notification**: Sends a notification on job success.
7. **Send Failure Notification**: Sends a notification on job failure.

![Step-Function-Workflow-Diagram](https://github.com/desininja/Quality-Movie-Data-Pipeline/blob/main/Project%20Related%20Screenshots/stepfunctions_graph.png)

## Conclusion

The **Quality Movie Data Pipeline** efficiently automates the ETL process for movie data using AWS services. It is built to ensure high data quality, scalability, and cost-effectiveness, providing a strong foundation for data-driven decision-making.

## Improvement Opportunities

1. **Advanced Data Validation**: Introduce anomaly detection and outlier handling.
2. **Enhanced Monitoring**: Use AWS CloudWatch Alarms or third-party tools for better visibility.
3. **Performance Optimization**: Tune Glue jobs by optimizing Spark configurations and file formats.
4. **Data Lake Integration**: Implement AWS Lake Formation for data governance and security.
5. **Expanded Analytics**: Integrate visualization tools like Amazon QuickSight or Power BI.
6. **Cost Management**: Optimize costs by monitoring AWS usage and considering alternatives.

## Future Work

Future developments could include an interactive interface for managing ETL workflows, incorporating CI/CD pipelines for automated deployments, and expanding capabilities to handle more complex data processing requirements.
