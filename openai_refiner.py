from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def openai_refine(content: str, feedback: str, mode: str) -> str:
    prompt = f"""
You are an expert content editor.

Your job is to refine the given report based on user feedback.

Mode: {mode}

Instructions based on mode:
- Student: Simple, clear, concise
- Developer: Technical, structured, precise, coding stuff
- Researcher: Deep, detailed, well-organized, links to conference papers
and follow the rules given below
1. Remove ALL markdown symbols (*, **, #, etc.)
2. Use clean professional formatting
3. Add proper spacing between sections
4. Format like a formal report:

   - Title (centered style text, uppercase)
   - Section headings (clear and bold-like using capitalization)
   - Paragraph spacing (leave one blank line between paragraphs)
   - Numbered lists properly aligned
   - No unnecessary symbols

5. Structure:

   TITLE

   Executive Summary

   (paragraph)

   Section Heading

   (paragraph)

6. Ensure readability for PDF export
7. Keep it clean and minimal
8. Do NOT include any markdown or special characters

User Feedback:
{feedback}

Report:
{content}

Rules:
- Do NOT remove important existing content
- Improve quality and clarity
- Apply feedback strictly
- Keep it well-structured
- Remove markdowns and no use of unwanted symbols
- Should be in a professional and formatted report

Return the improved report.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",  
        messages=[
            {"role": "system", "content": "You are a professional report editor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )

    return response.choices[0].message.content