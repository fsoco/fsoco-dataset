# FSOCO Tools CLI

You've probably arrived here after reading [Tools website](https://www.fsoco-dataset.com/tools) or coming across the FSOCO Tools directly from GitHub.<br/> Either way, we're thrilled to have you here! This page should get you up and running in around 10-15 m reading time; <br/>we're looking forward to your contribution!
## Table Of Contents

* [Code of Conduct](./CODE_OF_CONDUCT.md)
* [How can I contribute?](#contribute)
    * [Reporting bugs](#bugs)
    * [Correcting or adding documentation](#correction)
    * [Adding a new tool](#add_tool)
        * [Adding a new command to an existing command group](#existing)
        * [Adding a new stand-alone command](#standalone)
        * [Adding a new command group](#group)
    * [Pull requests](#pull_requests)
* [Styleguides](#style)
    * [pep8](#pep)
    * [Documentation](#doc)
* [Additional notes](#notes)
    * [Issue and Pull request labels](#gh_labels)

The structure of this TOC is heavily borrowed from the [Atom editor Contribution Guidelines](https://github.com/atom/atom/blob/master/CONTRIBUTING.md)

### <a name="contribute"></a> How Can I Contribute?
#### <a name="bugs"></a> Reporting bugs

If you find unexpected or undocumented behavior within the tool suite, please open a bug report issue and fill in the details required by the template.
#### <a name="correction"></a> Correcting or adding documentation
Documentation is important.
If you find documentation that is missing, incomplete or unclear, please be pro-active and open a fitting Issue.
#### <a name="add_tool"></a> Adding a new tool

When considering the addition of a new tool, use these simple rules of thumb:

"Does the new tool fit into one of the existing categories?"

If it does, refer to [Adding a new command to an existing command group](#existing)<br/>
Otherwise, ask yourself the next question:

"Are there two or more scripts, also taking the new one into consideration, that would fit into one category that doesn't yet exist?"

If answered positively, a new command group should be created, for which please refer to [Adding a new command group](#group).<br/>
Otherwise, the newly added script should be a [stand-alone command](#standalone).
How to handle these cases is discussed in the two following sections. 
<br/>The procedure for merging your changes into the main repository is explained in [Pull Requests](#pull_requests) 

##### <a name="existing"></a>Adding a new command to an existing command group
Let's say team NitrousOcelots (NOX) uses a label format that isn't covered by the available label converters.
Since NOX is really keen on participating in the dataset and expanding the data available to their software team, 
they decide to write a simple Python script to convert their labels.  
Other teams might find this script useful as well, so NOX goes the extra mile and decides to also share their script with the community. 
By sharing their script, NOX improves their perception in two ways: 
1. Their pythonic work of art strikes awe in its readers and users
1. They are added as contributors in the FSOCO Tools package

Enough with the preliminaries, now for the details.
NOX wants to add the script `labelMe2yolo` to the tools suite. 
In order to do so, it needs to create a Python module within the `label_converters` module.
This is easily achieved by creating a directory with the same name and including an empty `__init__.py` file in it.
At this point in time, our tools directory should somewhat look like this:
```shell script
tools
├── label_converters
.   ├── labelMe2yolo
.   │   ├── __init__.py
.   │   └── labelMe2yolo.py
.   ├── yolo2sly
.   ├── __init__.py
.   └── label_converters.py
```
The next step is to actually integrate the tool into the CLI.
For this integration, we'll create a new Python file called `click_labelMe2yolo.py`

```python
% click_labelMe2yolo.py

import click
from .labelMe2yolo import main

@click.command()
@click.argument('arg1', required=True)
@click.option('--opt1', help="Short help", required=False)
def labelMe2yolo(arg1, opt1):
    """
    This not only is a docstring, it will also be the description shown when running:
    $ fsoco label-converters labelMe2yolo --help
    """
    click.echo("[LOG] Running labelMe2yolo script")
    main(arg1=arg1, opt1=opt1)


if __name__ == '__main__':
    click.echo("[LOG] This sub-module is not meant to be run as a stand-alone script. Please refer to\n $ fsoco --help")
```
What we are doing in this snippet is defining the new CLI command that we want to expose.
The entry point of the CLI command will be the imported `main` function. Making transition relatively easy from pre-existing scripts.
Regarding arguments and options, Click follows the conventions of Unix scripts. Please refer to their very thorough documentation
if you are curious or want to experiment with some of its other features for your own projects.

The last relevant information is that the name of the method we are defining here, will be the name of the command.
In this case, `labelMe2yolo`, as documented in the docstring, which doubles as help description.

The last step, after making sure that calling your script's `main` method this way works correctly, is to add this command 
to its parent command group. To add the command, two small changes in `label_converters.py` suffice:
1. Adding an import for its Click command:
    ```python
    import click
    from label_converters.yolo2sly.click_yolo2sly import yolo2sly
    from label_converters.labelMe2yolo.click_labelMe2yolo import labelMe2yolo
    ```
2. Adding its Click command to the `label_converters` group:

    ```python
    # Add the yolo2sly click command to the label-converters group
    label_converters.add_command(yolo2sly)    
    # Add the labelMe2yolo click command to the label-converters group
    label_converters.add_command(labelMe2yolo)
    ```
Summing up:
1. Fork the main repository
1. Create a python module within the directory for the command group
1. Write a small wrapper file for your script's Click interface
1. Add your wrapped script to the existing command group as a sub-command 
1. Make sure the naming expresses what your addition does 
1. Open a [Pull Request](#pull_requests)

##### <a name="standalone"></a> Adding a new stand-alone command
For a more creative contribution example, refer to [Adding a new command to an existing command group.](#existing)
The steps for adding a new stand-alone command are the following:
1. Fork the main repository
1. Create a python module within the `tools/` directory
    ```shell script
    tools
    ├── label_converters
    ├── similarity_scorer
    ├── watermark
    ├── your_module_here
    .
    .
    .
    ```
1. Write a small Click wrapper file to interface with your script as a command

    This is an example of the minimal setup for your module:
    ```shell script
    your_module
    ├── click_your_expressive_script_name.py
    ├── __init__.py
    └── your_expressive_script_name.py
    ```
1. Add the command created in your wrapper to the fsoco command group

    For this, you'll have to add two lines of code to `click_fsoco.py`
    ```python
    from your_module.click_your_expressive_script_name import your_command
    fsoco.add_command(your_command, name="command_name")
    ``` 
    The name parameter can be left out, if its contents are equivalent to `your_command`, in this case. 
1. Open a [Pull Request](#pull_requests)
##### <a name="group"></a> Adding a new command group

For a more creative contribution example, refer to [Adding a new command to an existing command group.](#existing)
The steps for adding a new command group are the following:
1. Fork the main repository
1. Open an Issue to discuss the creation of the new command group
    1. Only continue after discussion/confirmation
1. Create a python module within the `tools/` directory
    ```shell script
    tools
    ├── label_converters
    ├── similarity_scorer
    ├── watermark
    ├── your_module_here
    .
    .
    .
    ```
1. Write a small Click wrapper file to interface with your script as a command

    This is an example of the minimal setup for your module:
    ```shell script
    your_module
    ├── __init__.py
    ├── new_command_group.py
    ├── sub_command_1.py
    |   ├── __init__.py
    |   ├── click_sub_command_1.py
    |   └── sub_command_1.py 
    └── sub_command_2.py
        .
        .
    ```
    
3. Add the command created in your wrapper to the fsoco command group

    For this, you'll have to add two lines of code to `click_fsoco.py`
    ```python
    from your_module.click_your_expressive_script_name import your_command
    fsoco.add_command(your_command, name="command_name")
    ``` 
    The name parameter can be left out, if its contents are equivalent to `your_command`, in this case. 
1. Open a [Pull Request](#pull_requests)    
#### <a name="pull_requests"></a> Pull requests
The workflow for the contribution is the same as in [GitHub Flow](https://guides.github.com/introduction/flow/index.html) two additions.
* Forking repository before opening PR
* Naming convention for branches
    * Feature Branches: `feature/#XX_expressive-branch-name`
    * Documentation Branches: `docs/#XX_expressive-branch-name`
    * Bug-Fix Branches: `bug-fix/#XX_expressive-branch-name`

Please note that `#10` in GitHub is used to reference issue nr. 10.
<br/>Likewise, `!10` works the same way for Pull Requests.

Pull Requests should always resolve a previously opened Issue and reference it in its header.

For those more visually inclined:

![FSOCO GitHub Flow](https://fsoco.github.io/fsoco-dataset/assets/img/tools/FSOCO_branching.svg)
### <a name="style"></a> Styleguides
#### <a name="pep"></a> [PEP 8](https://www.python.org/dev/peps/pep-0008/)
Please use the official Style Guide for Python Code (PEP 8) to ensure consistency and readability.
The easiest way to ensure this is to use the [pre-commit hook](https://githooks.com/) from the tools repository, and correct whichever inconsistencies weren't fixed by the formatter.
If you're curious as to how it is setup, have a look at the `.pre-commit-config.yaml` and `.flake8` files in the root repository directory.
Also, you need to follow the installation instructions for the pre-commit hooks to be run, as `pre-commit` needs to be installed.
#### <a name="doc"></a> Documentation
If your method name clearly states its purpose and doesn't span too many lines, you don't need to write a docstring for it, although it is appreciated.
An example is:
```python
 94 def pil_to_cvmat(pil_img): 
 95     # From https://stackoverflow.com/questions/43232813/convert-opencv-image-       +++format-to-pil-image-format 
 96     # use numpy to convert the pil_image into a numpy array 
 97     np_img = np.array(pil_img) 
 98  
 99     # convert to a opencv image, notice the COLOR_RGB2BGR which means that 
100     # the color is converted from RGB to BGR format 
101     cv_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR) 
102  
103     return cv_img 
```

Please take into consideration that the Click command docstrings double as the help description on the command-line. 
<br/>To make sure that the help information is readable, test your addition with `fsoco ARGUMENTS --help`
### <a name="notes"></a> Additional notes
#### <a name="gh_labels"></a> Issue and Pull request labels
The following is a list of the available labels and their purpose:
* Bug: If you found something that doesn't behave as expected or documented, let us know this way.
* Documentation: If you think the documentation contains a mistake or needs clarification.
* Tools: If your issue deals with additions to the tool suite.
