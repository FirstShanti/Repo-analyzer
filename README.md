# Repo-analyzer
Python script for geting information about activity of Public Github repository with query period and branch. Analysis results output to stdout.
# Features:
- Python 3.7.0
- Requests
- Github API v3
# Description:
#### Values that script monitoring:
- Commits (
The most active participants. A table of 2 columns: author login, number of it
commits. The table is sorted by the number of commits in descending order. Not
more than 30 lines. The analysis is carried out for a given period of time and branch.):
    - `username:` `count`
    
- Pull Requests (The number of open, closed and old* pull requests for a given period of time PR creation date and the specified branch, which is the base for this PR):
    > *If the repository does not close for more than thirty days from the moment of opening and falls within the time range of the request, then it is considered old
    -    `open:` `count`
    -    `closed:` `count`
    -    `old:` `count`  
    
- Issues (Count of open, closed and "old"*, for a given period of time by date create issue):
    > *The number of "old" issues for a given period of time by the date the issue was created. Issue is considered old if it does not close within 14 days
    -    `open:` `count`
    -    `closed:` `count`
    -    `old:` `count` 
    
# Getting Started

### Preparing Environment
For first clone this repository:

` git clone https://github.com/FirstShanti/Repo-analyzer `

Install virtualenv:

` sudo apt install python3.7-venv `

Create virtual environment:

` python3.7 -m venv name_of_your_environment `

Activate environment:

` source ./name_of_your_environment/bin/activate `

Install python packages from requirements:

` pip install -r requirements.txt `

### Add GitHub Personal access token

Get access token at https://github.com/settings/tokens and put it in variable ` TOKEN ` in ` config.py `

# All is done

You can try a simple query without any options:

` python start.py https://github.com/FirstShanti/Repo-analyzer `

In order to familiarize yourself with the script commands and instructions, run file:

` python start.py `
