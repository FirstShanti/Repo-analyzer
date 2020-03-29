from datetime import datetime
import requests
import time
import sys
from models import User, Params, Query
from argv_parse import get_params
from loading import loading
from man import *


loading = loading()
len_name = set()


def print_commit(commiters, len_name):
	try:
		max_len = int(max(list(len_name)))
	except ValueError:
		print('\nNo commits\n')
		return
	if commiters:
		commiters = {k: v for k, v in sorted(commiters.items(), key=lambda item: item[1], reverse=True)}
		count = 30
		sys.stdout.write('\033[2K\033[1G')
		print('\nCOMMITS: ', sum([v for v in commiters.values()]))
		for login, commits in commiters.items():
			print(f'{login}:{" "*int(max_len-len(login))} {commits}')
			count -= 1
			if count <= 0:
				break
				return
		print('\n')
	else:
		print('\nNo commits\n')


def add_commiters(commit, commiters):
	try:
		if commit['author']['login'] == "invalid-email-address":
			login = commit['commit']['author']['name']
		else:
			login = commit['author']['login']
	except TypeError:
		login = commit['commit']['author']['name']
	
	if login not in commiters:
		commiters[login] = 1
		next(loading)
	else:
		commiters[login] += 1
		next(loading)
	len_name.add(len(login))

	return commiters


def add_pulls(j, pulls):
	if datetime.fromisoformat(j['created_at'][:-1:]) >= query.params.start_date\
	  and datetime.fromisoformat(j['created_at'][:-1:]) <= query.params.end_date:
		if (query.params.end_date - datetime.fromisoformat(j['created_at'][:-1:])).days >= 30 and j['state'] == 'open':
			pulls['open']['old'] += 1
			next(loading)
		elif j['state'] == 'closed':
			pulls['closed'] += 1
			next(loading)
		else:
			pulls['open']['new'] += 1
			next(loading)
	return pulls


def get_commiters(query):
	commiters = {}
	res = query.request_commits

	if res.links:
		for i in range(1, int(res.links['last']['url'].split('=')[-1])+1):
			next(loading)
			res_ = requests.get(url=f"{res.url}&page={i}", headers=query.headers)
			for j in res_.json():
				next(loading)
				commiters.update(add_commiters(j, commiters))
	elif not res.links:
		for i in res.json():
			next(loading)
			commiters.update(add_commiters(i, commiters))
	else:
		print('\nNo commits\n')

	sys.stdout.write('\033[2K\033[1G')
	print_commit(commiters, len_name)

	return
				

def get_pulls(query):
	pulls = {'open':{'old': 0, 'new': 0}, 'closed': 0}
	res = query.request_pulls
		
	if res.links:
		last_pull_number_on_49_page = int(requests.get(res.links['last']['url'], headers=query.headers_pulls).json()[-1]['url'].split('/')[-1])
		for i in range(1, int(res.links['last']['url'].split('=')[-1])+1):
			next(loading)
			res = requests.get(f'{query.url_repo_pulls}?state=all&base={query.params.branch}&page={i}', headers=query.headers)
			if datetime.fromisoformat(res.json()[-1]['created_at'][:-1:]) > query.params.end_date:
				continue
			elif datetime.fromisoformat(res.json()[0]['created_at'][:-1:]) < query.params.start_date:
				break
			else:
				for j in res.json():
					next(loading)
					pulls.update(add_pulls(j, pulls))
		if last_pull_number_on_49_page >= 1:
			for i in range(last_pull_number_on_49_page, 1):
				next(loading)
				res_ = requests.get(f'{query.url_repo_pulls}/{i}', headers=query.headers)
				if res_.json():
					if datetime.fromisoformat(res_.json()['created_at'][:-1:]) > query.params.end_date:
						continue
					elif datetime.fromisoformat(res_.json()['created_at'][:-1:]) < query.params.start_date:
						break
					else:
						for j in res_.json():
							next(loading)
							pulls.update(add_pulls(j, pulls))
	elif not res.links:
		for j in res.json():
			next(loading)
			pulls.update(add_pulls(j, pulls))
	else:
		print('\nNo pulls\n')
		return

	sys.stdout.write('\033[2K\033[1G')
	sys.stdout.write(f"PULLS\nOpen:   {pulls['open']['old'] + pulls['open']['new']}\
		\nClosed: {pulls['closed']}\
		\nOld:    {pulls['open']['old']}\n"
	)
	return


def get_issues(query):
	issues = {'open':{'old': 0, 'new': 0}, 'closed': 0}
	pages = 0
	res = query.request_issues

	if res.json():
		pages = int((int(res.json()[0]['html_url'].split('/')[-1]) / 30) // 1 + 1)

	if pages >= 1:
		for i in range(1, pages + 1):
			next(loading)
			res = requests.get(f"{query.url_repo_issues}?filter=all&state=all&since={query.params.s_date}&page={i}", headers=query.headers_issues)
			if res.json() and datetime.fromisoformat(res.json()[-1]['created_at'][:-1:]) > query.params.end_date:
				continue
			elif res.json() and datetime.fromisoformat(res.json()[0]['created_at'][:-1:]) < query.params.start_date:
				break
			else:
				if res.json():
					for j in res.json():
						next(loading)
						if datetime.fromisoformat(j['created_at'][:-1:]) >= query.params.start_date\
							and datetime.fromisoformat(j['created_at'][:-1:]) <= query.params.end_date\
							and j['html_url'].split('/')[-2] != 'pull':
							if (query.params.end_date - datetime.fromisoformat(j['created_at'][:-1:])).days >= 14\
							and j['state'] == 'open':
								issues['open']['old'] += 1
							else:
								if j['state'] == 'closed':
									issues['closed'] += 1
								else:
									issues['open']['new'] += 1
						next(loading)
	sys.stdout.write('\033[2K\033[1G')
	sys.stdout.write(f"\nISSUES\nOpen:   {issues['open']['old'] + issues['open']['new']}\
		\nClosed: {issues['closed']}\
		\nOld:    {issues['open']['old']}\n\n"
	)
	return


if __name__ == ("__main__"):
	user = User()
	if user.authorized:
		params = Params()
		if params.params:
			query = Query(params)
			get_commiters(query)
			get_pulls(query)
			get_issues(query)
		else:
			print(man)
	else:
		print(man_no_auth)
	
