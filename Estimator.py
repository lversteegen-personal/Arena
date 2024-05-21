import keras.layers as kl
from keras.models import Model
from keras.optimizers import Adam
import keras.regularizers as regularizer
import numpy as np
import BoardEncoder
import Data

def build():

    input = kl.Input(shape=(BoardEncoder.index_length*Data.num_players,))
    x = kl.Dense(256,kernel_regularizer=regularizer.L1L2(0.001,0.01))(input)
    x = kl.LeakyReLU(alpha=0.05)(x)
    x = kl.Dense(256,kernel_regularizer=regularizer.L1L2(0.001,0.01))(x)
    x = kl.LeakyReLU(alpha=0.05)(x)
    x = kl.Dense(256,kernel_regularizer=regularizer.L1L2(0.001,0.01))(x)
    x = kl.LeakyReLU(alpha=0.05)(x)
    x = kl.Dense(Data.num_players,kernel_regularizer=regularizer.L1L2(0.001,0.01))(x)
    #x = kl.Activation(activation="sigmoid")(x)

    model = Model(inputs=input, outputs=x)
    opt = Adam(learning_rate=0.001)
    model.compile(optimizer=opt, loss="mean_squared_error")

    return model



