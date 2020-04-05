import sys
import asyncio
import aiohttp
import requests
import json
from datetime import datetime
from time import time
from man import *
from models import User, Params, Query
from loading import loading


start = time()
loading = loading()
len_name = set()
#requests = 0
reset = datetime.now()

user = User()
if user.authorized:
	params = Params()
	params.validation()
	query = Query(params)
	print(f"Start from: {params.start_date}\nTo: {params.end_date}\nbranch: {params.branch}\n")
else:
	print(man_no_auth)
	exit()


# convert string created time to <datetime> whithout 'Z'
def date_format(j):
	return datetime.fromisoformat(j['created_at'][:-1:])


async def fetch(session, url, params={}):
	global requests
	global reset
	async with session.get(url, params=params) as response:
		try:
			if response.status == 200 and int(response.headers['X-RateLimit-Remaining']) < 5000:
				try:
					pages = int(str(response.links['last']['url']).split('=')[-1])
				except KeyError:
					pages = 1
				requests = 5000 - int(response.headers['X-RateLimit-Remaining'])
				reset = datetime.fromtimestamp(int(response.headers["X-RateLimit-Reset"])).isoformat(timespec="seconds")
				res = await response.json()
				return (res, pages)
			else:
				sys.stdout.write('\r\033[2K\033[1G')
				print(f'Error: {response.status}\
					\nUrl: {response.url}\
					\nAvailable queries: {response.headers["X-RateLimit-Remaining"]}\
					\nLimit reset at: {reset}')
				exit()
		except Exception as e:
			raise e


def print_commit(commiters, len_name):
	try:
		max_len = int(max(list(len_name)))
	except ValueError:
		print('\nNo commits\n')
		return
	if commiters:
		commiters = {k: v for k, v in sorted(commiters.items(), key=lambda item: item[1], reverse=True)}
		count = 30
		sys.stdout.write('\r\033[2K\033[1G')
		print('\rCOMMITS: ', sum([v for v in commiters.values()]))
		for login, commits in commiters.items():
			print(f'{login}:{" "*int(max_len-len(login))} {commits}')
			count -= 1
			if count <= 0:
				break
		print('\n')
	return


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
	if (params.end_date - date_format(j)).days >= 30 and j['state'] == 'open':
		pulls['open']['old'] += 1
		next(loading)
	elif j['state'] == 'closed':
		pulls['closed'] += 1
		next(loading)
	else:
		pulls['open']['new'] += 1
		next(loading)
	return pulls


async def get_commiters(session):

	commiters = {}
	res, pages = await fetch(session, query.url_repo_commits, params=params.payload)

	for i in range(1, pages+1):
		query.payload.update({'page':f'{i}'})
		next(loading)
		res_, _ = await fetch(session, query.url_repo_commits, params=params.payload)
		for j in res_:
			next(loading)
			commiters.update(add_commiters(j, commiters))

	print_commit(commiters, len_name)
	return


async def get_pulls(session):
	pulls = {'open':{'old': 0, 'new': 0}, 'closed': 0}
	res, pages = await fetch(session, query.url_repo_pulls, params={'state':'all', 'base':params.branch})

	for i in range(1, pages+1):
		next(loading)
		res_, _ = await fetch(session, f'{query.url_repo_pulls}?state=all&base={params.branch}&page={i}')
		if pages>2 and datetime.fromisoformat(res_[-1]['created_at'][:-1:]) > params.end_date:
			next(loading)
			continue
		elif pages>2 and datetime.fromisoformat(res_[0]['created_at'][:-1:]) < params.start_date:
			break
		else:
			for j in res_:
				if date_format(j) <= params.end_date and date_format(j) >= params.start_date:
					next(loading)
					pulls.update(add_pulls(j, pulls))

	sys.stdout.write('\r\033[2K\033[1G')
	print(f"\rPULLS     \nOpen:   {pulls['open']['old'] + pulls['open']['new']}\
		\nClosed: {pulls['closed']}\
		\nOld:    {pulls['open']['old']}\n"
	)
	return


async def get_issues(session):
	issues = {'open':{'old': 0, 'new': 0}, 'closed': 0}
	res, pages = await fetch(session, query.url_repo_issues, params={'filter':'all', 'state':'all', 'since':params.payload['since']})

	for i in range(1, pages + 1):
		next(loading)
		res_, _= await fetch(session, query.url_repo_issues, params={'filter':'all', 'state':'all', 'since':params.payload['since'], 'page':str(i)})
		if pages > 2 and datetime.fromisoformat(res_[-1]['created_at'][:-1:]) > params.end_date:
			continue
		elif pages > 2 and datetime.fromisoformat(res_[0]['created_at'][:-1:]) < params.start_date:
			break
		for j in res_:
			next(loading)
			if date_format(j) >= params.start_date\
				and date_format(j) <= params.end_date\
				and j['html_url'].split('/')[-2] != 'pull':
				if (params.end_date - date_format(j)).days >= 14\
				and j['state'] == 'open':
					issues['open']['old'] += 1
				else:
					if j['state'] == 'closed':
						issues['closed'] += 1
					else:
						issues['open']['new'] += 1
			next(loading)

	sys.stdout.write('\r\033[2K\033[1G')
	sys.stdout.write(f"\rISSUES    \nOpen:   {issues['open']['old'] + issues['open']['new']}\
		\nClosed: {issues['closed']}\
		\nOld:    {issues['open']['old']}\n\n"
	)
	return


async def main():
	async with aiohttp.ClientSession(headers=user.headers, json_serialize=json.dumps) as session:
			
			task1 = asyncio.create_task(get_commiters(session))
			task2 = asyncio.create_task(get_pulls(session))
			task3 = asyncio.create_task(get_issues(session))
			
			await asyncio.gather(task1, task2, task3)
			

if __name__ == ("__main__"):
	t0 = time()
	asyncio.run(main())
	print('Total time:   ', round(time()-t0, 2)
		, 'sec')
	print(f'Total request: {requests}\nRequests limit update after: {reset}')

