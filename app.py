import os
import re
import markdown

from dotenv import load_dotenv
from flask import Flask, render_template, request
from google import genai


load_dotenv()

app = Flask(__name__)

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


SYSTEM_PROMPT = """
You are LessonForge AI, an assistant that creates classroom-ready educational materials for teachers.

Follow these rules:

1. Use the teacher's selected grade level, subject, topic, material type, difficulty, class time, and instructions.
2. Keep the output practical, clear, age-appropriate, and easy for a teacher to copy and edit.
3. Do not invent citations or URLs.
4. Before creating a quiz, test, homework assignment, or study guide, define a brief lesson scope showing the key concepts students are expected to know.
5. Assessment questions must only test concepts included in the lesson scope or explicitly mentioned by the teacher.
6. For quizzes and tests, include answer keys when requested.
7. For multiple choice questions, provide four answer choices labeled A-D and only one correct answer.
8. For essay questions, make sure students could reasonably answer using the lesson scope.
9. For class activities, include simple materials teachers can easily procure, such as paper, index cards, markers, sticky notes, posters, dice, or printable handouts.
10. Do not include unnecessary explanation about how you generated the material.
11. Use clean Markdown formatting with headings, numbered lists, and bullet points.
12. Do not use LaTeX math formatting.
13. Do not wrap formulas or equations in dollar signs.
14. Do not use LaTeX commands such as \\text{}, \\frac{}, \\rightarrow, ^, _, or H$_2$.
15. For chemical formulas and equations, use readable Unicode/plain text formatting such as H₂O, CO₂, NaCl, and 2H₂ + O₂ → 2H₂O.
16. For math formulas, use readable plain text or Unicode formatting such as x = (-b ± √(b² - 4ac)) / 2a.
17. Do not overuse complex notation for lower grade levels.
"""


