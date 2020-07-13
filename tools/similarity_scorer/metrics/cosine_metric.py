import time

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .metric import Metric
from ..utils.logger import Logger


class CosineMetric(Metric):
    def __init__(self, threshold: float = 0.95, use_sum: bool = False):
        Metric.__init__(self)
        self.threshold = threshold
        self.use_sum = use_sum

        if use_sum:
            self.name = f"Cosine_{threshold:.2f}_Cum"
        else:
            self.name = f"Cosine_{threshold:.2f}"

    def get_metric(self, per_folder: bool = True):
        metric = {}
        start_time = time.time()
        if per_folder:
            Logger.log_info(
                "Start cosine similarity calculation per folder ...", ctx=self.name
            )
            for _, index in self.get_index_per_folder():
                new_index, img_vecs = self.get_feature_vectors_for_index(index)
                similarity_matrix = self._calculate_similarity(img_vecs)
                metric_value = self._get_similarity_metric_value(similarity_matrix)
                metric.update({key: metric_value[i] for key, i in new_index.items()})

        else:
            Logger.log_info(
                "Start cosine similarity calculation for all images ...", ctx=self.name
            )
            all_images_index = self.get_index_for_all_images()
            new_index, img_vecs = self.get_feature_vectors_for_index(all_images_index)

            similarity_matrix = self._calculate_similarity(img_vecs)
            metric_value = self._get_similarity_metric_value(similarity_matrix)

            metric.update({key: metric_value[i] for key, i in new_index.items()})

        time_elapsed = time.time() - start_time
        Logger.log_info(
            f"Calculated {'per folder' if per_folder else 'global'} cosine similarity in {time_elapsed:.2f}s",
            ctx=self.name,
        )

        return metric

    @staticmethod
    def _calculate_similarity(img_vec):
        similarity_matrix = cosine_similarity(img_vec)
        return similarity_matrix.astype(np.float32)

    def _get_similarity_metric_value(self, similarity_matrix):
        num_images = similarity_matrix.shape[0]

        # set self similarity to 0
        similarity_matrix = similarity_matrix - np.identity(num_images)

        if self.use_sum:
            similarity_matrix[similarity_matrix < self.threshold] = 0.0
            counter = similarity_matrix.sum(axis=0)
        else:
            counter = (similarity_matrix > self.threshold).sum(axis=0)

        return counter
