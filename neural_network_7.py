# -*- coding: utf-8 -*-
"""Neural_Network_7.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1O9y8tGLF_FK3DdC4clQjjOu_05X3-NOr

Трансформационная свёрточная нейронная сеть

Задача: Раскрашивание изображений серых оттенков в цветные

База данных: черно-белые и цветные фотографии, Kaggle

#Загрузка данных
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from google.colab import files
from PIL import Image
from tensorflow import keras
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import BatchNormalization, Conv2D, Dropout, InputLayer, Input, UpSampling2D, concatenate, Conv2DTranspose
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.applications import VGG16, VGG19, ResNet50
from skimage.color import rgb2lab, lab2rgb
from skimage.io import imsave
from pathlib import Path
from tqdm import tqdm
import os
import os.path
from tensorflow.keras.utils import plot_model
from IPython.display import Image

! kaggle datasets download -d theblackmamba31/landscape-image-colorization

! unzip /content/landscape-image-colorization.zip

path = '/content/landscape Images/color'

train_datagen = ImageDataGenerator(rescale=1./255)
img_size = 128
image_files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
data = pd.DataFrame({'filename': image_files})
data

"""#Предобработка данных"""

train = train_datagen.flow_from_dataframe(data,
    directory=path,
    x_col='filename',
    y_col=None,
    target_size=(img_size, img_size), #128, 128
    batch_size=5000,
    class_mode=None,
    shuffle=True)

X = []
y = []
for img in tqdm(train[0]):
    lab = rgb2lab(img)
    X.append(lab[:,:,0]) #Тут данные о яркости изображения(L)
    y.append(lab[:,:,1:] / 128) #тут данные о цветах изображения(a, b)

X = np.array(X)
y = np.array(y)
X = X.reshape(X.shape+(1,))
print(X.shape)
print(y.shape)

X_train = X[:4500]
y_train = y[:4500]

X_test = X[4500:]
y_test = y[4500:]

X_train = np.reshape(X_train, (len(X_train), 128,128,1))
y_train = np.reshape(y_train, (len(y_train), 128,128,2))
print('Train color image shape:', X_train.shape)

X_test = np.reshape(X_test, (len(X_test), 128,128,1))
y_test = np.reshape(y_test, (len(y_test), 128,128,2))
print('Test color image shape', X_test.shape)

"""#Создание и обучение нейронной сети"""

def down(filters , kernel_size, apply_batch_normalization = True):
    downsample = Sequential()
    downsample.add(Conv2D(filters,kernel_size,padding = 'same', strides = 2))
    if apply_batch_normalization:
        downsample.add(BatchNormalization())
    downsample.add(keras.layers.LeakyReLU())
    return downsample


def up(filters, kernel_size, dropout = False):
    upsample = Sequential()
    upsample.add(Conv2DTranspose(filters, kernel_size,padding = 'same', strides = 2))
    if dropout:
        upsample.dropout(0.2)
    upsample.add(keras.layers.LeakyReLU())
    return upsample

inputs = Input((128, 128, 1))

d1 = down(128, (3, 3), False)(inputs) #Без BatchNormalization()
d2 = down(128, (3, 3), False)(d1) #Без BatchNormalization()
d3 = down(256, (3, 3), True)(d2) #С BatchNormalization()
d4 = down(512, (3, 3), True)(d3) #С BatchNormalization()
d5 = down(512, (3, 3), True)(d4) #С BatchNormalization()


u1 = up(512, (3, 3), False)(d5)
u1 = concatenate([u1, d4])
u2 = up(256, (3, 3), False)(u1)
u2 = concatenate([u2, d3])
u3 = up(128, (3, 3), False)(u2)
u3 = concatenate([u3, d2])
u4 = up(128, (3, 3), False)(u3)
u4 = concatenate([u4, d1])
u5 = up(2, (3,3), False)(u4)
u5 = concatenate([u5,inputs])

outputs = Conv2D(2, (1, 1), activation='tanh', padding='same')(u5)

model = Model(inputs=inputs, outputs=outputs)

plot_model(model, to_file='model.png', show_shapes=True)
Image("model.png")

model.compile(optimizer='adam', loss='mae', metrics = ['Accuracy', 'AUC'])

callbacks = [EarlyStopping(monitor='val_loss', patience=2, verbose=1),
             ModelCheckpoint(filepath='best_model7.h5', monitor='val_loss', save_best_only=True)]

model.fit(X_train, y_train, batch_size=32, epochs=20, callbacks=callbacks, validation_split=0.1)

"""#Тестирование нейронной сети"""

model7 = keras.models.load_model('best_model7.h5')

model7.evaluate(X_test, y_test)

from skimage import color as clr
def plot_images(color,grayscale,predicted):

    plt.figure(figsize=(5 *3, 5))
    plt.subplot(1,2,1)
    plt.title('color image')

    result = np.zeros((img_size, img_size, 3))
    result[:,:,0] = grayscale.squeeze()
    result[:,:,1:] =  np.clip(color, -1, 1)*128
    get  = lab2rgb(result)
    plt.imshow(get)



    combined_lab = np.zeros((img_size, img_size, 3))
    combined_lab[:,:,0] = grayscale.squeeze()
    combined_lab[:,:,1:] = np.clip(predicted, -1, 1)*128
    # Convert LAB to RGB
    predicted_rgb = lab2rgb(combined_lab)




    # Plot L channel
    plt.subplot(1, 2, 2)
    plt.imshow(predicted_rgb)
    plt.title('Predicted image')

    plt.show()

predicted = model7.predict(X_test)
for i in range(len(predicted)):
    plot_images(y_test[i],X_test[i],predicted[i])

#С новыми файлами
from PIL import Image
from io import BytesIO
upl = files.upload()
names = list(upl.keys())
img = Image.open(BytesIO(upl[names[0]]))

def processed_image(img):
  image = img.resize( (256, 256), Image.BILINEAR)
  image = np.array(image, dtype=float)
  size = image.shape
  lab = rgb2lab(1.0/255*image)
  X, Y = lab[:,:,0], lab[:,:,1:]

  Y /= 128    # нормируем выходные значение в диапазон от -1 до 1
  X = X.reshape(1, size[0], size[1], 1)
  Y = Y.reshape(1, size[0], size[1], 2)
  return X, Y, size


X, Y, size = processed_image(img)

output = model7.predict(X)

output *= 128
min_vals, max_vals = -128, 127
ab = np.clip(output[0], min_vals, max_vals)

cur = np.zeros((size[0], size[1], 3))
cur[:,:,0] = np.clip(X[0][:,:,0], 0, 100)
cur[:,:,1:] = ab
plt.subplot(1, 2, 1)
plt.imshow(img)
plt.subplot(1, 2, 2)
plt.imshow(lab2rgb(cur))