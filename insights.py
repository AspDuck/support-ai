"""Grounded natural-language analytics: parameterized SQL from fixed templates only."""
import pandas as pd

DIMENSIONS = {'region': 'region', 'issue': 'issue', 'age': 'age_band', 'channel': 'channel', 'triage': 'triage', 'referral': 'referral', 'outcome': 'outcome'}

def answer(question, frame):
    q = question.casefold().strip()
    if not q:
        return 'Ask a question about trends, regions, issues, referrals, or outcomes.', None
    if frame.empty:
        return 'No interactions match the current filters.', None
    if any(w in q for w in ('month', 'trend', 'season', 'over time', 'weekly')):
        s = frame.copy()
        s['month'] = pd.to_datetime(s.created_at).dt.to_period('M').astype(str)
        grouped = s.groupby('month').size().reset_index(name='interactions').sort_values('month')
        peak = grouped.loc[grouped.interactions.idxmax()]
        return f'Across {len(frame):,} filtered interactions, the busiest month is {peak["month"]} with {int(peak["interactions"]):,} contacts. The chart shows monthly contact volume, not population-adjusted rates.', grouped
    if any(w in q for w in ('follow-up', 'follow up', 'followup')):
        pct = 100*frame.follow_up.mean()
        by = frame.groupby('triage')['follow_up'].agg(['sum','count']).reset_index()
        by['follow_up_rate_%']=(100*by['sum']/by['count']).round(1)
        return f'{int(frame.follow_up.sum()):,} of {len(frame):,} contacts ({pct:.1f}%) were flagged for follow-up in this fictional dataset.', by[['triage','count','follow_up_rate_%']]
    if any(w in q for w in ('response time', 'respond', 'hours', 'speed')):
        grouped=frame.groupby('channel').response_hours.agg(['median','count']).round(1).reset_index().rename(columns={'median':'median_hours', 'count':'contacts'})
        return f'The overall median first response time is {frame.response_hours.median():.1f} hours. Medians by channel are below.', grouped
    if any(w in q for w in ('urgent', 'high priority', 'escalat')):
        n=int((frame.triage=='Urgent').sum())
        grouped=frame.groupby('region').apply(lambda x: (x.triage=='Urgent').sum(),include_groups=False).reset_index(name='urgent_contacts').sort_values('urgent_contacts', ascending=False)
        return f'{n:,} contacts ({100*n/len(frame):.1f}%) were classified as urgent. These are simulated triage labels, not clinical diagnoses.', grouped.head(10)
    keyword_map = {'region':['region','county','area','location','where'], 'issue':['issue','need','reason','problem','concern','common'], 'age':['age','young','older','demographic'], 'channel':['channel','phone','chat','email','web'], 'triage':['triage','priority','severity'], 'referral':['referral','referred','service'], 'outcome':['outcome','resolved','resolution','result']}
    dimension = next((d for d,words in keyword_map.items() if any(w in q for w in words)), 'issue')
    col=DIMENSIONS[dimension]
    grouped=frame.groupby(col).size().sort_values(ascending=False).reset_index(name='contacts')
    leader=grouped.iloc[0]
    return f'For {len(frame):,} filtered contacts, the largest {dimension} group is {leader[col]} with {int(leader.contacts):,} interactions ({100*leader.contacts/len(frame):.1f}%). These are counts, not causal conclusions.', grouped.head(12)
