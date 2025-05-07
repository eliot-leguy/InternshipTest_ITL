# Auto-FAQ Generator

A simple web application that lets companies upload documents (PDF, TXT) and instantly generate a clean, browsable FAQ using OpenAI. Built with FastAPI + HTML/JS.

---

## Features

- Upload `.pdf` and `.txt` files
- Automatically generates a combined FAQ with OpenAI GPT-4o-mini
- All data stored locally – no database

---

## 🚀 Setup

### 1. Clone + Install

```bash
git clone https://github.com/eliot-leguy/InternshipTest_ITL.git
cd auto-faq-generator
python -m venv .venv
source .venv/bin/activate      # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## ▶️ Run the app

Start the development server:

```bash
python app.py

```
Connect to http://localhost:8000

---

## How the FAQ generation works

- All uploaded .pdf and .txt files are parsed into raw text
- Their content is then cleaned of excessive blank spaces and table of contents
- The full content is passed to an OpenAI model (gpt-4o-mini)
- A prompt asks the model to extract useful, clear question-answer pairs
- The output is parsed, cleaned, and saved to faq.json
- The frontend loads and displays the FAQ

### Prompt

```bash
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
```