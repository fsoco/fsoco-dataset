import sys

from requests.exceptions import HTTPError
from difflib import SequenceMatcher

from similarity_scorer.utils.logger import Logger


def safe_request(request, *args, **kwargs):
    try:
        return request(*args, **kwargs)
    except HTTPError as e:
        Logger.log_error(e.__str__())
        sys.exit(-1)
    Logger.log_error("An unknown exception occurred.")
    sys.exit(-1)


def extract_geometry_type_from_job_name(job_name: str):
    rectangle_name = "Bounding Boxes".lower()
    bitmap_name = "Segmentation".lower()
    job_name = job_name.lower()

    if rectangle_name in job_name:
        return "rectangle"
    if bitmap_name in job_name:
        return "bitmap"

    rectangle_longest_match_size = max(
        [
            match.size
            for match in SequenceMatcher(
                None, rectangle_name, job_name
            ).get_matching_blocks()
        ]
    )
    bitmap_longest_match_size = max(
        [
            match.size
            for match in SequenceMatcher(
                None, bitmap_name, job_name
            ).get_matching_blocks()
        ]
    )
    if (
        rectangle_longest_match_size > bitmap_longest_match_size
        and rectangle_longest_match_size >= 5
    ):
        return "rectangle"
    if (
        bitmap_longest_match_size > rectangle_longest_match_size
        and bitmap_longest_match_size >= 5
    ):
        return "bitmap"

    Logger.log_warn(f"Cannot determine geometry type from job name: {job_name}")
    return ""
