# -*- coding: utf-8 -*-

import pickle
from simpletransformers.language_representation import RepresentationModel
from simpletransformers.config.model_args import ModelArgs

data_path = 'clinical_notes.pkl'
texts = pickle.load(open(data_path, 'rb'))

model_args = ModelArgs(max_seq_length=512, silent=True)
model = RepresentationModel(
    "bert", "emilyalsentzer/Bio_ClinicalBERT", args=model_args)
text_features = model.encode_sentences(
    texts, combine_strategy="mean")

pickle.dump([text_features], open('text_features.pkl', 'wb'))
