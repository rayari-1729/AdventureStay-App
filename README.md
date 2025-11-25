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

## Deployment Notes

- The project is cloud-ready: set `USE_AWS=1` and configure the DynamoDB table, SQS queue, SNS topic, and S3 bucket listed above (IAM role permissions required).
- `requirements.txt` references the released PyPI name `adventurestay-utils` so containers or CI pipelines can install the shared logic cleanly.
- Templates intentionally lightweight; front-end teams can enhance them without touching the core booking flow.
