import os
import sys
import praw
import json
from datetime import datetime
from pprint import pprint
from yattag import Doc
import sqlite3

def get_submissions(reddit):
    # Get new submissions
    submissions = [sub for sub in reddit.subreddit('hiphopheads').top('year', limit=5000)]
    # Filter 'FRESH'
    submissions = [sub for sub in submissions if 'FRESH' in sub.title]
    # Filter score
    submissions = [sub for sub in submissions if sub.score >= 250]
    # Return submissions
    return [format_submission(sub) for sub in submissions]

def format_submission(submission):
    sub = {}
    sub['id'] = submission.id
    sub['title'] = submission.title
    sub['url'] = submission.url
    sub['date'] = str(datetime.fromtimestamp(submission.created).date())
    sub['score'] = submission.score
    return sub

def update_database(c, submissions):
    ids = set(row[0] for row in c.execute('SELECT id FROM submissions'))
    print('existing entries: ' + str(len(ids)))
    for sub in submissions:
        if sub['id'] in ids:
            c.execute('UPDATE submissions SET score = ? WHERE id = ?', (sub['score'], sub['id']))
        else:
            c.execute('INSERT INTO submissions VALUES (?,?,?,?,?)', (sub['id'], sub['title'], sub['url'], sub['date'], sub['score']))

def generate_page(submissions):
    doc, tag, text = Doc().tagtext()
    doc.asis('<!DOCTYPE html>')

    with tag('html'):
        with tag('head'):
            with tag('title'):
                text('hhhfresh')
            doc.stag('link', rel='stylesheet', href='style.css')
        with tag('body'):
            with tag('table'):
                with tag('tr'):
                    with tag('th'):
                        text('Date')
                    with tag('th'):
                        text('Title')
                    with tag('th'):
                        text('Score')
                for sub in submissions:
                    with tag('tr'):
                        with tag('td'):
                            text(sub[3])
                        with tag('td'):
                            with tag('a', href=sub[2]):
                                text(sub[1])
                        with tag('td'):
                            text(sub[4])

    with open('index.html', 'w') as f:
        f.write(doc.getvalue())

if __name__ == '__main__':
    # Authenticate reddit user
    reddit = praw.Reddit(client_id='mnDkhx_goM32iQ',
        client_secret=os.environ['SECRET'],
        user_agent='getting fresh stuff',
        username=os.environ['USER'],
        password=os.environ['PASS'])

    # Connect to database
    conn = sqlite3.connect('fresh.db')
    c = conn.cursor()

    # Create table
    #c.execute('''CREATE TABLE submissions
                     #(id TEXT PRIMARY KEY, title TEXT, url TEXT, date TEXT, score INTEGER)''')

    # Get fresh submissions
    #submissions = get_submissions(reddit)

    # Update database
    #update_database(c, submissions)
    #conn.commit()

    # Generate HTML
    submissions = [row for row in c.execute('SELECT * FROM submissions ORDER BY date DESC, score DESC')]
    generate_page(submissions)

    # Close connection
    conn.close()
