# tools/llm/modify.py

import os
from openai import OpenAI
from typing import List

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def modify_lesson_content(text: str, rules: List[str]) -> str:
    """
    Uses GPT‑4o to apply lesson adaptation rules to the input lesson content.
    Produces a structured output: Engager → I Do → We Do → You Do.
    Enforces side-by-side translations or accessibility features if required.
    """
    prompt = f"""
You are an expert inclusive education designer who adapts lessons for multilingual and special‑needs learners.

== Student Profile Rules ==
{chr(10).join(f"- {rule}" for rule in rules)}

== TASK ==
Rewrite the following lesson using the “Engager → I Do → We Do → You Do” framework described below.
Apply *all relevant rules*, including any language‑ or accessibility‑specific adaptations.

== SECTION GUIDELINES ==

1. **Engager**  
   Start with a warm‑up or connection activity that emotionally or intellectually prepares the learner.  
   Ask simple reflection questions, or connect the story theme to their life.

2. **I Do**  
   This section should feel like a teacher reading and guiding the story to students step-by-step.  
   🔸 **DO NOT summarize**. You must **retell the entire story in full detail**, not in brief.  
   🔸 Use simple, engaging English with embedded emotions, pauses, and reactions.  
   🔸 At key moments, ask questions like “What do you think Daedalus felt here?”  
   🔸 For **hard vocabulary**, embed Dominant Language translations in parentheses.  
   🔸 If the rules require **bilingual scaffolding**, also add Dominant Language translations for whole sentences where the English may be too complex.  
   🔸 Use `[Insert Image: ...]` and `[Insert Audio: ...]` only if the rule demands media.  
   🔸 Do not skip any key detail from the original lesson — treat it as a full retelling, not an outline.  
   🔸 Think of it as storytelling for a multilingual classroom, not as summarization.  
   🔸 **Go paragraph by paragraph through the story**, retelling each one in full. For each paragraph:  
       - Retell the events in simple teacher-style English.  
       - Add reactions (“How might Icarus feel here?”).  
       - Translate full sentences if the English is complex.  
       - Embed Dominant Language translations (in parentheses) next to hard words.  
       - Only insert images if it helps explain that specific part.

3. **We Do**  
   Create a teacher-guided collaborative activity.  
   🔸 Use dominant language for support if required by rules.  
   🔸 Ask comprehension or prediction questions, or design a role-play or discussion.

4. **You Do**  
   Design an independent task that lets the student show understanding.  
   🔸 Include options for writing, drawing, speaking — support multiple learning styles.  
   🔸 Allow students to use both English and their language if rules suggest bilingualism.

5. **Assessment**  
   Create 3 multiple-choice questions that assess the **main concept** or learning goal of the lesson — not just the retelling in “I Do”.  
   🔸 Each question should check the student’s understanding of the key ideas or themes.  
   🔸 Provide 3–4 answer options in a vertical list, with clear line breaks between them and use alphabetical notation for each option.  
   🔸 Do **not** include the correct answer — the student must choose.  
   🔸 include translated versions of each question and option in the Dominant Language below the English.  
   🔸 If audio is required, add `[Insert Audio: Question X]` after each question.  
   🔸 Use student-friendly language and keep vocabulary consistent with the rest of the modified lesson.

== GENERAL REQUIREMENTS ==
- Do not include the rules in the output.
- Maintain clear structure: Engager → I Do → We Do → You Do.
- Use simple but expressive language.
- Insert visuals or audio only where specifically needed by rules.
- Maintain clear structure with H1 for title, H2 for sections, H3 for subheadings, and normal text elsewhere.
- Keep the tone teacher-like, expressive, and friendly.
- Avoid summarizing — this must feel like a teacher leading a full story reading session.

== LESSON INPUT ==
\"\"\"{text}\"\"\"

Now produce the fully modified lesson based on the student profile rules.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an inclusive education assistant who strictly follows adaptation rules. "
                        "You must always apply bilingual or accessibility modifications when requested."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            timeout=60
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        raise RuntimeError(f"Failed to modify lesson with LLM: {str(e)}")
    


def modify_lesson_content_worksheet(text: str, rules: List[str]) -> str:
    """
    Uses GPT‑4o to adapt worksheet content (questions, instructions, or exercises)
    according to the provided student adaptation rules.

    - Simplifies complex vocabulary and sentence structure.
    - Adds bilingual support or translations if rules require.
    - Adds [Insert Image: ...] and [Insert Audio: ...] placeholders only if rules demand media.
    - Keeps the original worksheet’s logical structure (no Engager/I Do/We Do/You Do).
    """

    prompt = f"""
You are an expert inclusive education designer adapting **worksheet content** for multilingual and special-needs students.

== Student Profile Rules ==
{chr(10).join(f"- {rule}" for rule in rules)}

== TASK ==
Adapt the following worksheet into valid, clean **Markdown format** with clear headings, questions, and options. Make the content **accessible, bilingual (if required), and structured for readability**, without changing its original intent.

== OUTPUT FORMAT ==
- Use proper Markdown formatting:
  - `##` for main worksheet sections (e.g., "Reading Comprehension", "Vocabulary Practice")
  - `###` for each numbered question or instruction
  - Plain paragraphs for question body and answer options

- For multiple-choice questions:
  - Use **alphabetical format**, one line per option:
    A) Option one  
    B) Option two  
    C) Option three  
    D) Option four
    
  - Use proper Dividers after each Question

  - For each **question and option**,
    - Add **translated version** in parentheses directly below in Dominant Language
    - Then add audio placeholder like:
      [Insert Audio: Question 1] or [Insert Audio: Option A]

== CONTENT ADAPTATION RULES ==
1. **Simplify & Translate**
   - Use plain, age-appropriate English
   - Add translations (in parentheses) for complex vocabulary or full sentences, only if rules demand

2. **Preserve Structure**
   - Keep original order and numbering
   - Preserve blanks, underlines, and response spaces where present

3. **Media Support**
   - If image support is required, add `[Insert Image: Description]` below relevant question
   - If audio support is required, use `[Insert Audio: ...]` after question or option

4. **Tone**
   - Friendly, instructional tone that guides the student
   - Avoid overly formal or academic wording

5. **DO NOT**
   - Use backticks (```)
   - Wrap output in code blocks
   - Add unrelated content or remove exercises
   - Use Engager/I Do/We Do structure (this is a worksheet)

== WORKSHEET INPUT ==
\"\"\"{text}\"\"\"

== OUTPUT REQUIREMENTS ==
- Output must be clean, valid Markdown.
- Use `##` for section headings, `###` for questions, plain text for options.
- Insert translated versions and `[Insert Audio: ...]` only if required by student profile rules.
- Do NOT use any Markdown code fences or triple backticks in the output.

Now output the fully adapted worksheet in Markdown format only.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a multilingual inclusive education assistant. "
                        "You rewrite worksheets for students with diverse learning and language needs, "
                        "keeping the structure unchanged while adding supports and placeholders."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            timeout=60
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        raise RuntimeError(f"Failed to modify worksheet with LLM: {str(e)}")