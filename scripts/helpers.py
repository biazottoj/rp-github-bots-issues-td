import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def create_dataset_row(bot, issue, text_section='title', is_comment=False, comment_number=None, owner=None, project=None): 
    if not is_comment:
        return {
            "bot":bot,
            'owner': owner,
            'project': project,
            'issue' : issue['number'],
            'text' : issue[text_section],
            'type' : text_section,
            'n-comments': issue['comments'],
            'author-login': issue['user']['login'],
            'open-date':  issue['created_at'],
            'state' : issue['state'],
            'close-date': issue['closed_at'],
            'closed-by': issue['closed_by']['login'] if issue['closed_by'] != None else '-',
            'td-label': '-'
        }
    
    return {
            "bot":bot,
            'owner': owner,
            'project': project,
            'issue' : issue['issue_url'].split('/')[-1],
            'text' : issue['body'],
            'type' : f'comment_{comment_number}',
            'author-login': issue['user']['login'],
            'open-date': issue['created_at'],
            'state' : '-',
            'close-date' :'-',
            'closed-by': '-',
            'td-label': '-'
        }
def requests_retry_session(retries=5, backoff_factor=5, session=None):
    """
    Retry request
    :param retries:
    :param backoff_factor:
    :param session:
    :return:
    """
    session = session or requests.Session()

    Retry.BACKOFF_MAX = 60
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(403, 500, 502, 503, 504),
    )
    adapter = HTTPAdapter(max_retries=retry)

    # super important
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session