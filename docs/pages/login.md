---
layout: page
title: "Login"
permalink: /login
feature-img: assets/img/fsg/raw/fsg_inspection.jpg
feature-img-credits: Photo ©FSG Wintermantel
order: 7
---
<style>
    iframe{
        border-style: none;
        width: 100%;
        height: 700px;
    }
    button{
        background-color: #337AB7;
        color: white;
        padding: 3px 5px;
    }
</style>

### Manage my contribution

On this page, you can:<br>
1) get an estimate of your current position on our waiting list.<br>
2) check the current status of all labeling tasks assigned to your team.<br>
3) trigger a couple of automated tests on these jobs.<br>
4) show the download links of the FSOCO dataset *(access is granted after a successful contribution)*.

To identify, please enter the same email address that your team used to submit the contribution request.

<form id="my_form" target="_status_iframe">
    <label for="email"><b>Email:</b></label>
    <input id="email" type="email" name="email" required/>
    <br>
    <br>
    On waiting list: 
    <button type="submit" id="waiting_list" value="waiting_list">Show position</button>
    <br>
    In contribution process: 
    <button type="submit" id="task_overview" value="task_overview">Show task status</button>
    <button type="submit" id="sanity_checks" value="sanity_checks">Run checks</button>
    <br>
    Contributor: 
    <button type="submit" id="dataset_url" value="dataset_url">Show link to dataset</button>
</form>

> **Note**
> <br>
> This page uses JavaScript to handle your input. Please make sure to enable client-side usage.<br>
> Additionally, if you experience issues and receive a "Sorry, unable to open the file at present." Google Drive error, either log out of all your Google Accounts or open this page in incognito mode.

<h3 id="loading_text" style="display:none;">Loading...</h3>
<div id="blanko_container" style="display:none;">
    <iframe name="_checks_iframe" id="blanko_iframe" style="height: 400px"></iframe>
</div>
<div id="contrib_procedure_container" style="display:none;">
  <iframe name="_status_iframe" id="contribution_status_iframe"></iframe>
  <h3>Job Status Legend</h3>
  <table id="job_status_legend">
      <thead>
      <tr>
        <th>Status</th>
        <th>Description</th>
      </tr>
        <td><font color="orange">Pending</font></td>
        <td>The labeling job has been created but the annotator has not started it yet.</td>
      <tr>
        <td><font color="blue">In progress</font></td>
        <td>The labeling job is currently being annotated. Note that you need to submit a job for us to be able to review it.</td>
      </tr>
      <tr>
        <td><font color="red">To be reviewed</font></td>
        <td>The labeling job has been submitted for review. We will allocate time to review it as soon as possible.</td>
      </tr>
      <tr>
        <td><font color="green">On review</font></td>
        <td>The labeling job is currently being reviewed.</td>
      </tr>
      </thead>
      <tbody>
      </tbody>
    </table>
</div>



<script>
document.forms[0].onsubmit = function(event) {
    event.preventDefault() // Cancel form submission
    // Which button has been pressed?
    var button_type = document.activeElement['value']
    // Hide position container
    document.getElementById("contrib_procedure_container").style.display = "none"
    document.getElementById("blanko_container").style.display = "none"
    // Show loading text
    document.getElementById("loading_text").style.display = "block"
    var team_email = document.getElementById("email").value;
    if (button_type == "task_overview") {
        // Set iframe target to HTML waiting position web app response
        var iframe = document.getElementById("contribution_status_iframe")
        var url = "https://script.google.com/macros/s/AKfycbzxi0VKZJPCpySqvnxiGLsfBYOiHuxKo2Wtg4dONoxI_Huw-YkjqJVmBGCfGS7CfhPJ/exec" + "?email=" + team_email + "&what=get_job_status"
        iframe.src = url
        iframe.onload = function() {
            //iframe.style.height = iframe.contentWindow.document.body.offsetHeight + 'px'
            // Hide loading text
            document.getElementById("loading_text").style.display = "none"
            // Show position container
            document.getElementById("contrib_procedure_container").style.display = "block"
        }
    } else {
        var iframe = document.getElementById("blanko_iframe")
        var url = ""
        if (button_type == "sanity_checks") { 
            url = "https://script.google.com/macros/s/AKfycbzxi0VKZJPCpySqvnxiGLsfBYOiHuxKo2Wtg4dONoxI_Huw-YkjqJVmBGCfGS7CfhPJ/exec" + "?email=" + team_email + "&what=run_checks"
        } else if (button_type == "dataset_url") {
            url = "https://script.google.com/macros/s/AKfycbzxi0VKZJPCpySqvnxiGLsfBYOiHuxKo2Wtg4dONoxI_Huw-YkjqJVmBGCfGS7CfhPJ/exec" + "?email=" + team_email + "&what=get_dataset_url"
        } else if (button_type == "waiting_list") {
            url = "https://script.google.com/macros/s/AKfycbzxi0VKZJPCpySqvnxiGLsfBYOiHuxKo2Wtg4dONoxI_Huw-YkjqJVmBGCfGS7CfhPJ/exec" + "?email=" + team_email + "&what=get_waiting_list"
        }
        // Set iframe target to HTML waiting position web app response
        iframe.src = url
        iframe.onload = function() {
            // iframe.style.height = iframe.contentWindow.document.body.offsetHeight + 'px'
            // Hide loading text
            document.getElementById("loading_text").style.display = "none"
            // Show position container
            document.getElementById("blanko_container").style.display = "block"
        }
    }
}

// ToDo: Re-activate this functionality
// // Handle parameters for pre-filled contribution status page
// window.onload = function () {
//     // Check iframe src
//     if (iframe = document.getElementById("contribution_status_iframe").src == "") {
//         (new URL(window.location.href)).searchParams.forEach(
//             (val, param) => document.getElementsByName(param).forEach(
//             (el) => el.value = val)
//         );
//         // Submit form if there is pre-filled input
//         document.getElementById("task_overview").click()
//     };
// };
</script>
