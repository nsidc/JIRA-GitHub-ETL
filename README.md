<p align="center">
  <img alt="NSIDC logo" src="https://nsidc.org/themes/custom/nsidc/logo.svg" width="150" />
</p>


# Converting JIRA Tickets to GitHub Issues

This software will allow JIRA and Github user to convert JIRA tickets to Github issues while maintaing as many features as possible.


## Level of Support

* This repository is fully supported by NSIDC. If you discover any problems or bugs,
  please submit an Issue. If you would like to contribute to this repository, you may fork
  the repository and submit a pull request. 
* This repository is not actively supported by NSIDC but we welcome issue submissions and
  pull requests in order to foster community contribution.

See the [LICENSE](LICENSE) for details on permissions and warranties. Please contact
nsidc@nsidc.org for more information.


## Requirements

* JIRA Ticket XML
* Access to GitHub repository
* Anaconda and Conda installed locally

## Conda Environment Setup
This section will serve as a guide to set up the proper environment with the required libraries.

1. Clone this repository into a directory of your choosing
2. Open the Anaconda Prompt (do a search on your computer for 'Anaconda Prompt' or open any terminal that can use the `conda` keyword; check using `conda --version` to see if a version pops up)
3. Path to where you cloned the repository in the terminal of your choosing
4. Run the command `conda env create -f environment.yml` to create a new environment with the necessary libraries
    (Note: If you want to use the development environment, type conda env create -f environment-dev.yml` instead)
5. Accept the creation and allow the dependencies to be installed
6. Activate the new environment with `conda activate JG-ETL` and have fun! 
    (Note: If you are using the development evironment use `conda activate JG-ETL-Dev` instead)

**Other Conda Notes:**
- Use `conda --version` to check the version of conda
- Use `conda env list` to see your current conda environments
- Use `conda env export > environment.yml` to update the environmnt file after changes
- Use `conda remove -n JG-ETL --all` to remove the environment
    * `conda remove -n JG-ETL-Dev --all` if you installed the dev version instead
- Use `conda install <packagename>=<version>` to install packages
    * Be sure to update the environment.yml if any packages are added

## Usage

This is a conversion tool to convert JIRA tickets to GitHub Issues while preserving as many features as possible. 

The user will be able to provide a list of JIRA tickets in the form of an XML, which will then be converted to GitHub issues. The conversion will maintain the title, description, checklist (if possible), user who created the JIRA ticket (if possible), user who is assigned to the ticket, and the people subscribed to the ticket. 

## Credit

This content was developed by the National Snow and Ice Data Center with funding from
multiple sources.
