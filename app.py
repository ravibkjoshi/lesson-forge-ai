import os
import re
import markdown

from dotenv import load_dotenv
from flask import Flask, render_template, request
from google import genai


# Load environment variables from the local .env file.
# This keeps the Google API key out of the source code and out of GitHub.
load_dotenv()

app = Flask(__name__)

# Create a Gemini client using the API key stored in .env.
# The app expects GOOGLE_API_KEY to be defined locally.
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


# Main system prompt for LessonForge AI.
# This controls the overall behavior of the generated educational materials.
# It keeps outputs practical, teacher-friendly, grade-appropriate, and formatted cleanly.
SYSTEM_PROMPT = """
You are LessonForge AI, an assistant that creates educational materials for classroom, tutoring, homeschool, and flexible learning settings.

Follow these rules:

1. Use the selected learning setting, grade level, subject, topic, material type, difficulty, class time, and instructions.
2. Keep the output practical, clear, age-appropriate, and easy for a teacher to copy and edit.
3. Do not invent citations or URLs.
4. Before creating a quiz, test, or homework assignment, define a brief lesson scope showing the key concepts students are expected to know.
5. Assessment questions must only test concepts included in the lesson scope or explicitly mentioned by the teacher.
6. For quizzes, tests, and homework assignments, include answer keys when requested.
7. For multiple choice questions, provide four answer choices labeled A-D and only one correct answer.
8. For essay questions, make sure students could reasonably answer using the lesson scope.
9. For class activities, follow the selected materials preference. If materials are needed, keep them simple, low-cost, and easy to access.
10. Do not include unnecessary explanation about how you generated the material.
11. Use clean Markdown formatting with headings, numbered lists, and bullet points.
12. Do not use LaTeX math formatting.
13. Do not wrap formulas or equations in dollar signs.
14. Do not use LaTeX commands such as \\text{}, \\frac{}, \\rightarrow, ^, _, or H$_2$.
15. For chemical formulas and equations, use readable Unicode/plain text formatting such as H₂O, CO₂, NaCl, and 2H₂ + O₂ → 2H₂O.
16. For math formulas, use readable plain text or Unicode formatting such as x = (-b ± √(b² - 4ac)) / 2a.
17. Do not overuse complex notation for lower grade levels.
"""
def get_learning_setting_guidance(learning_setting):
    """
    Returns short, selected-only guidance for the chosen learning setting.

    This is token-optimized because the prompt only receives the guidance
    for the selected setting, not every possible setting.
    """

    setting_guidance = {
        "Classroom": (
            "Learning Setting: Classroom. "
            "Assume one instructor working with a full class. "
            "Group work, pair activities, class discussion, and classroom timing are appropriate."
        ),
        "Tutoring": (
            "Learning Setting: Tutoring. "
            "Assume one instructor working with one student or a very small group. "
            "Prioritize direct explanation, guided practice, checks for understanding, and flexible pacing."
        ),
        "Homeschool": (
            "Learning Setting: Homeschool. "
            "Assume the material may be used at home with one or a few students and simple materials. "
            "Avoid full-class group activities unless specifically requested."
        ),
        "General / Flexible": (
            "Learning Setting: General / Flexible. "
            "Do not assume a classroom, tutoring, or homeschool environment. Keep the material adaptable."
        ),
    }

    return setting_guidance.get(learning_setting, "")
def build_materials_preference_instruction(materials_preference):
    """
    Returns short guidance for the selected materials preference.

    This keeps the prompt token-friendly while still making sure
    Gemini considers whether the teacher wants no materials, simple
    household materials, or normal classroom materials.
    """

    if materials_preference == "Use no physical materials if possible":
        return (
            "Materials Preference: Prefer no physical materials. "
            "If materials help, make them minimal, common, and optional."
        )

    if materials_preference == "Use simple household materials":
        return (
            "Materials Preference: Use only simple household materials when needed. "
            "Keep the materials list short and inexpensive."
        )

    if materials_preference == "Materials are fine":
        return (
            "Materials Preference: Physical materials are allowed when useful, "
            "but keep them practical, safe, and age-appropriate."
        )

    return "Materials Preference: Keep any materials practical and easy to access."

