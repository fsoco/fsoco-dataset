import logging
import argparse
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument(
    "-f",
    "--html_file",
    type=str,
    action="store",
    required=True,
    help="Path to the html file you want to use.",
)
parser.add_argument(
    "-o",
    "--output_file",
    default="stats_for_nerds_bokeh.slides.html",
    type=str,
    action="store",
    required=True,
    help="Path to the output file descriptor.",
)

args = parser.parse_args()

logging.info(f"Preparing slides notebook html file: {args.html_file}.")

with open(args.html_file) as fp:
    nb_html = BeautifulSoup(fp, features="lxml")

prepped_html = repr(nb_html.body)

with open(args.output_file, "w") as slides_file:
    slides_file.write(prepped_html)
