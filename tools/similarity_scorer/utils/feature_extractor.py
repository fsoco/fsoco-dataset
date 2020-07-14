import multiprocessing as mp
import os
import sys
import time
import warnings
from glob import glob
from pathlib import Path
import hashlib

import torch
from PIL import Image
from img2vec_pytorch import Img2Vec
from tqdm import tqdm

from .logger import Logger
from .cache import Cache

# Img2Vec

IMG2VEV_MODEL = "alexnet"
IMG2VEV_OUTPUT_LAYER = 3
IMG2VEV_OUTPUT_SIZE = 4096

TORCH_CACHE = Path.home() / ".cache/torch/checkpoints"
PRETRAINED_MODEL_GLOB = "alexnet-owt-*"

# will be initialized in every pool process!
img2vec = None
use_gpu = False
process_local_cache = None
warnings.filterwarnings("ignore")  # for PyTorch warnings

# Multiprocessing

DEBUG_DISABLE_MULTIPROCESSING = False

# Cache
# If set to True, the feature vector is linked to
USE_CACHE = True
CACHE_FILE = ".feature_vectors.cache"
CACHE_MODULE_NAME = (
    f"Feature_Vectors_{IMG2VEV_MODEL}_{IMG2VEV_OUTPUT_SIZE}_{IMG2VEV_OUTPUT_LAYER}"
)


class FeatureExtractor:
    def __init__(self, num_workers: int = 2, gpu: bool = True):
        global use_gpu
        self.num_workers = num_workers

        use_gpu = gpu

        self.cache = None
        if USE_CACHE:
            self.cache = Cache()
            self._load_cache(Path(CACHE_FILE))

    def __del__(self):
        if USE_CACHE and self.cache is not None:
            file = Path(CACHE_FILE)
            self.cache.store_to_file(file)
            Logger.log_info(f"Saved cache to {file}")

    def _load_cache(self, cache_file: Path):
        if cache_file.exists():
            if self.cache.load_from_file(cache_file):
                Logger.log_info(f"Using cache file [{cache_file}].")
            else:
                Logger.log_error(f"Failed to load cache from {cache_file}!")

    @staticmethod
    def _pretrained_model_is_downloaded():
        return len(list(TORCH_CACHE.glob(PRETRAINED_MODEL_GLOB))) > 0

    @staticmethod
    def _pool_process_init():
        global img2vec, use_gpu, process_local_cache
        # somewhat inefficient as the model gets loaded to GPU as many times as there are processes!
        # but so far good enough

        process_id = (
            int(mp.current_process().name.split("-")[1])
            if not DEBUG_DISABLE_MULTIPROCESSING
            else 1
        )
        use_gpu = use_gpu and torch.cuda.is_available()

        cache_file = Path(CACHE_FILE)

        if USE_CACHE and cache_file.exists():
            process_local_cache = Cache(read_only=True)
            process_local_cache.load_from_file(cache_file)

        if process_id == 1:  # This code will be executed only by the first worker
            # print only once
            print("\r", end="")  # fix for progress bar
            Logger.log_info(
                f"Will use {'GPU' if use_gpu else 'CPU'} for feature extracting."
            )
        else:  # This code will be executed by all other workers
            # This code keeps the other processes from downloading the pretrained model if it is not already downloaded
            retires = 0
            while (
                not FeatureExtractor._pretrained_model_is_downloaded()
                and retires < 10000
            ):
                time.sleep(0.5)
                retires += 1

        img2vec = Img2Vec(
            cuda=use_gpu,
            model=IMG2VEV_MODEL,
            layer_output_size=IMG2VEV_OUTPUT_SIZE,
            layer=IMG2VEV_OUTPUT_LAYER,
        )

    def extract_feature_vectors_for_files(self, image_glob: str):
        Logger.log_info("Start extracting feature vectors ...")

        files = sorted([Path(f) for f in glob(image_glob)])
        files = [f for f in files if f.is_file()]

        if len(files) == 0:
            Logger.log_error(f"Found no files for glob {image_glob}!")
            exit(-1)
        else:
            Logger.log_info(f"Found {len(files)} files to check.")
            time.sleep(0.05)  # just display stuff

        start_time = time.time()

        with tqdm(total=len(files), desc="extracting feature vectors") as pbar:
            if DEBUG_DISABLE_MULTIPROCESSING:
                FeatureExtractor._pool_process_init()
                results = []
                for res in map(FeatureExtractor._extract_features_from_image, files):
                    results.append(res)
                    pbar.update(1)
            else:
                results = []
                with mp.Pool(
                    self.num_workers, initializer=FeatureExtractor._pool_process_init
                ) as pool:
                    for res in pool.imap_unordered(
                        FeatureExtractor._extract_features_from_image, files
                    ):
                        results.append(res)
                        pbar.update(1)

        duration = time.time() - start_time

        feature_vectors = []
        failed = []
        num_cached = 0

        for image_file, feature_vector, file_hash, cached in results:
            if feature_vector is not None:
                feature_vectors.append((image_file, feature_vector))
                # only master process can write to cache
                self.cache.add_cache_item(
                    module=CACHE_MODULE_NAME, key=file_hash, data=feature_vector
                )

                if cached:
                    num_cached += 1
            else:
                failed.append((image_file, feature_vector))

        Logger.log_info(
            f"Needed {duration:.4f}s to extract {len(feature_vectors)} feature vectors."
        )

        if USE_CACHE:
            chached_percent = (num_cached / len(feature_vectors)) * 100
            Logger.log_info(
                f"Retrieved {chached_percent:.2f}% of the feature vectors from cache."
            )

        if len(failed) > 0:
            Logger.log_warn(f"Failed to extract features with {len(failed)} images!")

        return feature_vectors

    @staticmethod
    def _extract_features_from_image(image_file: Path):
        global process_local_cache
        feature_vector = None
        file_hash = ""
        cached = False
        cache_item = None

        if image_file.exists():
            with open((str(image_file)), "rb") as f:
                file_hash = hashlib.md5(f.read()).hexdigest()

            if process_local_cache is not None:
                cache_item = process_local_cache.get_cache_item(
                    module=CACHE_MODULE_NAME, key=file_hash, default_value=None
                )
            if cache_item is None:
                try:
                    image = Image.open(str(image_file))

                    # convert RGBA and grayscale images to RGB images
                    if image.mode != "RGB":
                        image = image.convert("RGB")

                    # stupid workaround to keep Img2Vec from printing the shape of the result tensor
                    sys.stdout = open(os.devnull, "w")
                    feature_vector = img2vec.get_vec(image)
                    sys.stdout = sys.__stdout__

                except:  # noqa: E722
                    Logger.log_warn(f"Could not read {image_file}!")

            else:
                feature_vector = cache_item
                cached = True

        else:
            Logger.log_warn(f"Could not find {image_file}!")

        return image_file, feature_vector, file_hash, cached
