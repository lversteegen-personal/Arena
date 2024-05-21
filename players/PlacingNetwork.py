import keras.layers as kl
from keras.models import Model
from keras.optimizers import Adam
import keras.regularizers as regularizer
import numpy as np
import tensorflow as tf
import keras
import BoardEncoder
from Board import Board
import Data

class PlacingNetwork(keras.Model):

    def __init__(self, downstream_network, *args, **kwargs):
        super(PlacingNetwork, self).__init__(*args, **kwargs)
        tf.random.set_seed(0)
        self.downstream_network=downstream_network
        self.eval_tracker = keras.metrics.Mean("eval")

    def reset_metrics(self):
        self.eval_tracker.reset_states()

    @property
    def metrics(self):
        return [self.eval_tracker]

    tf.function
    def train_step(self: "PlacingNetwork", data):

        if data.shape[0] == 0:
            return None

        num_players = Data.num_players
        
        batch_size = tf.shape(data)[0]
        boards = tf.reshape(data,(-1,BoardEncoder.index_length,num_players))
        budgets = tf.reduce_max(boards[:,BoardEncoder.budget_index],axis=1)
        playerOneHot = boards[:,BoardEncoder.turnId_index]
        playerIds = tf.argmax(playerOneHot,axis=1)
        boards = tf.reshape(boards,(-1,BoardEncoder.index_length*num_players))

        #Compute placing and estimator
        with tf.GradientTape() as tape:
            y = self(boards, training=True)
            boards = tf.reshape(boards,(-1,BoardEncoder.index_length,num_players))
            indices = tf.concat([tf.range(batch_size,dtype=tf.int64)[:,None],tf.ones((batch_size,1),dtype=tf.int64)*BoardEncoder.budget_index,playerIds[:,None]],axis=1)
            boards = tf.tensor_scatter_nd_update(boards,indices,tf.zeros(batch_size))
            
            boards = tf.transpose(boards,[1,0,2])
            values = budgets[:,None] * y
            values = tf.transpose(values,[1,0])
            values = values[:,:,None] * boards[BoardEncoder.turnId_index][None,:,:]

            boards = tf.tensor_scatter_nd_add(boards,BoardEncoder.unit_indices[:,None],values)
            boards = tf.tensor_scatter_nd_add(boards,BoardEncoder.moveable_unit_indices[:,None],values)

            boards = tf.transpose(boards,[1,0,2])
            boards = tf.reshape(boards,(-1,BoardEncoder.index_length*num_players))

            q = tf.reduce_sum(self.downstream_network(boards) * playerOneHot, axis=1)

        # Compute gradients
        trainable_vars = self.trainable_variables
        gradients = tape.gradient(q, trainable_vars)
        gradients = [tf.negative(g) for g in gradients]

        # Update weights
        self.optimizer.apply_gradients(zip(gradients, trainable_vars))

        self.eval_tracker.update_state(tf.reduce_mean(q))
        return {m.name: m.result() for m in self.metrics}


def build(downstream_network):

    downstream_network.trainable = False
    input = kl.Input(shape=(BoardEncoder.index_length*Data.num_players,))
    x = kl.Dense(256,kernel_regularizer=regularizer.L1L2(0.001,0.01))(input)
    x = kl.LeakyReLU(alpha=0.05)(x)
    x = kl.Dense(256,kernel_regularizer=regularizer.L1L2(0.001,0.01))(x)
    x = kl.LeakyReLU(alpha=0.05)(x)
    x = kl.Dense(256,kernel_regularizer=regularizer.L1L2(0.001,0.01))(x)
    x = kl.LeakyReLU(alpha=0.05)(x)
    x = kl.Dense(Data.size,kernel_regularizer=regularizer.L1L2(0.001,0.01))(x)
    x = kl.ReLU()(x)
    x = kl.Lambda(lambda t:t+tf.constant(0.0001))(x)
    x = kl.Lambda(lambda t: t/tf.reduce_sum(t,axis=-1)[:,None])(x)

    model = PlacingNetwork(downstream_network, inputs=input, outputs=x)
    opt = Adam(learning_rate=0.001)
    model.compile(optimizer=opt,run_eagerly=False)

    return model