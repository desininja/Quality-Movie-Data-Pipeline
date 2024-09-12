---

# Quality-Movie-Data-Pipeline

## Overview

The Quality Movie Data Pipeline project is designed to automate the ingestion, processing, and storage of movie data using various AWS services. This pipeline uses AWS Glue, Amazon S3, Amazon Redshift, AWS Step Functions, and AWS EventBridge to create a robust ETL (Extract, Transform, Load) solution with data quality checks. It filters movies based on their IMDb rating and stores the processed data in Redshift for further analysis. 

### Architectural Diagram

![Quality-Movie-Data-Ingestion-Architecture](https://github.com/desininja/Quality-Movie-Data-Pipeline/blob/main/Project%20Related%20Screenshots/Quality-Movie-Data-Ingestion-Architecture.png)

## Objective

The main goal is to create a reliable ETL pipeline on AWS that:

1. **Stores raw data** in Amazon S3.
2. **Triggers a data pipeline** using AWS EventBridge and Step Functions.
3. **Processes data using AWS Glue**, applying data quality checks.
4. **Stores clean data in Amazon Redshift** for analytics.
5. **Saves bad records and rule outcomes** back to S3 for review.

## Components

1. **Amazon S3**: Used to store input data, bad records, and rule outcomes.
2. **AWS Glue Crawler**: Crawls the input data stored in S3 to create or update the metadata in the Glue Data Catalog.
3. **AWS Glue ETL Job**: Processes the data, applies data quality rules, and loads it into Amazon Redshift.
4. **AWS Step Functions**: Orchestrates the Glue ETL pipeline and manages the workflow.
5. **AWS EventBridge**: Triggers the Step Function based on specific events.

## Bucket Structure

- `quality-movie-bucket/input_data/`: Contains the input data in CSV format.
- `quality-movie-bucket/bad-records/`: Contains the records that failed data quality checks.
- `quality-movie-bucket/rule_outcome_from_etl/`: Stores the outcome of the data quality rules applied during the ETL process.

## Permissions Required

To ensure that all the services interact correctly, appropriate IAM roles and permissions must be assigned:

1. **AWS Glue IAM Role**: Must have permissions to read/write to Amazon S3, run Glue jobs, access the Glue Data Catalog, redshift and log to CloudWatch.
2. **Amazon S3 Bucket Policy**: Allow access from AWS Glue and Redshift.
3. **Redshift IAM Role**: Must have permissions to load data from Glue.
4. **VPC Endpoints**: Add S3, Glue, and monitoring endpoints to the VPC associated with the Glue job.
5. **Redshift Security Group**: Edit inbound rules to allow access from the VPC where the Glue job runs.

Ensure that all the services interacting with each other have the respective policies attached to their IAM roles.

## ETL Pipeline Steps

### AWS Glue Step-by-Step Process:
- [Glue Job Code](https://github.com/desininja/Quality-Movie-Data-Pipeline/blob/main/Glue_Script.py)  

1. **Start AWS Glue Crawler**:
   - The crawler scans the input data stored in `quality-movie-bucket/input_data/` in S3 and updates the metadata in the AWS Glue Data Catalog.

2. **Check Crawler Status**:
   - The Step Function checks if the crawler is running or has finished. If it's running, it waits and checks again after 15 seconds.

3. **Run AWS Glue ETL Job**:
   - Once the crawler finishes, the Glue ETL job starts. This job reads the data from the Glue Data Catalog and applies data quality checks.

4. **Apply Data Quality Checks**:
   - The Glue job filters the movies based on IMDb ratings (e.g., between 8.5 and 10.3). Movies not meeting the criteria are considered "bad records."

5. **Save Bad Records**:
   - Records that fail the data quality check are saved in `quality-movie-bucket/bad-records/`.

6. **Store Rule Outcomes**:
   - The results of the data quality checks (e.g., number of failed records) are stored in `quality-movie-bucket/rule_outcome_from_etl/`.

7. **Change Data Schema and Load to Redshift**:
   - The Glue job modifies the schema of the filtered data and loads it into the Amazon Redshift table `redshiftdev_movies_imdb_movies_rating` for further analysis.

8. **Send Notification**:
   - If the Glue job completes successfully, an SNS notification is sent to inform users. If it fails, a failure notification is sent instead.

![Glue-Visual-ETL-Diagram](https://github.com/desininja/Quality-Movie-Data-Pipeline/blob/main/Project%20Related%20Screenshots/Glue%20Visual%20ETL.png)

## AWS Step Function Workflow:
- [Step Function Code](https://github.com/desininja/Quality-Movie-Data-Pipeline/blob/main/Step_function.json)

1. **Start the Crawler**: Initiates the process to scan the input data.
2. **Check If the Crawler is Running**: Continuously checks the status of the crawler.
3. **Wait Until Crawler Completes**: Waits for 15 seconds and checks again if the crawler is still running.
4. **Run Glue Job**: Once the crawler is done, it triggers the Glue ETL job.
5. **Check Glue Job Status**: Verifies if the Glue job has successfully completed.
6. **Send Success Notification**: If the job is successful, a notification is sent.
7. **Send Failure Notification**: If the job fails, a different notification is sent.

![Step-Function-Workflow-Diagram](https://github.com/desininja/Quality-Movie-Data-Pipeline/blob/main/Project%20Related%20Screenshots/stepfunctions_graph.png)
