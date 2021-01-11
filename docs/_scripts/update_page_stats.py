import os
import logging
import requests
import argparse
import pandas as pd
from bs4 import BeautifulSoup
from markdown import markdown as md2html


# Files to update stats
FILES = ["overview_stats.html", "../README.md"]
box_stats_url = "https://drive.google.com/u/1/uc?id=1Om1iwSnJrJ1o_U9UGouVXuzWhkHYVEXf&export=download"
img_stats_url = "https://drive.google.com/u/1/uc?id=1OtPr1xZR6Ntt_XOYHymzlh2_fedrqO5c&export=download"
seg_stats_url = "https://drive.google.com/u/1/uc?id=1GOaH3itz7FaNXsH0PGFqRmlCqdlqJ3bd&export=download"
seg_img_stats_url = "https://drive.google.com/u/1/uc?id=1nuZVEVeBw6F9pC7mhdw3mSnpm5POomgx&export=download"

temp_box_df = "temp_box_stats.df"
temp_img_df = "temp_img_stats.df"
temp_seg_df = "temp_seg_stats.df"
temp_seg_img_stats = "temp_seg_img_stats.df"


def update_stats_badges(md_paths: [str], stats: dict):
    """
        Updates shield.io image tags according to stats and saves the changed Markdown files.
        Matches the tags to be updated by their id attributes.
        The id is equivalent to the stats dictionary key, whose value is used for updating.
    """
    updated_soups = []
    for md_path in md_paths:
        with open(md_path) as fp:
            html = md2html(fp.read())
            bs_badges = BeautifulSoup(html, features="lxml")

        for tag in bs_badges.find_all("img"):
            tag_id = tag.get("id")
            if tag_id in stats.keys():
                if tag["id"] == "num_teams":
                    tag[
                        "src"
                    ] = f"https://img.shields.io/badge/Teams-{stats['num_teams']:,}-green.svg"
                    tag["alt"] = f"Teams: {stats['num_teams']}"
                elif tag["id"] == "num_bbox_images":
                    tag[
                        "src"
                    ] = f"https://img.shields.io/badge/Images-{stats['num_bbox_images']:,}-blue.svg"
                    tag["alt"] = f"Number of labeled images: {stats['num_bbox_images']}"
                elif tag["id"] == "num_bbox_cones":
                    tag[
                        "src"
                    ] = f"https://img.shields.io/badge/Cones-{stats['num_bbox_cones']:,}-blue.svg"
                    tag["alt"] = f"Number of labeled cones: {stats['num_bbox_cones']}"
        updated_soups.append(bs_badges)
    for stats_soup, md_path in zip(updated_soups, md_paths):
        logging.info(
            f"Overwriting with current stats the following markdown file: {md_path}"
        )
        with open(md_path, "w") as stats_md:
            # Gets the first p tag
            top_empty_paragraph = stats_soup.p
            top_empty_paragraph.decompose()
            stats_soup.find_all("p")[-1].decompose()

            stats_md.write(repr(stats_soup))


def update_span_stats_pages(html_paths: [str], stats: dict):
    """
        Updates _includes files that contain stats and saves the changed HTML files.
        Matches span tags with id attributes to the stats dict.
        Only updates if the id matches a key in the stats dict.
    """
    updated_soups = []
    for html_path in html_paths:
        with open(html_path) as fp:
            bs_overview = BeautifulSoup(fp, features="lxml")

        for tag in bs_overview.find_all("span"):
            tag_id = tag.get("id")
            if tag_id in stats.keys():
                if isinstance(stats[tag["id"]], float):
                    tag.string.replace_with(f"{stats[tag['id']]:6,.2f}")
                else:
                    tag.string.replace_with(f"{stats[tag['id']]:,}")
            elif tag_id:
                logging.info(
                    f"Found span tag with id and no matching stats dictionary entry for key: {tag['id']}."
                )
        updated_soups.append(bs_overview)
    for stats_soup, html_path in zip(updated_soups, html_paths):
        logging.info(
            f"Overwriting with current stats the following include file: {html_path}"
        )
        with open(html_path, "w") as stats_include:
            stats_include.write(repr(stats_soup))


def download_gdrive_df(df_url, fp):
    r = requests.get(df_url)
    open(fp, "wb").write(r.content)


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

    logging.basicConfig(level=logging.INFO)
    logging.info(f"Updating stats in the following files: {relative_paths}.")

    download_gdrive_df(box_stats_url, temp_box_df)
    download_gdrive_df(img_stats_url, temp_img_df)
    download_gdrive_df(seg_stats_url, temp_seg_df)
    download_gdrive_df(seg_img_stats_url, temp_seg_img_stats)

    box_stats_df = pd.read_pickle(temp_box_df)
    img_stats_df = pd.read_pickle(temp_img_df)
    seg_stats_df = pd.read_pickle(temp_seg_df)
    seg_img_stats_df = pd.read_pickle(temp_seg_img_stats)

    # The keys match the id's of the span tags to be filled
    stats = {
        "num_bbox_images": len(img_stats_df),
        "num_bbox_cones": len(box_stats_df),
        "num_seg_images": len(seg_img_stats_df),
        "num_seg_cones": len(seg_stats_df),
    }
    stats["avg_bbox_per_img"] = stats["num_bbox_cones"] / stats["num_bbox_images"]
    stats["avg_seg_per_img"] = stats["num_seg_cones"] / stats["num_seg_images"]
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

    os.remove(temp_box_df)
    os.remove(temp_img_df)
    os.remove(temp_seg_df)
    os.remove(temp_seg_img_stats)


if __name__ == "__main__":
    main()
