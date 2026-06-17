# LessonForge AI

LessonForge AI is a Flask-based AI education web app that helps teachers generate classroom-ready instructional materials from a structured form.

Teachers can select the grade level, subject, topic, material type, difficulty level, class time, question types, and style preferences. The app then uses Google Gemini to generate clean, editable educational materials that are easier to copy, print, regenerate, or save as PDFs.

## What This Project Does

LessonForge AI can generate:

* Lesson plans
* Quizzes
* Tests
* Homework assignments
* Study guides
* Discussion questions
* Class activities

The goal is to turn a teacher’s structured inputs into practical, classroom-ready materials without requiring the teacher to write a long prompt from scratch.

## Current Features

* Structured form for selecting grade level, subject, topic, material type, difficulty, and tone
* Dynamic prompt-building based on the selected material type
* Google Gemini integration using `gemini-2.5-flash`
* Teacher-friendly Markdown output
* Markdown-to-HTML rendering for clean browser display
* Assessment-specific logic for quizzes, tests, and homework assignments
* Separate teacher lesson scope for assessments
* Separate student version and answer key sections
* Copy buttons for generated content
* Student PDF and answer key PDF options
* Regenerate button that resubmits the original form inputs
* Clean responsive UI with custom CSS
* Environment variable support with `.env`
* Local Flask development server

## Material-Specific Behavior

LessonForge AI does not use one generic prompt for every request. The backend builds different instructions depending on the material type selected.

### Lesson Plans

Lesson plans include structure for:

* Overview
* Learning objective
* Materials
* Warm-up / Do Now, if requested
* Direct instruction
* Guided practice
* Independent practice
* Assessment
* Exit ticket
* Teacher notes

### Quizzes, Tests, and Homework Assignments

Assessment-style materials include:

* A teacher-facing lesson scope
* A student-facing version
* Optional answer key
* Optional explanations
* Multiple choice, short answer, essay, or mixed question formats

The app also includes backend logic to prevent essay questions for Math and Science, where short answer, multiple choice, and problem-based questions are usually a better fit.

### Study Guides

Study guides are treated separately from assessments. They are designed to summarize and organize concepts rather than behave like quizzes or tests.

Study guides can include:

* Overview
* Key concepts
* Important vocabulary
* Core ideas to remember
* Examples
* Common mistakes or misconceptions
* Quick review checklist

### Class Activities

Class activities can include:

* Classroom games
* Group activities
* Role plays
* Debates
* Simulations
* Hands-on activities
* Discussion-based activities

The prompt asks Gemini to keep materials simple, low-cost, and realistic for classroom use.

### Discussion Questions

Discussion question outputs are formatted as teacher-ready prompts with optional follow-up questions.

## Tech Stack

* Python
* Flask
* Jinja2 templates
* Google Gemini API
* `google-genai`
* Markdown rendering
* HTML/CSS
* JavaScript
* Python dotenv
* SQLAlchemy / Flask-SQLAlchemy dependencies added for future database work
* PostgreSQL dependency added through `psycopg2-binary`

## Project Structure

```text
lesson-forge-ai/
├── app.py
├── requirements.txt
├── .env
├── .gitignore
├── templates/
│   ├── index.html
│   └── result.html
└── static/
    └── styles.css
```

## Environment Variables

Create a `.env` file in the root directory and add your Google API key:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

The `.env` file should not be committed to GitHub.

## How to Run Locally

Clone the repository:

```bash
git clone https://github.com/ravibkjoshi/lesson-forge-ai.git
cd lesson-forge-ai
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your `.env` file:

```bash
touch .env
```

Add your Google API key to `.env`:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

Run the Flask app:

```bash
python3 app.py
```

Open the app in your browser:

```text
http://localhost:5050
```

## What This Project Demonstrates

This project demonstrates how to build a practical AI-powered web app that combines a traditional Flask application with LLM-based content generation.

It shows experience with:

* Building a Flask web application
* Designing a structured user workflow
* Creating dynamic prompts based on form inputs
* Integrating Google Gemini into a Python app
* Rendering AI-generated Markdown as HTML
* Separating student-facing and teacher-facing outputs
* Handling environment variables securely
* Building a polished frontend with HTML, CSS, and Jinja templates
* Planning for future database-backed features with SQLAlchemy and PostgreSQL

## Planned Improvements

Planned next steps include:

* Add audience options for teachers, tutors, and homeschool parents
* Dynamically adjust activity options based on the selected audience
* Add PostgreSQL setup
* Add SQLAlchemy models
* Create a `SavedMaterial` model
* Add a Save Material button
* Add a Saved Materials page
* Add user accounts and login so each user has their own saved material library
* Make the repository private before storing real user-generated materials or account data

## Notes

This is an early-stage portfolio project. The current version focuses on generating useful classroom materials from structured form inputs. Future versions will add persistence, saved materials, and user-specific libraries.

## Why I Built This

I built LessonForge AI as a practical AI education tool and portfolio project. The goal was to show how a structured web app can use AI to produce useful, editable outputs instead of acting like a basic chatbot.

This project combines backend development, frontend form logic, API integration, prompt design, and user-focused output formatting into a working MVP.

## Disclaimer

LessonForge AI is intended to help teachers quickly draft educational materials. Generated content should be reviewed and edited by a teacher before being used in the classroom, especially for factual accuracy, grade-level fit, and school-specific requirements.
