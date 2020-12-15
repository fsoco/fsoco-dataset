---
layout: page
title: Tools
permalink: /tools/
feature-img: assets/img/fsg/HD/fsg_res.jpg
feature-img-credits: Photo ©FSG Haertl
order: 3
---

## Tools
{:.no_toc}

The FSOCO Tools [CLI](https://en.wikipedia.org/wiki/Command-line_interface "Opens in a new tab."){:target="_blank"} facilitates preparing your dataset to contribute to the project.
It is a small, extensible tool for data manipulation and analysis that is based on [Click](https://click.palletsprojects.com/en/7.x/ "Opens in a new tab."){:target="_blank"} to sensibly combine scripts into a uniform package.
For installation, please refer to the [README](https://github.com/fsoco/fsoco-dataset/blob/master/tools/README.md).

We welcome contributions and would be thrilled to review and, hopefully, accept your contribution as well.
If you are interested, please refer to [CONTRIBUTING](https://github.com/fsoco/fsoco-dataset/blob/master/CONTRIBUTING.md).
<br/>
A good way to find inspiration is by looking for "Help Wanted" Issues.

* TOC
{:toc}
---

### In-house Tools

#### Image Similarity Score
This tool will check your dataset for similarly looking images.
Its purpose is to assure that all contributions are actually expanding the dataset, helping to achieve algorithms with greater generalization potential.
Please find detailed information and instructions how to use our image similarity scorer on [this page](./image_similarity_score).


####  Label Viewer
The FSOCO label viewer is an easy way to visualize our dataset. Currently, it supports bounding boxes in both Supervisely and Darknet YOLO format and segmentation labels from Supervisely.

Example usage:
```bash
# Activate python venv where tools are installed
conda activate fsoco-tools 
fsoco viewers supervisely input_directory/
```

#### Team Logo Watermark
This tool allows you to test how your watermarked images will look like when using the Supervisely import plugin for image donations. Please refer to the tool's help for usage details.

Example usage:
```bash
# Activate python venv where tools are installed
conda activate fsoco-tools 
fsoco watermark input_directory/ jpg logo.png
```
This will generate watermarked images based on the matched contents of `input_directory/` with a `watermarked_` prefix.

##### Watermark Details
{:.no_toc}

The generated watermark will consist of your team's logo and a timestamp. Borders of `140px` on each edge will be added to the image.
The logo will be resized to a height of `100px`, while keeping the aspect ratio unchanged. To guarantee a crisp version of your logo and avoid unexpected distortions, use a version of your logo that fits these constraints.
Furthermore, the background on which the logo will be placed is black. To guarantee a good result, use a version of your logo with a black background. 
Transparency is not guaranteed to work.

##### Example Watermarked Images
{:.no_toc}

{% include aligner.html images="tools/watermarked_mms.jpg,tools/watermarked_amz.png,tools/watermarked_ff.jpeg" column=3 %}
<br>

#### Label Converters
The converter tools enable you to quickly convert your dataset of bounding boxes to comply with the submission format.
The currently available conversions are:

| Label Formats| Darknet YOLO | Supervisely | LabelBox | COCO | VOC | MM | NAS |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Darknet YOLO | - | <span style='font-size:20px;'>&#9989;</span> | - | - | - | - | - | 
| Supervisely | <span style='font-size:20px;'>&#9989;</span> | - | - | - | <span style='font-size:20px;'>&#9989;</span> | - | - |
| LabelBox | - | <span style='font-size:20px;'>&#9989;</span> | - | - | - | - | - | 
| COCO | <span style='font-size:20px;'>&#9989;</span><sup><small> [1]</small></sup> | - | - | - | - | - | - |
| VOC | <span style='font-size:20px;'>&#9989;</span><sup><small> [1]</small></sup> | - | - | - | - | - | - |
| MM | <span style='font-size:20px;'>&#9989;</span><sup><small> [1]</small></sup> | - | - | - | - | - | - |
| NAS | <span style='font-size:20px;'>&#9989;</span><sup><small> [1]</small></sup> | - | - | - | - | - | - |

[1] [These scripts](https://github.com/ddavid/fsoco/tree/master/scripts/label-converters) and a [summary of their label formats](https://ddavid.github.io/fsoco/#annotation-types) can be found on the [documentation page](https://ddavid.github.io/fsoco/) of the **deprecated** first version of the project. <br/>

Example usage:
```bash
# Activate python venv where tools are installed
conda activate fsoco-tools
fsoco label-converter yolo2sly -p project_name -d dataset_name img/ darknet_labels/ .
```

The `project_name` and `dataset_name` parameters will set the names of the created directory structure.
For uploading the created directories with converted labels and original images to Supervisely, please use the `project_name` root directory to ensure the correct metadata file `meta.json` is used.
More information is available in the documentation of the Supervisely FSOCO import plugins below.

### 3rd Party Tools
#### [Supervisely](https://supervise.ly/)
From Supervisely's [documentation page:](https://docs.supervise.ly)
> Supervisely is a powerful platform for computer vision development, where individual researchers and large teams can annotate and experiment with datasets and neural networks.
>
> Our mission is to help people with and without machine learning expertise to create state-of-the-art computer vision applications.

##### [Plugins](https://docs.supervise.ly/customization/plugins#what-is-a-plugin)
{:.no_toc}
> A Plugin is a set of docker images that can be executed on the node using the agent from the web interface.

Writing a plugin allows you to run any program you would like with data either being imported or already accessible through your Supervisely account, neatly encapsulated in a Docker container.
For the purposes of FSOCO, there are two relevant plugins that we provide you with.

* <a alt="FSOCO Image Import" href="https://app.supervise.ly/explore/plugins/fsoco-image-import-75571/overview" target="_blank">FSOCO Image Import</a>: Import for raw images that does the watermarking for you, provided a valid logo image.
* <a alt="FSOCO Supervisely Import" href="https://app.supervise.ly/explore/plugins/fsoco-supervisely-import-75595/overview" target="_blank">FSOCO Supervisely Import</a>: Import projects in the Supervisely format and have the contained images watermarked and labels adjusted accordingly.

Both plugins are documented to allow for a seamless experience when adjusting your data to fit the required format. 
If you are interested in writing your own plugin, please refer to [Supervisely's documentation on custom plugins](https://github.com/supervisely/supervisely/blob/master/help/tutorials/01_create_new_plugin/how_to_create_plugin.md).