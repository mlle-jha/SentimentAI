# SentimentAI --- Development Process Notes

**Developer:** Cassey\
**Role:** AI Model and Sentiment Classification

## 1. Project Objective

The goal of this component was to develop a sentiment-classification
system that identifies whether submitted text expresses:

-   **Positive** --- satisfaction, happiness, approval, or favorable
    opinions.
-   **Negative** --- dissatisfaction, sadness, criticism, or unfavorable
    opinions.
-   **Neutral** --- information or statements without a clearly positive
    or negative sentiment.

The classifier is integrated into SentimentAI, which accepts manually
entered text and uploaded PDF documents.

## 2. Development Process

### 2.1 Environment Setup

-   Used Python 3.13.9.
-   Created a Python virtual environment named `.venv`.
-   Installed the project's required Python libraries.
-   Prepared the development environment in Visual Studio Code.

**Purpose:** The virtual environment keeps project dependencies separate
from other Python installations and projects.

### 2.2 Installed NLP and Machine-Learning Libraries

-   **PyTorch** --- provides the machine-learning framework used to run
    the model.
-   **Hugging Face Transformers** --- loads and runs the pretrained
    sentiment model.
-   **spaCy** --- supports natural language processing tasks in the
    text-processing component.
-   **NLTK** --- provides natural language processing utilities.

**Purpose:** These libraries provide the tools needed to process text
and perform sentiment classification.

### 2.3 Selected a Pretrained Model

**Model:** `iam-tsr/distilbert-finetuned-sentiment-analysis`

-   Based on the DistilBERT architecture.
-   Supports Positive, Negative, and Neutral classifications.
-   Retrieved from Hugging Face.

**Why DistilBERT?** DistilBERT is a smaller, more efficient version of
BERT. It is designed to retain much of BERT's language-understanding
capability while using fewer resources.

### 2.4 Implemented Sentiment Classification

Created the file `backend/sentiment_analyzer.py`.

Its responsibilities include:

-   Loading the pretrained model.
-   Accepting input text.
-   Splitting the text into individual sentences.
-   Predicting the sentiment of each sentence.
-   Obtaining confidence scores and class probabilities.
-   Calculating sentiment counts and percentages.
-   Determining the overall sentiment.
-   Providing an interpretation of the results.

**Why sentence-level analysis?** It allows the system to identify
different sentiments within one document instead of treating the entire
document as one undivided statement.

### 2.5 Integrated the Classifier with Flask

-   Connected the sentiment analyzer to `app.py`.
-   Connected the text-processing component to the classifier.
-   Added sentiment results to the API response.
-   Supported both manual text input and PDF uploads.

**Why Flask?** Flask acts as the backend that connects the frontend,
text-processing module, and sentiment classifier.

### 2.6 Connected the Frontend

-   Displayed the overall sentiment.
-   Displayed positive, negative, and neutral percentages.
-   Updated the sentiment chart dynamically.
-   Displayed text statistics and keywords returned by the
    text-processing module.

**Purpose:** The frontend makes the classification results
understandable and accessible to users.

### 2.7 Testing and Troubleshooting

-   Tested sample sentences with different sentiments.
-   Tested paragraphs containing mixed sentiments.
-   Tested PDF uploads.
-   Fixed integration and frontend display issues.
-   Observed how spelling mistakes can affect predictions.

**Important observation:** During testing, the misspelled word `hapy`
produced a different prediction from the correctly spelled word `happy`.
This demonstrated that spelling errors can influence pretrained model
predictions. Spelling correction was not added to the implementation.

## 3. Technologies and Tools Used

  Technology                  Purpose
  --------------------------- ---------------------------------------------------------
  Python                      Main programming language
  PyTorch                     Machine-learning framework used to run the model
  Hugging Face Transformers   Loads and runs the pretrained model
  DistilBERT                  Architecture used by the sentiment-classification model
  Flask                       Backend API
  PyMuPDF                     PDF text extraction
  spaCy                       Natural language processing and text processing
  NLTK                        NLP utilities
  JavaScript                  Frontend interaction
  HTML                        Webpage structure
  CSS                         Webpage styling
  Visual Studio Code          Development environment

## 4. How the System Works

The general workflow of SentimentAI is:

1.  **User Input:** The user enters text manually or uploads a PDF.
2.  **Flask Backend:** Flask receives the request and routes it to the
    appropriate processing function.
3.  **Text Processing:** The text-processing module extracts or
    processes the submitted text and provides text statistics and
    related information.
4.  **Sentiment Classification:** The DistilBERT-based classifier
    analyzes the original text sentence by sentence and predicts a
    sentiment for each sentence.
5.  **Result Aggregation:** The classifier calculates sentiment counts
    and percentages, determines the overall sentiment, and prepares an
    interpretation.
6.  **Frontend Display:** The frontend displays the sentiment results,
    chart, text statistics, and keywords.

### Simplified Workflow

``` text
User Input
(Manual Text or PDF)
        |
        v
 Flask Backend
        |
        v
 Text Processing Module
        |
        v
 Sentiment Classifier
     (DistilBERT)
        |
        v
 Sentiment Results
(labels, scores, percentages,
 overall sentiment, interpretation)
        |
        v
 Frontend Dashboard
```

**Important distinction:** The text-processing module and
sentiment-classification module have separate responsibilities. Text
processing extracts and prepares information, while the classifier
predicts sentiment.

## 5. Important Concepts to Understand

### What is Sentiment Analysis?

Sentiment analysis is a Natural Language Processing (NLP) task that
identifies the emotional tone or opinion expressed in a piece of text.

### What is DistilBERT?

DistilBERT is a transformer-based language model derived from BERT. It
has a smaller architecture designed to make language processing more
efficient while retaining much of BERT's language-understanding
capability.

### What is a Pretrained Model?

A pretrained model is a model that has already learned patterns from
previously processed training data. Instead of training a model from
scratch, this project uses an existing model and its learned parameters
to perform sentiment classification.

### What is Sentence-Level Classification?

Sentence-level classification means that the system predicts the
sentiment of individual sentences. The predictions are then combined to
calculate the sentiment distribution and determine the overall sentiment
of the submitted text.

### What is a Confidence Score?

A confidence score is a numerical value indicating how strongly the
model favors a particular prediction. It does not guarantee that the
prediction is correct.

### What is the Difference Between Confidence and Accuracy?

-   **Confidence** describes how strongly the model favors a prediction
    for a particular input.
-   **Accuracy** measures how often the model's predictions match the
    correct labels across a labeled evaluation dataset.

A model's confidence score should not be presented as its accuracy.
