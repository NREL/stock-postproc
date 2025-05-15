import random

from prefect import flow, task

# @flow(name="ResStock Publish Baseline Annual Results")
# def publish_baseline_annual_results(failed_bldgs: set[int], base: pl.LazyFrame) -> pl.LazyFrame:
#     col_maps = get_col_maps()
#     base = base.filter(~pl.col("building_id").is_in(failed_bldgs))
#     base = get_transformed_cols(base, col_maps)
#     base = base.with_columns(pl.lit(True).alias("applicability"))
#     base = base.with_columns([pl.lit(0).alias("upgrade"), pl.lit("Baseline").alias("upgrade_name")])
#     base = add_income_and_burden(base)
#     base = add_county_column(base)
#     base = add_puma_column(base)
#
#     all_cols = base.collect_schema().names()
#     print("Fixing site energy and site emission total for baseline ...")
#     base = fix_site_energy_total(base, all_cols)
#     base = fix_all_fuels_emissions(base, all_cols)
#     base = add_upgrade_columns(base)
#     base = reorder_columns(base, col_maps, is_baseline=True)
#     return base


# @flow(name="ResStock Publish Upgrade Annual Results")
# def publish_upgrade_annual_results(failed_bldgs: set[int], base: pl.LazyFrame, upgrade: pl.LazyFrame,
#                                    upgrade_num: int) -> pl.LazyFrame:
#     col_maps = get_col_maps()
#     upgrade = upgrade.filter((~pl.col("building_id").is_in(failed_bldgs)) &
#                              (pl.col("completed_status") == "Success"))
#
#     upgrade = get_transformed_cols(upgrade, col_maps)
#     upgrade = upgrade.with_columns([pl.lit(upgrade_num).alias("upgrade")])
#     base_cols = base.collect_schema().names()
#     upgrade_cols = upgrade.collect_schema().names()
#     missing_cols = list(set(base_cols) - set(upgrade_cols)) + ["bldg_id"]
#     upgrade = upgrade.join(base.select(missing_cols), on="bldg_id", how="left")
#     all_cols = upgrade.collect_schema().names()
#     print("Fixing site energy and site emission total for upgrade ...")
#     upgrade = fix_site_energy_total(upgrade, all_cols)
#     upgrade = fix_all_fuels_emissions(upgrade, all_cols)
#     upgrade = add_upgrade_columns(upgrade)
#     upgrade = upgrade.with_columns(pl.lit("True").alias("applicability"))
#     # get upgrade_name
#     upgrade_name_df = upgrade.select(pl.col("upgrade_name").first())
#     missing_bldgs_df = base.join(
#         upgrade,
#         on="bldg_id",
#         how="anti"  # Keep rows from 'base' with no match in 'upgrade'
#     )
#     missing_bldgs_df = missing_bldgs_df.with_columns([
#         pl.lit("False").alias("applicability"),
#         pl.lit(upgrade_num).alias("upgrade"),
#     ]).drop("upgrade_name")
#     upgrade_cols = upgrade.collect_schema().names()
#     missing_bldgs_df = missing_bldgs_df.join(upgrade_name_df, how="cross")
#     upgrade = pl.concat([upgrade, missing_bldgs_df], how="diagonal_relaxed")
#     upgrade = upgrade.sort("bldg_id")
#     upgrade = add_saving_cols(upgrade, base)
#     upgrade = reorder_columns(upgrade, col_maps, is_baseline=False)
#     return upgrade


@task
def get_building_ids() -> list[str]:
    # Fetch building IDs from remote source
    return [f"building{n}" for n in random.choices(range(100), k=10)]  # noqa: S311


@task
def process_building(building_id: str) -> str:
    # Process a building customer
    return f"Processed {building_id}"


@flow(name="ResStock")
def resstock_demo() -> list[str]:
    building_ids = get_building_ids()
    results = process_building.map(building_ids)
    return results


if __name__ == "__main__":
    # publish_baseline_annual_results()
    resstock_demo()
