# automated-scraper
This repository is an example of how you can use Github Actions to automate a python script. It was created in part using [this tutorial](https://www.python-engineer.com/posts/run-python-github-actions/).

## TL;DR
Go to the Actions tab on your repository's homepage and click "set up a workflow yourself." Paste the following content into the file that is created, and change information in brackets to the correct information for your repository. 

``` yml
name: [workflow-name-here]
on:
  schedule:
    - cron:  '[time-interval-in-cron]'
jobs:
  build:
    runs-on: ubuntu-latest
  steps:
    - name: checkout repo content
        uses: actions/checkout@v4.1.1 
    - name: Setup Python
        uses: actions/setup-python@v5.1.0
        with:
            python-version: '3.11.8'
    - name: install python packages
        run: |
            python -m pip install --upgrade pip
            [one line for each library, with this syntax: pip install package-name]
    - name: execute py script 
        run: python [python-script-name]
    - name: commit files
        run: |
            git config --local user.email "action@github.com"
            git config --local user.name "Github Action"
            git add -A
            git diff-index --quiet HEAD || (git commit -a -m "[commit-message]" --allow-empty)

    - name: GitHub Push
        uses: ad-m/github-push-action@v0.8.0
        with:
            github_token: ${{ secrets.GITHUB_TOKEN }}
            branch: [desired-branch]
```

Commit and push your changes to the file. Go to your repository's settings, and under Actions>General, select Read and write permissions under Workflow permissions. Then click Save.

Your workflow should run automatically according to your specifications. For reference on cron time syntax, look [here](https://docs.gitlab.com/ee/topics/cron/) and [here](https://crontab.guru/).

To authenticate gspread for Google Sheets use, check out the [Push to Google Sheets](#push-to-google-sheets) part of this README.

## Repository structure
This repository includes a python script that pulls data from [Cal OES](https://gis.data.ca.gov/datasets/CalEMA::power-outage-incidents/explore) power outage API. The script pulls data from the API and pushes results to both a Google sheet and a csv file (oes-pge-outages.csv). 

The repository also includes a .gitignore file to ensure local files that are not essential to the repository are not pushed to Github. 

The .github/workflows/main.yml creates a Github Actions workflow to automate the script.

**NOTE:** It seems that Github Actions doesn't like Jupyter Notebook (.ipynb) files. If you're working in Jupyter Notebook, click File > Download as > Python (.py). Add the downloaded python script to your repository. You can edit the python script in VSCode or another python editor and push your changes to Github. Alternatively, you could continue to edit your file in Jupyter Notebook and each time you save your changes, re-download the file and add it to your Github repo.

## Automate script
To automatically run your script at a certain time interval, you will need to add a yml file to your repository. You can either manually add it to your repo at .github/workflows/\[your-file\].yml (the period before github is important and should be included in your directory name), or you can navigate to the Actions tab on your repo's homepage in Github. There, you can click the "set up a workflow yourself" hyperlink, which will create a main.yml file at the correct filepath in your repository. 

In the yml file, you first need to name your workflow. In this repository, the workflow is named "run scraper." To add the name of your workflow to the yml file, write the following on the first line:

``` yml
name: run scraper
```

On the next line, you can specify under which conditions the workflow should run. The workflow can depend on a specific time or action. To specify a time at which the script should run, you'll need to use [cron syntax](https://docs.gitlab.com/ee/topics/cron/). You can check the interpretation of your cron syntax [here](https://crontab.guru/). The code snippet below is an example of how to schedule your workflow to run everyday at 9:00 AM ET.

``` yml
on:
  schedule:
    - cron '0 13 * * *'
```

For more complex repositories, you can schedule multiple jobs to run during your workflow. For a simple scraper, you should only need one job with one build. To add this job, paste the following code onto the next few lines:

``` yml
jobs:
  build:
    runs-on: ubuntu-latest
  steps:
```

Next, you will need to list the steps for this job. Each step has a name, and some syntax for what that step does. For this scraper, the job first uses the [actions/checkout](https://github.com/actions/checkout) package to navigate the current repository.

``` yml
    - name: checkout repo content
        uses: actions/checkout@v4.1.1 
```

The next two step use the [actions/setup-python](https://github.com/actions/setup-python) package to install the specified version on python, and pip to install the specified packages. 

``` yml
    - name: Setup Python
        uses: actions/setup-python@v5.1.0
        with:
            python-version: '3.11.8'
    - name: install python packages
        run: |
            python -m pip install --upgrade pip
              pip install pandas
              pip install requests
              pip install gspread
              pip install oauth2client
              pip install gspread_dataframe
```

Once the job has been set up, it runs the python script (called cal-oes-scraper.py in this repository).

``` yml
- name: execute py script 
        run: python cal-oes-scraper.py
```

The job can also commit and push any changes it makes to the repository. To allow the workflow to push changes, you need to navigate to your repository settings. Under Actions > General, scroll to "Workflow permissions" and select "Read and write permissions." Then click Save.

``` yml
- name: commit files
    run: |
        git config --local user.email "action@github.com"
        git config --local user.name "Github Action"
        git add -A
        git diff-index --quiet HEAD || (git commit -a -m "updated logs" --allow-empty)

- name: GitHub Push
    uses: ad-m/github-push-action@v0.8.0
    with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
         branch: main
```

Once you have filled out your yml file with the correct information, commit your changes and push the file to your repository. The workflow will run at your specified time interval. You can check the workflow runs in the Actions tab of your repository's homepage on Github.

## Push to Google Sheets
The python script in this repository uses the [gspread](https://docs.gspread.org/en/v6.0.0/) library to push data to Google Sheets. Gspread requires authentication to access Google Sheets, either througha a real Google account or through an automated service account. The python script in this repository uses a service account to authenticate, which requires an authentication key. The key can be obtained from an existinig auth.json file, or by following the directions [here](https://docs.gspread.org/en/latest/oauth2.html). 

An authentication key should be hidden from the public.  One way to do this is to store it as a repository secret. To do this, go to your repository's settings, then Secrets and variables > Actions > Repository secrets > New repository secret. Name your secret (`AUTH_CREDENTIALS` in this repo - secrets automatically have names in all caps). Paste your auth information into the "Secret" field. To access this secret in your script, you first need to add it to your environment through your yml file.

In .github/workflows/main.yml, paste the following code on the line before your python script is run. Replace `AUTH_CREDENTIALS` with your repository secret's name if needed.

``` yml
env:
  AUTH_CREDENTIALS: ${{ secrets.AUTH_CREDENTIALS }}
```

So the whole step for running your script should look something like:

``` yml
- name: execute py script
  env:
    AUTH_CREDENTIALS: ${{ secrets.AUTH_CREDENTIALS }}
  run: python cal-oes-scraper.py
```

You can now access the secret in your python script by importing the [os module](https://www.w3schools.com/python/module_os.asp) and calling `os.environ["SECRET_NAME"]`. The secret automatically saves as a string in the python script. To use the secret for gspread, you need to change it from a string to a dictionary and call gspread.service_account_from_dict(). 

``` python
import os 

try:
    credentials = json.loads(os.environ["AUTH_CREDENTIALS"])
except KeyError:
    credentials = "Token not available!"
gc = gspread.service_account_from_dict(credentials)
```
