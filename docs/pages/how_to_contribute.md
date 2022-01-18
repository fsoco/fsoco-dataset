---
layout: page
title: How to contribute?
permalink: /how_to_contribute/
feature-img: assets/img/fsg/HD/fsg_cones_in_jail.jpg
feature-img-credits: Photo ©FSG Schulz
order: 5
---

## How to contribute?
{:.no_toc}

*"Sharing is caring."*

In order to continuously increase the size of the FSOCO dataset, we only grant access to our data once your team submitted their contribution.
Please note, that you will only get access to those types of annotations you included in your submission, e.g., teams submitting bounding box labels will only get access to our existing bounding boxes.
To access our segmentation data, a separate contribution is required.
A detailed step-by-step description of the process is given below the terms and conditions.

You just started with Formula Student Driverless and do not have your own images yet?
Don't worry, we've got you covered!
We will provide you with raw images that your team can label to get access to FSOCO.

If you have more high quality images than you can annotate within your team, consider to donate them to FSOCO.
We will assign those images to teams without raw data.

* TOC
{:toc}
---

### Terms and Conditions

#### Contribution policy

> Before you upload your data please make sure your team has full ownership of this data. In particular, all images need to be recorded on your own car or be taken by your team. Examples of violations of this policy are images from the FSG media server or screenshots of YouTube videos of other teams.
>
> By uploading your data, you confirm that it complies with the rules on this site and that you allow other FSOCO contributors to use your data for academic and competition-oriented work related to Formula Student Driverless.

#### Contribution requirements

We have defined a set of minimum requirements for submitting to FSOCO.
They are based on the experience with the first version of FSOCO.

* Your team's **bounding box** contribution should:  
  1. Contain at least 2,500 official cones, e.g., 250 images with 10 cones/image (approx. labeling effort of 15h for one person). *Please let us know if the time is entirely off for you.*  
  2. Consist of approx. 50% images showing on-board data of rules-compliant tracks (acceleration, skidpad, autocross).  
  3. Not contain images, where one can identify people and license plates without their (owners) explicit permission.  
  4. Comply with the contribution policy above.
<br>
* Your team's **segmentation** contribution should:  
  1. Contain at least 1,000 official cones, i.e., 200 images with 5 cones/image (approx. labeling effort of 14h for one person).  
  2. Consist of approx. 50% images showing on-board data of rules-compliant tracks (acceleration, skidpad, autocross, trackdrive).  
  3. Not contain images, where one can identify people and license plates without their (owners) explicit permission.  
  4. Comply with the contribution policy above.   

> **Note**
> <br>
> If you are interested in testing [panoptic segmentation](https://medium.com/@danielmechea/what-is-panoptic-segmentation-and-why-you-should-care-7f6c953d2a6a "Opens in a new tab."){:target="_blank"} for your autonomous pipeline but do not want to commit to a full scale submission yet, please contact us for other options.

> **Tips and Tricks**
> <br>
> We recommend to pre-label your images with your cone detector since then your goal becomes to beat the AI, making you make more aware of mistakes done by the detector.
> Do not forget to add the object tags.
> If you do not have a cone detector yet, just start training as soon as you have a basic set and then continuously re-train it while extending your dataset.
> <br>
> For segmentation labels, Supervisely's smart labeling tool works very well for nearby cones.
> For cones that are farther away, it is typically faster to first draw the boundary and then fill it.

### Step-by-step Manual

<!-- Comment via script because of unfortunate Mermaid syntax -->
<script>
/*
For prototyping/theming: https://mermaid-js.github.io/mermaid-live-editor
<div class="mermaid">
%%{init: {"theme": "default", "themeVariables": { "primaryColor": "white", "nodeBorder": "black", "background": "#3884c7", "mainBkg": "#3884c7", "textColor": "#222222", "labelColor": "#ffffff" }}}%%

stateDiagram
  state fork_state <<fork>>
  state join_state <<join>>
    state "Team Ready" as s0: Waiting list = True
    state "Labeling Exam" as s1: 
    state "FSOCO Ready" as s2:
    state "Pre-label Adjustment" as s3: Label and tag all the Cones
    state "Review Implementation" as s4:
    state "FSOCO Review" as s5:
    state "FSOCO Done" as s6: Team added as contributor
    
    

    [*] --> s0: Labeling guidelines read
    s0 --> s1: Free slot
    s1 --> s2: Exam passed
    s2 --> fork_state
    fork_state --> s3: Donations dataset assigned
    s3 --> join_state: Finished labeling
    fork_state --> join_state: Uploaded own dataset
    join_state --> s5
    s5 --> s6: Review passed
    s5 --> s4: Issues found
    s4 --> s5: Issues fixed
    s6 --> [*]
</div>
*/
</script>

<img src="../assets/img/examples/contribution_process.svg" style="width: 60%;  height: auto; float:center;">

#### Preparation

1. Submit the form on our [contact us]({{ "/contact_us/" | relative_url }}) page. Information on the similarity score can be found [here]({{ "/tools/#image-similarity-score" | relative_url }}).
2. We will check your sample images. If you already have labels, please include them there.
3. You will get an email from us covering the next steps.
4. If you have not done yet, please create an account on [Supervisely](https://supervise.ly/ "Opens in a new tab."){:target="_blank"} and send us the username by replying to our email.
5. We will add this account to our FSOCO team and assign a labeling exam to you to ensure that you are familiar with our [labeling guidelines]({{ "/labels/#labeling_guidelines" | relative_url }}).


#### Upload your data

The following steps depend on whether your team already has raw images and existing labels.

**We have images and labels**
1. Please verify that your existing data comply with our terms and conditions above and our labeling guidelines.
2. You can use one of our provided [label converters]({{ "/tools/#label-converters" | relative_url }}). If you need to write your own tool, please consider making a PR to our tools suite.
3. Add the [FSOCO Supervisely Import]({{ "/tools/#plugins" | relative_url }}) plugin to your Supervisely team. You will also need to add one of your team's computers as an agent; just follow the instructions on Supervisely.
4. Upload your data to a private Supervisely team using our import plugin. Please ensure the following style:
* Clearly note the project of interest.
* The project should contain a single dataset named such everyone can clearly identify your team, e.g., the usual abbreviation, the team identifier at events, the name of your school, the city, ...
* The files in the dataset should be named like this *teamID_00001.png*. Use the same ID as in the name of the dataset and a 5 figures number. Combine both using an underscore.
5. Add our Supervisely account *fsocov2* as a developer to this team. We will copy your data and then remove us from the team.

**We have unlabeled images**
1. Please verify that your images comply with our terms and conditions above.
2. Upload your images to a private Supervisely team.
3. Organize a labeling party in your team. A great chance for team bonding and to teach everyone how your magic perception system works under the hood.
4. Once you are done, follow the instructions above for "We have images and labels".

**We do not have images**
1. We will assign a labeling job with raw data to your Supervisely account.  
2. If you would like to add more accounts to share the work within your team, please send us the usernames. We support a maximum number of 5 labelers; each of them has to pass the exam.

#### Access the dataset

1. Once we copied your contribution, we will inform you.
2. We host our data on Google Drive. In order to share the FSOCO dataset with you, please provide us with an email address of a Google account. By sharing the data only with specific Google accounts, we can ensure the integrity of FSOCO and can easily update the dataset.
3. If you ever lose access to this Google account, please contact us so that we can update your credentials.
4. We will add your team's logo to our contributors gallery.
5. Please note that a small portion of your data will not be added to the public dataset since we plan to publish a separate test set.
