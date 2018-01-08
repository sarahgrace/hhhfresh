import os
import sys
import praw
import json
import pickle
from datetime import datetime
from pprint import pprint
from yattag import Doc

def get_submissions(reddit):
    # Get new submissions
    submissions = [sub for sub in reddit.subreddit('hiphopheads').top('month', limit=5000)]
    # Filter 'FRESH'
    submissions = [sub for sub in submissions if 'FRESH' in sub.title]
    # Filter score
    submissions = [sub for sub in submissions if sub.score >= 250]
    # Return submissions
    print(str(len(submissions)))
    return [format_submission(sub) for sub in submissions]

def serializable(obj):
    try:
        json.dumps(obj)
    except:
        return False
    return True

def format_submission(submission):
    sub = {}
    sub['title'] = submission.title
    sub['id'] = submission.id
    sub['url'] = submission.url
    sub['score'] = submission.score
    sub['date'] = str(datetime.fromtimestamp(submission.created).date())
    return sub

def generate_page(submissions):
    doc, tag, text = Doc().tagtext()
    doc.asis('<!DOCTYPE html>')

    with tag('html'):
        with tag('body'):
            with tag('table'):
                with tag('tr'):
                    with tag('th'):
                        text('Title')
                    with tag('th'):
                        text('Date')
                    with tag('th'):
                        text('Score')
                for sub in submissions:
                    with tag('tr'):
                        with tag('td'):
                            with tag('a', href=sub['url']):
                                text(sub['title'])
                        with tag('td'):
                            text(sub['date'])
                        with tag('td'):
                            text(sub['score'])

    with open('index.html', 'w') as f:
        f.write(doc.getvalue())

if __name__ == '__main__':
    # Authenticate reddit user
    reddit = praw.Reddit(client_id='mnDkhx_goM32iQ',
        client_secret='7r1Xi0j9lsgiFk4t_Cz2XxPl-3g',
        user_agent='getting fresh stuff',
        username=os.environ['USER'],
        password=os.environ['PASS'])

    # Unpickle fresh database
    #with open('fresh.pkl', 'rb') as f:
    #    fresh = pickle.load(f)
    fresh = []

    # Get fresh submissions
    submissions = get_submissions(reddit)

    # Generate HTML
    generate_page(submissions)

    # Pickle fresh database
    with open('fresh.pkl', 'wb') as f:
        pickle.dump(fresh, f)

