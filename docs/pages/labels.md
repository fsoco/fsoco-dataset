---
layout: page
title: Labels
permalink: /labels/
feature-img: assets/img/fsg/HD/fsg_cones.jpg
feature-img-credits: Photo ©FSG Klein
order: 3
---

Thanks for your interest in participating in FSOCO! Your contribution will **help other teams** to increase the size of their dataset for cone detection, segmentation and, at the same time, **it will help you** to improve your very own pipeline.  
Combining data from the entire FSD community is a huge challenge as both sensor setups and data quality differ across the teams. Thus, we have to settle on a few ground rules that every submission needs to comply with.

1.  Be consistent! Ensure that your labels adhere to the [guidelines](#labeling-guidelines) below.
2.  **Data is king.** Even the most sophisticated approach can only perform as well as the underlying data allows for.
3.  Images, where only half the cones are labeled, will confuse a human learner and a computer alike.
4.  [Cones](#classes) have to adhere to the official FSG rules. You can upload images with non-compliant cones but those annotations will not count towards your contribution.
5.  [Tags](#tags) allow to further analyze the FSOCO dataset
6.  To get started with the Supervisely annotation tool, check out this [overview page](https://docs.supervise.ly/labeling/editors/images "Opens in a new tab."){:target="_blank"}.

---
* TOC
{:toc}
---

### Classes
Classes are the same for bounding boxes and segmentation annotations.

|Class|Example|
|---|:---:|:---:|:---:|
|Blue|<img src="https://i.ibb.co/cb9xwV9/class-blue.png" width="150"/>|
|Yellow|<img src="https://i.ibb.co/q0S2XCp/class-yellow.png" width="150"/>|
|Small orange|<img src="https://i.ibb.co/M5fWNp0/class-small-orange.png" width="150"/>|
|Large orange|<img src="https://i.ibb.co/1zsCZTr/class-large-orange.png" width="150"/>|
|Other cone (not rules compliant)|<img src="https://i.ibb.co/rM5TMHc/class-other.gif" width="150"/>|

### Tags
Tags are the same for bounding boxes and segmentation annotations.

|Tag|Example|
| --- |:---:|:---:|
| Knocked over | <img src="https://i.ibb.co/HV4XC3v/tag-knocked-over.png" width="150"/> |
| Tape removed or event sticker | <img src="https://i.ibb.co/gDS7xj8/tag-tape-removed.png" width="150"/> <img src="https://i.ibb.co/NjJFRyd/tag-sticker.png" width="150"/> |
| Truncated | <img src="https://i.ibb.co/WnnGshy/tag-truncated.png" width="150"/> |

<a id="labeling_guidelines" style="text-decoration : none"></a>
### Labeling Guidelines

| Instruction                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |Annotation sample|
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---:|
| Pay attention to **pixel-level accuracy** of the bounding boxes. Please **include the entire base plate**.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | <img src="https://i.ibb.co/XJVVMvM/box-base-plate.png" width="200"/>
| Label cones with a segmentation mask that contains the entire cone but is as close to the boundary as possible.<br> **Tip:** Use your mouse wheel to zoom in and the right mouse button to move within the scene. Zooming in allows for you to be more precise with the bitmap brush, while zooming out makes it easier to see if the boundaries are set correctly.                                                                                                                                                                                                                                     | <img src="https://i.ibb.co/qnRZHLg/segmentation.png" width="200" /> |
| **Label all cones in the image that have a defined shape.** A good rule of thumb is to always include areas of more than 100 pixels^2.<br> To the right is an example of a small cone that should be labeled and a cone that is too small and should not be labeled. If your pipeline focuses on cones up to a certain range, you can easily remove very small cones, which are further away, using a simple size-based filter.<br> Segmentation: for such small objects it is advisable to directly use the brush to save time, as the Smart Labeling Tool likely will not work well.                  | <img src="https://i.ibb.co/y0zv3z8/box-shape-positive.png" width="200"/> <img src="https://i.ibb.co/DYF7CdX/segmentation-shape-positive.png" width="200"/> <img src="https://i.ibb.co/8mytTWJ/guidelines-shape-negative.png" width="200" /> |
| **Label overlapping cones** and tag the overlapped cone as *truncated*. Do not extend the bounding box but only include the visible part of a cone.<br> **Important:** Create **non-overlapping masks** for segmentation. With differing colors, the overlapping masks are easier to spot. If the involved cones are of the same color, zoom in and use a small brush. Overlapping pixels should be less transparent, so it is possible to spot them. We advise to label the cones first as different classes and then change the label afterwards.                                                     | <img src="https://i.ibb.co/GJy3FxW/box-overlapping.png" width="200"/> <img src="https://i.ibb.co/Sxd6bsk/segmentation-overlapping.png" width="200"/> |
| **Label cones that are cut off** on the side of an image if you, the human annotator, can clearly identify them.<br> For the same reasons as before, tag them as *truncated*. Pay attention when dealing with orange cones: when you can only see a single stripe, it might be ambiguous whether it is a small or a large cone.                                                                                                                                                                                                                                                                         | <img src="https://i.ibb.co/X4XLmbG/box-truncated.png" width="200"/> <img src="https://i.ibb.co/tsthQG8/segmentation-truncated.png" width="200"/> |
| **Label cones that are knocked over** and tag them as *knocked_over*.<br>Cones could be knocked-over on purpose, e.g., FSG uses them to separate the track from the preparation area, or because the car touched them in a previous lap. Either way, depending on your setup you might want to filter them out.                                                                                                                                                                                                                                                                                         | <img src="https://i.ibb.co/LRKkB6D/box-knocked-over.png" width="200"/> <img src="https://i.ibb.co/BK1nHbq/segmentation-knocked-over.png" width="200"/> |
| **Tag cones that have stickers**, e.g., FSG, or whose tape has been removed. Tag them as *sticker_band_removed*.<br>Make sure to only add this tag if you can read the sticker and not only because you know that this image has been taken at FSG. That is, tag the upper cone but do not tag the lower cone.                                                                                                                                                                                                                                                                                          | <img src="https://i.ibb.co/DVSCTt1/tag-sticker-do.png" width="200"/> <img src="https://i.ibb.co/wMhCBS4/tag-sticker-dont.png" width="200"/> |

### Tips & Tricks (Supervisely)

#### General

When dealing with truncated cones, it might be hard to recognize what exactly should be labeled when occluded by other bounding boxes or segmentation masks.
To better be able to label a single object, you can hide all objects that are not currently selected with CTRL+H.
This can be done by taking the following steps:
- Choose the selection tool _(hot key: `2`)_.
- Click on an object.
- Toggle the unselected objects' visibility _(hot key: `CTRL+H`)_.

![Easily adjust or label truncated cones.]({{ "assets/img/labels/2022-01-16_bbox-hide-others-ctrl-H.gif" | relative_url}})

#### Segmentation

Using Supervisely's polyfill tool greatly increases the labeling speed for segmentation masks. 
The steps to take are the following:
1. Start a new segmentation instance with the brush tool _(hot key: `9`)_.
2. Choose the polyfill tool.
3. Create the bounding polygon by left-clicking and, possibly, adjusting control points afterwards.
4. Confirm the polygon _(hot key: `BACKSPACE`)_.
5. Confirm the segmentation instance _(hot key: `BACKSPACE`)_.
  - Note that if you forget to perform both confirm steps above, you will end up with several cones within one object/mask.

![Polyfill video tutorial]({{ "assets/img/labels/2022-01-16_seg-polyfill.gif" | relative_url}})

When creating segmentation masks, a common mistake is to add several single instances in one Supervisely object.
To preempt this, you can quickly check if all instances are correctly separated by using the random instance color keyboard hot key: `SHIFT+H`.
Supervisely will then assign a random color to each instance, making it easy to recognize connected ones.
By pressing `SHIFT+H` again, the regular colors assigned to each class will be rendered again.

![Same class cones that are adjacent]({{ "assets/img/labels/2022-01-16_seg-rnd-colors-shift-H.gif" | relative_url}})

Note that you can use the "Cut tool" in the segmentation toolbox to easily create single instances if their masks are not overlapping.

![Disjunct instance masks but in the same object]({{ "assets/img/labels/2022-01-16_seg-find-cut-connected-instances.gif" | relative_url}})


### Well labeled images

#### Bounding Boxes

<img src="https://i.ibb.co/vQmvFMd/box-example-1.png" width="1000"/>

<img src="https://i.ibb.co/QYXrzN8/box-example-2.png" width="1000"/>

#### Segmentation

<img src="https://i.ibb.co/RPR21TJ/segmentation-example-1.png" width="1000"/>

<img src="https://i.ibb.co/mcF9qk0/segmentation-example-2.png" width="1000"/>
