# -*- coding: utf-8 -*-

from setuptools import find_packages
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="fsoco tools",
    version="0.0.1",
    author=u"David Dodel, Michael Schötz, Niclas Vödisch + further contributors if importing from original FSOCO",
    author_email="fsoco.dataset@gmail.com",
    description="Tools and scripts for everything revolving around the FSOCO dataset. For more details and listings,"
    " please refer to the further documentation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.fsoco-dataset.com/tools/",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "opencv-python",
        "tqdm",
        "pillow>=6.2.1",
        "click>=7.0.0",
        "pyyaml>=5.0.0",
        "numpy",
        "scipy",
        "sklearn",
        "torch>=1.4.0",
        "img2vec_pytorch",
        "pandas",
        "matplotlib",
        "screeninfo",
        "networkx",
        "requests",
        "pascal_voc_writer",
        "imgaug",
        "sk-video",
    ],
    extras_require={
        "sly": [
            "supervisely[apps]",
        ]
    },
    entry_points="""
        [console_scripts]
        fsoco=click_fsoco:fsoco
    """,
)
