from collections import defaultdict

import pandas as pd

from .metrics.cosine_metric import CosineMetric
from .metrics.metric import Metric
from .utils.feature_extractor import FeatureExtractor
from .utils.logger import Logger
from .utils.similarity_viewer import SimilarityViewer
from .utils.similarity_clustering import SimilarityClustering

# pandas
pd.set_option("display.max_rows", 500)
pd.set_option("display.max_columns", 500)
pd.set_option("display.width", 1000)

# Metrics
GLOBAL_SCORE_METRIC = "global_Cosine_0.95"
LOCAL_SCORE_METRIC = "folder_Cosine_0.95"


class SimilarityScorer:
    def __init__(
        self,
        image_glob: str,
        clustering_threshold: float = 0.0,
        num_workers: int = 2,
        gpu: bool = True,
        report_csv: str = None,
        debug: bool = False,
        show: int = 0,
    ):
        self.image_glob = image_glob
        self.report_csv = report_csv
        self.debug = debug

        self.metrics = []
        self.metric_results = {}
        self.df = None
        self.single_folder = False

        self.extractor = FeatureExtractor(num_workers=num_workers, gpu=gpu)
        self.similarity_viewer = SimilarityViewer(sample_percent=show)
        self.similarity_clustering = SimilarityClustering(
            clustering_threshold=clustering_threshold
        )

        # baseline metrics
        self.add_metric(CosineMetric(threshold=0.99, use_sum=False))
        self.add_metric(CosineMetric(threshold=0.98, use_sum=False))
        self.add_metric(CosineMetric(threshold=0.95, use_sum=False))

        self.global_prefix = "global_"
        self.per_folder_prefix = "folder_"

    def add_metric(self, metric: Metric):
        self.metrics.append(metric)

    def _calculate_metrics(self, feature_vectors):
        for metric in self.metrics:
            metric.load_feature_vectors(feature_vectors)
            self.metric_results[
                f"{self.global_prefix}{metric.name}"
            ] = metric.get_metric(per_folder=False)

            if metric.can_be_applied_per_folder():
                self.metric_results[
                    f"{self.per_folder_prefix}{metric.name}"
                ] = metric.get_metric(per_folder=True)

    def _prepare_results(self):
        combined = defaultdict(dict)
        for metric_name, results in self.metric_results.items():
            for file, value in results.items():
                if file not in combined:  # new key
                    folder = "./"
                    if len(file.parts) > 1:
                        folder = "/".join(file.parts[:-1])

                    combined[file]["folder"] = folder
                    combined[file]["file_name"] = file.name

                combined[file][metric_name] = value

        df = pd.DataFrame(combined.values())
        self.df = df
        self.single_folder = self.df["folder"].value_counts().size == 1

    def _print_results(self):
        pd.set_option("display.width", 100)
        pd.set_option("display.max_colwidth", 20)
        pd.set_option("float_format", "{:04.2f}".format)
        self.df["folder"] = self.df["folder"].str.slice(
            start=-20
        )  # workaround for displaying

        global_score = self.df[GLOBAL_SCORE_METRIC].mean()

        print(f"{Logger.Colors.OKBLUE}{Logger.Colors.BOLD}")
        print("[Lower is better]\n")
        print(
            f"Your{' ' if self.single_folder else ' global '}score is: {global_score:.2f}"
        )
        print(f"{Logger.Colors.ENDC} {Logger.Colors.OKBLUE}")
        print(
            f"This means that on average, your images have {global_score:.2f} images that have a cosine similarity "
            f"higher than 0.95."
        )
        print("Or put simply, they have a lot of image features in common.")
        print(
            "So you should take a look if these images add enough new training information."
        )
        print(
            "Please note, that the score is mainly based on the 'background' features, as it looks at the entire "
            "image."
        )
        print("To improve your score, you can try different background scenes.")
        print(
            "If your images are composed of similar-looking backgrounds but different cone position/lighting "
            "conditions, it is still ok to have a higher score."
        )
        print()

        if not self.single_folder:
            print()
            print("Score per folder:")
            print(self.df.groupby("folder")[LOCAL_SCORE_METRIC].mean())
            print()

        if self.debug:
            debug_info = self.df.groupby("folder").describe(
                percentiles=[0.25, 0.5, 0.75, 0.95]
            )

            Logger.log_info("Debug statistics:   [lower is better]")
            print(Logger.Colors.OKBLUE)
            print(debug_info)
            print(Logger.Colors.ENDC)

    def _save_report(self):
        if self.report_csv is not None:
            Logger.log_info(f"Saving results to {self.report_csv}")
            self.df.to_csv(self.report_csv)

    def run(self):
        # extract features
        feature_vectors = self.extractor.extract_feature_vectors_for_files(
            self.image_glob
        )

        self._calculate_metrics(feature_vectors)

        self._prepare_results()
        self._save_report()
        self._print_results()

        if self.similarity_clustering.active():
            Logger.log_info("Start similarity clustering.")
            self.similarity_clustering.load_images(feature_vectors)
            self.similarity_clustering.run()

        if self.similarity_viewer.active():
            self.similarity_viewer.load_images(feature_vectors)
            self.similarity_viewer.show_samples()

    def collect_stats(self):
        # extract features
        feature_vectors = self.extractor.extract_feature_vectors_for_files(
            self.image_glob
        )

        self._calculate_metrics(feature_vectors)
        self._prepare_results()

        return self.df


if __name__ == "__main__":
    print("Please use the fsoco command!")
