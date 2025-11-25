"""Bootstrap AWS resources for AdventureStay."""

from __future__ import annotations

import os
import sys
import uuid

import boto3
from botocore.exceptions import ClientError


def aws_enabled() -> bool:
    return os.getenv("USE_AWS", "0") == "1"


def main() -> None:
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

    if not aws_enabled():
        print("USE_AWS is not enabled. Dry-run mode; no resources created.", file=sys.stderr)
        return

    session = boto3.Session(region_name=region)
    dynamodb = session.resource("dynamodb")
    s3 = session.client("s3")
    sqs = session.client("sqs")
    sns = session.client("sns")

    packages_table = ensure_packages_table(dynamodb)
    bookings_table = ensure_bookings_table(dynamodb)
    bucket_name = ensure_bucket(s3, region)
    queue_url = ensure_queue(sqs)
    topic_arn = ensure_topic(sns)

    print("\nSet these environment variables:")
    print(f"AWS_DEFAULT_REGION={region}")
    print(f"DDB_PACKAGES_TABLE_NAME={packages_table}")
    print(f"DDB_BOOKINGS_TABLE_NAME={bookings_table}")
    print(f"S3_BUCKET_NAME={bucket_name}")
    print(f"SQS_BOOKING_QUEUE_URL={queue_url}")
    print(f"SNS_BOOKING_TOPIC_ARN={topic_arn}")


def ensure_packages_table(dynamodb):
    table_name = "adventurestay_packages"
    try:
        table = dynamodb.Table(table_name)
        table.load()
        return table_name
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "ResourceNotFoundException":
            raise

    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "package_id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "package_id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    table.wait_until_exists()
    return table_name


def ensure_bookings_table(dynamodb):
    table_name = "adventurestay_bookings"
    try:
        table = dynamodb.Table(table_name)
        table.load()
        return table_name
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "ResourceNotFoundException":
            raise

    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "booking_id", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "booking_id", "AttributeType": "S"},
            {"AttributeName": "package_id", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "package_id-index",
                "KeySchema": [{"AttributeName": "package_id", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.wait_until_exists()
    return table_name


def ensure_bucket(s3, region: str) -> str:
    bucket_name = f"adventurestay-images-{uuid.uuid4().hex[:8]}"
    kwargs = {"Bucket": bucket_name}
    if region != "us-east-1":
        kwargs["CreateBucketConfiguration"] = {"LocationConstraint": region}
    s3.create_bucket(**kwargs)
    return bucket_name


def ensure_queue(sqs) -> str:
    response = sqs.create_queue(QueueName="adventurestay-bookings-queue")
    return response["QueueUrl"]


def ensure_topic(sns) -> str:
    response = sns.create_topic(Name="adventurestay-booking-notifications")
    return response["TopicArn"]


if __name__ == "__main__":
    main()
