# -*- coding: utf-8 -*-
"""Neural_Network_9.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1bp21BSt-4p9Oz5-ya1XkiQ5kUSvbrY7K

Реккурентные нейронные сети

Задача: прогнозирование слов

База данных: своя, просто текст

#Загрузка данных
"""

import os
import numpy as np
import re

from tensorflow.keras.saving import save_model, load_model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.layers import Dense, SimpleRNN, Input, Embedding, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.text import Tokenizer, text_to_word_sequence
from tensorflow.keras.utils import to_categorical

with open('/content/Униженные и оскорбленные.txt', 'r', encoding='utf-8') as f:
    text = f.read()
    text = text.replace('\ufeff', '')
    text = re.sub(r'[^А-я ]', '', text)

"""#Предоработка данных"""

maxWordsCount = 2000
tokenizer = Tokenizer(num_words=maxWordsCount, filters='!–"—#$%&amp;()*+,-./:;<=>?@[\\]^_`{|}~\t\n\r«»',
                      lower=True, split=' ', char_level=False)
tokenizer.fit_on_texts([text])

dist = list(tokenizer.word_counts.items())
print(dist)

data = tokenizer.texts_to_sequences([text])
res = np.array( data[0] )

inp_words = 4 #Количество слов для предсказания
n = res.shape[0] - inp_words

X = np.array([res[i:i + inp_words] for i in range(n)])
y = to_categorical(res[inp_words:], num_classes=maxWordsCount)

"""#Создание и обучение нейронной сети"""

model = Sequential()
model.add(Input((4, )))
model.add(Embedding(2000, 256))
model.add(Dropout(0.8))
model.add(SimpleRNN(256, activation='tanh'))
model.add(Dense(128, activation='relu'))
model.add(Dense(2000, activation='softmax'))
model.summary()

model.compile(loss='categorical_crossentropy', metrics=['accuracy'], optimizer='adam')

callbacks = [EarlyStopping(monitor='loss', patience=3, verbose=1),
             ModelCheckpoint(filepath='best_model9.h5.keras', monitor='loss', save_best_only=True)]

history = model.fit(X, y, batch_size=32, epochs=40)

model9 = save_model(model, 'best_model9.h5.keras')

"""#Тестирование нейронной сети"""

model9 = load_model('best_model9.h5.keras')

def buildPhrase(texts, str_len=20):
    res = texts
    data = tokenizer.texts_to_sequences([texts])[0]
    for i in range(str_len):
        x = data[i: i + inp_words]
        inp = np.expand_dims(x, axis=0)

        pred = model9.predict(inp, verbose=False)
        indx = pred.argmax(axis=1)[0]
        data.append(indx)

        res += " " + tokenizer.index_word[indx]

    return res

res = buildPhrase('Я не буду')
print(res)