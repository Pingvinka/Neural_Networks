"""
Итак, чисто ради практики и личного понимания я сейчас буду делать нейронку небольшую. Хочу попрактиковаться на уже излюбленном датасете Ирисов (ну, помним, да?)

Задача многоклассовой (3) классификации

База данных: Ирисы Фишера
"""
"""#Загрузка данных"""

from sklearn import datasets
iris = datasets.load_iris()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tensorflow import keras
from keras.activations import softmax
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import SGD
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical

data = pd.DataFrame(data= np.hstack([iris['data'], np.atleast_2d(iris['target_names'][iris['target']]).T]),
                 columns= iris['feature_names']+['species'])
data.iloc[50:]

"""#Предобработка данных"""

data['species'].value_counts(normalize=True) #Проверяю масштабируемость данных
data.isna().sum() #Проверяю данные на пропуски (в случае появления: если пропусков мало - удали, если много - замени)
data['species'].unique() #Это понадобиться для следующей функции
X = data.drop('species', axis=1)

#Код ниже написан не до конца (для нейронной сети, которую я хотела построить). А всё потому, что вместе y = [0, 1, 1, 2, 0, ...] мне нужны были значения y = [[1, 0, 0], [0, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 0], ...], чтобы использовать функцию активации softmax. Вот и вся проблема!
def not_categorical(value):
    if value == "setosa":
      return 0
    elif value == "versicolor":
      return 1
    elif value == "virginica":
      return 2
data['species'] = data['species'].apply(not_categorical) #Убираем категориальные значения
data

#Снизу то, что я добавила после
y = data['species']
y = to_categorical(y, num_classes=3)
y

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(X_train)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

"""#Создание и обучение нейронной сети"""

model = Sequential()
model.add(Dense(80, activation='relu'))
model.add(Dense(40, activation='relu'))
model.add(Dense(3, activation='softmax'))

model.compile(optimizer='adam',
              loss = 'categorical_crossentropy',
              metrics = ['accuracy'])

# Обучение модели
history = model.fit(X_train,
                    y_train,
                    epochs=100,
                    batch_size=100,
                    validation_split=0.2,
                    verbose=0)

plt.plot(history.history['accuracy'], label = 'Верные ответы при обучении')
plt.plot(history.history['val_accuracy'], label = 'Верные ответы при проверке')
plt.xlabel('эпоха')
plt.ylabel('верные ответы')
plt.legend()
plt.show()

"""#Тестирование нейронной сети"""

loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
print(f"Loss: {loss:.4f}, Accuracy: {accuracy:.4f}")

#Проверка на абсолютно новых данных
new_data = {'sepal length (cm)': [5.0, 6.0, 7.1],
            'sepal width (cm)': [3.6, 2.9, 3.3],
            'petal length (cm)': [1.3, 5.0, 4.6],
            'petal width (cm)': [0.3, 1.9, 1.4]}
df = pd.DataFrame(new_data)
df = scaler.transform(df)
a = model.predict(df)
a

for i in range(0,3):
  print(np.argmax(a[i]))
