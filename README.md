# Mental Health Tracker

A Django-based web application for tracking mental well-being through structured assessments, journal-based sentiment analysis, mood visualization, and an interactive mental health chatbot.

The project is designed as an educational and experimental platform that combines web development with natural language processing to help users record and understand changes in their emotional state over time.

## Features

### User Authentication

* User registration and login
* Session-based authentication
* Individual user data and activity

### Mental Health Assessment

* Structured questionnaire for mental health screening
* Automatic score calculation
* Result interpretation based on the obtained score
* Personalized feedback based on assessment results

### Mental Health Journal

* Users can record their thoughts and feelings
* Journal entries are stored for later review
* Text sentiment is analyzed using NLP
* Sentiment polarity is associated with each journal entry

### Mood Tracking

* Historical mood information is displayed through charts
* Journal sentiment can be tracked over time
* Dashboard provides a visual overview of recorded information

### Dashboard

The dashboard provides a centralized view of:

* Assessment results
* Journal activity
* Mood trends
* Historical assessment information

### Mental Health Chatbot

The application includes a conversational interface where users can enter messages such as:

* "I'm feeling sad"
* "I'm anxious"
* "Any tips?"
* "I'm not feeling well"

The chatbot provides general responses and guidance based on the user's input.

---

## Technology Stack

| Component       | Technology                 |
| --------------- | -------------------------- |
| Backend         | Python, Django             |
| Frontend        | HTML, CSS, Bootstrap       |
| Database        | SQLite                     |
| NLP             | TextBlob / NLTK            |
| Visualization   | Chart.js                   |
| Environment     | Python Virtual Environment |
| Version Control | Git & GitHub               |

---

## Project Structure

```text
mental-health-tracker/
│
├── manage.py
├── requirements.txt
├── .gitignore
│
├── detector/
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── mentalhealth/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── ...
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── dashboard.html
│   ├── journal.html
│   ├── assessment.html
│   ├── result.html
│   ├── chatbot.html
│   ├── login.html
│   └── signup.html
│
├── nltk_data/
│
└── Images:Output/
```

---

## Requirements

Before running the project, make sure you have:

* Python 3.x
* pip
* Git
* A web browser

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ruthvikreddyv/mental-health-tracker.git
cd mental-health-tracker
```

---

### 2. Create a Virtual Environment

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If the project requires additional NLP resources, install/download the required NLTK or TextBlob resources according to the packages used by the project.

---

## Environment Variables

The project uses an environment variable for the OpenAI API key.

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_api_key_here
```

**Never commit `.env` to GitHub.**

The repository includes `.env` in `.gitignore` to prevent API credentials from being uploaded.

---

## Database Setup

Apply Django migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Create an Administrator

To create a Django administrator account:

```bash
python manage.py createsuperuser
```

Follow the prompts to configure the account.

---

## Run the Application

Start the Django development server:

```bash
python manage.py runserver
```

Open the application in your browser:

```text
http://127.0.0.1:8000/
```

---

## Application Workflow

The typical workflow is:

```text
User
  │
  ▼
Registration / Login
  │
  ├───────────────┐
  ▼               ▼
Assessment       Journal
  │               │
  ▼               ▼
Score          NLP Sentiment
  │               │
  └───────┬───────┘
          ▼
       Dashboard
          │
          ▼
     Mood Tracking
          │
          ▼
       Chatbot
```

---

## NLP-Based Journal Analysis

Journal entries are processed using natural language processing techniques to estimate sentiment polarity.

The resulting sentiment information can be used to visualize changes in the user's recorded mood over time.

Sentiment analysis is intended as an indicative measure and should not be interpreted as a clinical diagnosis.

---

## Mental Health Assessment

The assessment component uses a structured questionnaire to calculate a score based on the user's responses.

The resulting score is presented with an interpretation and general feedback.

This assessment is intended for educational and informational purposes and is **not a substitute for a professional psychological or medical evaluation**.

---

## Security

The project follows basic practices for protecting application credentials:

* API keys are stored in environment variables
* `.env` is excluded from version control
* Python virtual environments are excluded from Git
* SQLite database files are excluded from Git
* Python cache files are excluded from Git

Before deploying the application publicly, additional production security measures should be implemented.

---

## Running in Development

For development, use:

```bash
python manage.py runserver
```

For debugging, Django's development tools can be used while developing locally.

Do not use Django's development server as the production deployment server.

---

## Limitations

The current system has several limitations:

* NLP sentiment analysis may not accurately capture complex emotional states.
* Text sentiment does not provide a clinical diagnosis.
* Chatbot responses are intended for general guidance rather than professional treatment.
* Assessment scores should not be interpreted as a definitive medical diagnosis.
* The application currently uses SQLite for local development.
* Production deployment would require additional security, scalability, and privacy considerations.

---

## Future Enhancements

Potential future improvements include:

* More advanced emotion classification
* Transformer-based NLP models
* Improved conversational AI
* Personalized mental well-being recommendations
* More detailed mood analytics
* Improved visualization of long-term trends
* Additional assessment instruments
* PostgreSQL or another production database
* Secure production deployment
* Role-based administration
* Improved privacy and data protection mechanisms
* Mobile application support

---

## Screens and Modules

The application contains interfaces for:

1. Home
2. User Registration
3. User Login
4. Mental Health Assessment
5. Assessment Results
6. Journal
7. Dashboard
8. Mental Health Chatbot

---

## Disclaimer

This project is intended for **educational, research, and demonstration purposes only**.

The Mental Health Tracker does not provide medical diagnosis, professional psychological assessment, treatment, or emergency assistance.

Users experiencing significant mental health difficulties should seek help from a qualified healthcare or mental health professional.

---

## Author

**Ruthvik Reddy**

GitHub:

https://github.com/ruthvikreddyv

Project Repository:

https://github.com/ruthvikreddyv/mental-health-tracker

---

## License

This project currently does not specify a license.

If the project is intended for public reuse, an appropriate open-source license can be added to the repository.
