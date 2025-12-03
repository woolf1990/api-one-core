import os
from app.core.config import settings
try:
    import boto3
    _has_boto = True
except Exception:
    _has_boto = False

def upload_bytes_to_s3(bytes_data: bytes, key: str) -> str:
    # If AWS credentials are set, use S3; otherwise, save to local storage folder
    if settings.AWS_S3_BUCKET and settings.AWS_ACCESS_KEY_ID and _has_boto:
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        s3.put_object(Bucket=settings.AWS_S3_BUCKET, Key=key, Body=bytes_data)
        return f"s3://{settings.AWS_S3_BUCKET}/{key}"
    else:
        # local storage
        storage_dir = os.path.join(os.getcwd(), "storage")
        os.makedirs(storage_dir, exist_ok=True)
        path = os.path.join(storage_dir, key.replace('/', '_'))
        with open(path, 'wb') as f:
            f.write(bytes_data)
        return f"file://{path}"
