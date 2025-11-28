# AdventureStay

AdventureStay is a Django 5 web application that showcases curated adventure staycation experiences (trekking, hills staycations, jungle safaris, and rustic lodging). All booking logic (validation, availability, pricing, itinerary summaries) is delegated to the reusable [`adventurestay-utils`](../adventurestay-utils) library, keeping the web layer lean.

## Features

- Manage packages and bookings with Django models/admin.
- Booking form integrates `adventurestay-utils` validators and price calculator.
- AWS integration layer (DynamoDB, S3, SQS, SNS) guarded by the `USE_AWS` flag for safe local development.
- Simple templates demonstrating listing, booking, and confirmation flows.

## Setup

1. Activate the provided `.venv`.
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
   During local dev the sibling library is installed editable via `pip install -e ../adventurestay-utils`.
3. Apply migrations:
   ```bash
   python manage.py migrate
   ```
4. Create a superuser (optional for admin):
   ```bash
   python manage.py createsuperuser
   ```
5. Run the dev server:
   ```bash
   python manage.py runserver
   ```

## AWS / Environment Variables

| Variable | Purpose |
| --- | --- |
| `USE_AWS` | Enable AWS clients when set to `1` (defaults to `0`) |
| `AWS_REGION` | Region for all AWS clients (default `ap-south-1`) |
| `DDB_BOOKINGS_TABLE_NAME` | DynamoDB table for persisting bookings |
| `DDB_PACKAGES_TABLE_NAME` | DynamoDB table for packages (future expansion) |
| `S3_BUCKET_NAME` | Bucket used to build package image URLs |
| `SQS_BOOKING_QUEUE_URL` | Queue for booking-created events |
| `SNS_BOOKING_TOPIC_ARN` | Topic used to send booking confirmations |
| `DJANGO_SECRET_KEY` | Override the default dev secret key |
| `ALLOWED_HOSTS` | Comma-separated hosts for deployment |

When `USE_AWS=0` or variables are missing, the app logs a fallback message and skips the API call to keep local testing frictionless.

## Tests

The project uses `pytest` + `pytest-django`.

```bash
python -m pytest
```

## AWS Verification

Use the built-in management command to manually exercise the AWS pipeline (creates a sample booking and triggers DynamoDB/SQS/SNS):

```bash
python manage.py verify_aws_booking_pipeline
```

The command is safe to run locally (it respects `USE_AWS`) and is handy for Cloud9/EC2 smoke tests once environment variables are configured.

## Lambda Thumbnail Pipeline

Package images uploaded to `packages/` can be post-processed by an AWS Lambda function that generates thumbnails and writes them back to S3/DynamoDB. The code lives under `lambda_functions/image_processor.py` with infrastructure defined in `infra/lambda_image_processor.yaml`.

Deploy workflow from Cloud9 (requires Pillow bundled into the deployment zip or a Lambda layer):

```bash
# 1. Package the Lambda code (include dependencies under site-packages/)
mkdir -p build/image_processor
cp lambda_functions/image_processor.py build/image_processor/
# cp -r vendor/PIL build/image_processor/  # if bundling Pillow
cd build/image_processor
zip -r ../image_processor.zip .

# 2. Upload to an S3 bucket used for CloudFormation packages
aws s3 cp ../image_processor.zip s3://<deployment-bucket>/lambda/image_processor.zip

# 3. Package the CloudFormation template
cd ~/environment/adventurestay
aws cloudformation package \
  --template-file infra/lambda_image_processor.yaml \
  --s3-bucket <deployment-bucket> \
  --output-template-file infra/lambda_image_processor-packaged.yaml \
  --parameter-overrides \
      CodeS3Bucket=<deployment-bucket> \
      CodeS3Key=lambda/image_processor.zip \
      PackagesBucketName=<your-adventurestay-bucket> \
      PackagesTableName=adventurestay_packages

# 4. Deploy the stack
aws cloudformation deploy \
  --template-file infra/lambda_image_processor-packaged.yaml \
  --stack-name adventurestay-image-processor \
  --capabilities CAPABILITY_IAM
```

After deployment, every new object under `packages/` triggers the Lambda, which writes a thumbnail to `thumbnails/` and updates the DynamoDB item with `thumbnail_key`.

## Deployment Notes

- The project is cloud-ready: set `USE_AWS=1` and configure the DynamoDB table, SQS queue, SNS topic, and S3 bucket listed above (IAM role permissions required).
- `requirements.txt` references the released PyPI name `adventurestay-utils` so containers or CI pipelines can install the shared logic cleanly.
- Templates intentionally lightweight; front-end teams can enhance them without touching the core booking flow.
