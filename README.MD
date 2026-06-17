# LessonForge AI

LessonForge AI is a Flask-based web app that helps instructors, tutors, and homeschool parents generate classroom-ready and learning-ready educational materials using Google Gemini.

Users can select an audience type, grade level, subject, topic, difficulty, material type, and optional instructions. The app then generates structured educational materials such as lesson plans, quizzes, tests, homework assignments, study guides, discussion questions, and class activities.

The goal of this MVP is to create a simple, practical tool that turns structured educational inputs into editable, printable learning materials.

## Features

* Generate educational materials from a structured form
* Audience-aware generation for:

  * Instructors
  * Tutors
  * Homeschool parents
* Dynamic form sections based on selected material type
* Frontend options adjust based on selected audience
* Conditional backend prompt logic to reduce unnecessary prompt bloat
* Google Gemini-powered content generation
* Markdown rendering for clean generated output
* Copy-to-clipboard actions for generated materials
* Browser-based PDF/print workflow
* Separate student-facing and instructor-facing assessment output
* Lesson Scope section for quizzes, tests, and homework assignments
* Student Version and Answer Key separation
* Printable answer spaces for student assessments

  * Lined space for short answer responses
  * Larger lined space for essay responses
  * Blank workspace for math, science, and problem-solving questions
* Responsive HTML/CSS interface

## Supported Material Types

LessonForge AI currently supports:

* Lesson plans
* Quizzes
* Tests
* Homework assignments
* Study guides
* Discussion questions
* Class activities

## Assessment Output Flow

For quizzes, tests, and homework assignments, LessonForge AI separates the output into three sections:

1. **Lesson Scope**
   Gives the instructor, tutor, or homeschool parent context about what students are expected to know before completing the assessment.

2. **Student Version**
   Student-facing questions or assignment content, without answers.

3. **Answer Key**
   Instructor-facing answers, explanations, or grading guidance.

This keeps printable student materials clean while still giving the educator useful context and answer support.

## Audience-Aware Generation

The app supports different educational use cases through an audience selector.

### Instructor

Uses classroom-oriented language and supports classroom-style materials, group activities, and traditional instructional workflows.

### Tutor

Uses language better suited for one-on-one or small-group instruction.

### Homeschool Parent

Uses home-friendly language, simpler materials, and avoids unnecessary classroom assumptions when possible.

The prompt instructions are conditionally added based on the selected audience instead of sending one large generic prompt every time. This keeps the prompts more focused and helps reduce unnecessary token usage.

## Tech Stack

* Python
* Flask
* Google Gemini API
* HTML
* CSS
* JavaScript
* Markdown
* python-dotenv

## What This Project Demonstrates

This project demonstrates how a structured web application can use an AI model to generate useful, editable educational materials from form-based user inputs.

It shows:

* Building a Flask web app with multiple routes
* Creating dynamic forms with HTML and JavaScript
* Passing form data from the frontend to a Flask backend
* Building conditional prompts based on user selections
* Optimizing prompt logic by material type and audience
* Calling the Google Gemini API from Python
* Rendering AI-generated Markdown as HTML
* Splitting AI output into separate educator and student sections
* Adding copy-to-clipboard functionality
* Adding browser-based PDF export
* Formatting printable outputs with CSS
* Creating a practical AI workflow beyond a basic chatbot

## Project Structure

```text
lesson-forge-ai/
├── app.py
├── requirements.txt
├── .gitignore
├── templates/
│   ├── index.html
│   └── result.html
└── static/
    └── styles.css
```

## How It Works

1. A user fills out the form on the homepage.
2. The user selects an audience, grade level, subject, topic, difficulty, and material type.
3. The frontend shows or hides fields based on the selected material type and audience.
4. Flask receives the submitted form data.
5. Flask builds a structured prompt based on the selected inputs.
6. The app sends the prompt to Google Gemini.
7. Gemini returns educational content in Markdown.
8. Flask splits assessment output into lesson scope, student version, and answer key when needed.
9. The app converts the Markdown response into formatted HTML.
10. The user can copy the content or save printable sections as PDFs.

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/ravibkjoshi/lesson-forge-ai.git
cd lesson-forge-ai
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the virtual environment

On macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 5. Create a `.env` file

Create a `.env` file in the root folder and add your Google API key:

```bash
GOOGLE_API_KEY=your_google_api_key_here
```

### 6. Run the app

```bash
python3 app.py
```

Then open:

```text
http://localhost:5050
```

## Environment Variables

This project uses `python-dotenv` to load environment variables from a local `.env` file.

Required variable:

```bash
GOOGLE_API_KEY=your_google_api_key_here
```

The `.env` file should not be committed to GitHub.

## Requirements

The project dependencies are listed in `requirements.txt`:

```text
google-genai
python-dotenv
flask
markdown
```

## MVP Notes

This public MVP uses Gemini directly from the Flask backend.

It does not currently use Tavily, LangChain, PostgreSQL, SQLAlchemy, user accounts, or saved materials. That is intentional for the public MVP. The goal is to keep the app lightweight and focus on the core workflow:

```text
Structured input → AI generation → formatted educational material → copy or PDF export
```

Future versions may add source-grounded generation, saved material libraries, user accounts, and database persistence after the repository is made private.

## Current Limitations

* Generated content should be reviewed before use with students.
* PDF export currently uses the browser print flow.
* Browser print settings may add headers or footers unless disabled in the print dialog.
* Generated content is not currently saved to a database.
* There are no user accounts or saved libraries yet.
* Source-grounded generation with Tavily and LangChain is planned for a later private-repo version.

## Future Improvements

Planned next steps:

* Switch the repository private before database and user-account work
* Add optional source-grounded generation using Tavily
* Add LangChain orchestration for retrieval and prompt routing
* Add source notes or reference sources for research-heavy topics
* Add PostgreSQL
* Add SQLAlchemy
* Add saved materials
* Add user accounts and login
* Connect saved materials to individual user accounts
* Improve PDF generation with a backend PDF workflow
* Add editable generated content before export
* Add downloadable `.docx` support
* Add stronger standards alignment options

## Why I Built This

I built LessonForge AI as a practical AI education tool and portfolio project. The goal was to show how a structured web app can use AI to produce useful, editable outputs instead of acting like a basic chatbot.

This project combines backend development, frontend form logic, API integration, prompt design, conditional UX behavior, and user-focused output formatting into a working MVP.

## Disclaimer

LessonForge AI is intended to help instructors, tutors, and homeschool parents quickly draft educational materials. Generated content should be reviewed and edited before being used with students, especially for factual accuracy, grade-level fit, accessibility, and institution-specific requirements.
