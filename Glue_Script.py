import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrameCollection
from awsgluedq.transforms import EvaluateDataQuality
import concurrent.futures
import re

class GroupFilter:
      def __init__(self, name, filters):
        self.name = name
        self.filters = filters

def apply_group_filter(source_DyF, group):
    return(Filter.apply(frame = source_DyF, f = group.filters))

def threadedRoute(glue_ctx, source_DyF, group_filters) -> DynamicFrameCollection:
    dynamic_frames = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_filter = {executor.submit(apply_group_filter, source_DyF, gf): gf for gf in group_filters}
        for future in concurrent.futures.as_completed(future_to_filter):
            gf = future_to_filter[future]
            if future.exception() is not None:
                print('%r generated an exception: %s' % (gf, future.exception()))
            else:
                dynamic_frames[gf.name] = future.result()
    return DynamicFrameCollection(dynamic_frames, glue_ctx)

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Script generated for node AWS Glue Data Catalog
AWSGlueDataCatalog_node1726079566775 = glueContext.create_dynamic_frame.from_catalog(database="imdb-movies", table_name="input_data", transformation_ctx="AWSGlueDataCatalog_node1726079566775")

# Script generated for node Evaluate Data Quality
EvaluateDataQuality_node1726079815134_ruleset = """
    # Example rules: Completeness "colA" between 0.4 and 0.8, ColumnCount > 10
    Rules = [
        ColumnValues "imdb_rating" between 8.5 and 10.3
    ]
"""

EvaluateDataQuality_node1726079815134 = EvaluateDataQuality().process_rows(frame=AWSGlueDataCatalog_node1726079566775, ruleset=EvaluateDataQuality_node1726079815134_ruleset, publishing_options={"dataQualityEvaluationContext": "EvaluateDataQuality_node1726079815134", "enableDataQualityCloudWatchMetrics": True, "enableDataQualityResultsPublishing": True}, additional_options={"observations.scope":"ALL","performanceTuning.caching":"CACHE_NOTHING"})

# Script generated for node rowLevelOutcomes
rowLevelOutcomes_node1726079864460 = SelectFromCollection.apply(dfc=EvaluateDataQuality_node1726079815134, key="rowLevelOutcomes", transformation_ctx="rowLevelOutcomes_node1726079864460")

# Script generated for node ruleOutcomes
ruleOutcomes_node1726079866786 = SelectFromCollection.apply(dfc=EvaluateDataQuality_node1726079815134, key="ruleOutcomes", transformation_ctx="ruleOutcomes_node1726079866786")

# Script generated for node Conditional Router
ConditionalRouter_node1726079943414 = threadedRoute(glueContext,
  source_DyF = rowLevelOutcomes_node1726079864460,
  group_filters = [GroupFilter(name = "failed_records", filters = lambda row: (bool(re.match("Failed", row["DataQualityEvaluationResult"])))), GroupFilter(name = "default_group", filters = lambda row: (not(bool(re.match("Failed", row["DataQualityEvaluationResult"])))))])

# Script generated for node failed_records
failed_records_node1726079944294 = SelectFromCollection.apply(dfc=ConditionalRouter_node1726079943414, key="failed_records", transformation_ctx="failed_records_node1726079944294")

# Script generated for node default_group
default_group_node1726079944174 = SelectFromCollection.apply(dfc=ConditionalRouter_node1726079943414, key="default_group", transformation_ctx="default_group_node1726079944174")

# Script generated for node Change Schema
ChangeSchema_node1726080147183 = ApplyMapping.apply(frame=default_group_node1726079944174, mappings=[("poster_link", "string", "poster_link", "string"), ("series_title", "string", "series_title", "string"), ("released_year", "string", "released_year", "string"), ("certificate", "string", "certificate", "string"), ("runtime", "string", "runtime", "string"), ("genre", "string", "genre", "string"), ("imdb_rating", "double", "imdb_rating", "double"), ("overview", "string", "overview", "string"), ("meta_score", "long", "meta_score", "long"), ("director", "string", "director", "string"), ("star1", "string", "star1", "string"), ("star2", "string", "star2", "string"), ("star3", "string", "star3", "string"), ("star4", "string", "star4", "string"), ("no_of_votes", "long", "no_of_votes", "long"), ("gross", "string", "gross", "string")], transformation_ctx="ChangeSchema_node1726080147183")

# Script generated for node Amazon S3
AmazonS3_node1726084967885 = glueContext.write_dynamic_frame.from_options(frame=ruleOutcomes_node1726079866786, connection_type="s3", format="json", connection_options={"path": "s3://quality-movie-bucket/rule_outcome_from_etl/", "compression": "snappy", "partitionKeys": []}, transformation_ctx="AmazonS3_node1726084967885")

# Script generated for node Amazon S3
AmazonS3_node1726080517179 = glueContext.write_dynamic_frame.from_options(frame=failed_records_node1726079944294, connection_type="s3", format="json", connection_options={"path": "s3://quality-movie-bucket/bad-records/", "compression": "snappy", "partitionKeys": []}, transformation_ctx="AmazonS3_node1726080517179")

# Script generated for node AWS Glue Data Catalog
AWSGlueDataCatalog_node1726080382738 = glueContext.write_dynamic_frame.from_catalog(frame=ChangeSchema_node1726080147183, database="imdb-movies", table_name="redshiftdev_movies_imdb_movies_rating", redshift_tmp_dir="s3://aws-glue-assets-861276114026-us-east-1/temporary/",additional_options={"aws_iam_role": "arn:aws:iam::861276114026:role/service-role/AmazonRedshift-CommandsAccessRole-20240908T203537"}, transformation_ctx="AWSGlueDataCatalog_node1726080382738")

job.commit()
