from __future__ import division
import cv2, os
import numpy as np
import pandas as pd
from collections import defaultdict
from PIL import Image
import sys

from keras.layers import Input, Dense, Dropout, Flatten
from keras.models import Model, Sequential
from keras import applications
from keras import backend as K
K.set_image_dim_ordering('tf')

### TODO: Must be put into a config object or file
cropped_photos_folder = './cropped_photos/'
#setups labels reading from csv
labels = pd.read_csv('French_labels.txt', skipinitialspace=True, names=['labels'])

def machine_learning():
    input_tensor = Input(shape=(150, 150, 3)) #this will be size of input image
    base_model = applications.VGG16(weights='imagenet', include_top=False, input_tensor=input_tensor)

    top_model = Sequential()
    top_model.add(Flatten(input_shape=base_model.output_shape[1:]))
    top_model.add(Dense(256, activation='relu'))
    top_model.add(Dropout(0.5))
    top_model.add(Dense(31, activation='softmax'))
    top_model.load_weights('bottleneck_fc_model.h5')
    model = Model(input=(base_model.input), output=(top_model(base_model.output)))
    #ERROR: model = Model(outputs=Tensor(top_model(base_model.output)), inputs=Tensor((base_model.input)))

    return model

def cropper(original_path):
    #input example: ./file_uploads/banana_apple.jpg
    file_name = original_path.split('/')[-1] #banana_apple.jpg , banana.apple.jpg.jpg
    new_folder_name = file_name[:file_name.rfind('.')] #banana_apple,

    test_image = Image.open(original_path)
    test_image = test_image.resize((300, 300))

    cropped_paths = [] #used to have list of file paths

    image_number = 1 #used to name the file
    right = 150
    lower = 150

    for _ in range(49):
        cropped = test_image.crop((right-150, lower-150, right, lower)) #left, upper, right, lower

        #store each image
        #store into new folder
        #./cropped_photos/<filename>
        new_folder = os.path.join(cropped_photos_folder, new_folder_name)
        if not os.path.exists(new_folder):
            os.makedirs(new_folder)

        cropped_path = os.path.join(new_folder, str(image_number) + "_" +  file_name)
        cropped.save(cropped_path)
        cropped_paths.append(cropped_path.encode('utf-8'))

        right += 25
        image_number += 1

        if (image_number - 1) % 7 == 0:
            right = 150
            lower += 25
    # print cropped_paths
    return cropped_paths

def predictor(cropped_paths, model): #'/Users/philliptan/Desktop/top_left.jpg'
    answer = defaultdict(list)
    for cropped_path in cropped_paths:

        im = cv2.resize(cv2.imread(cropped_path), (150, 150)).astype(np.float32)
        im = (im / 255)

        im = np.expand_dims(im, axis=0)

        output = model.predict(im)

        top_prediction = np.argsort(-output)[:,:1][0][0]
        corresponding_softmax = output[:,top_prediction][0]
        label = str(labels.loc[top_prediction]['labels'])

        answer[label].append(corresponding_softmax)

    return answer

def predictor_counter(answer):
    label_tuples = []
    for key, val in answer.items():
        label_tuple = (len(val), key)
        label_tuples.append(label_tuple)
    #sorted label_tuples
    return list(reversed(sorted(label_tuples)))

def ingredients_list(threshold, sorted_labels):
    ingredients_list = []
    percent_sum = 0
    print sorted_labels
    for pairs in sorted_labels:
        percent_sum += pairs[0] / 49
        if percent_sum < threshold:
            ingredients_list.append(pairs[1])
        else:
            break
    if not ingredients_list:
        ingredients_list.append(pairs[1])

    return ingredients_list

def endpoint(image_path):
    model = machine_learning()
    ingredients = ingredients_list(0.667,  \
        sorted_labels=predictor_counter(predictor(cropper(image_path), model=model)))
    print ingredients
    return ingredients
