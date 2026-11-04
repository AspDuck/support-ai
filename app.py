"""Support AI | fictional Nova Scotia support intelligence demo."""
from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st
from generate_data import generate, DB
from insights import answer
from triage import classify

st.set_page_config(page_title='Support AI | Intelligence Studio', page_icon='◈', layout='wide', initial_sidebar_state='expanded')
st.markdown('''<style>
.stApp {background:#f7f9fc;color:#12253b}
.block-container {padding-top:1.5rem;max-width:1260px}
[data-testid="stMetric"] {background:white;border:1px solid #e5eaf1;padding:16px;border-radius:13px}
[data-testid="stSidebar"] {background:#edf3f9}
h1,h2,h3 {color:#102a43}
.kicker{letter-spacing:.13em;font-size:.78rem;font-weight:800;color:#287ea0;text-transform:uppercase}
.hero{padding:18px 24px;border-radius:16px;background:linear-gradient(115deg,#0c304c,#166986);color:white;margin-bottom:16px}
.hero h1{color:white;margin:2px 0;font-size:2.2rem}
.hero p{color:#d3e7f1;margin:0}
.notice{background:#eaf4f8;border-left:4px solid #1383a0;padding:11px 14px;border-radius:4px;font-size:.88rem;margin-bottom:15px}
</style>''',unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_data():
    if not DB.exists():
        generate()
    with sqlite3.connect(DB) as conn:
        df = pd.read_sql_query('SELECT * FROM interactions',conn)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['month'] = df.created_at.dt.to_period('M').astype(str)
    return df

raw = load_data()
st.sidebar.markdown('## ◈ Support AI')
st.sidebar.caption('Nova Scotia · Intelligence Studio')
st.sidebar.divider()
st.sidebar.markdown('**Explore the data**')
selected_regions=st.sidebar.multiselect('Regions', sorted(raw.region.unique()),default=[])
selected_issues=st.sidebar.multiselect('Support needs',sorted(raw.issue.unique()),default=[])
selected_channels=st.sidebar.multiselect('Channels',sorted(raw.channel.unique()),default=[])
selected_triage=st.sidebar.multiselect('Priority',sorted(raw.triage.unique()),default=[])
date_range=st.sidebar.date_input('Date range', value=(raw.created_at.min().date(),raw.created_at.max().date()), min_value=raw.created_at.min().date(),max_value=raw.created_at.max().date())
st.sidebar.divider()
st.sidebar.caption('DEMO DATA ONLY · 10,000 simulated interactions · No real client information.')

filtered=raw.copy()
for col,values in [('region',selected_regions),('issue',selected_issues),('channel',selected_channels),('triage',selected_triage)]:
    if values: filtered=filtered[filtered[col].isin(values)]
if len(date_range)==2:
    filtered=filtered[(filtered.created_at.dt.date >= date_range[0])&(filtered.created_at.dt.date <= date_range[1])]

st.markdown('''<div class="hero"><div class="kicker" style="color:#80d6e8">PORTFOLIO DEMONSTRATION</div>
<h1>Support Intelligence Studio</h1><p>See the patterns. Ask better questions. Route the right response.</p></div>''',unsafe_allow_html=True)
st.markdown('<div class="notice">All interactions are fictional and generated for demonstration. Insights describe only this sample and should never be interpreted as real Nova Scotia health statistics.</div>',unsafe_allow_html=True)
tab1,tab2,tab3,tab4=st.tabs(['📊 Overview','💬 Ask the data','🧭 Ticket triage','ℹ️ About the demo'])
with tab1:
    st.subheader('Support operations at a glance')
    a,b,c,d=st.columns(4)
    a.metric('Contacts',f'{len(filtered):,}')
    b.metric('Urgent classification',f'{100*(filtered.triage=="Urgent").mean():.1f}%' if len(filtered) else 'N/A')
    c.metric('Follow-up flagged',f'{100*filtered.follow_up.mean():.1f}%' if len(filtered) else 'N/A')
    d.metric('Median response',f'{filtered.response_hours.median():.1f} h' if len(filtered) else 'N/A')
    if filtered.empty:
        st.info('No records match the filters. Widen the selected date range or remove a filter.')
    else:
        left,right=st.columns([1.45,1])
        with left:
            st.markdown('#### Monthly contact volume')
            st.line_chart(filtered.groupby('month').size().rename('Contacts'),height=280)
        with right:
            st.markdown('#### Top support needs')
            st.bar_chart(filtered.issue.value_counts().head(7),horizontal=True,height=280)
        left,right=st.columns(2)
        with left:
            st.markdown('#### Regional contacts')
            st.bar_chart(filtered.region.value_counts().head(8),horizontal=True,height=280)
        with right:
            st.markdown('#### Referral destinations')
            st.bar_chart(filtered.referral.value_counts().head(8),horizontal=True,height=280)
        with st.expander('View anonymized sample rows and download CSV'):
            cols=['id','created_at','region','age_band','channel','issue','triage','referral','outcome','response_hours']
            st.dataframe(filtered[cols].head(150),use_container_width=True,hide_index=True)
            st.download_button('Download filtered dataset', filtered[cols].to_csv(index=False).encode('utf-8'), 'support-ai-filtered.csv','text/csv')
with tab2:
    st.subheader('Ask the data')
    st.write('Ask a question in everyday language. Answers are computed from the filtered synthetic records, not invented by a language model.')
    question=st.text_input('Your question',placeholder='Which support needs are most common?')
    examples=['Which issues are most common?','How did contact volume trend by month?','What is the urgent case volume?','How many contacts need follow-up?','What is the median response time by channel?','Which regions have the most contacts?']
    selection=st.selectbox('Or try a sample question', ['Choose an example…']+examples)
    if st.button('Get insight',type='primary',use_container_width=True):
        chosen=question.strip() or (selection if selection!= 'Choose an example…' else '')
        summary, table=answer(chosen, filtered)
        st.markdown('#### Answer')
        st.write(summary)
        if table is not None:
            st.dataframe(table,use_container_width=True,hide_index=True)
            if len(table) and len(table.columns)>1 and pd.api.types.is_numeric_dtype(table.iloc[:,1]):
                st.bar_chart(table.set_index(table.columns[0]).iloc[:,0],horizontal=True)
    st.caption('Safety by design: supported questions map to fixed Python aggregations; the app does not execute AI-generated SQL.')
with tab3:
    st.subheader('Support ticket triage & reply drafting')
    st.write('Paste a fictional incoming message to see a proposed priority, ownership route, and editable draft. Every draft requires human review.')
    presets={
        'Account access': 'I cannot log in to my account. I keep receiving a password reset error.',
        'Referral question': 'I am looking for a counsellor but I am not sure what services I am eligible for.',
        'Urgent safety example': 'I am thinking about suicide and I cannot stay safe tonight.',
    }
    choice=st.selectbox('Sample tickets',['Write my own']+list(presets))
    message=st.text_area('Incoming support ticket',value=presets.get(choice,''),height=130,placeholder='Describe a fictional support issue…')
    if st.button('Analyze ticket',type='primary',use_container_width=True):
        if not message.strip():
            st.warning('Enter a ticket message first.')
        else:
            result=classify(message)
            c1,c2,c3=st.columns(3)
            c1.metric('Suggested priority',result['priority'])
            c2.metric('Category',result['category'])
            c3.metric('Suggested owner',result['route'])
            if result['signal']:
                st.error('Safety-related wording detected. Escalate to a trained human immediately. This demo cannot handle emergencies.')
            st.markdown('#### Suggested reply (edit before use)')
            st.text_area('Draft for human review',result['draft'],height=160,key='draft_reply')
            st.warning('Human approval required. No message has been sent and no ticket was created.')
    st.caption('Keyword-based triage is intentionally transparent and imperfect. It cannot replace a trained professional or crisis assessment.')
with tab4:
    st.subheader('What this prototype demonstrates')
    st.markdown('''**Tool 1: Support intelligence.** Explore 10,000 fictional Nova Scotia support contacts, filter operational metrics, and ask grounded natural-language questions.\n\n**Tool 2: Ticket intelligence.** Classify a support request, suggest a queue and produce a human-reviewed reply.\n\n**Design decisions:** privacy-first synthetic data, no embedded credentials, no AI-generated database queries, clear safety escalation, and no automatic outbound replies.\n\n**Technology:** Python, Streamlit, SQLite, pandas. No external API or paid service required for the core demonstration.''')
    st.info('This is a portfolio proof of concept, not a clinical system, medical device, or production help desk.')
