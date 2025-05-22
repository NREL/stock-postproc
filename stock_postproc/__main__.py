from typing import Any

from prefect import flow, task
from prefect.cache_policies import INPUTS, TASK_SOURCE
from prefect_aws.s3 import S3Bucket
from pydantic import BaseModel, Field

s3_com_sdr_bucket = S3Bucket.load("s3-com-sdr")
minio_com_sdr_bucket = S3Bucket.load("minio-com-sdr")


class Inputs(BaseModel):
    upgrade_id: int = Field(ge=0, le=57, title="Upgrade ID")


@task(cache_policy=TASK_SOURCE + INPUTS)
def list_parquet_files(upgrade: int) -> list[dict[str, Any]]:
    files = s3_com_sdr_bucket.list_objects(folder=f"euss_fy25/production_runs/2025_r2/full/sdr_2025_r2_1of5_30802/sdr_2025_r2_1of5_30802/timeseries/upgrade={upgrade}/")
    print(f"========== {len(files)} file{'' if len(files) == 1 else 's'} ==========")
    # print(json.dumps(files, indent=2, default=str))
    return files


@task
def cache_has_key(key: str) -> bool:
    result = minio_com_sdr_bucket.list_objects(folder=key)
    print(f"Cache key {'exists' if len(result) == 1 else 'does not exist'}: {key}")
    return len(result) == 1


@task
def download_and_cache_key(key: str) -> None:
    # TODO
    pass


@flow(name="Optimize Parquet Files", log_prints=True)
def optimize_parquet_files(time_series: Inputs) -> list[dict[str, Any]]:
    """
    Given an upgrade id, fetches the first 3 files and optimizes them

    Args:
        time_series: Upgrade id, between 0 and 57
    """
    files = list_parquet_files(time_series.upgrade_id)
    keys = [obj["Key"] for obj in files[:3]]
    cache_futures = cache_has_key.map(keys)
    missing_cache_files = [i for i, ok in zip(keys, cache_futures.result()) if not ok]
    print("missing_cache_files", missing_cache_files)
    # download_and_cache_key.map(missing_cache_files)
    return files


if __name__ == "__main__":
    optimize_parquet_files(Inputs(upgrade_id=0))
