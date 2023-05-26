from keras.models import load_model
from keras_preprocessing.text import tokenizer_from_json
from keras_preprocessing.sequence import pad_sequences
import re                                  # library for regular expression operations
import string                              # for string operations
import json

from nltk.corpus import stopwords          # module for stop words that come with NLTK
from nltk.tokenize import TweetTokenizer   # module for tokenizing strings
from nltk.stem import WordNetLemmatizer


def preprocess_text(initial_text):
  try:
    text = re.sub(r'^RT[\s]+', '', initial_text) 
    text = re.sub(r'https?:\/\/.*[\r\n]*', '', text)
    text = re.sub(r'#', '', text)
    tokenizer = TweetTokenizer(preserve_case=False, strip_handles=True, reduce_len=True)
    text_tokens = tokenizer.tokenize(text)
    stopwords_english = stopwords.words('english')
    text_clean = []

    for word in text_tokens:
      # Remove stopwords and punctuation
      if (word not in stopwords_english and word not in string.punctuation):
          text_clean.append(word)

    lemmatizer = WordNetLemmatizer()
    text_lem = [] 

    for word in text_clean:
        try:
          word = word.lower()
        except:
          continue

        lem_word = lemmatizer.lemmatize(word)  # lemmatizing word
        text_lem.append(lem_word) 

    return ' '.join(text_lem)
  except:
    return initial_text


def load_tokenizer_from_file(tokenizer_path: str):
    with open(tokenizer_path) as f:
        data = json.load(f)
        loaded_tokenizer = tokenizer_from_json(data)
    return loaded_tokenizer


def load_model_from_file(model_path: str):
    model_path = model_path
    pretrained_model = load_model(model_path)
    return pretrained_model


def analyse_review(model, tokenizer, review: str):
    preprocessed_review = preprocess_text(review)
    reviews_list = [preprocessed_review]
    reviews_tokenized = tokenizer.texts_to_sequences(reviews_list)
    reviews_padded = pad_sequences(reviews_tokenized, padding='post', maxlen=100)
    reviews_sentiments = model.predict(reviews_padded)
    return reviews_sentiments


if __name__ == "__main__":
    pass
