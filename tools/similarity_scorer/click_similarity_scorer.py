import click
from pathlib import Path

from .similarity_scorer import SimilarityScorer
from .utils.logger import Logger


# TODO add selection threshold description


@click.command()
@click.argument("image_glob", type=str)
@click.argument("catch_wildcard_expansion", nargs=-1)
@click.option(
    "--clustering_threshold",
    help="Search for clusters that have high similarity and copy the images into the “Cluster” folder."
    "Specify the similarity threshold. 0.985 is a good starting value.",
    type=click.FloatRange(0.0, 1.0),
    default=0.0,
)
@click.option(
    "--auto",
    "--auto_select",
    help="Automatically selects the best images based on the clustering threshold.",
    is_flag=True,
    default=False,
)
@click.option(
    "--num_workers",
    default=4,
    help="Number of workers for extraction process, max number depends on GPU memory!",
    type=click.IntRange(1, 256),
)
@click.option("--gpu", is_flag=True, help="Use GPU for feature extraction")
@click.option("--report_csv", help="Saves report to the specified csv file", type=str)
@click.option("--debug", is_flag=True, help="Display advanced statistics")
@click.option(
    "--show",
    help="Show for a random percentage of the dataset the five most similar images.",
    type=click.IntRange(0, 100),
    default=0,
)
@click.option(
    "--cache_dir",
    default=".",
    help="Specify the folder to save cache files in. If not specified, the current directory will be used.",
    type=click.Path(),
)
def similarity_scorer(
    image_glob,
    catch_wildcard_expansion,
    clustering_threshold,
    auto,
    num_workers,
    gpu,
    report_csv,
    debug,
    show,
    cache_dir,
):
    """
    \b
    Dataset originality score
    \b
    This tool helps you to select the best images to be labeled from an extensive collection of raw data.
    A AlexNet feature vector is used to calculate the cosine similarity for your given input images.
    The clustering option helps you to identify similar looking images and may drop some of them, to improve your score.

    Usage:
    fsoco similarity-scorer '*/*.jpeg'

    \b
    Input:
    ── images_folder_a
       ├── img_x.jpeg
       ├── img_y.jpeg
       └── img_z.jpeg
    ── images_folder_b
       ├── img_r.jpeg
       ├── img_t.jpeg
       └── img_d.jpeg

    \b
    Output:
    ── images_folder_a
       ├── img_w.jpeg
       ├── img_x.jpeg
       ├── img_y.jpeg
       ├── img_z.jpeg
       └── Clusters
            ├── Cluster_0000
            │   ├── img_w.jpeg
            │   └── img_x.jpeg
            ├── Cluster_0001
            │   ├── img_y.jpeg
            │   └── img_z.jpeg
            └── _No_Cluster_
    ── images_folder_b
       ├── img_r.jpeg
       ├── img_t.jpeg
       ├── img_d.jpeg
       ├── img_f.jpeg
       ├── img_m.jpeg
       └── Clusters
            ├── Cluster_0000
            │   ├── img_t.jpeg
            │   ├── img_m.jpeg
            │   └── img_d.jpeg
            └── _No_Cluster_
                ├── img_r.jpeg
                └── img_f.jpeg

    """

    cache_dir = Path(cache_dir)
    if not cache_dir.exists():
        Logger.log_info(f"Create cache directory '{cache_dir}'.")
    cache_dir.mkdir(parents=True, exist_ok=True)

    # check for non quoted image glob
    if len(catch_wildcard_expansion):
        Logger.log_error(
            "It looks like you did not put your image glob into quotes and the shell already expanded it!"
        )
        Logger.log_error("Please put your Glob into quotation marks.")
        Logger.log_error("fsoco similarity-scorer '*/*.jpeg'")
        return False

    if auto and clustering_threshold == 0.0:
        Logger.log_error("Auto selection called without threshold!")
        Logger.log_error("Please specify like '--clustering_threshold 0.985'")
        return False

    Logger.log_info("Running image similarity scorer")

    # allows the glob to work when passed in double quotes
    image_glob = image_glob.replace('"', "")

    checker = SimilarityScorer(
        image_glob=image_glob,
        clustering_threshold=clustering_threshold,
        auto_select=auto,
        num_workers=num_workers,
        gpu=gpu,
        report_csv=report_csv,
        debug=debug,
        show=show,
        cache_dir=cache_dir,
    )
    checker.run()


if __name__ == "__main__":
    click.echo(
        "[LOG] This sub-module is not meant to be run as a stand-alone script. Please refer to\n $ fsoco --help"
    )
