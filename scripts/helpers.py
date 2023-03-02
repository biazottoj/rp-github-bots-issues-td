import csv
import os
import tempfile
import json
import logging
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from git import Repo
from github import RateLimitExceededException, Github
import pydriller as pdl


class CachedRequests:
    def __init__(self, cache_dir=None):
        self.cache_dir = Path(cache_dir if cache_dir else tempfile.mkdtemp())
    
    def _get_remote(self, url, headers):
        return requests.get(url,headers=headers).json()
    
    def _get_cache_or_remote(self, url, headers, params):
        path = re.sub(r'^https?://(.*)/?$',r'\1',url).replace('?q=involves:','/').replace('+is:issue','') + f"/{params['page']}"
        filepath = self.cache_dir.joinpath(path)
        jsonpath = filepath.joinpath('json')
        if not jsonpath.exists():
            logging.warning(url)
            filepath.mkdir(parents=True, exist_ok=True)
            with jsonpath.open('w') as f:
                res = requests.get(url,headers=headers, params=params).json()
                json.dump(res,f)
        with jsonpath.open() as f:
            return json.load(f)


class GHRequests(CachedRequests):
    def __init__(self, token=None, api_url='https://api.github.com', owner=None, repo=None, cache_dir=None):
        self.token = token
        self.api_url = api_url
        super().__init__(cache_dir)
    
    def _parse_details(self,owner, repo):
        u = owner if owner else self.owner
        r = repo if repo else self.repo
        return (u,r)
    
    def _get(self,endpoint, force=False):
        headers = {"accept": "application/vnd.github.v3+json",
                   "authorization": f"token {self.token}"}
        url = f'{self.api_url}{endpoint}'
        if force:
            return super()._get_remote(url,headers)
        else:
            return super()._get_cache_or_remote(url,headers)

    def get_issue_info(self,issue_number,owner=None, repo=None):
        (o,r) = self._parse_details(owner,repo)
        endpoint = f'/repos/{o}/{r}/issues/{issue_number}'
        return self._get(endpoint)
    
    def get_issue_comments(self,comment_id,owner=None, repo=None):
        (o,r) = self._parse_details(owner,repo)
        endpoint = f'/repos/{o}/{r}/issues/comments/{comment_id}'
        return self._get(endpoint)
    
    def get_api_limit_info(self):
        return self._get('/rate_limit', force=True)

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
    with open(filename, 'r') as f:
        reader = csv.DictReader(f, dialect=dialect)
        return [row for row in reader]

    
def save_csv_dataset(filename, data, header=None):
    header = header if header else list(data[0].keys())
    with open(filename, 'w') as f:
        writer = csv.DictWriter(f,fieldnames=header)
        writer.writeheader()
        for d in data:
            writer.writerow(d)

def dict_csv_to_dataframe(dataset):
    return pd.DataFrame.from_records(dataset)


