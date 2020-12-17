import sys

from requests.exceptions import HTTPError

from similarity_scorer.utils.logger import Logger


def safe_request(request, *args, **kwargs):
    try:
        return request(*args, **kwargs)
    except HTTPError as e:
        Logger.log_error(e.__str__())
        sys.exit(-1)
    Logger.log_error("An unknown exception occurred.")
    sys.exit(-1)