def build_generation_prompt(form_data):
    """
    Builds the user-specific prompt that gets sent to Gemini.

    The form always sends core details like grade level, subject, topic,
    material type, difficulty, tone, and additional instructions.

    Depending on the selected material type, this function adds extra
    instructions for lesson plans, assessments, study guides, class activities,
    or discussion questions.
    """
    material_type = form_data.get("material_type")
    learning_setting = form_data.get("learning_setting")
    materials_preference = form_data.get("materials_preference")

    learning_setting_guidance = get_learning_setting_guidance(learning_setting)
    materials_preference_guidance = build_materials_preference_instruction(materials_preference)
    
    



    prompt_sections = [
   "Create the following educational material.",
    "",
    learning_setting_guidance,
    materials_preference_guidance,
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

    # Lesson plan-specific prompt instructions.
    # These are only included when the teacher selects "Lesson Plan".
    if material_type == "Lesson Plan":
        prompt_sections.extend([
            "Lesson Plan Requirements:",
            f"Estimated Class Time: {form_data.get('lesson_length')}",
            f"Learning Objective: {form_data.get('learning_objective') or 'Generate an appropriate learning objective based on the topic.'}",
            f"Include Warm-Up / Do Now: {form_data.get('include_warmup')}",
            "",
            "Format the lesson plan with sections for overview, learning objective, materials, warm-up if requested, direct instruction, guided practice, independent practice, assessment, exit ticket if requested, and teacher notes.",
            "",
        ])

    # Assessment-specific prompt instructions.
    # These are only included for quizzes, tests, and homework assignments.
    # Study guides are intentionally excluded because they should not behave
    # like assessments or include answer keys.
    if material_type in ["Quiz", "Test", "Homework Assignment"]:
        subject = form_data.get("subject")

        # Math and Science currently avoid essay questions because short answer,
        # multiple choice, and problem-based questions are usually a better fit.
        # This backend rule protects the app even if the frontend sends essay_count.
        essay_count = "0" if subject in ["Science", "Math"] else form_data.get("essay_count")

        prompt_sections.extend([
            "Assessment Requirements:",
            f"Question Type: {form_data.get('question_type')}",
            f"Multiple Choice Count: {form_data.get('multiple_choice_count')}",
            f"Essay Question Count: {essay_count}",
            f"Short Answer Count: {form_data.get('short_answer_count')}",
            f"Include Answer Key: {form_data.get('include_answer_key')}",
            f"Include Explanations: {form_data.get('include_explanations')}",
            "",
                    # Always give the teacher a separate scope/context section.
                    # This helps the teacher understand what students are expected to know.
                    # This section should appear on the results page, but not inside the student PDF.
               "For quizzes, tests, and homework assignments, always include an instructor-facing lesson scope before the student version.",
"Start that section with the exact Markdown heading: ## Teacher Lesson Scope",
"Format the Teacher Lesson Scope with clean Markdown subheadings and short paragraphs, not a single flat bullet list.",
"Use this structure when helpful:",
"### What Students Should Know",
"Write 2-4 sentences explaining the main concepts students need before answering the assessment.",
"### Key Skills",
"List 3-6 specific skills students will practice or demonstrate.",
"### Important Vocabulary",
"Include only the most relevant terms, with brief plain-language explanations.",
"### Assessment Boundaries",
"Briefly explain what the assessment will and will not cover so the instructor knows the scope.",
"Do not include the Teacher Lesson Scope inside the student version.",

# Give the student document a predictable heading.
# The split helper can use this to separate the student material cleanly.
"Start the student-facing material with the exact Markdown heading: ## Student Version",
*get_answer_space_instructions(subject),
# Printable student response spaces.
# This only affects the student version, not the teacher scope or answer key.
"Student Version Formatting:",
"Add printable answer space in the student version only for short answer, essay, and math/problem-solving questions.",
"Do not add answer spaces in the Teacher Lesson Scope or Answer Key.",
"Do not add answer spaces after multiple choice questions.",
"Put each answer-space HTML block on its own line with a blank line before and after it.",
'For short answer questions, place this exact HTML after the question: <div class="answer-space short-answer-space"></div>',
'For essay questions, place this exact HTML after the question: <div class="answer-space essay-space"></div>',
'For math or calculation questions that require work, place this exact HTML after the question: <div class="answer-space work-space"></div>',
"When repeating questions in the answer key, do not include or repeat any answer-space HTML.",

            # Keep questions fair and limited to the selected topic, grade level, and teacher instructions.
            "Only write questions that are answerable from the selected topic, grade level, and teacher instructions.",
            "Do not test obscure facts, advanced concepts, or material outside the selected grade level unless the teacher specifically requested it.",

            # Keep multiple choice formatting consistent.
            "If multiple choice questions are requested, each question must have A-D answer choices and one correct answer.",

            # Essay handling, if essay questions are still allowed.
            "If essay questions are requested, include a suggested answer or grading guidance when answer keys are requested.",

            # Give the answer key a predictable heading.
            # The app uses this heading to split the answer key from the student version.
            "If an answer key is requested, start it with the exact Markdown heading: ## Answer Key",

            # Make the answer key self-contained.
            # This prevents the answer key PDF from only showing letters like 1. C, 2. D.
            "The Answer Key must repeat each original question before giving the answer.",
            "For multiple choice questions, repeat the question and all answer choices before showing the correct answer.",
            "For short answer or essay questions, repeat the question before showing the answer or grading guidance.",

            # Explanation placement.
            "If explanations are requested, include the explanation directly under the answer.",

            # Keep the order correct.
            "Do not place the answer key before the student-facing assignment.",
            "",
            "",
        ])

    # Study guide-specific prompt instructions.
    # Study guides should summarize and organize concepts rather than act
    # like quizzes, tests, homework assignments, or problem sets.
    if material_type == "Study Guide":
        prompt_sections.extend([
            "Study Guide Requirements:",
            f"Estimated Class Time: {form_data.get('lesson_length')}",
            "",
            "Create a student-friendly study guide, not a quiz, test, homework assignment, or problem set.",
            "Do not include essay questions.",
            "Do not include an answer key.",
            "Do not include a long list of practice problems unless the teacher specifically asks for practice questions.",
            "",
            "Format the study guide with these sections:",
            "- Overview",
            "- Key Concepts",
            "- Important Vocabulary",
            "- Core Ideas to Remember",
            "- Examples",
            "- Common Mistakes or Misconceptions",
            "- Quick Review Checklist",
            "",
        ])

    # Class activity-specific prompt instructions.
    # These help Gemini create structured classroom games, simulations,
    # group activities, debates, role plays, or hands-on activities.
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

    # Discussion-specific prompt instructions.
    # These are only included when the teacher selects "Discussion Questions".
    if material_type == "Discussion Questions":
        prompt_sections.extend([
            "Discussion Requirements:",
            f"Number of Discussion Questions: {form_data.get('discussion_count')}",
            f"Discussion Style: {form_data.get('discussion_style')}",
            "",
            "Format the output as teacher-ready discussion prompts with optional follow-up questions.",
            "",
        ])

    # Final output rules that apply to every generated material type.
    # These keep the response clean, teacher-ready, and easy to render as HTML/PDF.
    prompt_sections.extend([
        "Output Requirements:",
        "- Start with a brief overview.",
        "- Then provide the full instructor-ready material.",
        "- Use clean Markdown formatting with headings, numbered lists, and bullet points.",
        "- Do not use asterisks for bullet points, bold text, or horizontal dividers ever.",
        "- Avoid horizontal rules like *** or ---.",
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
    """
    Sends the final prompt to Gemini and returns the generated text.

    The system prompt defines the app's overall behavior.
    The teacher request contains the specific form inputs from the user.
    """
    full_prompt = f"{SYSTEM_PROMPT}\n\nTeacher Request:\n{prompt}"

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_prompt,
    )

    return response.text


def is_assessment_material(material_type):
    """
    Checks whether the selected material type should have a separate
    student-facing document and answer key document.

    Only assessment-style materials need answer keys.
    Study guides, lesson plans, class activities, and discussion questions do not.
    """

    # Define the material types that should be treated like assessments.
    # These are the only options where an answer key makes product sense.
    assessment_materials = ["Quiz", "Test", "Homework Assignment"]

    # Return True if the selected material type is one of the assessment types.
    # Return False for lesson plans, study guides, class activities, and discussions.
    return material_type in assessment_materials
def get_answer_space_instructions(subject):
    """
    Returns lightweight prompt instructions for printable student answer spaces.

    We use simple markers instead of asking Gemini to write HTML directly.
    Python later converts those markers into styled HTML blocks.
    """

    if subject in ["Math", "Science"]:
        return [
            "For student-facing non-multiple-choice questions, place [BLANK_WORK_SPACE] after the question.",
            "Do not add answer-space markers after multiple choice questions.",
            "Do not add answer-space markers in the Teacher Lesson Scope or Answer Key.",
        ]

    return [
        "For student-facing short answer questions, place [SHORT_ANSWER_SPACE] after the question.",
        "For student-facing essay questions, place [ESSAY_SPACE] after the question.",
        "Do not add answer-space markers after multiple choice questions.",
        "Do not add answer-space markers in the Teacher Lesson Scope or Answer Key.",
    ]


def apply_answer_space_markers(markdown_text):
    """
    Converts answer-space markers into HTML blocks.

    This only runs on the student version, so the teacher scope and answer key
    stay clean.
    """

    replacements = {
        "[SHORT_ANSWER_SPACE]": '<div class="answer-space short-answer-space"></div>',
        "[ESSAY_SPACE]": '<div class="answer-space essay-space"></div>',
        "[BLANK_WORK_SPACE]": '<div class="answer-space blank-work-space"></div>',
    }

    for marker, html in replacements.items():
        markdown_text = markdown_text.replace(marker, f"\n\n{html}\n\n")

    return markdown_text


def remove_answer_space_markers(markdown_text):
    """
    Removes any answer-space markers that accidentally appear outside
    the student version.
    """

    markers = [
        "[SHORT_ANSWER_SPACE]",
        "[ESSAY_SPACE]",
        "[BLANK_WORK_SPACE]",
    ]

    for marker in markers:
        markdown_text = markdown_text.replace(marker, "")

    return markdown_text

def split_assessment_sections(markdown_text):
    """
    Splits Gemini's generated Markdown into three separate pieces:

    1. teacher_scope:
       The teacher-facing lesson scope/context.

    2. student_material:
       The student-facing quiz, test, or homework assignment.

    3. answer_key:
       The answer key section, including repeated questions, answers,
       explanations, or grading guidance.

    Expected Gemini format:

    ## Teacher Lesson Scope
    teacher-facing context

    ## Student Version
    student-facing questions

    ## Answer Key
    repeated questions, answers, and explanations
    """

    teacher_scope_pattern = r"(?im)^((?:#{1,6}\s*)?teacher lesson scope[^\n]*)$"
    student_pattern = r"(?im)^((?:#{1,6}\s*)?student version[^\n]*)$"
    answer_key_pattern = r"(?im)^((?:#{1,6}\s*)?answer key[^\n]*)$"

    teacher_scope_match = re.search(teacher_scope_pattern, markdown_text)
    student_match = re.search(student_pattern, markdown_text)
    answer_key_match = re.search(answer_key_pattern, markdown_text)

    teacher_scope = ""
    student_material = markdown_text.strip()
    answer_key = ""

    if teacher_scope_match and student_match:
        teacher_scope = markdown_text[teacher_scope_match.end():student_match.start()].strip()

    if student_match and answer_key_match:
        student_material = markdown_text[student_match.end():answer_key_match.start()].strip()
    elif student_match:
        student_material = markdown_text[student_match.end():].strip()

    if answer_key_match:
        answer_key = markdown_text[answer_key_match.end():].strip()

    return teacher_scope, student_material, answer_key

@app.route("/")
def index():
    """
    Displays the main LessonForge AI form.

    The form is defined in templates/index.html and collects the teacher's
    grade level, subject, topic, material type, and related options.
    """
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    """
    Handles form submission and generates the final classroom material.

    Flow:
    1. Read the submitted form values.
    2. Store the original form data for the Regenerate button.
    3. Build a structured prompt for Gemini.
    4. Generate the material with Gemini.
    5. If the material is an assessment, split the student version from the answer key.
    6. Convert the student version and answer key into HTML separately.
    7. Render the result page with copy, regenerate, and PDF options.
    """
    grade_level = request.form.get("grade_level")
    subject = request.form.get("subject")
    topic = request.form.get("topic")
    material_type = request.form.get("material_type")
    difficulty = request.form.get("difficulty")
    learning_setting = request.form.get("learning_setting")

    # Store the original form inputs so the result page can resubmit them
    # if the teacher clicks "Regenerate".
    form_data = request.form.to_dict()

    # Build the prompt from the submitted form data.
    # This turns the teacher's form choices into a structured Gemini prompt.
    prompt = build_generation_prompt(request.form)

    # Send the prompt to Gemini and store the full raw Markdown response.
    # At this point, generated_text may include both the student material
    # and the answer key.
    generated_text = generate_with_gemini(prompt)

    # Decide whether this material type should support a separate answer key.
    # This will only be True for Quiz, Test, and Homework Assignment.
    has_answer_key_document = is_assessment_material(material_type)

    # Default behavior:
    # Treat the full generated response as the student-facing material.
    # This is what we want for non-assessment materials like Study Guide,
    # Lesson Plan, Class Activity, and Discussion Questions.
    teacher_scope_text = ""
    student_material_text = generated_text
    answer_key_text = ""

    # Assessment behavior:
    # If the material is a quiz, test, or homework assignment,
    # split the generated content into:
    # 1. student_material_text: everything before "## Answer Key"
    # 2. answer_key_text: "## Answer Key" and everything after it
    if has_answer_key_document:
          teacher_scope_text, student_material_text, answer_key_text = split_assessment_sections(generated_text)
    student_material_text = apply_answer_space_markers(student_material_text)
    teacher_scope_text = remove_answer_space_markers(teacher_scope_text)
    answer_key_text = remove_answer_space_markers(answer_key_text)

    # Convert the student-facing Markdown into HTML for the main result display.
    # For assessments, this should no longer include the answer key.
    # For non-assessments, this is just the full generated content.
    generated_html = markdown.markdown(
        student_material_text,
        extensions=["extra", "nl2br"]
    )
    
    teacher_scope_html = markdown.markdown(
    teacher_scope_text,
    extensions=["extra", "nl2br"]
) if teacher_scope_text else ""

    # Convert the answer key Markdown into HTML only if an answer key exists.
    # If answer_key_text is empty, keep answer_key_html as an empty string.
    answer_key_html = markdown.markdown(
        answer_key_text,
        extensions=["extra", "nl2br"]
    ) if answer_key_text else ""

    return render_template(
        "result.html",
        grade_level=grade_level,
        subject=subject,
        topic=topic,
        material_type=material_type,
        difficulty=difficulty,
            learning_setting=learning_setting,

        # Original full Gemini response.
        # Useful to keep around for debugging or future full-copy behavior.
        generated_text=generated_text,

        # HTML version of the student-facing material.
        generated_html=generated_html,
        
        teacher_scope_text=teacher_scope_text,
        teacher_scope_html=teacher_scope_html,

        # Raw Markdown version of the student-facing material.
        student_material_text=student_material_text,

        # Raw Markdown answer key, only used for assessments.
        answer_key_text=answer_key_text,

        # HTML answer key, only used for assessments.
        answer_key_html=answer_key_html,

        # Boolean flag result.html can use to decide whether to show
        # answer-key-specific buttons or sections.
        has_answer_key_document=has_answer_key_document,

        # Original form data used by the Regenerate button.
        form_data=form_data,
    )


if __name__ == "__main__":
    # Run the Flask development server locally.
    # This is for local development only, not production hosting. Reminds the developer where to access the app in the browser.
    print("Open LessonForge AI at: http://localhost:5050")
    app.run(debug=True, host="127.0.0.1", port=5050)