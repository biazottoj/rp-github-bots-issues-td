from pathlib import Path
from model_li2022_emse import *
from minirig import load_csv_dataset
import pandas as pd
import json
import os
import sys

def load_issues_per_bot(bot, issue_count):
    issues = []
    cnt = 1
    for owner in os.listdir(bots_issues_dir.joinpath(bot)):
        for project in os.listdir(bots_issues_dir.joinpath(bot).joinpath(owner)):
            for issue in os.listdir(bots_issues_dir.joinpath(bot).joinpath(owner).joinpath(project).joinpath('issues')):
                issue_path = bots_issues_dir.joinpath(bot).joinpath(owner).joinpath(project).joinpath('issues').joinpath(issue)
                try:
                    with open(issue_path.joinpath('json')) as f:
                        issue_file = json.load(f)
                        yield {'path':issue_path, 'content':issue_file}
                except:
                    continue
                    
def store_labeled_issues(batch, predictions):
    for i, issue in enumerate(batch):
        issue['content']['td-label-li2022-emse'] = str(predictions[i])
        with open(Path(issue['path']).joinpath('json'), 'w') as f:
            json.dump(issue['content'], f)

def load_issues_comments_per_bot(bot, issue_count):
    issues = []
    cnt = 1
    for owner in os.listdir(bots_issues_dir.joinpath(bot)):
        for project in os.listdir(bots_issues_dir.joinpath(bot).joinpath(owner)):
            for issue in os.listdir(bots_issues_dir.joinpath(bot).joinpath(owner).joinpath(project).joinpath('issues')):
                comments_path = bots_issues_dir.joinpath(bot).joinpath(owner).joinpath(project).joinpath('issues').joinpath(issue).joinpath('comments')
                try:
                    with open(comments_path.joinpath('json')) as f:
                        comments_file = json.load(f)
                        yield {'path':comments_path, 'content':comments_file, 'n-comments':len(comments_file)}
                except:
                    continue

def prepare_comments_batch(batch):
    batched_comments = []
    for comments_file in batch:
        for c in comments_file['content']:
            batched_comments.append(c['body'])
    return batched_comments

def store_labeled_comments(batch, predictions):
    pred_idx = 0
    for comments in batch:
        for i in range(int(batch['n-comments'])):       
            comments['content'][i]['td-label-li2022-emse'] = str(predictions[pred_idx])
            pred_idx += 1
                       
        with open(Path(comments['path']).joinpath('json'), 'w') as f:
            json.dump(issue['content'], f)

def label_comments():
    nltk.download('punkt')
    model1_li2022_emse = Model1_IssueTracker_Li2022_ESEM('../model/mode1-issue-tracker-li2022-emse/model1-issue-tracker-li2022-esem-weight_file.hdf5', 
                    '../model/mode1-issue-tracker-li2022-emse/model1-issue-tracker-li2022-esem-word_embedding_file.bin')
    batch_size = 8
    bots_dataset = pd.read_csv('../data/bots-dataset-labeling-management.csv',delimiter=',')
    for i in bots_dataset.index:
        cnt = 1
        if bots_dataset['label_comments_finished'][i] == 'yes':
            continue
        bot = bots_dataset['account'][i]
        batch = []
        batched_comments = []
        for comments in load_issues_comments_per_bot(bot, bots_dataset['issue_count'][i]):
            model1_li2022_emse.clear_model_session()
            if cnt != 455:
                batch.append(comments)
            if len(batch) >= batch_size:
                batched_comments = prepare_comments_batch(batch)
                try:
                    predictions = model1_li2022_emse.label_sections_in_batch(batched_comments, batch_size=len(batched_comments))
                    store_labeled_comments(batch, predictions)
                except:
                    pass
                batch = []
            sys.stdout.flush()
            print(f'{bot}: {cnt}/{bots_dataset["issue_count"][i]} (len batch:{np.sum([x["n-comments"] for x in batch])})', end="\r")
            cnt += 1
            
        if len(batch) > 0:
            try:
                predictions = model1_li2022_emse.label_sections_in_batch(batched_comments, batch_size=len(batched_comments))
                store_labeled_comments(batch, predictions)
            except:
                pass
            batch = []
            
        bots_dataset['label_finished'][i] = 'yes'
        bots_dataset.to_csv('../data/bots-dataset-labeling-management.csv', index=False)

if __name__ == "__main__":
    '''data_dir = Path('../data')
    cache_dir_github = data_dir.joinpath('github')
    bots_dataset_path = data_dir.joinpath('bots-dataset.csv')
    bots_issues_dir = data_dir.joinpath('bots-issues')
    label_comments()'''
    import tensorflow as tf
    print(tf.config.list_physical_devices('GPU'))
    