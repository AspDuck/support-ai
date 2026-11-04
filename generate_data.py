"""Generate fully synthetic support interactions. No real client or patient records."""
from pathlib import Path
import random
import sqlite3
from datetime import datetime, timedelta

DB = Path(__file__).with_name('support_demo.sqlite3')
COUNT = 10_000
REGIONS = ['Halifax', 'Cape Breton', 'Colchester', 'Kings', 'Lunenburg', 'Pictou', 'Hants', 'Annapolis', 'Cumberland', 'Yarmouth', 'Other NS']
REGION_WEIGHTS = [39, 14, 9, 7, 6, 6, 5, 4, 4, 3, 3]
ISSUES = ['Access to counselling', 'Anxiety / stress', 'Financial stress', 'Housing insecurity', 'Family / relationships', 'Depression / low mood', 'Substance use', 'Loneliness / isolation', 'Navigation / eligibility']
ISSUE_WEIGHTS = [15, 18, 14, 12, 10, 12, 7, 6, 6]
CHANNELS = ['Phone', 'Chat', 'Email', 'Web form']
AGE_BANDS = ['Under 18', '18–24', '25–34', '35–44', '45–54', '55–64', '65+', 'Not provided']
TRIAGE = ['Routine', 'Elevated', 'Urgent']
OUTCOMES = ['Information provided', 'Referral accepted', 'Follow-up required', 'Unable to connect', 'Resolved at first contact']
REFERRALS = ['Community counselling', '211 / community services', 'Primary care', 'Housing support', 'Financial support', 'Crisis support', 'Self-guided resources', 'No referral']


def generate(path=DB, count=COUNT):
    rng = random.Random(20261101)
    conn = sqlite3.connect(path)
    conn.execute('DROP TABLE IF EXISTS interactions')
    conn.execute('''CREATE TABLE interactions (
        id INTEGER PRIMARY KEY, created_at TEXT NOT NULL, region TEXT NOT NULL,
        age_band TEXT NOT NULL, channel TEXT NOT NULL, issue TEXT NOT NULL,
        triage TEXT NOT NULL, referral TEXT NOT NULL, outcome TEXT NOT NULL,
        response_hours REAL NOT NULL, follow_up INTEGER NOT NULL
    )''')
    start = datetime(2025, 1, 1)
    rows=[]
    for idx in range(1, count + 1):
        day = rng.randrange(0, 665)
        dt = start + timedelta(days=day, hours=rng.randint(8, 21), minutes=rng.randint(0, 59))
        issue = rng.choices(ISSUES, ISSUE_WEIGHTS)[0]
        region = rng.choices(REGIONS, REGION_WEIGHTS)[0]
        age = rng.choices(AGE_BANDS, [6, 15, 21, 20, 15, 11, 8, 4])[0]
        channel = rng.choices(CHANNELS, [40, 29, 22, 9])[0]
        triage = rng.choices(TRIAGE, [74, 21, 5])[0]
        if issue in ('Housing insecurity', 'Substance use') and rng.random() < .25:
            triage = rng.choice(['Elevated', 'Urgent'])
        referral = rng.choices(REFERRALS, [19, 18, 13, 11, 10, 5, 15, 9])[0]
        if issue == 'Housing insecurity' and rng.random() < .63:
            referral = 'Housing support'
        if issue == 'Financial stress' and rng.random() < .55:
            referral = 'Financial support'
        if triage == 'Urgent' and rng.random() < .7:
            referral = 'Crisis support'
        outcome = rng.choices(OUTCOMES, [24, 30, 19, 9, 18])[0]
        if triage == 'Urgent' and rng.random() < .45:
            outcome = 'Follow-up required'
        response = round(max(.1, rng.lognormvariate(.65, .85) * (1.5 if triage=='Routine' else .75)), 1)
        follow_up = int(outcome == 'Follow-up required' or (triage == 'Urgent' and rng.random() < .3))
        rows.append((idx, dt.isoformat(timespec='minutes'), region, age, channel, issue, triage, referral, outcome, response, follow_up))
    conn.executemany('''INSERT INTO interactions VALUES (?,?,?,?,?,?,?,?,?,?,?)''', rows)
    conn.execute('CREATE INDEX ix_date ON interactions(created_at)')
    conn.execute('CREATE INDEX ix_region ON interactions(region)')
    conn.commit()
    conn.close()
    return path

if __name__ == '__main__':
    print(f'Generated {count if False else COUNT:,} synthetic interactions: {generate()}')
