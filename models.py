import sys
import requests
import json
from datetime import datetime
from argv_parse import get_params
from config import TOKEN, USERNAME
from man import info


def get_token():
    return TOKEN


class User():
    def __init__(self):
        self.token()
        self.headers = { 
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'token {self.token}'
        }


    def token(self):
        self.token = get_token()


    @property
    def authorized(self):
        auth_res = requests.get('https://api.github.com/user', headers=self.headers)
        if auth_res.ok:
            print('--Authorized--')
            return True
        else:
            print(info)
            print('**Not authorized**')
            return False


class Params(User):
    def __init__(self, argv=get_params(), *args, **kwargs):
        super(Params, self).__init__(*args, **kwargs)
        self.url = argv.get('url')
        self.start_date = argv.get('start_date')
        self.end_date = datetime.fromisoformat(argv.get('end_date').isoformat(timespec='seconds'))
        self.branch = argv.get('branch')
        self.payload = {'until' : f"{self.end_date.isoformat(timespec='seconds')}Z"}


    def validation(self):
        self.check_url()
        self.check_branch()
        self.check_start_date()


    def check_url(self):
        if not self.url.endswith('/'):
            try:
                url, owner, repo = self.url.split('/')[2:]
                if url != 'github.com':
                    print(f'\nInvalid url: {url}\n\nExample: https://github.com/<username>/<repository>\n')
                    exit()
                else:
                    res = requests.get(f'https://api.github.com/users/{owner}', headers={
                        'Authorization': f'token {self.token}'
                        }
                    )
                    if res.status_code != 200:
                        if res.status_code == 404:
                            print(f'\nUser <{owner}> not found\n\n')
                            exit()
                    else:
                        res = requests.get(f'https://api.github.com/repos/{owner}/{repo}', headers={
                            'Authorization': f'token {self.token}'
                            }
                        )
                        if res.status_code != 200:
                            if res.status_code == 404:
                                print(f'\nRepository <{repo}> not found\n\n')
                                exit()
                        else:               
                            self.url = f'https://api.github.com/repos/{owner}/{repo}'
                            return self.url
            except ValueError:
                print(f'\nInvalid url: {self.url}\n\nExample: https://github.com/username/repository\n')
                exit()
        else:
            print(f'\nInvalid url: {self.url}\n\nExample: https://github.com/username/repository\n')
            exit()


    def check_branch(self):
        res = requests.get(f'{self.url}/branches/{self.branch}', headers={
            'Authorization': f'token {self.token}'
            }
        )
        if res.status_code != 200:
            if res.status_code == 404:
                print(f'\nBranch <{self.branch}> not found\n')
                exit()
        else:
            self.payload['branch'] = self.branch
            self.payload['sha'] = self.branch
            return self.branch


    def check_start_date(self):
        if self.start_date:
            self.start_date = datetime.fromisoformat(self.start_date.isoformat(timespec='seconds'))
            self.payload['since'] = f"{self.start_date.isoformat(timespec='seconds')}Z"
        else:
            res = requests.get(self.url, headers={
                'Authorization': f'token {self.token}'
                }
            )
            self.start_date = datetime.fromisoformat(res.json()['created_at'][:-1:])
            self.payload['since'] = res.json()['created_at']


class Query(User):
    def __init__(self, params, *args, **kwargs):
        super(Query, self).__init__(*args, **kwargs)
        self.params = params
        self.url_repo = params.url
        self.url_repo_branch = self.url_repo + f'/branches/{self.params.branch}'
        self.url_repo_commits = self.url_repo + '/commits'
        self.url_repo_pulls = self.url_repo + '/pulls'
        self.url_repo_issues = self.url_repo + '/issues'
        self.payload = self.params.payload

