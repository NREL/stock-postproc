import urllib.parse

from prefect import flow, get_run_logger, task, unmapped
from prefect.futures import wait
from prefect.runtime import task_run
from prefect_aws.s3 import S3Bucket


def get_object_name(key: str) -> str:
    return key.rsplit("/", 1)[-1]


@task(
    name="Parse S3 URL",
    task_run_name="Parse S3 URL",
)
def parse_s3_url(s3_url: str) -> tuple[str, str]:
    """
    Parse an S3 URL of the form s3://bucket-name/path/to/object.txt
    and return (bucket, key).
    """
    parsed = urllib.parse.urlparse(s3_url)
    if parsed.scheme.lower() != "s3":
        raise ValueError(f"Invalid scheme in URL: {parsed.scheme!r}, expected 's3'")
    bucket = parsed.netloc
    key = parsed.path.lstrip("/")
    return bucket, key


def download_task_title() -> str:
    params = task_run.parameters
    name = get_object_name(params["key"])
    return f"Download {name}"


@task(
    name="Download",
    task_run_name=download_task_title,
    tags=["download"],
)
def download(
    key: str,
    bucket: str,
    aws_bucket: S3Bucket,
    minio_bucket: S3Bucket,
) -> None:
    """
    Stream object from AWS to MinIO
    """
    logger = get_run_logger()

    # Get boto3 S3 clients
    aws_client = aws_bucket._get_s3_client()
    minio_client = minio_bucket._get_s3_client()

    # Download from AWS
    resp = aws_client.get_object(Bucket=bucket, Key=key)
    body_stream = resp["Body"]

    # Stream directly into MinIO
    logger.info(f"Streaming {key!r} to MinIO bucket {minio_bucket.bucket_name!r}")
    minio_client.upload_fileobj(
        Fileobj=body_stream,
        Bucket=minio_bucket.bucket_name,
        Key=key,
    )
    logger.info(f"Synchronized {key!r} → MinIO")


@flow(name="Sync S3 to MinIO", log_prints=True)
def sync_s3_to_minio(s3_url: str, filename_filter: str | None = None):
    logger = get_run_logger()

    aws_bucket = S3Bucket.load("aws-oedi-data-lake")
    minio_bucket = S3Bucket.load("minio-oedi-data-lake")

    bucket, key = parse_s3_url(s3_url)
    files = aws_bucket.list_objects(key)
    if filename_filter:
        files = [f for f in files if filename_filter in get_object_name(f["Key"])]

    aws_objects = {o["Key"]: o["Size"] for o in files}

    if len(aws_objects) == 0:
        raise ValueError(f"No objects found in {s3_url!r}")

    minio_objects = {o["Key"]: o["Size"] for o in minio_bucket.list_objects(key)}

    missing_keys = [key for key, size in aws_objects.items() if aws_objects[key] != minio_objects.get(key)]
    logger.info(f"Downloading {len(missing_keys)} file{'s' if len(missing_keys) != 1 else ''}")

    downloads = download.map(missing_keys, unmapped(bucket), unmapped(aws_bucket), unmapped(minio_bucket))
    wait(downloads)


if __name__ == "__main__":
    # Example usage
    sync_s3_to_minio(
        "s3://oedi-data-lake/nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2024/resstock_amy2018_release_2/metadata_and_annual_results/national/parquet/",
        filename_filter="metadata_and_annual_results",
    )
