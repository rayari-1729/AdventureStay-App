# AdventureStay Deployment & Troubleshooting Guide

## 1. Project Overview

AdventureStay is a Django + AWS-based booking platform using:
- **Elastic Beanstalk** (Hosting)
- **DynamoDB** (Packages & bookings)
- **S3** (Images)
- **SNS** (Booking email notifications)
- **SQS** (Event pipeline)
- **Lambda** (Image processing)
- **Cloud9** (Local development)

This documentation summarizes:
- Project structure  
- Deployment flow  
- DynamoDB image fix  
- SNS notification fix  
- Required environment variables  
- Troubleshooting steps  

---

## 2. Project Structure

```
adventurestay/
├── adventurestay/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│
├── experiences/
│   ├── services/
│   │   ├── aws_s3.py
│   │   ├── aws_sns.py
│   │   ├── aws_sqs.py
│   │   ├── dynamodb_repository.py
│   │   ├── packages_repository.py
│   ├── templates/
│   ├── views.py
│   ├── models.py
│
├── infra/
│   ├── seed_packages.py
│   ├── bootstrap_aws.py
│   ├── lambda_image_processor.yaml
│
├── .ebextensions/
├── .platform/
├── manage.py
├── requirements.txt
```

---

## 3. Deployment Workflow (Elastic Beanstalk)

### **Deploy**
```
eb deploy
```

### **Create new EB environment**
```
eb create <env-name> --service-role LabRole --instance_profile LabInstanceProfile
```

### **Check status**
```
eb status
```

---

## 4. DynamoDB Package Image Issue & Fix

### Problem  
Images were stuck on:
```
https://images.example.com/...
```

### Causes  
1. Django DB (`db.sqlite3`) had old seed data  
2. EB was reading from Django DB, NOT DynamoDB  
3. `USE_AWS=1` missing  
4. `S3_BUCKET_NAME` missing → `resolve_image_url()` returned raw filenames  
5. package_code mismatch:  
   - DynamoDB: `TREK-001`  
   - Django: `TREK001`  

### Fix  
Set correct EB environment variables:

```
eb setenv USE_AWS=1 DDB_PACKAGES_TABLE_NAME=adventurestay_packages DDB_BOOKINGS_TABLE_NAME=adventurestay_bookings AWS_DEFAULT_REGION=us-east-1 S3_BUCKET_NAME=adventurestay-images-xxxxxx
```

Then redeploy:
```
eb deploy
```

---

## 5. SNS Booking Notification Issue & Fix

### Problem  
SNS booking confirmation emails were not arriving.

### Causes  
1. SNS client used wrong region (`AWS_REGION` missing)  
2. Missing EB variable: `SNS_BOOKING_TOPIC_ARN`  
3. Email subscription not confirmed  

### Fix

#### **1. Update SNS client region**
In `aws_sns.py`:

```python
def get_sns_client():
    if not aws_enabled():
        log_local_fallback("sns")
        return None
    region = getattr(settings, "AWS_DEFAULT_REGION", "us-east-1")
    return boto3.client("sns", region_name=region)
```

#### **2. Set SNS topic in EB**
```
eb setenv SNS_BOOKING_TOPIC_ARN=arn:aws:sns:us-east-1:XXXXXX:adventurestay-booking-notifications
```

#### **3. Test SNS**
```
aws sns publish --topic-arn <arn> --message "Test"
```

---

## 6. Correct EB Environment Variables (Final)

```
USE_AWS=1
AWS_DEFAULT_REGION=us-east-1
DDB_PACKAGES_TABLE_NAME=adventurestay_packages
DDB_BOOKINGS_TABLE_NAME=adventurestay_bookings
S3_BUCKET_NAME=adventurestay-images-xxxxxx
SNS_BOOKING_TOPIC_ARN=arn:aws:sns:us-east-1:xxxxxxx:adventurestay-booking-notifications
```

---

## 7. DynamoDB Package Seeding

### Seed all packages
```
USE_AWS=1 python infra/seed_packages.py
```

Requires:
- DDB table name  
- AWS_DEFAULT_REGION  
- USE_AWS=1  

---

## 8. Booking Flow Summary

1. User submits booking  
2. Django saves booking to local DB  
3. Saves to DynamoDB  
4. Sends SQS message  
5. Publishes SNS confirmation  
6. Email arrives to user  

---

## 9. Troubleshooting Checklist

### **Images not loading**
- Check `S3_BUCKET_NAME` is set  
- Check DynamoDB image_url  
- Check `resolve_image_url()` output  
- Use `USE_AWS=1`  

### **SNS not sending**
- Check `SNS_BOOKING_TOPIC_ARN`  
- Check AWS region  
- Check email subscription status  

### **Packages still old**
- Delete all items in DynamoDB  
- Reseed with `USE_AWS=1`  

---

## 10. Conclusion

This guide captures:
- Full deployment setup  
- DynamoDB image fix  
- SNS fix  
- Environment variables  
- Project structure  
- Root cause analysis  

Add this `.md` file to GitHub for future debugging and onboarding.
