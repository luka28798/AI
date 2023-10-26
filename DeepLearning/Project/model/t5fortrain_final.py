# -*- coding: utf-8 -*-
"""t5fortrain -final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1lMzwLrE1t0HxnEPwt-1eEir3Ey_wsNlD
"""

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

load_data_train = load_dataset('csv', data_files ='./cnn_dailymail/train.csv')
load_data_valid = load_dataset('csv', data_files ='./cnn_dailymail/validation.csv')

#i = 0
dataset_train = load_data_train['train']
dataset_valid = load_data_valid['train']

dataset_train[0]

from datasets import load_dataset

#articles = []
#highlights = []
load_data_train = load_dataset('csv', data_files ='./cnn_dailymail/train.csv')
load_data_valid = load_dataset('csv', data_files ='./cnn_dailymail/validation.csv')

#i = 0
dataset_train = load_data_train['train']
dataset_valid = load_data_valid['train']
articles_train = dataset_train['article'][:28000]
highlights_train = dataset_train['highlights'][:28000]
articles_valid = dataset_valid['article'][:1500]
highlights_valid = dataset_valid['highlights'][:1500]

#i = 0
#for article in articles_train:
#    article = re.findall(r"[\w']+", article)
#    articles_train[i] = article
#    i += 1
#j = 0
#for highlight in highlights_train:
#    highlight = re.findall(r"[\w']+", highlight)
#    highlights_train[j] = highlight
#    j += 1

!nvidia-smi

"""DATASET"""

class SummarizationDataset(Dataset):
  def __init__(
      self,
      data_articles: list,
      data_highlights: list,
      tokenizer = T5Tokenizer,
      article_max_token_len : int = 512,
      highlight_max_token_len : int = 128
  ):
      self.tokenizer = tokenizer
      self.data_articles = data_articles
      self.data_highlights = data_highlights
      self.article_max_token_len = article_max_token_len
      self.highlight_max_token_len = highlight_max_token_len

  def __len__(self):
      return len(self.data_articles)

  def __getitem__(self, index : int):

    article = self.data_articles[index]
    highlight = self.data_highlights[index]

    article_encoding = tokenizer(
        article,
        max_length = self.article_max_token_len,
        padding = 'max_length',
        truncation = True,
        return_attention_mask = True,
        add_special_tokens = True,
        return_tensors = 'pt'
    )
    highlight_encoding = tokenizer(
        highlight,
        max_length = self.highlight_max_token_len,
        padding = 'max_length',
        truncation = True,
        return_attention_mask = True,
        add_special_tokens = True,
        return_tensors = 'pt'
    )

    labels = highlight_encoding['input_ids']
    labels[labels == 0] = -100

    return dict(
        article = article,
        highlight = highlight,
        input_ids = article_encoding['input_ids'].flatten(),
        attention_mask = article_encoding['attention_mask'].flatten(),
        labels = labels.flatten(),
        labels_attention_mask = highlight_encoding['attention_mask'].flatten()
    )

MODEL_NAME = 't5-small'

tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME, model_max_length = 512)

article_max_token_len = 512
highlight_max_token_len = 128

ds_train = SummarizationDataset(articles_train, highlights_train, tokenizer, article_max_token_len, highlight_max_token_len)
ds_valid = SummarizationDataset(articles_valid, highlights_valid, tokenizer, article_max_token_len, highlight_max_token_len)

ds_train[4]['labels']

batch_size = 8
dl_train = DataLoader(ds_train, batch_size = batch_size, shuffle = True, num_workers = 2)
dl_valid = DataLoader(ds_valid, batch_size = batch_size, shuffle = True, num_workers = 2)

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME, return_dict = True)
model.to(device)

optimizer = optim.AdamW(model.parameters(), lr = 0.00005)

torch.cuda.empty_cache()

import gc
gc.collect()

TOKENIZERS_PARALLELISM = True

checkpoint = torch.load('./model_checkpoint.pt')
model.load_state_dict(checkpoint['model_state_dict'])
optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

epochs = 20
losses_train = []
losses_valid = []
train_losses_per_epoch = []
valid_losses_per_epoch = []
print("bzzz")

for epoch in range(epochs):
    torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'train_loss_list': train_losses_per_epoch,
            'validation_loss_list': valid_losses_per_epoch
    }, './model_checkpoint.pt')
    running_loss = 0.0
    losses_train = []
    losses_valid = []
    model.train()
    for i, data in enumerate(dl_train, 0):
        input_ids = data['input_ids'].to(device)
        attention_mask = data['attention_mask'].to(device)
        labels =  data['labels'].to(device)
        decoder_attention_mask = data['labels_attention_mask'].to(device)
        optimizer.zero_grad()
        output_loss = model(input_ids = input_ids, attention_mask = attention_mask, decoder_attention_mask = decoder_attention_mask, labels = labels).loss
        losses_train.append(output_loss.item())

        output_loss.backward()
        optimizer.step()

        running_loss += output_loss.item()

        if i % 500 == 499:
            print(f'[{epoch + 1}, {i + 1:2d}] loss: {running_loss / 500:.3f}')
            running_loss = 0.0

    validation_running_loss = 0.0
    model.eval()
    with torch.no_grad():
        for j, data_val in enumerate(dl_valid, 0):
            input_ids_val = data_val['input_ids'].to(device)
            attention_mask_val = data_val['attention_mask'].to(device)
            decoder_attention_mask_val = data_val['labels_attention_mask'].to(device)
            labels_val =  data_val['labels'].to(device)
            output_loss_val = model(input_ids = input_ids_val, attention_mask = attention_mask_val, decoder_attention_mask = decoder_attention_mask_val, labels = labels_val).loss
            losses_valid.append(output_loss_val.item())
            validation_running_loss += output_loss_val.item()
            if j % 50 == 49:
                print(f'[{epoch + 1}, {j + 1:2d}] validation_loss: {validation_running_loss / 50:.3f}')
                validation_running_loss = 0.0
    train_losses_per_epoch.append(losses_train)
    valid_losses_per_epoch.append(losses_valid)
    print(f'Epoch {epoch + 1} / {epochs} train_loss : {output_loss} validation_loss: {output_loss_val}')

