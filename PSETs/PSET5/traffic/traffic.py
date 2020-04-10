import cv2
import numpy as np
import os
import sys
import tensorflow as tf
from tensorflow.keras.layers import Input, Conv2D, BatchNormalization, ReLU, Add, MaxPool2D, GlobalAvgPool2D, Dense
from tensorflow.keras import Model

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
# test number of categories
# NUM_CATEGORIES = 3
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # normalize x data
    x_train, x_test = x_train/255.0, x_test/255.0

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    # https://realpython.com/working-with-files-in-python/
    # https://stackoverflow.com/questions/7762948/how-to-convert-an-rgb-image-to-numpy-array
    # https://www.tutorialkart.com/opencv/python/opencv-python-resize-image/
    images = []
    labels = []
    with os.scandir(data_dir) as dirs:
        for d in dirs:
            if (os.path.isdir(d)):
                with os.scandir(d) as files:
                    for f in files:
                        if (os.path.isfile(f)):
                            category = d.name
                            img = cv2.imread(f"{data_dir}/{category}/{f.name}", cv2.IMREAD_UNCHANGED)
                            img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT), cv2.INTER_AREA)
                            images.append(img)
                            labels.append(category)
    return (images, labels)

def conv_batchnorm_relu(x, filters, kernel_size, strides=1):
    x = Conv2D(filters=filters, kernel_size=kernel_size, strides=strides, padding='same')(x)
    x = BatchNormalization()(x)
    x = ReLU()(x)
    return x

def identity_block(tensor, filters):
    x = conv_batchnorm_relu(tensor, filters=filters, kernel_size=1, strides=1)
    x = conv_batchnorm_relu(x, filters=filters, kernel_size=3, strides=1)
    x = Conv2D(filters=4*filters, kernel_size=1, strides=1)(x)
    x = BatchNormalization()(x)
    
    x = Add()([tensor,x])
    x = ReLU()(x)
    return x

def projection_block(tensor, filters, strides):
    # left stream
    x = conv_batchnorm_relu(tensor, filters=filters, kernel_size=1, strides=strides)
    x = conv_batchnorm_relu(x, filters=filters, kernel_size=3, strides=1)
    x = Conv2D(filters=4*filters, kernel_size=1, strides=1)(x)
    x = BatchNormalization()(x)
    
    #right stream
    shortcut = Conv2D(filters=4*filters, kernel_size=1, strides=strides)(tensor)
    shortcut = BatchNormalization()(shortcut)
    x = Add()([shortcut,x])
    x = ReLU()(x)
    
    return x

def resnet_block(x, filters, reps, strides):
    x = projection_block(x, filters, strides)
    for _ in range(reps-1):
        x = identity_block(x, filters)
    return x

def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    # choosing a resnet architecture
    
    # training on the small dataset gets nearly 100% train acc but ~15% test acc, haha, overfitting
    # just trained on the full dataset, 77% train acc, 74% test acc, seems data has a 
    # regularizing/generalizing effect, which is expected since there are orders of magnitude more
    # parameters than data

    # need data augmentation and regularization
    # how is keras initializing the weights and biases?

    start = Input(shape=(IMG_WIDTH,IMG_HEIGHT,3))
    x = conv_batchnorm_relu(start, filters=64, kernel_size=7, strides=2)
    x = MaxPool2D(pool_size=3, strides=2)(x)
    x = resnet_block(x, filters=64, reps=3, strides=1)
    x = resnet_block(x, filters=128, reps=4, strides=2)
    x = resnet_block(x, filters=256, reps=6, strides=2)
    x = resnet_block(x, filters=512, reps=3, strides=2)
    x = GlobalAvgPool2D()(x)
    output = Dense(units=NUM_CATEGORIES, activation='softmax')(x)

    model = Model(inputs=start, outputs=output)

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    return model


if __name__ == "__main__":
    main()
