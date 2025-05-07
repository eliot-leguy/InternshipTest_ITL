import fitz
import re


def extract_text_from_pdf(path) -> str:
    doc = fitz.open(path)
    return "\n\n".join(page.get_text() for page in doc)

def get_all_texts(UPLOAD_DIR) -> str:
    texts = []

    for f in UPLOAD_DIR.glob("*"):
        if f.suffix == ".pdf":
            texts.append(f"From document {f.name}:\n\n")
            texts.append(extract_text_from_pdf(f))
        elif f.suffix == ".txt":
            texts.append(f"From document {f.name}:\n\n")
            texts.append(f.read_text(encoding="utf-8", errors="ignore"))

    return "\n\n---\n\n".join(texts)


def clean_json_response(text: str) -> str:
    # remove ```json ... ``` if present
    return re.sub(r"^```json\s*|\s*```$", "", text.strip(), flags=re.DOTALL)

def generate_faq(client, text: str) -> dict:
    prompt = f"""
            You are a professional documentation assistant for a company.

            Your task is to extract useful and accurate Frequently Asked Questions (FAQs) from internal company documents. These FAQs are intended for external clients or users, to help them understand the company's products, services, or policies.

            Based on the content below, generate a list of helpful question-answer pairs. Prioritize:

            - Clarity: questions should be easy to understand
            - Usefulness: address real concerns a client may have
            - Coverage: include various parts of the content
            - Conciseness: avoid overly technical or verbose answers

            Output only a JSON array in the following format:

            [
            {{
                "question": "...",
                "answer": "..."
            }},
            ...
            ]

            Content:
            {text}
            """

    text = re.sub(r"\n{2,}", "\n\n", text)  # collapse blank lines
    text = re.sub(r"(?i)table of contents.*?(\n\n|\Z)", "", text, flags=re.DOTALL)


    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2048,
    )

    if r.choices[0].finish_reason != "stop":
        raise ValueError("Failed to generate FAQ")

    raw = r.choices[0].message.content
    cleaned = clean_json_response(raw)

    return cleaned