"""# Novi odjeljak

# Novi odjeljak
"""

times_train = [i for i in range(0, len(losses_train))]

len(losses_valid)

times_valid = [i for i in range(0, len(losses_valid))]

import matplotlib.pyplot as plt

fig = plt.figure()
ax0 = fig.add_subplot(121, title="loss")
ax0.plot(times_train, losses_train, label='train')
ax0.plot(times_valid, losses_valid, label='val')

new_model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME, return_dict = True)

checkpoint = torch.load('./model_checkpoint.pt')
new_model.load_state_dict(checkpoint['model_state_dict'])
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
      max_length = 150,
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

sample_row = articles_train[2]
#text = 'South African authorities are investigating the deaths of at least 22 young people in a nightclub. The victims were found strewn across floors and tables the Enyobeni Tavern in the coastal town of East London. The bodies were taken to mortuaries, where post-mortem examinations - including toxicology tests - will seek to establish a cause of death. South African President Cyril Ramaphosa expressed his "deepest condolences" to families of the victims. "This tragedy is made even more grave by its occurrence during Youth Month - a time during which we... advocate and advance opportunities for improved socio-economic conditions for the youth of our nation," he said in a tweet. Oscar Mabuyane, premier of East Cape Province where the tragedy happened, did not give possible reasons for the deaths, but condemned the "unlimited consumption of liquor". Speaking at the scene, he said: "You cannot just trade in the middle of society like this and think that young people are not going to experiment." The incident occurred in the early hours of Sunday. Those found dead were aged between 18 and 20. A provincial safety official told AFP news agency that a stampede had been ruled out as the cause of death as there were "no visible wounds". "Forensic [investigators] will take samples and test to see if there was any poisoning of any sort," Unathi Binqose said.'
text = sample_row
#text = 'Stam spices up Man Utd encounter\n \nAC Milan defender Jaap Stam says Manchester United "know they made a mistake" by selling him in 2001.\n\nThe sides meet at Old Trafford in the Champions League game on Wednesday and the 32-year-old\'s Dutchman\'s presence is sure to add spice to the fixture. "United made a mistake in selling me," Stam told Uefa\'s Champions magazine. "I was settled at Manchester United, but they wanted to sell me. If a club want to sell you, there is nothing you can do. You can be sold like cattle." Sir Alex Ferguson surprised the football world - and Stam - by selling the Dutchman to Lazio for 16.5m in August 2001. The decision came shortly after Stam claimed in his autobiography that Ferguson had tapped him up when he was at PSV Eindhoven. But Ferguson insisted he sold the defender because the transfer fee was too good to refuse for a player past his prime. The affair still rankles with the Dutchman.\n\n"I was settled at Manchester United, I had even just ordered a new kitchen, but they wanted to sell me," he said. "In what other industry can a good employee be ushered out the door against their wishes? "Of course, you can refuse to go, but then the club have the power to put you on the bench. I don\'t agree that players control the game. "There have been opportunities to confront them in the newspapers, but I have turned them down. What\'s the point?"\n\nWednesday\'s game at Old Trafford will provide an intriguing confrontation between United\'s young attackers Wayne Rooney and Cristiano Ronaldo and Milan\'s veteran defence of Stam, Paolo Maldini, Cafu and Alessandro Costacurta. Stam says Rooney\'s teenage stardom is in stark contract to his own start in the game. "We can\'t all be Wayne Rooneys - at his age I was training to be an electrician and thought my chance of becoming a professional footballer had gone," he said. "Starting late can be a good thing. Some kids who start early get bored. "I had my youth - having fun, drinking beers, blowing up milk cannisters. It sounds strange but it\'s a tradition where I grew up in Kampen - and I had done all the things I wanted to do."\n'
model_summary = summarizeText(text)
text

model_summary

highlights_train[2]

load_data_test = load_dataset('csv', data_files ='./cnn_dailymail/test.csv')
dataset_test = load_data_test['train']

predictions = []
references = []

for i in range(0, 10):
    predictions.append(summarizeText(dataset_test['article'][i]))
    references.append(dataset_test['highlights'][i])

import datasets

!pip install rouge_score

rouge = datasets.load_metric('rouge')
results = rouge.compute(predictions=predictions, references=references)

from evaluate-metric import evaluate

rouge = evaluate.load('rouge')
results = rouge.compute(predictions=predictions, references=references)

from rouge_score import rouge_scorer, scoring

rouge_types = ["rouge1", "rouge2", "rougeL", "rougeLsum"]

scorer = rouge_scorer.RougeScorer(rouge_types=rouge_types)

for ref, pred in zip(references, predictions):
    score = scorer.score(ref, pred)

    scores.append(score)

scores = []

scores[2]

for result in results.values():
    print(result)