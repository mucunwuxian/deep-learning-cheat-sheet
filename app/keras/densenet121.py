import numpy as np
from keras.layers import Input, GlobalAveragePooling2D, Concatenate
from keras.layers.core import Dense, Activation, Flatten
from keras.layers.normalization import BatchNormalization
from keras.layers.convolutional import Conv2D, MaxPooling2D, AveragePooling2D
from keras.models import Model
from keras.datasets import fashion_mnist


class DenseNet121(object):
    '''
    "Densely Connected Convolutional Networks"
    Gao Huang et al.
    https://arxiv.org/abs/1608.06993
    '''
    def __init__(self, input_shape, output_dim, k=32, theta=0.5):
        '''
        # Arguments
            k:     growth rate
            theta: compression rate
        '''
        self.k = k
        self.theta = theta

        x = Input(shape=input_shape)
        h = Conv2D(64, kernel_size=(7, 7), strides=(2, 2), padding='same')(x)
        h = BatchNormalization()(h)
        h = Activation('relu')(h)
        h = MaxPooling2D(pool_size=(3, 3), strides=(2, 2), padding='same')(h)
        h, n_channel = self._dense_block(h, 64, 6)
        h, n_channel = self._transition(h, n_channel)
        h, n_channel = self._dense_block(h, n_channel, 12)
        h, n_channel = self._transition(h, n_channel)
        h, n_channel = self._dense_block(h, n_channel, 24)
        h, n_channel = self._transition(h, n_channel)
        h, _ = self._dense_block(h, n_channel, 16)
        h = GlobalAveragePooling2D()(h)
        h = Dense(1000, activation='relu')(h)
        y = Dense(output_dim, activation='softmax')(h)
        self.model = Model(x, y)

    def __call__(self):
        return self.model

    def _dense_block(self, x, n_channel, nb_blocks):
        h = x
        for _ in range(nb_blocks):
            stream = h
            h = BatchNormalization()(h)
            h = Activation('relu')(h)
            h = Conv2D(128, kernel_size=(1, 1), padding='same')(h)
            h = BatchNormalization()(h)
            h = Activation('relu')(h)
            h = Conv2D(self.k, kernel_size=(3, 3), padding='same')(h)
            h = Concatenate()([stream, h])
            n_channel += self.k

        return h, n_channel

    def _transition(self, x, n_channel):
        n_channel = int(n_channel * self.theta)
        h = BatchNormalization()(x)
        h = Activation('relu')(h)
        h = Conv2D(n_channel, kernel_size=(1, 1), padding='same')(h)
        return AveragePooling2D()(h), n_channel


if __name__ == '__main__':
    '''
    Build model
    '''
    densenet = DenseNet121((224, 224, 3), 10)
    model = densenet()
    model.summary()
