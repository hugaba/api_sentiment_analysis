import pandas as pd
import numpy as np
from gensim.models import Word2Vec, Phrases
from keras.models import model_from_json
import torch
from transformers import CamembertTokenizer, CamembertForSequenceClassification
from keras.preprocessing.sequence import pad_sequences

MAX_LEN = 128
batch_size = 16
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def aggregate_vector_model(words: list, model: Word2Vec, num_features: int):
    # Pre-initialising empty numpy array for speed
    feature_vec = np.zeros(num_features, dtype="float32")
    counter = 0

    # Converting Index2Word which is a list to a set for better speed in the execution.
    index2word_set = set(model.wv.index2word)

    for word in words:
        if word in index2word_set:
            counter += 1
            feature_vec = np.add(feature_vec, model[word])  # add word vectors element by element

    # Dividing the result by number of words to get average
    feature_vec = np.divide(feature_vec, counter)
    return feature_vec


# Function for calculating the average feature vector
def get_average_vector_model(reviews: pd.Series, model: Word2Vec, num_features: int) -> np.array:
    counter = 0
    review_feature_vecs = np.zeros((len(reviews), num_features), dtype="float32")

    for review in reviews:
        review_feature_vecs[counter] = aggregate_vector_model(review, model, num_features)
        counter += 1

    return review_feature_vecs


def vectorize(df, model, num_features):
    df_vect = get_average_vector_model(df['review'], model, num_features)
    df_vect = np.nan_to_num(df_vect)
    return df_vect


def predict(df: pd.DataFrame) -> pd.DataFrame:
    """
    predict the sentiment of reviews
    :param df: dataframe with reviews
    :return: dataframe: dataframe with prediction of reviews
    """
    # load pretrained Word2Vec model
    model = Word2Vec.load("100features_40minwords_20context_bigram")
    # transform words into vectors
    df_vect = vectorize(df, model, 100)

    # load json and create model
    json_file = open('model_bigram.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights("model_bigram.h5")
    loaded_model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['accuracy'])

    # predict sentiment with pretrained model
    predictions = loaded_model.predict(df_vect)

    # convert list of list of probabilities into list of probabilities
    predictions = [x for _list in predictions for x in _list]
    # Convert probabilities into binary predictions
    predictions = [1 if i >= 0.5 else 0 for i in predictions]
    df = pd.DataFrame(data={"site": df["site"], "date": df["date"],
                            "review": df["review"], "sentiment": predictions})
    return df


def predict_camembert(df: pd.DataFrame) -> pd.DataFrame:
    """
    predict the sentiment of reviews
    :param df: dataframe with reviews
    :return: dataframe: dataframe with prediction of reviews
    """
    df['space'] = ' '
    df['comments'] = df[['titre', 'space', 'comment']].fillna('').sum(axis=1)
    df = df.dropna(subset=['comments'], axis="rows")
    comments = df['comments'].to_list()
    # camemBERT
    state_dict = torch.load("camemBERT_38000_state_dict.pt", map_location=torch.device('cpu'))
    model = CamembertForSequenceClassification.from_pretrained('camembert-base', num_labels=2, state_dict=state_dict)

    # Initialize CamemBERT tokenizer
    tokenizer = CamembertTokenizer.from_pretrained('camembert-base', do_lower_case=True)

    # Encode the comments
    tokenized_comments_ids = [tokenizer.encode(comment,
                                               add_special_tokens=True, max_length=MAX_LEN) for comment in comments]
    # Pad the resulted encoded comments
    tokenized_comments_ids = pad_sequences(tokenized_comments_ids, maxlen=MAX_LEN, dtype="long",
                                           truncating="post", padding="post")

    # Create attention masks
    attention_masks = []
    for seq in tokenized_comments_ids:
        seq_mask = [float(i > 0) for i in seq]
        attention_masks.append(seq_mask)

    prediction_inputs = torch.tensor(tokenized_comments_ids)
    prediction_masks = torch.tensor(attention_masks)

    predictions = []
    with torch.no_grad():
        # Forward pass, calculate logit predictions
        outputs = model(prediction_inputs.to(device), token_type_ids=None,
                         attention_mask=prediction_masks.to(device))
        logits = outputs[0]
        logits = logits.detach().cpu().numpy()
        predictions.extend(np.argmax(logits, axis=1).flatten())

    df = pd.DataFrame(data={"site": df["site"], "date": df["date"],
                            "review": df["review"], "sentiment": predictions})
    return df
