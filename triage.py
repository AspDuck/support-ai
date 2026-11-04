"""Demonstration support triage. Never used for clinical decision-making."""
import re

HIGH_RISK = ['suicide','suicidal','kill myself','self harm','self-harm','overdose','immediate danger','hurt myself','can’t stay safe',"can't stay safe"]
ELEVATED = ['eviction','homeless','no place to stay','panic attack','can’t afford food',"can't afford food",'withdrawal','urgent','unsafe']
ROUTES = {
    'Account / access': ['password','login','log in','locked out','sign in','account','verification'],
    'Referral / eligibility': ['eligible','eligibility','referral','counsellor','counselor','therapy','service'],
    'Scheduling': ['appointment','schedule','booking','reschedule','availability'],
    'Billing / financial': ['invoice','charge','bill','payment','insurance','cost','afford'],
    'Technical issue': ['error','bug','broken','not loading','website','app','crash','link']
}

def classify(text):
    value = text.casefold().strip()
    signals = [phrase for phrase in HIGH_RISK if phrase in value]
    urgency = 'Immediate human escalation' if signals else ('Elevated review' if any(term in value for term in ELEVATED) else 'Standard queue')
    category = next((k for k,terms in ROUTES.items() if any(re.search(r'(?<!\w)'+re.escape(term)+r'(?!\w)',value) for term in terms)), 'General support')
    route = 'Safety lead / trained responder' if signals else ('Senior support specialist' if urgency=='Elevated review' else ('Account support' if category=='Account / access' else 'Support operations'))
    if signals:
        reply = ('Thank you for reaching out. I’m concerned about your immediate safety, and I’m escalating this to a trained member of our team now. '
                 'If you are in immediate danger, call local emergency services. In Canada, you can call or text 988 for suicide crisis support. '
                 'Please do not rely on this demo for emergency assistance.')
    else:
        reply = ('Thanks for contacting our support team. I understand you need help with '+ category.lower()+'. '
                 'I’ve noted your request and will direct it to the appropriate team for review. '
                 'Could you share any relevant details, such as when this started and what you have already tried? '
                 'We’ll review the information before sending a response.')
    return {'priority':urgency, 'category':category, 'route':route,'review_required':True,'draft':reply,'signal': bool(signals)}
