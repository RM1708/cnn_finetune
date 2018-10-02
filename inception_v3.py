# -*- coding: utf-8 -*-
'''
@DEFECT
Throws:
    ValueError: Negative dimension size caused by subtracting 3 from 1 for 
    'conv2d_2/convolution' (op: 'Conv2D') with input shapes: 
        [?,1,149,32], [3,3,32,32].
        
Problem occurs:  
    (NOTE: Line nos are likely to differ, owing to editing. Locate the statements)
  File "/home/rm/github-cnn_fine_tune/inception_v3.py", line 273, in <module>
    model = inception_v3_model(img_rows, img_cols, channel, num_classes)

  File "/home/rm/github-cnn_fine_tune/inception_v3.py", line 93, in inception_v3_model
    x = conv2d_bn(x, 32, 3, 3, border_mode='valid')

  File "/home/rm/github-cnn_fine_tune/inception_v3.py", line 67, in conv2d_bn
    name=conv_name)(x)
    
@OBSERVATION:
    See the statement:
        img_input = Input(shape=(channel, img_rows, img_cols))
        
    It seems that Image is supposed to be in Theano format - channels as 
    dimension 0. The calling function sends it in TensorFlow format - channel
    as dimension 3.
'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

'''
#from keras.models import Sequential
from keras.optimizers import SGD
from keras.layers import Input, \
                            Dense, \
                            Convolution2D, \
                            MaxPooling2D, \
                            AveragePooling2D, \
                            Flatten, \
                            Activation, \
                            GlobalAveragePooling2D, \
                            merge
#                          ,  Reshape, \
#                            Dropout, \
                            #ZeroPadding2D
                            