def build_generation_prompt(form_data):
    material_type = form_data.get("material_type")

    prompt_sections = [
        "Create the following classroom-ready educational material.",
        "",
        f"Grade Level: {form_data.get('grade_level')}",
        f"Subject: {form_data.get('subject')}",
        f"Topic: {form_data.get('topic')}",
        f"Material Type: {material_type}",
        f"Difficulty: {form_data.get('difficulty')}",
        f"Tone: {form_data.get('tone')}",
        f"Additional Instructions: {form_data.get('additional_instructions') or 'None provided.'}",
        "",
    ]

    if material_type == "Lesson Plan":
        prompt_sections.extend([
            "Lesson Plan Requirements:",
                    f"Estimated Class Time: {form_data.get('lesson_length')}",
            f"Learning Objective: {form_data.get('learning_objective') or 'Generate an appropriate learning objective based on the topic.'}",
            f"Include Warm-Up / Do Now: {form_data.get('include_warmup')}",
            f"Include Exit Ticket: {form_data.get('include_exit_ticket')}",
            f"Standards Alignment: {form_data.get('standards_alignment')}",
            "",
            "Format the lesson plan with sections for overview, learning objective, materials, warm-up if requested, direct instruction, guided practice, independent practice, assessment, exit ticket if requested, and teacher notes.",
            "",
        ])

    if material_type in ["Quiz", "Test", "Homework Assignment", "Study Guide"]:
        prompt_sections.extend([
            "Assessment Requirements:",
            f"Question Type: {form_data.get('question_type')}",
            f"Multiple Choice Count: {form_data.get('multiple_choice_count')}",
            f"Essay Question Count: {form_data.get('essay_count')}",
            f"Short Answer Count: {form_data.get('short_answer_count')}",
            f"Include Answer Key: {form_data.get('include_answer_key')}",
            f"Include Explanations: {form_data.get('include_explanations')}",
            "",
            "Before writing the questions, include a brief 'Lesson Scope' section that lists the specific concepts students are expected to have learned.",
            "Only write questions that are answerable from that Lesson Scope.",
            "Do not test obscure facts, advanced concepts, or material outside the selected grade level unless the teacher specifically requested it.",
            "If multiple choice questions are requested, each question must have A-D answer choices and one correct answer.",
            "If essay questions are requested, include a suggested answer or grading guidance when answer keys are requested.",
            "If an answer key is requested, start it with the exact Markdown heading: ## Answer Key",
            "Do not place the answer key before the student-facing assignment.",
            "",
        ])

    if material_type == "Class Activity":
        prompt_sections.extend([
            "Class Activity Requirements:",
                    f"Estimated Class Time: {form_data.get('lesson_length')}",
            f"Activity Style: {form_data.get('activity_style')}",
            f"Materials Preference: {form_data.get('materials_preference')}",
            f"Activity Goal: {form_data.get('activity_goal') or 'Generate an appropriate activity goal based on the topic.'}",
            f"Include Reflection Questions: {form_data.get('include_reflection')}",
            "",
            "Format the activity with sections for overview, learning objective, time needed, materials needed, teacher setup, step-by-step activity instructions, student instructions, discussion/reflection questions if requested, and a quick assessment or exit ticket.",
            "Generate the materials needed yourself. Keep them simple, low-cost, and easy for teachers to procure.",
            "",
        ])

    if material_type == "Discussion Questions":
        prompt_sections.extend([
            "Discussion Requirements:",
            f"Number of Discussion Questions: {form_data.get('discussion_count')}",
            f"Discussion Style: {form_data.get('discussion_style')}",
            "",
            "Format the output as teacher-ready discussion prompts with optional follow-up questions.",
            "",
        ])

    prompt_sections.extend([
        "Output Requirements:",
        "- Start with a brief overview.",
        "- Then provide the full teacher-ready material.",
        "- Use clean Markdown formatting with headings, numbered lists, and bullet points.",
        "- Do not repeat the assignment overview metadata if it is already shown on the results page.",
        "- Do not use LaTeX formatting.",
        "- Do not use dollar signs around equations.",
        "- Do not use LaTeX commands such as \\text{}, \\frac{}, \\rightarrow, ^, _, or H$_2$.",
        "- For chemical formulas and equations, use readable Unicode/plain text such as H₂O, CO₂, NaCl, and 2H₂ + O₂ → 2H₂O.",
        "- For math formulas, use readable plain text or Unicode, such as x = (-b ± √(b² - 4ac)) / 2a.",
        "- Do not overuse complex notation for lower grade levels.",
        "- Do not mention that you are an AI.",
        "- Do not include citations yet unless sources are provided in a future version.",
    ])

    return "\n".join(prompt_sections)


def generate_with_gemini(prompt):
    full_prompt = f"{SYSTEM_PROMPT}\n\nTeacher Request:\n{prompt}"

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_prompt,
    )

    return response.text


def add_pdf_page_break_before_answer_key(markdown_text):
    """
    Inserts a print-only page break before the Answer Key section.
    This affects the rendered PDF view, but not the raw copied text.
    """
    if '<div class="pdf-page-break"></div>' in markdown_text:
        return markdown_text

    pattern = r"(?im)^((?:#{1,6}\s*)?answer key[^\n]*)$"

    return re.sub(
        pattern,
        r'<div class="pdf-page-break"></div>' + "\n\n" + r"\1",
        markdown_text,
        count=1
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    grade_level = request.form.get("grade_level")
    subject = request.form.get("subject")
    topic = request.form.get("topic")
    material_type = request.form.get("material_type")
    difficulty = request.form.get("difficulty")

    prompt = build_generation_prompt(request.form)
    generated_text = generate_with_gemini(prompt)

    display_markdown = add_pdf_page_break_before_answer_key(generated_text)

    generated_html = markdown.markdown(
        display_markdown,
        extensions=["extra", "nl2br"]
    )

    return render_template(
        "result.html",
        grade_level=grade_level,
        subject=subject,
        topic=topic,
        material_type=material_type,
        difficulty=difficulty,
        generated_text=generated_text,
        generated_html=generated_html,
    )


if __name__ == "__main__":
    print("Open LessonForge AI at: http://localhost:5050")
    app.run(debug=True, host="127.0.0.1", port=5050)