import os
from dotenv import load_dotenv
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from .models import Assessment, JournalEntry
from textblob import TextBlob
import openai

# 🌱 Load environment variables
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =======================
# 🔐 Authentication Views
# =======================

def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

# ============================
# 🧠 Mental Health Assessment
# ============================

from .models import MentalHealthResponse  # Make sure this is imported at the top

@login_required
def assessment_view(request):
    questions = {
        1: "Over the last two weeks, how often have you felt little interest or pleasure in doing things?",
        2: "How often have you felt down, depressed, or hopeless?",
        3: "How often have you had trouble sleeping (too much or too little)?",
        4: "How often have you felt tired or had little energy?",
        5: "How often have you felt bad about yourself or felt like a failure?",
        6: "How often have you had trouble concentrating on things?",
        7: "How often have you felt anxious or worried?",
        8: "How often have you felt restless or unable to sit still?",
        9: "How often have you experienced feelings of worthlessness?",
        10: "How often have you thought about hurting yourself or others?",
    }

    options = [
        (0, "Not at all"),
        (1, "Several days"),
        (2, "More than half the days"),
        (3, "Nearly every day")
    ]

    if request.method == 'POST':
        total_score = sum(int(request.POST.get(f'q{q_num}', 0)) for q_num in questions)

        # ✅ Save detailed responses
        MentalHealthResponse.objects.create(
            user=request.user,
            q1=int(request.POST.get('q1')),
            q2=int(request.POST.get('q2')),
            q3=int(request.POST.get('q3')),
            q4=int(request.POST.get('q4')),
            q5=int(request.POST.get('q5')),
            q6=int(request.POST.get('q6')),
            q7=int(request.POST.get('q7')),
            q8=int(request.POST.get('q8')),
            q9=int(request.POST.get('q9')),
            q10=int(request.POST.get('q10')),
            total_score=total_score
        )

        return redirect('result', score=total_score)

    return render(request, 'assessment.html', {'questions': questions, 'options': options})

@login_required
def result_view(request, score):
    score = int(score)
    request.session['last_score'] = score  # For dashboard

    # Save to DB
    Assessment.objects.create(user=request.user, score=score)

    if score <= 10:
        message = "You seem to be doing well. Keep taking care of your mental health!"
        ai_tip = "Maintain your mental health by journaling, staying active, and nurturing connections with friends or family."
    elif 11 <= score <= 20:
        message = "You might be experiencing some challenges. Consider talking to someone about how you're feeling."
        ai_tip = "Try taking short breaks, deep breathing exercises, or speaking with a trusted friend. You’re not alone."
    else:
        message = "It's important to seek help. Please consider reaching out to a mental health professional."
        ai_tip = "Consider seeking professional support. In the meantime, prioritize rest, limit social media, and be kind to yourself."

    return render(request, 'result.html', {
        'score': score,
        'message': message,
        'ai_tip': ai_tip
    })

# =======================
# 📓 Journal View
# =======================

@login_required
def journal_entry(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity
        subjectivity = analysis.sentiment.subjectivity

        JournalEntry.objects.create(
            user=request.user,
            text=text,
            polarity=polarity,
            subjectivity=subjectivity
        )
        return redirect('journal')

    entries = JournalEntry.objects.filter(user=request.user).order_by('created_at')

    for entry in entries:
        if entry.polarity < -0.3:
            entry.mood_class = "bg-danger text-white"
        elif entry.polarity > 0.3:
            entry.mood_class = "bg-success text-white"
        else:
            entry.mood_class = "bg-warning"

    labels = [entry.created_at.strftime('%b %d') for entry in entries]
    data = [entry.polarity for entry in entries]

    show_resources = entries.exists() and entries.last().polarity < -0.5

    # AI Tip or Static Tip
    ai_tip = "Take deep breaths and go for a short walk — even small actions help improve mood."

    return render(request, 'journal.html', {
        'entries': entries,
        'labels': labels,
        'data': data,
        'show_resources': show_resources,
        'ai_tip': ai_tip,
    })

# =======================
# 📊 Dashboard View
# =======================

@login_required
def dashboard(request):
    entries = JournalEntry.objects.filter(user=request.user).order_by('created_at')
    labels = [entry.created_at.strftime('%b %d') for entry in entries]
    data = [entry.polarity for entry in entries]
    total_entries = entries.count()
    avg_polarity = entries.aggregate(avg=Avg('polarity'))['avg'] or 0
    latest_polarity = entries.last().polarity if entries.exists() else None

    assessments = Assessment.objects.filter(user=request.user).order_by('taken_at')
    assess_labels = [a.taken_at.strftime('%b %d') for a in assessments]
    assess_scores = [a.score for a in assessments]
    last_score = assessments.last().score if assessments.exists() else None

    if last_score is None:
        assessment_msg = "You haven't taken the assessment yet. Try it now!"
    elif last_score <= 10:
        assessment_msg = "You seem to be doing well. Keep taking care of your mental health!"
    elif 11 <= last_score <= 20:
        assessment_msg = "You might be facing some challenges. Consider talking to someone about how you're feeling."
    else:
        assessment_msg = "It's important to seek help. Please consider reaching out to a mental health professional."

    return render(request, 'dashboard.html', {
        'labels': labels,
        'data': data,
        'total_entries': total_entries,
        'avg_polarity': avg_polarity,
        'latest_polarity': latest_polarity,
        'assess_labels': assess_labels,
        'assess_scores': assess_scores,
        'last_score': last_score,
        'assessment_msg': assessment_msg,
    })

# =======================
# 🤖 Chatbot View
# =======================

@login_required
def chatbot_view(request):
    response = None
    user_message = None

    if request.method == 'POST':
        user_message = request.POST.get('message')

        system_prompt = (
            "You are a compassionate and supportive mental health assistant. "
            "You do not give medical advice or diagnoses. Your job is to respond gently "
            "to user inputs with affirmations, suggestions, or emotional support."
        )

        try:
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=200,
                temperature=0.7,
            )
            response = completion.choices[0].message.content.strip()
        except Exception as e:
            response = f"⚠️ Error communicating with AI: {e}"

    return render(request, 'chatbot.html', {
        'response': response,
        'user_message': user_message
    })