from keras.layers.normalization import BatchNormalization
from keras.models import Model
#from keras import backend as K
'''
#import os
#
###########
#RM
import keras
from  keras_applications import get_keras_submodule
###########
                        
backend = get_keras_submodule('backend')
engine = get_keras_submodule('engine')
layers = get_keras_submodule('layers')
models = get_keras_submodule('models')
keras_utils = get_keras_submodule('utils')

########################
#import keras.applications.imagenet_utils as imagenet_utils
#from keras.applications.imagenet_utils import decode_predictions
#from keras_applications.imagenet_utils import _obtain_input_shape
################################################


CHANNEL_AXIS = 3

def conv2d_bn(x, \
            nb_filter, \
            nb_row, \
            nb_col, \
              padding='same', \
              strides=(1, 1), \
              name=None):
    """
    Utility function to apply conv + BN for Inception V3.
    """
    if name is not None:
        bn_name = name + '_bn'
        conv_name = name + '_conv'
    else:
        bn_name = None
        conv_name = None
#    bn_axis = 1
    bn_axis = CHANNEL_AXIS
#/home/rm/github-cnn_fine_tune/inception_v3.py:68: UserWarning: 
#    Update your `Conv2D` call to the Keras 2 API: 
#        `Conv2D(32, (3, 3), activation="relu", \
#                name=None, strides=(2, 2), padding="valid")`

#    x = Convolution2D(nb_filter, \
#                        nb_row, nb_col,
#                      subsample=subsample,
#                      activation='relu',
#                      border_mode=border_mode,
#                      name=conv_name)(x)
    ###
    # The above Convolution2D() has differences compared to the one in inception_v3_keras_application.
    # The latter is in line with the warning copied above
    #
    # Also note the stage at which the ReLu activation is applied
    
#    x = Convolution2D(nb_filter, \
    x = layers.Conv2D(nb_filter, \
                        (nb_row, nb_col),
                        strides=strides,
                        use_bias=False,
                        padding=padding,
                        name=conv_name)(x)

#    x = BatchNormalization(axis=bn_axis, name=bn_name)(x)
    x = layers.BatchNormalization(axis=bn_axis, scale=False, name=bn_name)(x)
    x = layers.Activation('relu', name=name)(x)
    return x

#def inception_v3_model(img_rows, img_cols, channel=1, num_classes=None):
def InceptionV3(img_rows, img_cols, channel=1, num_classes=1000,
                include_top=True,
                weights='imagenet',
                input_tensor=None,
                input_shape=None,
                pooling=None):
    """
    Inception-V3 Model for Keras

    Model Schema is based on 
    https://github.com/fchollet/deep-learning-models/blob/master/inception_v3.py

    ImageNet Pretrained Weights 
    https://github.com/fchollet/deep-learning-models/releases/download/v0.2/inception_v3_weights_th_dim_ordering_th_kernels.h5

    Parameters:
      img_rows, img_cols - resolution of inputs
      channel - 1 for grayscale, 3 for color 
      num_classes - number of class labels for our classification task
    """
#    channel_axis = 1
    channel_axis = CHANNEL_AXIS
    ########################################################
    #PROBLEM
    #The shape is for Theano NOT TensorFlow
    #########################################################
#    img_input = Input(shape=(channel, img_rows, img_cols))
    img_input = layers.Input(shape=(img_rows, img_cols, channel))
    
    ##########################################################
    x = conv2d_bn(img_input, 32, 3, 3, strides=(2, 2), padding='valid')
    x = conv2d_bn(x, 32, 3, 3, padding='valid')
    x = conv2d_bn(x, 64, 3, 3)
    x = layers.MaxPooling2D((3, 3), strides=(2, 2))(x)
    #-------- OK ----------------
        
    x = conv2d_bn(x, 80, 1, 1, padding='valid')
    x = conv2d_bn(x, 192, 3, 3, padding='valid')
    x = layers.MaxPooling2D((3, 3), strides=(2, 2))(x)
    #-------- OK ----------------
    
    # -------- The following 3 blocks are in a loop in inception_v3.py from github-cnn_fine_tune
    # mixed 0, 1, 2: 35 x 35 x 256
    branch1x1 = conv2d_bn(x, 64, 1, 1)

    branch5x5 = conv2d_bn(x, 48, 1, 1)
    branch5x5 = conv2d_bn(branch5x5, 64, 5, 5)

    branch3x3dbl = conv2d_bn(x, 64, 1, 1)
    branch3x3dbl = conv2d_bn(branch3x3dbl, 96, 3, 3)
    branch3x3dbl = conv2d_bn(branch3x3dbl, 96, 3, 3)

    branch_pool = layers.AveragePooling2D((3, 3),
                                          strides=(1, 1),
                                          padding='same')(x)
    branch_pool = conv2d_bn(branch_pool, 32, 1, 1)
    x = layers.concatenate(
        [branch1x1, branch5x5, branch3x3dbl, branch_pool],
        axis=channel_axis,
        name='mixed0')
    name='mixed0'
    print("DONE: ", name)

    # mixed 1: 35 x 35 x 256
    branch1x1 = conv2d_bn(x, 64, 1, 1)

    branch5x5 = conv2d_bn(x, 48, 1, 1)
    branch5x5 = conv2d_bn(branch5x5, 64, 5, 5)

    branch3x3dbl = conv2d_bn(x, 64, 1, 1)
    branch3x3dbl = conv2d_bn(branch3x3dbl, 96, 3, 3)
    branch3x3dbl = conv2d_bn(branch3x3dbl, 96, 3, 3)

    branch_pool = layers.AveragePooling2D((3, 3),
                                          strides=(1, 1),
                                          padding='same')(x)
    branch_pool = conv2d_bn(branch_pool, 64, 1, 1) #In inception_v3.py from github-cnn_fine_tune it is (branch_pool, 32, 1, 1)
    x = layers.concatenate(
        [branch1x1, branch5x5, branch3x3dbl, branch_pool],
        axis=channel_axis,
        name='mixed1')
    name='mixed1'
    print("DONE: ", name)

    # mixed 2: 35 x 35 x 256
    branch1x1 = conv2d_bn(x, 64, 1, 1)

    branch5x5 = conv2d_bn(x, 48, 1, 1)
    branch5x5 = conv2d_bn(branch5x5, 64, 5, 5)

    branch3x3dbl = conv2d_bn(x, 64, 1, 1)
    branch3x3dbl = conv2d_bn(branch3x3dbl, 96, 3, 3)
    branch3x3dbl = conv2d_bn(branch3x3dbl, 96, 3, 3)

    branch_pool = layers.AveragePooling2D((3, 3),
                                          strides=(1, 1),
                                          padding='same')(x)
    branch_pool = conv2d_bn(branch_pool, 64, 1, 1) #In inception_v3.py from github-cnn_fine_tune it is (branch_pool, 32, 1, 1)
    x = layers.concatenate(
        [branch1x1, branch5x5, branch3x3dbl, branch_pool],
        axis=channel_axis,
        name='mixed2')
    name='mixed2'
    print("DONE: ", name)
    # ------ In inception_v3.py from github-cnn_fine_tune the above 3 are in a loop
    
    # mixed 3: 17 x 17 x 768
    branch3x3 = conv2d_bn(x, 384, 3, 3, strides=(2, 2), padding='valid')

    branch3x3dbl = conv2d_bn(x, 64, 1, 1)
    branch3x3dbl = conv2d_bn(branch3x3dbl, 96, 3, 3)
    branch3x3dbl = conv2d_bn(branch3x3dbl, 96, 3, 3, \
                            strides=(2, 2), \
                            padding='valid')

    branch_pool = layers.MaxPooling2D((3, 3), strides=(2, 2))(x)
    x = layers.concatenate([branch3x3, \
                            branch3x3dbl, \
                            branch_pool],
                        axis=channel_axis,
                        name='mixed3')
    name='mixed3'
    print("DONE: ", name)
    # ------------- OK ------------------------
    
    # mixed 4: 17 x 17 x 768
    branch1x1 = conv2d_bn(x, 192, 1, 1)

    branch7x7 = conv2d_bn(x, 128, 1, 1)
    branch7x7 = conv2d_bn(branch7x7, 128, 1, 7)
    branch7x7 = conv2d_bn(branch7x7, 192, 7, 1)

    branch7x7dbl = conv2d_bn(x, 128, 1, 1)
    branch7x7dbl = conv2d_bn(branch7x7dbl, 128, 7, 1)
    branch7x7dbl = conv2d_bn(branch7x7dbl, 128, 1, 7)
    branch7x7dbl = conv2d_bn(branch7x7dbl, 128, 7, 1)
    branch7x7dbl = conv2d_bn(branch7x7dbl, 192, 1, 7)

    branch_pool = layers.AveragePooling2D((3, 3),
                                          strides=(1, 1),
                                          padding='same')(x)
    branch_pool = conv2d_bn(branch_pool, 192, 1, 1)
    x = layers.concatenate([branch1x1, \
                            branch7x7, \
                            branch7x7dbl, \
                            branch_pool],
                        axis=channel_axis,
                        name='mixed4')
    name='mixed4'
    print("DONE: ", name)
    # ------------- OK ------------------------

    # mixed 5, 6: 17 x 17 x 768
    for i in range(2):
        branch1x1 = conv2d_bn(x, 192, 1, 1)

        branch7x7 = conv2d_bn(x, 160, 1, 1)
        branch7x7 = conv2d_bn(branch7x7, 160, 1, 7)
        branch7x7 = conv2d_bn(branch7x7, 192, 7, 1)

        branch7x7dbl = conv2d_bn(x, 160, 1, 1)
        branch7x7dbl = conv2d_bn(branch7x7dbl, 160, 7, 1)
        branch7x7dbl = conv2d_bn(branch7x7dbl, 160, 1, 7)
        branch7x7dbl = conv2d_bn(branch7x7dbl, 160, 7, 1)
        branch7x7dbl = conv2d_bn(branch7x7dbl, 192, 1, 7)

        branch_pool = layers.AveragePooling2D((3, 3), \
                                                strides=(1, 1), \
                                                padding='same')(x)
        branch_pool = conv2d_bn(branch_pool, 192, 1, 1)
        x = layers.concatenate( [branch1x1, \
                                branch7x7, \
                                branch7x7dbl, \
                                branch_pool],
                            axis=channel_axis,
                            name='mixed' + str(5 + i))
        print("DONE: ", 'mixed' + str(5 + i))
    # ------------- OK ------------------------

    # mixed 7: 17 x 17 x 768
    branch1x1 = conv2d_bn(x, 192, 1, 1)

    branch7x7 = conv2d_bn(x, 192, 1, 1)
    branch7x7 = conv2d_bn(branch7x7, 192, 1, 7)
    branch7x7 = conv2d_bn(branch7x7, 192, 7, 1)

    branch7x7dbl = conv2d_bn(x, 192, 1, 1)
    branch7x7dbl = conv2d_bn(branch7x7dbl, 192, 7, 1)
    branch7x7dbl = conv2d_bn(branch7x7dbl, 192, 1, 7)
    branch7x7dbl = conv2d_bn(branch7x7dbl, 192, 7, 1)
    branch7x7dbl = conv2d_bn(branch7x7dbl, 192, 1, 7)

    branch_pool = layers.AveragePooling2D((3, 3),
                                          strides=(1, 1),
                                          padding='same')(x)
    branch_pool = conv2d_bn(branch_pool, 192, 1, 1)
    x = layers.concatenate([branch1x1, \
                            branch7x7, \
                            branch7x7dbl, \
                            branch_pool],
                        axis=channel_axis,
                        name='mixed7')
    name='mixed7'
    print("DONE: ", name)
    # ------------- OK ------------------------

    # mixed 8: 8 x 8 x 1280
    branch3x3 = conv2d_bn(x, 192, 1, 1)
    branch3x3 = conv2d_bn(branch3x3, 320, 3, 3,
                          strides=(2, 2), padding='valid')

    branch7x7x3 = conv2d_bn(x, 192, 1, 1)
    branch7x7x3 = conv2d_bn(branch7x7x3, 192, 1, 7)
    branch7x7x3 = conv2d_bn(branch7x7x3, 192, 7, 1)
    branch7x7x3 = conv2d_bn(branch7x7x3, 192, 3, 3, \
                            strides=(2, 2), \
                            padding='valid')

    branch_pool = layers.MaxPooling2D((3, 3), \
                                        strides=(2, 2))(x)
    x = layers.concatenate([branch3x3, \
                            branch7x7x3, \
                            branch_pool],
                        axis=channel_axis,
                        name='mixed8')
    name='mixed8'
    print("DONE: ", name)
    # ------------- OK ------------------------

    # mixed 9: 8 x 8 x 2048
    for i in range(2):
        branch1x1 = conv2d_bn(x, 320, 1, 1)

        branch3x3 = conv2d_bn(x, 384, 1, 1)
        branch3x3_1 = conv2d_bn(branch3x3, 384, 1, 3)
        branch3x3_2 = conv2d_bn(branch3x3, 384, 3, 1)
        branch3x3 = layers.concatenate([branch3x3_1, \
                                        branch3x3_2],
                                    axis=channel_axis,
                                    name='mixed' + str(9 + i) + \
                                    '-' + str(i) + "a")

        branch3x3dbl = conv2d_bn(x, 448, 1, 1)
        branch3x3dbl = conv2d_bn(branch3x3dbl, 384, 3, 3)
        branch3x3dbl_1 = conv2d_bn(branch3x3dbl, 384, 1, 3)
        branch3x3dbl_2 = conv2d_bn(branch3x3dbl, 384, 3, 1)
        branch3x3dbl = layers.concatenate([branch3x3dbl_1, \
                                            branch3x3dbl_2], \
                                            axis=channel_axis,
                                            name='mixed' + str(9 + i) + \
                                            '-' +str(i) + "b")

        branch_pool = layers.AveragePooling2D((3, 3), \
                                                strides=(1, 1), \
                                                padding='same')(x)
        branch_pool = conv2d_bn(branch_pool, 192, 1, 1)
        x = layers.concatenate([branch1x1, \
                                branch3x3, \
                                branch3x3dbl, \
                                branch_pool],
                            axis=channel_axis,
                            name='mixed' + str(9 + i))
        name='mixed' + str(9 + i)
        print("DONE: ", name)
    # ------------- OK ------------------------

    # From this point this differs from inception_v3_keras_application.py
    #
    # Fully Connected Softmax Layer
    
    x_fc = layers.AveragePooling2D((8, 8), strides=(8, 8), name='avg_pool')(x)
    x_fc = layers.Flatten(name='flatten')(x_fc)
    x_fc = layers.Dense(1000, \
                activation='softmax', \
                name='predictions')(x_fc)
    name='predictions'
    print("DONE: ", name)
    # Create model
    print("Creating model ...")
    model = models.Model(img_input, x_fc)
    
#    x = layers.GlobalAveragePooling2D(name='avg_pool')(x)
#    x = layers.Dense(1000, \
#                    activation='softmax', \
#                    name='predictions')(x)

    # Ensure that the model takes into account
    # any potential predecessors of `input_tensor`.
#    if input_tensor is not None:
#        assert(False)
#        if hasattr(keras_utils, 'get_source_inputs'):
#            get_source_inputs = keras_utils.get_source_inputs
#        else:
#            get_source_inputs = engine.get_source_inputs
#        inputs = get_source_inputs(input_tensor)
#    else:
#        inputs = img_input
#        
#    print("Creating model ...")
#    model = models.Model(inputs, x, name='inception_v3')
    
    # Load ImageNet pre-trained data 

    # --------------------------------------
    #inception_v3_kras_application.py loads data from    
    WEIGHTS_PATH = (
        'https://github.com/fchollet/deep-learning-models/'
        'releases/download/v0.5/'
        'inception_v3_weights_tf_dim_ordering_tf_kernels.h5')
#        WEIGHTS_PATH_NO_TOP = (
#            'https://github.com/fchollet/deep-learning-models/'
#            'releases/download/v0.5/'
#            'inception_v3_weights_tf_dim_ordering_tf_kernels_notop.h5')

    # Use the same
    # --------------------------------------
#    model.load_weights('imagenet_models/inception_v3_weights_th_dim_ordering_th_kernels.h5')
    print("Loading pre-trained weights ...")
    weights_path = keras_utils.get_file(
                        'inception_v3_weights_tf_dim_ordering_tf_kernels.h5',
                        WEIGHTS_PATH,
                        cache_subdir='models',
                        file_hash='9a0d58056eeedaa3f26cb7ebd46da564')
    model.load_weights(weights_path)
    if(1000 == num_classes):
        print("Number Of Classes is 1000. Returning ..")
        return model
    # Truncate and replace softmax layer for transfer learning
    # Cannot use model.layers.pop() since model is not of Sequential() type
    # The method below works since pre-trained weights are stored in layers but not in the model
    print("Truncate & Replace ...")
    x_newfc = layers.AveragePooling2D((8, 8), strides=(8, 8), name='avg_pool_nu')(x)
    x_newfc = layers.Flatten(name='flatten_nu')(x_newfc)
    x_newfc = layers.Dense(num_classes, \
                    activation='softmax', \
                    name='predictions_nu')(x_newfc)
    name='predictions_nu'
    print("DONE: ", name)
    # Create another model with our customized softmax
    model = models.Model(img_input, x_newfc)
    print("New Model Created.")
    
    from keras.optimizers import SGD

    # Learning rate is changed to 0.001
    sgd = SGD(lr=1e-3, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(optimizer=sgd, \
                  loss='categorical_crossentropy',\
                  metrics=['accuracy'])
    print("New Model Compiled. Return ...")
    
    return model 

import keras.applications.imagenet_utils as imagenet_utils
#from keras_applications.imagenet_utils import _obtain_input_shape

def preprocess_input(x):
    """Preprocesses a numpy array encoding a batch of images.

    # Arguments
        x: a 4D numpy array consists of RGB values within [0, 255].

    # Returns
        Preprocessed array.
    """
    return imagenet_utils.preprocess_input(x, mode='tf')

if __name__ == '__main__':
    print("\nChecking decoding of image using imagenet ...")
    import numpy as np
    from keras.preprocessing import image

    img_rows, img_cols = 299, 299 # Resolution of inputs
    channel = 3
    print("Loading model_imagenet ...")
    model_imagenet = InceptionV3(img_rows, img_cols, channel, \
                        include_top=True, weights='imagenet')

    # let's visualize layer names and layer indices to see how many layers
    # we should freeze:
    for i, layer in enumerate(model_imagenet.layers):
       print(i, layer.name)
       
    img_path = '/home/rm/tmp/Images/cat01.jpg'         #'elephant.jpg'
    img = image.load_img(img_path, target_size=(299, 299))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)

    x = preprocess_input(x)

    preds = model_imagenet.predict(x)

    from keras.applications.imagenet_utils import decode_predictions
    from pprint import pprint as pp
    print('Predicted:')
    pp(decode_predictions(preds))
    #
    # -------------------------------------------------
    # Example to fine-tune on 3000 samples from Cifar10
    print("\nModify InceptionV3 to handle CIFAR10 classes ...")
    from sklearn.metrics import log_loss
    from load_cifar10 import load_cifar10_data
    
    img_rows, img_cols = 299, 299 # Resolution of inputs
    channel = 3
    num_classes = 10 
    batch_size = 16 
    nb_epoch = 3   #10

    # Load Cifar10 data. Please implement your own load_data() module for your own dataset
    X_train, Y_train, X_valid, Y_valid = load_cifar10_data(img_rows, img_cols)
    print("Num of Training Data Images: {}. Num of Validation Images: {}".format(\
                          X_train.shape[0], X_valid.shape[0]))
    # Load our model
    print("Loading model_cifar10 ...")
    model_cifar10 = InceptionV3(img_rows, img_cols, channel, num_classes,\
                        include_top=True, weights='imagenet')
    
    # let's visualize layer names and layer indices to see how many layers
    # we should freeze:
#    for i, layer in enumerate(model_cifar10.layers):
#       print(i, layer.name)
    '''
    # we chose to train the top 2 inception blocks, i.e. we will freeze
    # the first 249 layers and unfreeze the rest:
    for layer in model_cifar10.layers[:249]:
       layer.trainable = False
    for layer in model_cifar10.layers[249:]:
       layer.trainable = True
    
    # we need to recompile the model for these modifications to take effect
    # we use SGD with a low learning rate
    from keras.optimizers import SGD
#    model_cifar10.compile(optimizer=SGD(lr=0.0001, momentum=0.9), \
#                          loss='categorical_crossentropy')

    sgd = SGD(lr=1e-3, decay=1e-6, momentum=0.9, nesterov=True)
    model_cifar10.compile(optimizer=sgd, \
                  loss='categorical_crossentropy',\
                  metrics=['accuracy'])

    # Start Fine-tuning
    print("Fine-tunng on CIFAR10 data ...")
    model_cifar10.fit(X_train[:1000], Y_train[:1000],
              batch_size=batch_size,
              nb_epoch=nb_epoch,
              shuffle=True,
              verbose=1,
              validation_data=(X_valid, Y_valid),
              )

    # Make predictions
    predictions_valid = model_cifar10.predict(X_valid, \
                                              batch_size=batch_size, \
                                              verbose=1)

    # Cross-entropy loss score
    score = log_loss(Y_valid, predictions_valid)
    print("CIFAR10 Validation Score:", score)
    '''
    print("\n\tDONE: ", __file__)

