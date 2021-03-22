import pandas as pd
import re
# import nltk

# nltk.download('punkt')
from nltk import word_tokenize
from nltk.corpus import stopwords

# nltk.download('stopwords')
# nltk.download('wordnet')
import spacy
from spacy_lefff import LefffLemmatizer
from spacy.language import Language
import json
from collections import Counter
from datetime import datetime
from dateutil.relativedelta import relativedelta
from gensim.models import Phrases

# regex to keep letters (also with accent) and emojis
EMOJI_PATTERN = re.compile(
    "[^a-zA-Z"  # letters
    "\u00C0-\u024F\u1E00-\u1EFF"  # accent letters
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002702-\U000027B0"  # Dingbats
    "\U000024C2-\U0001F251"
    "]+"
)

stop_words = stopwords.words("french")
new_stop_words = ['avoir', 'être', 'dire', 'donc', 'si', 'livraison', 'livrer', 'car', 'command', 'commande',
                  'commander']
stop_words.extend(new_stop_words)

try:
    @Language.factory('french_lemmatizer')
    def create_french_lemmatizer(nlp, name):
        return LefffLemmatizer()
except:
    print('already exist')

nlp = spacy.load('fr_core_news_sm')
nlp.add_pipe('french_lemmatizer', name='lefff')


def clean_txt(txt: str) -> str:
    """
    clean_text : remove punctuation, numbers, and '<br />'
    Params
        txt --> string: string to clean
    Return
        txt --> string : cleaned string
    """

    # Keep alphanumerical
    txt = re.sub(EMOJI_PATTERN, ' ', txt)

    # remove spaces before and after string and lower letters
    txt = txt.strip().lower()

    return txt


def remove_stop_words(txt: list) -> list:
    """
    Remove stop words from list of words
    Params
        txt -> list : list of strings to remove stop words from.
    Return
        txt -> list : list of strings without stop words
    """
    txt = [x for x in txt if x not in stop_words]
    return txt


def lemmatization(txt: list) -> list:
    txt = ' '.join(txt)
    lemmatized_list = []
    txt = nlp(txt)
    for t in txt:
        if t.text not in stop_words:
            lemmatized_list.append(t.lemma_)
    return lemmatized_list


def preprocess(txt: str) -> list:
    """
    Cleans, tokenizes, lemmatize text and remove stop words
    Params:
        txt -> str: Text to preprocess
    Return:
        lemmas -> list: Preprocessed text
    """

    # 1. Clean text
    cleaned_txt = clean_txt(txt)

    # 2. Split into individual words
    cleaned_txt = word_tokenize(cleaned_txt)

    # 3. Remove stopwords
    cleaned_txt = remove_stop_words(cleaned_txt)

    # 4. Lemmatization
    cleaned_txt = lemmatization(cleaned_txt)

    # 5. Remove stopwords
    cleaned_txt = remove_stop_words(cleaned_txt)

    return cleaned_txt


def preprocess_df(df):
    df['review'] = df['titre'] + ' ' + df['comment']
    df['review'] = df['review'].apply(preprocess)
    bigram_transformer = Phrases(df['review'])
    df['review'] = bigram_transformer[df['review']]
    return df


def get_word_cloud(df: pd.DataFrame, nb_of_words=40) -> dict:
    """
    get number of occurence for 'nb_of_words' most common words
    :param df: dataframe
    :param nb_of_words: number of words to show
    :return: dict: dictionary of top words with nb of occurence
    """
    word_cloud = {}
    if len(df) > 0:
        list_of_words = df['review'].sum(axis=0)
        count_pos = Counter(list_of_words)
        word_cloud_tuples = count_pos.most_common()
        word_cloud_tuples = word_cloud_tuples[:nb_of_words]
        for elt in word_cloud_tuples:
            word_cloud[elt[0]] = elt[1]

    return word_cloud


def get_summary(df, refs='last_month'):
    df_pos = df[df['sentiment'] == 1]
    df_neg = df[df['sentiment'] == 0]
    summary = {
            'nb_review_analysed': len(df),
            'nb_review': {
                'pos': len(df_pos),
                'neg': len(df_neg)
            },
            'word_cloud': {
                'pos': get_word_cloud(df_pos),
                'neg': get_word_cloud(df_neg)
            }
        }

    if refs != 'last_month':
        summary['nb_concurent'] = len(refs[0])
        summary['nb_concurrent_analysed'] = len(refs[1])

    return summary


def get_details(df: pd.DataFrame) -> json:
    """
    get details from scraped sites
    :param df: full dataframe
    :return: json file
    """
    detail = {}
    for site in df['site'].unique():
        detail[site] = {
            'nb_review_analysed': len(df[df['site'] == site]),
            'nb_review': {
                'pos': len(df[(df['site'] == site) & (df['sentiment'] == 1)]),
                'neg': len(df[(df['site'] == site) & (df['sentiment'] == 0)])
            },
            'word_cloud': {
                'pos': get_word_cloud(df[(df['site'] == site) & (df['sentiment'] == 1)]),
                'neg': get_word_cloud(df[(df['site'] == site) & (df['sentiment'] == 0)])
            }
        }

    return detail


def get_last_month(df: pd.DataFrame) -> json:
    #df['date'] = df['date'].str.split('+', n=1, expand=True)[0]
    df['date'] = df['date'].str[:19]
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%dT%H:%M:%S')
    df = df[df['date'] >= (datetime.now() - relativedelta(months=+3))]
    last_month = get_summary(df)
    return last_month


def postprocess(df: pd.DataFrame, refs: list) -> json:
    """
    analyse dataframe to obtain json file
    :param df: full dataframe
    :param refs: list: total list of sites, scraped sites
    :return: json file
    """

    json_review = {
        'summary': get_summary(df, refs),
        'details': get_details(df),
        'last_3_month': get_last_month(df)
    }
    return json_review
