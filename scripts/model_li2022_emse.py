import argparse
import re
import string

import fasttext
import nltk
import numpy as np
from tensorflow.keras.models import load_model

class Model1_IssueTracker_Li2022_ESEM:
    """
    Self-admitted technical debt verifier
    """

    def __init__(self, weight_file, word_embedding_file):
        # Load the model and its weights
        print('Loading model {}...'.format(weight_file))
        self._model = load_model(weight_file)
        self._size_of_input = self._model.layers[0].get_output_at(0).get_shape()[1]

        # Load the FastText word embeddings
        self._word_embedding = fasttext.load_model(word_embedding_file)
        self._word_embedding_cache = {}

        # Initialize the tokenizer and punctuation settings
        self._tokenizer_words = nltk.TweetTokenizer()

        # Set up label configurations
        label_num = self._model.layers[-1].get_output_at(0).get_shape()[-1]
        self._labels = ['SATD', 'non-SATD']
        self._padding = '<pad>'

    def comment_pre_processing(self, comment):
        """
        Pre-process comment

        :param comment:
        :return:
        """
        # Remove comment delimiters and convert to lowercase
        comment = re.sub('(//)|(/\\*)|(\\*/)', '', comment).lower()
        # Tokenize comment into sentences and words
        tokens_sentences = [self._tokenizer_words.tokenize(t) for t in nltk.sent_tokenize(comment)]
        tokens = [word for t in tokens_sentences for word in t]
        return tokens

    def prepare_comments(self, comment):
        """
        Prepare comments for machine learning model

        :return:
        """
        # Pre-process the comment
        pre_stripped = self.comment_pre_processing(comment)

        # Pad or truncate the comment based on the input size
        if len(pre_stripped) > self._size_of_input:
            new_sentence = pre_stripped[:self._size_of_input]
        else:
            num_padding = self._size_of_input - len(pre_stripped)
            new_sentence = pre_stripped + [self._padding] * num_padding

        # Convert words to word embeddings
        x_test = []
        for word in new_sentence:
            if word not in self._word_embedding_cache:
                word_embed = self._word_embedding[word]
                self._word_embedding_cache[word] = word_embed
                x_test.append(word_embed)
            else:
                x_test.append(self._word_embedding_cache[word])
        return np.array([x_test])

    def predict(self, comment):
        """
        Classify a single comment

        :param comment:
        """
        # Prepare the comment for classification
        input_x = self.prepare_comments(comment)
        
        # Make predictions using the model
        y_pred = self._model.predict(input_x)
        y_pred_bool = np.argmax(y_pred, axis=1)

        # Print the prediction results
        return self._labels[y_pred_bool[0]]

