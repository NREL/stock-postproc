"""
This standalone script creates (and updates) AWS and MinIO credentials and storage blocks for Prefect workflows.
It also configures a Docker worker pool with default settings for container runs.

The blocks created include:
- AWS credentials for ResBuilding and anonymous access
- S3 bucket blocks for com-sdr, res-sdr and oedi-data-lake
- MinIO credentials and bucket blocks for local storage
- Docker pool configuration with env vars, networking and volume mounts
"""

import os

import anyio
from dotenv import load_dotenv
from prefect.client.orchestration import get_client
from prefect.client.schemas.actions import WorkPoolUpdate
from prefect.exceptions import ObjectNotFound
from prefect_aws import AwsClientParameters, AwsCredentials, MinIOCredentials, S3Bucket
from pydantic import SecretStr

load_dotenv()

buckets = ["com-sdr", "res-sdr", "resstock-core"]


async def configure_prefect():
    # Create AWS credentials
    print("Creating AWS credentials")

    aws_credentials_block = AwsCredentials(
        aws_access_key_id=os.getenv("AWS_RESBLDG_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_RESBLDG_SECRET_KEY"),
        # aws_session_token=os.getenv("AWS_RESBLDG_SESSION_TOKEN"),
        region_name=os.getenv("AWS_RESBLDG_REGION"),
    )
    await aws_credentials_block.save("aws-resbldg", overwrite=True)

    anonymous_credentials_block = AwsCredentials(
        aws_client_parameters=AwsClientParameters(
            config={
                "signature_version": "unsigned",
            },
        ),
    )
    await anonymous_credentials_block.save("aws-anonymous", overwrite=True)

    # Create AWS buckets
    print("Creating AWS buckets")

    for bucket in buckets:
        await S3Bucket(
            bucket_name=bucket,
            credentials=aws_credentials_block,
        ).save(f"aws-{bucket}", overwrite=True)

    await S3Bucket(
        bucket_name="oedi-data-lake",
        credentials=anonymous_credentials_block,
    ).save("aws-oedi-data-lake", overwrite=True)

    # Create MinIO credentials
    print("Creating MinIO credentials")

    minio_credentials_block = MinIOCredentials(
        minio_root_user=os.getenv("MINIO_ACCESS_KEY"),
        minio_root_password=SecretStr(os.getenv("MINIO_SECRET_KEY")),
        aws_client_parameters=AwsClientParameters(
            endpoint_url=os.getenv("MINIO_ENDPOINT"),
            use_ssl=False,
        ),
    )
    await minio_credentials_block.save("minio", overwrite=True)

    # Create MinIO buckets
    print("Creating MinIO buckets")

    for bucket in ["oedi-data-lake", "plot-results", *buckets]:
        await S3Bucket(
            bucket_name=bucket,
            credentials=minio_credentials_block,
        ).save(f"minio-{bucket}", overwrite=True)

    # Advanced worker pool configuration (this assumes the pool was created when the docker worker started up)
    pool_name = "docker-pool"

    print("Configuring Docker pool")

    async with get_client() as client:
        # Concurrency limits
        await client.create_concurrency_limit(tag="download", concurrency_limit=4)

        try:
            pool = await client.read_work_pool(pool_name)
        except ObjectNotFound as error:
            print("docker-pool doesn't exist yet, has the docker worker started?")
            raise error

        defaults = {
            "auto_remove": True,
            "env": {
                "PIP_ROOT_USER_ACTION": "ignore",
                "PLOTS_ROOT_FOLDER": "/share",
                "PREFECT_API_URL": "http://prefect:4200/api",
                "TZ": "America/Denver",
            },
            "networks": ["prefect_default"],
            # "volumes": ["/share/appdata/prefect/share:/share"],
            "volumes": ["/home/aswindle/docker/prefect/share:/share"],
        }
        template = pool.base_job_template
        # Set defaults for all docker runs
        for key, value in defaults.items():
            template["variables"]["properties"][key]["default"] = value

        await client.update_work_pool(
            pool_name,
            work_pool=WorkPoolUpdate(base_job_template=template),
        )


if __name__ == "__main__":
    anyio.run(configure_prefect)
