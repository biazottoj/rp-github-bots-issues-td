from minirig import load_csv_dataset, save_csv_dataset
import pandas as pd
import json
import os
from pathlib import Path
import random
import sys

data_dir = Path('../data')
cache_dir_github = data_dir.joinpath('github')
bots_dataset_path = data_dir.joinpath('bots-dataset.csv')
bots_issues_dir = data_dir.joinpath('bots-issues')
github_token = open('../gh-token.txt','r').readlines()[0].strip()



def load_issues_per_bot(bot, issue_count):
    issues = []
    cnt = 1
    for owner in os.listdir(bots_issues_dir.joinpath(bot)):
        for project in os.listdir(bots_issues_dir.joinpath(bot).joinpath(owner)):
            for issue in os.listdir(bots_issues_dir.joinpath(bot).joinpath(owner).joinpath(project).joinpath('issues')):
                issue_path = bots_issues_dir.joinpath(bot).joinpath(owner).joinpath(project).joinpath('issues').joinpath(issue)
                yield issue_path


def select_issues():
    bot = sys.argv[1]
    bots_more_100_issues = [x for x in load_csv_dataset(bots_dataset_path) if int(x['issue_count']) >= 100]
    comments_error = []
    bots_dataset_totals = []
    issue_error = []
    issues_not_labeled = []
    issues_bot = [issue for issue in load_issues_per_bot(bot, 100)]

    print('open')

    indexes = [random.randint(0,len(issues_bot)) for x in range(101)]

    for x in indexes:
        try:
            with open(issues_bot[x].joinpath('json')) as f:
                issue = json.load(f)
        except:
            continue
            
        try:
            has_td = issue['td-label-li2022-emse'] == 'SATD'
        except:
            continue
        
        if issue['user']['login'] == bot:
            print(issue['html_url'])

    print('close')

    indexes = [random.randint(0,len(issues_bot)) for x in range(11)]

    for x in indexes:
        try:
            with open(issues_bot[x].joinpath('json')) as f:
                issue = json.load(f)
        except:
            continue
            
        try:
            has_td = issue['td-label-li2022-emse'] == 'SATD'
        except:
            continue
            
        
        if issue['state'] == 'closed' and issue['closed_by']['login'] == bot:
            print(issue['html_url'])
    




select_issues()