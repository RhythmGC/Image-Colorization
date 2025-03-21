import tensorflow as tf
import numpy as np
import cv2
import os
from tensorflow.keras.layers import BatchNormalization,LeakyReLU,Flatten
from tensorflow.keras.layers import Conv2DTranspose as Deconv2d
from tensorflow.keras.models import Model




def downsample(filters, size, apply_batchnorm=True):

  result = tf.keras.Sequential()
  result.add(tf.keras.layers.Conv2D(filters, size, strides=2, padding='same',kernel_initializer='he_normal', use_bias=False))

  if apply_batchnorm:
    result.add(tf.keras.layers.BatchNormalization())

  result.add(tf.keras.layers.LeakyReLU())
  return result


def upsample(filters, size, apply_dropout=False):

  result = tf.keras.Sequential()
  result.add(tf.keras.layers.Conv2DTranspose(filters, size, strides=2,padding='same',kernel_initializer='he_normal',use_bias=False))
  result.add(tf.keras.layers.BatchNormalization())

  if apply_dropout:
      result.add(tf.keras.layers.Dropout(0.5))

  result.add(tf.keras.layers.ReLU())
  return result


def Generator():
  inputs = tf.keras.layers.Input(shape=[256,256,3])
  
  # Define a residual block

  def residual_block(x, filters, kernel_size=3):
      shortcut = x
      
      # First convolution layer
      x = tf.keras.layers.Conv2D(filters, kernel_size, padding='same', 
                                kernel_initializer=tf.random_normal_initializer(0., 0.02))(x)
      x = tf.keras.layers.BatchNormalization()(x)
      x = tf.keras.layers.LeakyReLU(0.2)(x)
      
      # Second convolution layer
      x = tf.keras.layers.Conv2D(filters, kernel_size, padding='same',
                                kernel_initializer=tf.random_normal_initializer(0., 0.02))(x)
      x = tf.keras.layers.BatchNormalization()(x)
      
      # Add the shortcut (input) to the output
      x = tf.keras.layers.Add()([shortcut, x])
      x = tf.keras.layers.LeakyReLU(0.2)(x)
      
      return x
  
  down_stack = [
    downsample(64, 4, apply_batchnorm=False), # (bs, 128, 128, 64)
    downsample(128, 4), # (bs, 64, 64, 128)
    downsample(256, 4), # (bs, 32, 32, 256)
    downsample(512, 4), # (bs, 16, 16, 512)
    downsample(512, 4), # (bs, 8, 8, 512)
    # downsample(512, 4), # (bs, 4, 4, 512)
    # downsample(512, 4), # (bs, 2, 2, 512)
    # downsample(512, 4), # (bs, 1, 1, 512)
  ]
    
  up_stack = [
    # upsample(512, 4, apply_dropout=True), # (bs, 2, 2, 1024)
    # upsample(512, 4, apply_dropout=True), # (bs, 4, 4, 1024)
    upsample(512, 4, apply_dropout=True), # (bs, 8, 8, 1024)
    upsample(512, 4), # (bs, 16, 16, 1024)
    upsample(256, 4), # (bs, 32, 32, 512)
    upsample(128, 4), # (bs, 64, 64, 256)
    upsample(64, 4), # (bs, 128, 128, 128)
  ]
  
  initializer = tf.random_normal_initializer(0., 0.02)
  last = tf.keras.layers.Conv2DTranspose(3, 4, strides=2, padding='same', 
                                         kernel_initializer=initializer, activation='tanh') # (bs, 256, 256, 3)
  
  x = inputs
  
  # Downsampling through the model
  skips = []
  for down in down_stack:
    x = down(x)
    # Add residual blocks after each downsampling layer
    if x.shape[-1] <= 512:  # Add residual blocks for features with 512 or fewer channels
      x = residual_block(x, x.shape[-1])
    skips.append(x)
  
  skips = reversed(skips[:-1])
  
  # Upsampling and establishing the skip connections
  for up, skip in zip(up_stack, skips):
    x = up(x)
    x = tf.keras.layers.Concatenate()([x, skip])
    # Add residual blocks after each upsampling and concatenation
    if x.shape[-1] <= 1024:  # Add residual blocks for features with 1024 or fewer channels
      x = residual_block(x, x.shape[-1])
  
  x = last(x)
  
  return tf.keras.Model(inputs=inputs, outputs=x)

