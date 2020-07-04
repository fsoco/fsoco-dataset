---
layout: page
title: Examples
permalink: /examples/
feature-img: assets/img/fsg/HD/fsg_yellow_cones.jpg
feature-img-credits: Photo ©FSG Klein
order: 2
---

## Examples
{:.no_toc}

To solve the task of cone detection, we provide manually annotated bounding boxes and segmentation masks.
Both annotation types consist of the same semantic classes and additional tags (see [overview]({{ "/overview/" | relative_url }})).
A small sample dataset can be downloaded at the bottom of this page helping you to understand our data structure.

* TOC
{:toc}
---

### Bounding Boxes

Below are examples of our bounding box labels.
Each color represents a different cone type.

{% include aligner.html images="examples/bounding_box_3.png,examples/bounding_box_4.png" column=2 %}
{% include aligner.html images="examples/bounding_box_1.png,examples/bounding_box_2.png" column=2 %}

### Segmentation

We further provide pixel-based semantic masks for a smaller subset of our images.
Note that each cone is labeled individually and, thus, allows for both class and instance segmentation.
In the case of overlapping cones, the mask of the partially covered cone might consist of multiple patches belonging to the same label.  

{% include aligner.html images="examples/segmentation_1.png,examples/segmentation_2.png" column=2 %}
{% include aligner.html images="examples/segmentation_3.png,examples/segmentation_4.png" column=2 %}

### Example Data

A sample dataset of FSOCO comprising 10 images can be downloaded [here](https://drive.google.com/file/d/1l2k7q0KG7ejqquepgJBMeJkwueVutf5t/view?usp=sharing "Opens in a new tab."){:target="_blank"}.
Note that we provide the same annotation files as if directly downloaded from Supervisely without further post-processing.
The folder structure is as shown below.

```
fsoco/
 ├── meta.json
 ├── images/
 │   ├── fsoco_0.jpg
 │   ├── fsoco_1.png
 │   └── ...
 ├── bounding_boxes/
 │   ├── fsoco_0.jpg.json
 │   ├── fsoco_1.png.json
 │   └── ...
 └── segmentation/
     ├── fsoco_0.jpg.json
     ├── fsoco_1.png.json
     └── ...
```