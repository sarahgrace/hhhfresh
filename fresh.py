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
    submissions = [sub for sub in reddit.subreddit('hiphopheads').top('week', limit=25)]
    # Filter 'FRESH'
    submissions = [sub for sub in submissions if 'FRESH' in sub.title]
    # Filter score
    submissions = [sub for sub in submissions if sub.score >= 500]
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
    print('before update: %d entries' % len(ids))
    for sub in submissions:
        if sub['id'] in ids:
            c.execute('UPDATE submissions SET score = ? WHERE id = ?', (sub['score'], sub['id']))
        else:
            c.execute('INSERT INTO submissions VALUES (?,?,?,?,?)', (sub['id'], sub['title'], sub['url'], sub['date'], sub['score']))
    ids = set(row[0] for row in c.execute('SELECT id FROM submissions'))
    print('after update: %d entries' % len(ids))

def generate_page(submissions):
    doc, tag, text = Doc().tagtext()
    doc.asis('<!DOCTYPE html>')

    '''
    <a title="Web Analytics Made Easy - StatCounter"
    href="http://statcounter.com/" target="_blank"><img
    src="//c.statcounter.com/11596056/0/e29090d6/1/" alt="Web
    Analytics Made Easy - StatCounter" ></a>
    '''

    with tag('html'):
        with tag('head'):
            with tag('title'):
                text('hhhfresh')
            doc.stag('link', rel='stylesheet', href='style.css')
            doc.stag('link', rel='stylesheet', href='https://fonts.googleapis.com/css?family=Open+Sans')
        with tag('body'):
            with tag('h1'):
                text('Welcome to hhhfresh')
            with tag('h3'):
                text('Fresh submissions pulled from ')
                with tag('a', href='https://www.reddit.com/r/hiphopheads'):
                    text('r/hiphophheads')
                with tag('a', title='StatCounter', href='http://statcounter.com/'):
                    with tag('img', src='https://c.statcounter.com/11596056/0/e29090d6/1/'):
                        text('')
            with tag('table'):
                with tag('tr'):
                    with tag('th', id='datecol'):
                        text('Date')
                    with tag('th', id='titlecol'):
                        text('Title')
                    with tag('th', id='scorecol'):
                        text('Score')
                for sub in submissions:
                    with tag('tr'):
                        with tag('td'):
                            text(format_date(sub[3]))
                        with tag('td', id='titlecell'):
                            with tag('a', href=sub[2]):
                                text(sub[1])
                        with tag('td'):
                            text(sub[4])

    with open('index.html', 'w') as f:
        f.write(doc.getvalue())

def format_date(date):
    abbr = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
    month = abbr[int(date[5:7])]
    return '%s. %s, %s' % (month, date[8:], date[:4])

if __name__ == '__main__':
    # Print date and time
    print('TIME: %s' % str(datetime.now()))

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
    submissions = get_submissions(reddit)

    # Update database
    update_database(c, submissions)
    conn.commit()

    # Generate HTML
    submissions = [row for row in c.execute('SELECT * FROM submissions ORDER BY date DESC, score DESC')]
    generate_page(submissions)

    # Close connection
    conn.close()

    # Print done
    print('Done.\n')
