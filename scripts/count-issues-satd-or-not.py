from minirig import load_csv_dataset, save_csv_dataset
import pandas as pd
import json
import os
from pathlib import Path

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


bots_more_100_issues = [x for x in load_csv_dataset(bots_dataset_path) if int(x['issue_count']) >= 100]

issue_error = []
bots_dataset_totals = []
issues_not_labeled = []
for bot_i in bots_more_100_issues:
    cnt = 1
    bot = bot_i['account']
    row = {"bot":bot,"n-issues-td":0, "n-issues-non-td": 0, "opened-satd": 0, "opened-non-satd": 0, "closed-satd": 0, "closed-non-satd": 0, "comments-satd": 0, "comments-non-satd": 0}
    for issue_path in load_issues_per_bot(bot, bot_i['issue_count']):
        try:
            with open(issue_path.joinpath('json')) as f:
                issue = json.load(f)
                is_closed = issue['state'] == 'closed'
        except:
            issue_error.append(f'{str(issue_path)}\n')
            continue
            
        try:
            has_td = issue['td-label-li2022-emse'] == 'SATD'
        except:
            issues_not_labeled.append(issue_path)
            continue

        if has_td:
            row['n-issues-td'] += 1
        else:
            row['n-issues-non-td'] += 1

        cnt += 1
        print(bot,cnt,bot_i['issue_count']) 

    bots_dataset_totals.append(row)
    save_csv_dataset(data_dir.joinpath('bots-dataset-totals-with-n-issues.csv'), bots_dataset_totals)