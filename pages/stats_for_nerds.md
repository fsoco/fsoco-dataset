---
layout: page
title: "Stats for Nerds"
permalink: /stats_for_nerds
slides: true
hide: true
bootstrap: false
---
<style>
    div.slides{
        margin-top: 0 !important;
        top: 0;      
    }
    article{
        height: 90vh;
        bottom: 0;
        position: absolute;
    }
    h3{
        height: 5vh;
    }
    
    div.output_subarea {
        overflow: hidden;
    }
    div.prompt{
        display: none;
    }
   
@media (min-height: 300px) {
    .nerds {
        font-size: 70%;
    }

@media (min-height: 600px) {
    .nerds {
        font-size: 80%;
    }
    .rendered_html table{
        font-size: 12px;
    }
    img.fsocone {
        width: 20px;
    }
}
@media (min-height: 800px) {
    .nerds {
        font-size: 90%;
    }
    .rendered_html table{
        font-size: 12px;
    }
    img.fsocone {
        width: 30px;
    }
}
@media (min-height: 900px) {
    .nerds {
        font-size: 110%;
    }
    .rendered_html table{
        font-size: 24px;
    }
    img.fsocone {
        width: 40px;
    }
}
</style>
<div class="nerds" style="width: 100%; height: 70vh; overflow-x: auto; position: relative; bottom: 0;">
{% include stats_for_nerds_bokeh.slides.html %}
 </div>
