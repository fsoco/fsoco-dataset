from pathlib import Path
import shutil
import networkx as nx
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

from .logger import Logger

# Clusters
CLUSTER_FOLDER_NAME = "clusters"


class SimilarityClustering:
    def __init__(self, clustering_threshold: float):
        self.clustering_threshold = clustering_threshold

        self.similarity_matrix = None
        self.image_name_for_index = None
        self.similarity_index = {}
        self.filenames_in_folder = defaultdict(list)
        self.ids_in_folder = defaultdict(list)

        self.clusters = []

    def active(self):
        return self.clustering_threshold > 0

    @staticmethod
    def _create_output_folders(folder: str):
        src_folder = Path(folder)
        review_folder = Path(f"{folder}/{CLUSTER_FOLDER_NAME}")

        shutil.rmtree(review_folder, ignore_errors=True)
        Path.mkdir(review_folder)

        return src_folder, review_folder

    def load_images(self, feature_vectors):
        vectors = np.zeros((len(feature_vectors), feature_vectors[0][1].shape[0]))
        for i, pair in enumerate(feature_vectors):
            file_name, feature_vector = pair
            vectors[i, :] = feature_vector
            self.similarity_index[str(file_name)] = i

            folder = file_name.parents[0]
            self.filenames_in_folder[folder].append(file_name)
            self.ids_in_folder[folder].append(i)

        self.similarity_matrix = cosine_similarity(vectors).astype(np.float32)
        self.image_name_for_index = {v: k for k, v in self.similarity_index.items()}

    def _find_clusters(self):
        high_similarity = self.similarity_matrix > self.clustering_threshold
        graph = nx.from_numpy_matrix(high_similarity, create_using=nx.Graph)
        self.clusters = [
            cluster for cluster in nx.connected_components(graph) if len(cluster) > 1
        ]
        self.clusters.sort(key=len)
        self.clusters.reverse()

    def _get_clusters_for_ids(self, ids_in_folder: set):
        clusters_in_folder = []

        for cluster in self.clusters:
            cluster_in_folder = cluster & ids_in_folder
            if len(cluster_in_folder) > 1:
                clusters_in_folder.append(cluster_in_folder)
                ids_in_folder = ids_in_folder - cluster_in_folder

        return clusters_in_folder, ids_in_folder

    def _get_filenames_for_ids(self, ids):
        for i in ids:
            yield self.image_name_for_index[i]

    def run(self):
        self._find_clusters()
        for folder, ids_in_folder in self.ids_in_folder.items():
            ids_in_folder = set(ids_in_folder)
            _, review_folder = self._create_output_folders(folder)
            clusters_in_folder, in_no_cluster = self._get_clusters_for_ids(
                ids_in_folder
            )

            cluster_ratio = (len(ids_in_folder) - len(in_no_cluster)) / len(
                ids_in_folder
            )
            Logger.log_info(
                f"{folder} -> {cluster_ratio * 100:.2f}% of the images are in dense clusters!"
            )

            for i, cluster in enumerate(clusters_in_folder):
                cluster_folder = Path(review_folder / f"cluster_{i:04d}")
                Path.mkdir(cluster_folder)

                for file in self._get_filenames_for_ids(cluster):
                    src = Path(file)
                    dst = cluster_folder / src.name
                    shutil.copy2(src, dst)

            no_cluster_folder = Path(review_folder / "_no_cluster_")
            Path.mkdir(no_cluster_folder)

            for file in self._get_filenames_for_ids(in_no_cluster):
                src = Path(file)
                dst = no_cluster_folder / src.name
                shutil.copy2(src, dst)
