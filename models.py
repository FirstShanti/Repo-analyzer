import sys
import requests
from datetime import datetime
from argv_parse import get_params
from config import TOKEN, USERNAME
from man import info


def get_username():
    return USERNAME


def get_token():
    return TOKEN


class Params():
    def __init__(self, get_params=get_params, argv=sys.argv):
        self.params = get_params(argv)
        if self.params:
            try:
                self.url, self.s_date, self.e_date, self.branch = self.params.values()
            except AttributeError:
                self.url, self.s_date, self.e_date, self.branch = self.params
            self.payload = {'sha': self.branch}
            self.get_repo_url()
            self.get_branch_url()

            if self.s_date:
                try:
                    self.start_date = datetime.fromisoformat(self.s_date)
                    self.payload['since'] = self.s_date.encode()
                except ValueError:
                    print(f'\nInvalid start format date: {self.s_date}\n')
                    print(f'Use this case: YYYY-MM-DDTHH:MM:SS - 2020-01-01T12:34:56\n{" "*15}YYYY-MM-DD{" "*10}- 2020-01-01\n')
                    exit()
            else:
                res = requests.get(self.url_repo, headers={
                    'Accept': 'application/vnd.github.nebula-preview+json',
                    'Authorization': f'token {TOKEN}'
                    }
                )
                self.start_date = datetime.fromisoformat(res.json()['created_at'][:-1:])
                self.s_date = res.json()['created_at']
                self.payload['since'] = self.s_date.encode()
                print("Start from: ", self.start_date)
            if self.e_date:
                try:
                    self.end_date = datetime.fromisoformat(self.e_date)
                    self.payload['until'] = f'{self.e_date}Z'.encode()
                except ValueError:
                    print(f'\nInvalid end format date: {self.e_date}\n')
                    print(f'Use this case: YYYY-MM-DDTHH:MM:SS - 2020-01-01T12:34:56\n{" "*15}YYYY-MM-DD{" "*10}- 2020-01-01\n')
                    exit()
            else:
                self.end_date = datetime.fromisoformat(datetime.now().isoformat(timespec='seconds'))
                self.payload['until'] = f"{self.end_date.isoformat(timespec='seconds')}Z".encode()
                print("End to: ", self.end_date)
            print(f'Branch: {self.branch}')
        else:
            self.params = False

    def get_repo_url(self):
        if not self.url.endswith('/'):
            try:
                url, owner, repo = self.url.split('/')[2:]
                if url != 'github.com':
                    print(f'\nInvalid url: {url}\n\nExample: https://github.com/<username>/<repository>\n')
                    exit()
                else:
                    res = requests.get(f'https://api.github.com/users/{owner}', headers={
                        'Accept': 'application/vnd.github.nebula-preview+json',
                        'Authorization': f'token {TOKEN}'
                        }
                    )
                    if res.status_code != 200:
                        if res.status_code == 404:
                            print(f'\nUser <{owner}> not found\n\n')
                            exit()
                    else:
                        res = requests.get(f'https://api.github.com/repos/{owner}/{repo}', headers={
                            'Accept': 'application/vnd.github.nebula-preview+json',
                            'Authorization': f'token {TOKEN}'
                            }
                        )
                        if res.status_code != 200:
                            if res.status_code == 404:
                                print(f'\nRepository <{repo}> not found\n\n')
                                exit()
                        else:               
                            self.url_repo = f'https://api.github.com/repos/{owner}/{repo}'
                            res = requests.get(self.url_repo, headers={
                                    'Accept': 'application/vnd.github.nebula-preview+json',
                                    'Authorization': f'token {TOKEN}'
                                    }
                                )
            except ValueError:
                print(f'\nInvalid url: {self.url}\n\nExample: https://github.com/<username>/<repository>\n')
                exit()
            else:
                return self.url_repo
        else:
            print(f'\nInvalid url: {self.url}\n\nExample: https://github.com/username/repository\n')
            exit()

    def get_branch_url(self):
        res = requests.get(f'{self.url_repo}/branches/{self.branch}', headers={
            'Accept': 'application/vnd.github.nebula-preview+json',
            'Authorization': f'token {TOKEN}'
            }
        )
        if res.status_code != 200:
            if res.status_code == 404:
                print(f'\nBranch <{self.branch}> not found\n')
                exit()
        else:
            return self.branch


class User():
    def __init__(self):
        self.username()
        self.token()
        self.headers = {
            'Authorization': f'token {self.token}'
        }
        self.headers_issues = {
            'Authorization': f'token {self.token}'
        }
        self.headers_pulls = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.VERSION.sha'
        }


    def username(self):
        self.username = get_username()


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


class Query(User):
    def __init__(self, params, *args, **kwargs):
        super(Query, self).__init__(*args, **kwargs)
        self.params = params
        self.url_repo = params.url_repo
        self.url_repo_branch = self.url_repo + f'/branches/{self.params.branch}'
        self.url_repo_commits = self.url_repo + '/commits'
        self.url_repo_pulls = self.url_repo + '/pulls'
        self.url_repo_issues = self.url_repo + '/issues'
        self.payload = self.params.payload
        self.request_repo()
        self.request_branch()
        self.request_commits()
        self.request_pulls()
        self.request_issues()


    def request_repo(self):
        self.request_repo =  requests.get(self.url_repo, headers=self.headers)
        return self.request_repo

    def request_branch(self):
        self.request_branch = requests.get(
            self.url_repo_branch,
            headers=self.headers
        )
        return self.request_branch


    def request_commits(self, url='', params={}):
        self.request_commits = requests.get(
            url=self.url_repo_commits,
            headers=self.headers,
            params=self.payload
        )
        return self.request_commits


    def request_pulls(self, url='', params={}):
        self.request_pulls = requests.get(
            url=self.url_repo_pulls,
            headers=self.headers,
            params={'state':'all', 'base':self.params.branch}
        )
        return self.request_pulls


    def request_issues(self):
        self.request_issues = requests.get(
            url=self.url_repo_issues,
            headers=self.headers_issues,
            params={'filter':'all', 'state':'all', 'since':self.params.s_date}
        )
        return self.request_issues
