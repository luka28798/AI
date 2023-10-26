import torch
import torch.nn as nn
import torch.optim as optim
import os
import math
import numpy as np
import random
import pandas as pd
import nltk
import glob
import regex as re
from datasets import load_dataset
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AdamW,
    T5ForConditionalGeneration,
    T5TokenizerFast as T5Tokenizer,
    TrainingArguments, Trainer

)

MODEL_NAME = 't5-small'

tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME, model_max_length = 512)


checkpoint = torch.load('./model_checkpoint - cnndm.pt', map_location=torch.device('cpu')) 
new_model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME, return_dict = True)
new_model.load_state_dict(checkpoint['model_state_dict'])

optimizer = optim.AdamW(new_model.parameters(), lr = 0.0001)
optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

def summarizeText(text):
  article_encoding = tokenizer(
      text,
      max_length = 512,
      padding = 'max_length',
      truncation = True,
      return_attention_mask = True,
      add_special_tokens = True,
      return_tensors = 'pt'
  )
  
  generated_ids = new_model.generate(
      input_ids = article_encoding['input_ids'],
      attention_mask = article_encoding['attention_mask'],
      max_length = 200,
      num_beams = 2,
      repetition_penalty = 2.5,
      length_penalty = 1.0,
      early_stopping = True
  )

  preds = [
           tokenizer.decode(gen_id, skip_special_tokens = True, clean_up_tokenization_spaces = True)
           for gen_id in generated_ids
  ]
  return "".join(preds)

text = 'South African authorities are investigating the deaths of at least 22 young people in a nightclub. The victims were found strewn across floors and tables the Enyobeni Tavern in the coastal town of East London. The bodies were taken to mortuaries, where post-mortem examinations - including toxicology tests - will seek to establish a cause of death. South African President Cyril Ramaphosa expressed his "deepest condolences" to families of the victims. "This tragedy is made even more grave by its occurrence during Youth Month - a time during which we... advocate and advance opportunities for improved socio-economic conditions for the youth of our nation," he said in a tweet. Oscar Mabuyane, premier of East Cape Province where the tragedy happened, did not give possible reasons for the deaths, but condemned the "unlimited consumption of liquor". Speaking at the scene, he said: "You cannot just trade in the middle of society like this and think that young people are not going to experiment." The incident occurred in the early hours of Sunday. Those found dead were aged between 18 and 20. A provincial safety official told AFP news agency that a stampede had been ruled out as the cause of death as there were "no visible wounds". "Forensic [investigators] will take samples and test to see if there was any poisoning of any sort," Unathi Binqose said.'
print(len(summarizeText(text)))
