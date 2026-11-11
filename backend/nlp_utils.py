import re
import string

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

NLTK_RESOURCES = [
    ("tokenizers/punkt", "punkt"),
    ("tokenizers/punkt_tab", "punkt_tab"),
    ("corpora/stopwords", "stopwords"),
    ("corpora/wordnet", "wordnet"),
    ("corpora/omw-1.4", "omw-1.4"),
]


def _ensure_nltk_data():
    for path, name in NLTK_RESOURCES:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(name, quiet=True)


def preprocess_text(text):
    if not text:
        return ""

    _ensure_nltk_data()

    text = text.lower()
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))

    stop_words = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()
    return " ".join(
        lemmatizer.lemmatize(token)
        for token in word_tokenize(text)
        if token.isalpha() and token not in stop_words
    )
