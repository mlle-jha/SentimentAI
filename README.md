# SentimentAI — Jhadieja's Text Processing Module

## What this part does
- Extracts selectable text from PDF files with PyMuPDF.
- Cleans and normalizes text.
- Removes stopwords while preserving negation words such as `not` and `never`.
- Calculates total words, sentences, and characters.
- Finds frequent words and candidate keywords.
- Returns `classification_text` for the sentiment-classification teammate/module.

**Important:** This module does not predict Positive, Neutral, or Negative. That belongs to the sentiment-classification component.

## 1. Install
Open a terminal in this folder:

```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

Install packages:
```bash
pip install -r requirements.txt
python setup_nlp.py
python -m spacy download en_core_web_sm
```

## 2. Run the API
Place `index.html` and `style.css` in this same folder, then run:

```bash
python app.py
```

Open `http://127.0.0.1:5000`.

Do not use Live Server for the API page unless your frontend JavaScript is configured to send requests to `http://127.0.0.1:5000`.

## 3. API contracts

### Manual text
`POST http://127.0.0.1:5000/api/analyze`

JSON body:
```json
{"text": "I love this product. It works very well!"}
```

### PDF upload
`POST http://127.0.0.1:5000/api/analyze-pdf`

Send multipart form data with the field name `file`.

## 4. Returned fields
- `total_words`
- `total_sentences`
- `total_characters`
- `frequent_words` — list of `{word, count}`
- `keywords` — list of `{keyword, count}`
- `cleaned_text`
- `processed_tokens`
- `classification_text`
- `sentences`
- `extracted_text` and `source` for PDF requests

## 5. Connect to the frontend
The existing HTML uses these IDs:
- `manualText`
- `pdfUpload`
- `analyzeBtn`
- `totalWords`
- `totalSentences`
- `totalChars`
- `keywordsContainer`

Your frontend JavaScript can call the API and display the returned metrics. The sentiment chart and `overallSentiment` should be populated by the sentiment-classification module, not this text-processing module.

## Notes / limitations
- PyMuPDF extracts selectable PDF text. Scanned/image-only PDFs need OCR, which is not included in this assigned scope.
- The sample NLP pipeline is configured for English.
- `total_characters` includes spaces and punctuation; `total_words` is counted from the original text, before stopword removal.
