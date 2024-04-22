# automated-scraper
This repository is an example of how you can use Github Actions to automate a python script. It was created in part using [this tutorial](https://www.python-engineer.com/posts/run-python-github-actions/).

## TL;DR
Go to the Actions tab on your repository's homepage and click "set up a workflow yourself." Paste the following content into the file that is created, and change information in brackets to the correct information for your repository. 

```
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
            git config --local user.email "[email-to-receive-build-notifications]"
            git config --local user.name "Github Action"
            git add -A
            git diff-index --quiet HEAD || (git commit -a -m "updated logs" --allow-empty)

    - name: GitHub Push
        uses: ad-m/github-push-action@v0.8.0
        with:
            github_token: ${{ secrets.GITHUB_TOKEN }}
            branch: [desired-branch]
```

Commit and push your changes to the file. Go to your repository's settings, and under Actions>General, select Read and write permissions under Workflow permissions. Then click Save.

Your workflow should run automatically according to your specifications. For reference on cron time syntax, look [here](https://docs.gitlab.com/ee/topics/cron/) and [here](https://crontab.guru/).

## Repository structure
This repository includes a python script that pulls data from [Cal OES](https://gis.data.ca.gov/datasets/CalEMA::power-outage-incidents/explore) power outage API. The script pulls data from the API and pushes results to both a Google sheet (auth.json needed for authentication) and a csv file (oes-pge-outages.csv). 

The repository also includes a .gitignore file to ensure local files that are not essential to the repository are not pushed to Github. 

The .github/workflows/main.yml creates a Github Actions workflow to automate the script.

**Note:** It seems that Github Actions doesn't like Jupyter Notebook (.ipynb) files. If you're working in Jupyter Notebook, click File > Download as > Python (.py). Add the downloaded python script to your repository. You can edit the python script in VSCode or another python editor and push your changes to Github. Alternatively, you could continue to edit your file in Jupyter Notebook and each time you save your changes, re-download the file and add it to your Github repo.

## How to automate script
To automatically run your script at a certain time interval, you will need to add a yml file to your repository. You can either manually add it to your repo at .github/workflows/\[your-file\].yml (the period before github is important and should be included in your directory name), or you can navigate to the Actions tab on your repo's homepage in Github. There, you can click the "set up a workflow yourself" hyperlink, which will create a main.yml file at the correct filepath in your repository. 

In the yml file, you should name your workflow. In this repository, the workflow is named "run scraper". This name will appear as the commit message any time the workflow runs. To add the name of your workflow to the yml file, write the following in the first line of the yml file:

```
name: [workflow-name-here]
```

On the next line, you will need to specify when the workflow should run. The workflow can depend on a specific time or action. To specify a time at which the script should run, you'll need to use [cron syntax](https://docs.gitlab.com/ee/topics/cron/). You can check the interpretation of your cron syntax [here](https://crontab.guru/). The code snippet below is an example of how to schedule your workflow to run everyday at 9:00 AM ET.

```
on:
  schedule:
    - cron:  '[time-interval-in-cron]'
```

For more complex repositories, you can schedule multiple jobs to run in your workflow. For a simple scraper, you'll just need one job with one build. The generic starter syntax for a yml workflow is:

```
jobs:
  build:
    runs-on: ubuntu-latest
  steps:
```

Followed by a list of steps the workflow should follow. For this scraper, the workflow first uses the [actions/checkout](https://github.com/actions/checkout) package to navigate the current repository.

```
- name: checkout repo content
    uses: actions/checkout@v4.1.1 
```

The next two step use the [actions/setup-python](https://github.com/actions/setup-python) package to install the specified version on python, and pip to install the specified packages. 

```
- name: Setup Python
    uses: actions/setup-python@v5.1.0
    with:
        python-version: '3.11.8'
- name: install python packages
    run: |
        python -m pip install --upgrade pip
        [one line for each library, with this syntax: pip install package-name]
```

Once the workflow has been set up, it runs the python script.

```
- name: execute py script 
        run: python [python-script-name]
```

The workflow can also commit and push any changes it makes to the repository. In order to allow the workflow to push changes, you need to navigate to your repository' settings. Under Actions > General, scroll to "Workflow permissions" and select Read and write permissions. Then click save.

```
- name: commit files
    run: |
        git config --local user.email "[email-to-receive-build-notifications]"
        git config --local user.name "Github Action"
        git add -A
        git diff-index --quiet HEAD || (git commit -a -m "updated logs" --allow-empty)

- name: GitHub Push
    uses: ad-m/github-push-action@v0.8.0
    with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
         branch: [desired-branch]
```

Once you have filled out your yml file with the correct information, commit your changes and push the file to your repository. The workflow will run at your specified time interval. You can check the workflow runs in the Actions tab of your repository's homepage on Github.

## TODO
Figure out how to implement a requirements.txt file to install all packages.
