# LessonForge AI

LessonForge AI is a Flask-based web app that helps teachers generate classroom-ready educational materials using AI.

Teachers can enter a grade level, subject, topic, difficulty, class time, material type, and optional instructions. The app then uses Google Gemini to generate structured teaching materials such as lesson plans, quizzes, tests, homework assignments, study guides, discussion questions, and class activities.

The goal of this MVP is to create a simple, practical tool that turns structured teacher inputs into editable, printable classroom content.

## Features

* Generate classroom-ready educational materials from a structured form
* Supports multiple material types:

  * Lesson plans
  * Quizzes
  * Tests
  * Homework assignments
  * Study guides
  * Discussion questions
  * Class activities
* Dynamic form sections based on the selected material type
* Gemini-powered content generation
* Prompt logic tailored to each material type
* Markdown rendering for cleaner generated output
* Copy-to-clipboard button for easy editing
* Browser-based PDF export
* Print/PDF formatting that separates the student-facing assignment from the answer key
* Clean, responsive UI built with HTML and CSS

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

This project demonstrates how a simple web application can use an AI model to generate useful, structured content from user inputs.

It shows:

* Building a Flask web app with multiple routes
* Creating dynamic forms with HTML and JavaScript
* Passing form data from the frontend to a Flask backend
* Building structured prompts based on user selections
* Calling the Google Gemini API from Python
* Rendering AI-generated Markdown as HTML
* Adding copy-to-clipboard functionality
* Adding browser-based PDF export
* Formatting printed/PDF output with CSS
* Separating answer keys from student-facing materials in PDF output

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

## How It Works

1. A teacher fills out the form on the homepage.
2. The form sends the teacher's selections to the Flask backend.
3. Flask builds a prompt based on the selected material type.
4. The app sends the prompt to Google Gemini.
5. Gemini returns classroom-ready educational content.
6. The app converts the Markdown response into formatted HTML.
7. The result page displays the generated content.
8. The teacher can copy the content or save it as a PDF.

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/lesson-forge-ai.git
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

```env
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

```env
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

This version uses Gemini directly from the Flask backend. It does not currently use Tavily or LangChain.

That was intentional for the MVP. The goal was to keep the app lightweight, reduce unnecessary token usage, and focus on the core workflow:

```text
Teacher input → AI generation → formatted classroom material → copy or PDF export
```

Future versions may add optional source-grounded generation using Tavily and LangChain for subjects or topics that benefit from reputable external sources.

## Future Improvements

Possible next steps:

* Add optional source-grounded generation using Tavily
* Add LangChain orchestration for retrieval and prompt routing
* Add user accounts and saved lesson history
* Add editable generated content before PDF export
* Add downloadable `.docx` support
* Add standards alignment options
* Add source citations for research-heavy topics
* Add templates for specific teaching formats
* Improve PDF layout with more advanced backend PDF generation

## Why I Built This

I built LessonForge AI as a practical AI education tool and portfolio project. The goal was to show how a structured web app can use AI to produce useful, editable outputs instead of acting like a basic chatbot.

This project combines backend development, frontend form logic, API integration, prompt design, and user-focused output formatting into a working MVP.

## Disclaimer

LessonForge AI is intended to help teachers quickly draft educational materials. Generated content should be reviewed and edited by a teacher before being used in the classroom, especially for factual accuracy, grade-level fit, and school-specific requirements.
