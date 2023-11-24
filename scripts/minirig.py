import csv
##import os
##import tempfile
##import json
##import logging
##import re
##import time
##from datetime import datetime, timedelta
from pathlib import Path
#
##import pandas as pd
##import requests
##from git import Repo
##import pydriller as pdl
#
#from helpers import requests_retry_session
#
#
#class CachedRequests:
#    def __init__(self, cache_dir=None):
#        self.cache_dir = Path(cache_dir if cache_dir else tempfile.mkdtemp())
#    
#    def _request(self, url, headers):
#        response = requests_retry_session().get(url, headers=headers)       
#        if response.status_code == 200:
#            return response.json()
#        elif response.status_code in [403, 429]:
#            reset_time = None
#            reset_headers = ['X-RateLimit-Reset', 'X-RateLimit-Reset-After', 'X-RateLimit-Reset-Time',
#                             'X-Rate-Limit-Reset', 'X-Rate-Limit-Reset-After', 'X-Rate-Limit-Reset-Time',
#                             'RateLimit-Reset', 'RateLimit-Reset-After', 'RateLimit-Reset-Time',
#                             'Rate-Limit-Reset', 'Rate-Limit-Reset-After', 'Rate-Limit-Reset-Time']
#            for header in reset_headers:
#                if header in response.headers:
#                    reset_time = int(response.headers[header])
#                    break
#            if reset_time is not None:
#                sleep_time = reset_time - time.time()
#                logging.warning(f'API rate limit exceeded, sleeping for {sleep_time} seconds')
#                time.sleep(sleep_time if sleep_time >= 0 else 0)
#                return self._request(url, headers)
#            else:
#                logging.error('Unable to find rate limit reset time')
#                return response.json()
#        else:
#            logging.error(f'Request failed ({response.status_code}): {url}')
#            return response.json()
#
#    def _url_to_path(self, url):
#        # if the url contains params
#        illegal_characters = r'[\<\>\:"\\\|\*]'
#        url_path = re.sub(r'^https?://(.*)/*$',r'\1',url)
#        url_path = url_path.replace('?','/').replace('//','/')
#        url_path = re.sub(illegal_characters, '_', url_path)
#        # tranform the url into a path
#        filepath = Path(self.cache_dir).joinpath(url_path)
#        filepath = filepath.joinpath('json')
#        return filepath
#
#    def _get_cache_or_remote(self, url, headers):
#        jsonpath = self._url_to_path(url)
#        if not jsonpath.exists():
#            logging.debug(f'Caching {url}')
#            jsonpath.parent.mkdir(parents=True, exist_ok=True)
#            with jsonpath.open('w', encoding='utf-8') as f:
#                res = self._request(url,headers=headers)
#                json.dump(res,f)
#        #print(jsonpath)
#        with jsonpath.open() as f:
#            return json.load(f)
#    
#    def _delete_cache(self, url):
#        jsonpath = self._url_to_path(url)
#        if jsonpath.exists():
#            jsonpath.unlink()
#
#
#class GHRequests(CachedRequests):
#    def __init__(self, token=None, api_url='https://api.github.com', owner=None, repo=None, cache_dir=None):
#        self.token = token
#        self.api_url = api_url
#        self.owner = owner
#        self.repo = repo
#        super().__init__(cache_dir)
#    
#    def _parse_details(self,owner, repo):
#        u = owner if owner else self.owner
#        r = repo if repo else self.repo
#        return (u,r)
#    
#    def _get(self,endpoint, force=False):
#        headers = {"accept": "application/vnd.github.v3+json"}
#        url = f'{self.api_url}{endpoint}'
#        if self.token:
#            headers['Authorization'] = f'token {self.token}'
#        if force:
#            return super()._request(url,headers)
#        else:
#            return super()._get_cache_or_remote(url,headers)
#    
#    def get_api_limit_info(self):
#        return self._get('/rate_limit', force=True)
#    
#    def get_pullrequests_for_commit(self,commit_sha, owner=None, repo=None):
#        (o,r) = self._parse_details(owner,repo)
#        endpoint = f'/repos/{o}/{r}/commits/{commit_sha}/pulls'
#        return self._get(endpoint)
#    
#    def get_pullrequest_commits(self,pr_number, owner=None, repo=None):
#        (o,r) = self._parse_details(owner,repo)
#        endpoint = f'/repos/{o}/{r}/pulls/{pr_number}/commits'
#        return self._get(endpoint)
#    
#    def get_commit_info(self,commit_sha,owner=None, repo=None):
#        (o,r) = self._parse_details(owner,repo)
#        endpoint = f'/repos/{o}/{r}/commits/{commit_sha}'
#        return self._get(endpoint)
#
#    def get_issue_info(self,issue_number,owner=None, repo=None, force=False):
#        (o,r) = self._parse_details(owner,repo)
#        endpoint = f'/repos/{o}/{r}/issues/{issue_number}'
#        return self._get(endpoint,force=force)
#
#    def get_number_issues_involving_user(self,username, force=False):
#        endpoint = f'/search/issues?q=involves:{username}+is:issue'
#        return self._get(endpoint, force=force)['total_count']
#    
#    def _get_page(self,url,page, force=False):
#        endpoint = f'{url}&page={page}'
#        return self._get(endpoint, force=force)
#
#    def get_comments_per_issue(self,issue_number,owner=None, repo=None, force=False):
#        (o,r) = self._parse_details(owner,repo)
#        endpoint = f'/repos/{o}/{r}/issues/{issue_number}/comments'
#        return self._get(endpoint,force=force)
#    
#    def get_issues_involving_user(self,username,from_date=None,force=False):
#        results_limit = 1000
#        per_page = 100
#        if from_date:
#            endpoint = f'/search/issues?q=involves:{username}+is:issue+updated:>={from_date}&sort=updated&order=asc&per_page={per_page}'
#        else:
#            endpoint = f'/search/issues?q=involves:{username}+is:issue&sort=updated&order=asc&per_page={per_page}'
#        
#        page_1 = self._get_page(endpoint,1,force=force)
#        total_pages = -(page_1['total_count'] // -per_page) # cieling division
#
#        for issue in page_1['items']:
#            yield issue
#        
#        for page in range(2, min(results_limit//per_page,total_pages)+1):
#            for issue in self._get_page(endpoint,page, force=force)['items']:
#                yield issue
#        
#        if total_pages > results_limit//per_page:
#            yield from self.get_issues_involving_user(username,issue['updated_at'],force=force)
#
#class JiraRequests(CachedRequests):
#    def __init__(self, api_url, cache_dir=None):
#        self.api_url = api_url
#        super().__init__(cache_dir)
#
#    def _get(self,endpoint):
#        headers = {"accept": "application/json"}
#        url = f'{self.api_url}{endpoint}'
#        return super()._get_cache_or_remote(url,headers)
#    
#    def get_issue_info(self, issue_key):
#        endpoint = f'/issue/{issue_key}'
#        return self._get(endpoint)
#    
#    def get_issue_reporter(self, issue_key):
#        issue = self.get_issue_info(issue_key)
#        reporter = issue['fields']['reporter']
#        return f"{reporter['displayName']} ({reporter['name']})"
#    
#    def get_issue_reporting_date(self, issue_key):
#        issue = self.get_issue_info(issue_key)
#        date_str = issue['fields']['created']
#        return date_str[:10]
#    
#    def get_issue_resolution_date(self, issue_key):
#        issue = self.get_issue_info(issue_key)
#        date_str = issue['fields']['resolutiondate']
#        return date_str[:10]
#    
#    def get_issue_commenter(self, issue_key, comment_number):
#        issue = self.get_issue_info(issue_key)
#        commenter = issue['fields']['comment']['comments'][comment_number]['author']
#        return f"{commenter['displayName']} ({commenter['name']})"
#    
#    def get_issue_commenting_date(self, issue_key, comment_number):
#        issue = self.get_issue_info(issue_key)
#        date_str = issue['fields']['comment']['comments'][comment_number]['created']
#        return date_str[:10]
#    
#    def get_all_issue_commenters(self, issue_key):
#        issue = self.get_issue_info(issue_key)
#        return [f"{c['author']['displayName']} ({c['author']['name']})" 
#                for c in issue['fields']['comment']['comments']]
#    
#    def get_issue_last_commenting_date(self, issue_key):
#        issue = self.get_issue_info(issue_key)
#        date_str = issue['fields']['comment']['comments'][-1]['created']
#        return date_str[:10]
#
#
#class GHRepo:
#    def __init__(self, owner, repo, repos_dir=tempfile.mkdtemp(), clone_repo=True):
#        self.owner = owner
#        self.repo = repo
#        self.local_dir = os.path.join(repos_dir, owner, repo)
#        if clone_repo:
#            self.clone_repo()
#    
#    def clone_repo(self, force=False):
#        try:
#            if force or not os.path.exists(self.local_dir):
#                url = f'https://github.com/{self.owner}/{self.repo}'
#                Repo.clone_from(url, self.local_dir)
#                logging.debug(f'Cloned {self.owner}/{self.repo} to {self.local_dir}')
#            logging.debug(f'{self.local_dir} already exists')
#        except:
#            logging.error(f'Could not clone {self.owner}/{self.repo}')
#    
#    # More traverse options:
#    #   https://pydriller.readthedocs.io/en/latest/repository.html#filtering-commits
#    def traverse_all_commits(self):
#        return pdl.Repository(self.local_dir).traverse_commits()
#
#    def get_commit(self, commit_sha):
#        return next(pdl.Repository(self.local_dir, single=commit_sha).traverse_commits())
#    
#    def get_commit_author(self, commit_sha):
#        try:
#            c = self.get_commit(commit_sha)
#            return f"{c.author.name} ({c.author.email})"
#        except:
#            logging.error(f'Commit not found: {self.owner}/{self.repo} {commit_sha}')
#            return '-'
#    
#    def get_commit_date(self, commit_sha):
#        try:
#            c = self.get_commit(commit_sha)
#            return c.author_date.strftime("%Y-%m-%d")
#        except:
#            logging.error(f'Commit not found: {self.owner}/{self.repo} {commit_sha}')
#            return '-'
#
#    
#def find_commits_jira_issues(gh_repo):
#    issue_commits = {}
#    for commit in gh_repo.traverse_all_commits():
#        #Jira issue pattern PROJECT-<issue_number>, we used a regex to filter the commits
#        closed_issues = re.findall(r'(\w+-\d+)', commit.msg.upper(), re.DOTALL)
#        for ci in closed_issues:
#            issue_commits[ci] = issue_commits.get(ci, []) + [commit.hash]
#    return issue_commits
#
#
#def days_between(d1, d2):
#    if re.search(r'^\d\d\d\d-\d\d-\d\d$', d1) and re.search(r'^\d\d\d\d-\d\d-\d\d$', d2):
#        d1 = datetime.strptime(d1, "%Y-%m-%d")
#        d2 = datetime.strptime(d2, "%Y-%m-%d")
#        return abs((d2 - d1).days)
#    else:
#        return 'unknown'


def in_list(cotainee, container):
    if isinstance(cotainee,str):
        return cotainee in container
    else:
        return any([c in container for c in cotainee])
    

def in_list_count(cotainee, container):
    if isinstance(cotainee,str):
        return cotainee in container
    else:
        return any([c in container for c in cotainee])


def load_csv_dataset(filename, dialect='excel'):
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, dialect=dialect)
        return [row for row in reader]

    
def save_csv_dataset(filename, data, header=None):
    header = header if header else list(data[0].keys())
    with open(filename, 'w', encoding="utf-8") as f:
        writer = csv.DictWriter(f,fieldnames=header)
        writer.writeheader()
        for d in data:
            writer.writerow(d)

def dict_csv_to_dataframe(dataset):
    return pd.DataFrame.from_records(dataset)


