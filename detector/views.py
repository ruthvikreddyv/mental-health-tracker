"""Privacy-aware views; the original 10-item form is not a validated clinical instrument."""
import logging
import os
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404,redirect,render
from django.views.decorators.http import require_POST
from textblob import TextBlob
from .forms import CheckinForm,JournalForm,SignupForm,SigninForm
from .models import Assessment,JournalEntry,MentalHealthResponse
logger=logging.getLogger(__name__)
QUESTIONS=[
    'Had little interest or pleasure in doing things?',
    'Felt down, sad, or hopeless?',
    'Had difficulty sleeping, or slept much more than usual?',
    'Felt tired or lacked energy?',
    'Felt disappointed in yourself or overly self-critical?',
    'Had difficulty concentrating?',
    'Felt anxious, tense, or worried?',
    'Felt unusually restless or unable to sit still?',
    'Felt worthless or disconnected from others?',
    'Had thoughts about harming yourself or someone else?',
]

def enabled():return settings.PERSISTENT_STORAGE_ENABLED

def screen(request,page,**context):return render(request,'detector/screen.html',{'page':page,**context})

def home(request):return screen(request,'home')

def demo(request):return render(request,'detector/demo.html',{'questions':QUESTIONS})

def health(request):return JsonResponse({'status':'ok','storage_configured':enabled()})

def signup(request):
    if not enabled():return redirect('demo')
    form=SignupForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        with transaction.atomic():
            user=form.save()
            login(request,user)
        return redirect('dashboard')
    return screen(request,'signup',form=form)

def signin(request):
    if not enabled():return redirect('demo')
    return LoginView.as_view(template_name='detector/screen.html',authentication_form=SigninForm,extra_context={'page':'login'})(request)

@require_POST
def signout(request):
    if enabled():logout(request)
    return redirect('home')

@login_required
def assessment_view(request):
    if not enabled():return redirect('demo')
    form=CheckinForm(QUESTIONS,request.POST or None)
    if request.method=='POST' and form.is_valid():
        answers=[form.cleaned_data[f'q{i}'] for i in range(1,11)]
        with transaction.atomic():
            response=MentalHealthResponse.objects.create(user=request.user,total_score=sum(answers),**{f'q{i}':v for i,v in enumerate(answers,1)})
            Assessment.objects.create(user=request.user,score=response.total_score)
        return redirect('result',response_id=response.id)
    return screen(request,'assessment',questions=[(i,q,form[f'q{i}']) for i,q in enumerate(QUESTIONS,1)],form=form)

@login_required
def result_view(request,response_id):
    if not enabled():return redirect('demo')
    response=get_object_or_404(MentalHealthResponse,pk=response_id,user=request.user)
    return screen(request,'result',response=response,urgent=response.q10>0)

@login_required
def journal_entry(request):
    if not enabled():return redirect('demo')
    form=JournalForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        text=form.cleaned_data['text'].strip()
        if text:
            sentiment=TextBlob(text).sentiment
            JournalEntry.objects.create(user=request.user,text=text,polarity=sentiment.polarity,subjectivity=sentiment.subjectivity)
            messages.success(request,'Reflection saved.')
            return redirect('journal')
        form.add_error('text','Write a few words before saving.')
    entries=JournalEntry.objects.filter(user=request.user).order_by('-created_at')[:100]
    return screen(request,'journal',entries=entries,form=form)

@login_required
@require_POST
def journal_delete(request,entry_id):
    if not enabled():return redirect('demo')
    get_object_or_404(JournalEntry,pk=entry_id,user=request.user).delete()
    messages.success(request,'Reflection deleted.')
    return redirect('journal')

@login_required
def dashboard(request):
    if not enabled():return redirect('demo')
    e=list(JournalEntry.objects.filter(user=request.user).order_by('created_at'))
    a=list(Assessment.objects.filter(user=request.user).order_by('taken_at'))
    return screen(request,'dashboard',total_entries=len(e),avg_polarity=sum(x.polarity for x in e)/len(e) if e else None,
        last_score=a[-1].score if a else None,
        mood_labels=[x.created_at.strftime('%d %b') for x in e],mood_values=[round(x.polarity,3) for x in e],
        checkin_labels=[x.taken_at.strftime('%d %b') for x in a],checkin_values=[x.score for x in a],
        recent_entries=list(reversed(e[-3:])))

@login_required
def chatbot_view(request):
    if not enabled():return redirect('demo')
    response=None
    message=''
    configured=bool(os.getenv('OPENAI_API_KEY'))
    if request.method=='POST':
        message=request.POST.get('message','').strip()[:1000]
        if not message:response='Please enter a message.'
        elif any(x in message.lower() for x in ('kill myself','hurt myself','suicide','end my life','hurt someone')):
            response=('If you may act on thoughts of harm, contact local emergency services immediately and reach a trusted person who can stay with you. A qualified professional can help.')
        elif not configured:
            response=('Live AI support is not configured. Consider writing down your feelings, taking a short break, or connecting with someone you trust. For ongoing concerns, speak with a qualified professional.')
        else:
            try:
                from openai import OpenAI
                client=OpenAI(api_key=os.environ['OPENAI_API_KEY'],timeout=12)
                completion=client.chat.completions.create(model=os.getenv('OPENAI_MODEL','gpt-4o-mini'),messages=[
                    {'role':'system','content':'Offer supportive, brief, non-diagnostic guidance, never imply you are a clinician, and encourage qualified professional support and immediate emergency support for safety concerns. Do not provide medical advice.'},
                    {'role':'user','content':message}],max_tokens=180,temperature=.5)
                response=completion.choices[0].message.content
            except Exception:
                logger.exception('Chat provider unavailable')
                response='The assistant is temporarily unavailable. Please try again later.'
    return screen(request,'chatbot',message=message,response=response,ai_configured=configured)
