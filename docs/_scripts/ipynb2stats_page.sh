#!/usr/bin/env bash
set -e
which jupyter >/dev/null || (echo "Couldn't find jupyter." && echo "Please make sure you've activated the correct virtual environment." && exit 1)

if [[ ! "$1" || "$1" == "-h" || "$1" == "--help" ]]; then
    echo "Please input a valid path to a Jupyter Notebook to convert and thereafter update the stats pages."
    echo ""
    echo "Usage: bash ipynb2stats_page.sh IPYNB_FILE [PYTHON_HTML_PREP_SCRIPT_PATH] [STATS4NERDS_INCLUDE_PATH]"
    echo ""
    echo "If no path is given for the python prep script or stats4nerds_include, this script assumes you are in the fsoco-dataset/docs/assets directory."
    exit 1
fi

prep_script=../_scripts/prepare_slides_html.py
update_pages_script=../_scripts/update_page_stats.py

if [[ "$2" ]]; then
    python_prep_script=$2
fi

stats_for_nerds_html=stats_for_nerds_bokeh.slides.html

stats_for_nerds_include_path=../_includes/stats_for_nerds_bokeh.slides.html
if [[ "$3" ]]; then
    stats_for_nerds_include_path=$3
fi

echo "Executing and converting stats notebook to HTML."
jupyter nbconvert --execute --to slides \
  --TemplateExporter.exclude_input=True \
  --TagRemovePreprocessor.enabled=True \
  --TagRemovePreprocessor.remove_all_outputs_tags="{'hide_output'}" \
  --output hidden_input-analyse_stats \
  --stdout $1 > $stats_for_nerds_html && echo "Successfully executed and updated stats notebook " $1 || (echo "Something went wrong while executing the stats notebook " $1 && exit 1)

echo "Trimming output notebook HTML file."
# sed -i 's/Reveal\.initialize({/Reveal.initialize({width: "100%", height: "100%", margin: 0, minScale: 1, maxScale: 1,/' $stats_for_nerds_html
sed -i 's/Reveal\.initialize({/Reveal.initialize({width: 900, height: 900, margin: 0, minScale: 0.2, maxScale: 2.0,/' $stats_for_nerds_html

python $prep_script -f $stats_for_nerds_html -o $stats_for_nerds_html
python $update_pages_script

mv $stats_for_nerds_html $stats_for_nerds_include_path && echo "Successfully updated Stats page at " $stats_for_nerds_include_path || (echo "Something went wrong while updating the Stats page at " $stats_for_nerds_include_path && exit 1)

