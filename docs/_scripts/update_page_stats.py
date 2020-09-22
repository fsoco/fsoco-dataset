import os
import logging
import requests
import argparse
import pandas as pd
from bs4 import BeautifulSoup

# Files to update stats
FILES = ["overview_stats.html", "dataset_stats_badges.html"]
box_stats_url = "https://drive.google.com/u/1/uc?id=1Om1iwSnJrJ1o_U9UGouVXuzWhkHYVEXf&export=download"


def update_stats_badges(html_paths: [str], stats: dict):
    """
    """
    updated_soups = []
    for html_path in html_paths:
        with open(html_path) as fp:
            bs_badges = BeautifulSoup(fp, features="lxml")

        for tag in bs_badges.find_all("img"):
            if tag["id"] == "num_teams":
                tag[
                    "src"
                ] = f"https://img.shields.io/badge/Teams-{stats['num_teams']:,}-green.svg"
                tag["alt"] = f"Teams: {stats['num_teams']}"
            elif tag["id"] == "num_bbox_images":
                tag[
                    "src"
                ] = f"https://img.shields.io/badge/Images-{stats['num_bbox_images']:,}-blue.svg"
                tag["alt"] = f"Amount of labeled images: {stats['num_bbox_images']}"
            elif tag["id"] == "num_bbox_cones":
                tag[
                    "src"
                ] = f"https://img.shields.io/badge/Cones-{stats['num_bbox_cones']:,}-blue.svg"
                tag["alt"] = f"Amount of labeled cones: {stats['num_bbox_cones']}"
        updated_soups.append(bs_badges)
    for stats_soup, html_path in zip(updated_soups, html_paths):
        logging.info(
            f"Overwriting with current stats the following include file: {html_path}"
        )
        with open(html_path, "w") as stats_include:
            stats_include.write(repr(stats_soup))


def update_span_stats_pages(html_paths: [str], stats: dict):
    """
    """
    updated_soups = []
    for html_path in html_paths:
        with open(html_path) as fp:
            bs_overview = BeautifulSoup(fp, features="lxml")

        for tag in bs_overview.find_all("span"):
            if tag.get("id"):
                if isinstance(stats[tag["id"]], float):
                    tag.string.replace_with(f"{stats[tag['id']]:6,.2f}")
                else:
                    tag.string.replace_with(f"{stats[tag['id']]:,}")
        updated_soups.append(bs_overview)
    for stats_soup, html_path in zip(updated_soups, html_paths):
        logging.info(
            f"Overwriting with current stats the following include file: {html_path}"
        )
        with open(html_path, "w") as stats_include:
            stats_include.write(repr(stats_soup))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--includes_directory",
        type=str,
        action="store",
        required=False,
        default="../_includes",
        help="Path to the _includes directory of the FSOCO documentation website.",
    )

    args = parser.parse_args()
    base_path = args.includes_directory
    relative_paths = [os.path.join(base_path, path) for path in FILES]
    # print(relative_paths)

    logging.basicConfig(level=logging.INFO)
    logging.info(f"Updating stats in the following _includes: {relative_paths}.")

    r = requests.get(box_stats_url)
    open("temp_box_stats.df", "wb").write(r.content)
    box_stats_df = pd.read_pickle("temp_box_stats.df")

    # The keys match the id's of the span tags to be filled
    stats = {}
    stats["num_bbox_images"] = len(pd.unique(box_stats_df["ann_file"]))
    stats["num_bbox_cones"] = len(box_stats_df)
    stats["avg_bbox_per_img"] = stats["num_bbox_cones"] / stats["num_bbox_images"]
    stats["num_teams"] = len(pd.unique(box_stats_df["team_name"]))
    stats["num_teams_data"] = len(
        pd.unique(
            box_stats_df["ann_file"].apply(
                lambda fp: os.path.basename(fp).split("_")[0]
            )
        )
    )

    update_stats_badges([relative_paths[1]], stats)
    update_span_stats_pages([relative_paths[0]], stats)


if __name__ == "__main__":
    main()
