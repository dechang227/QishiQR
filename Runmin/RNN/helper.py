import numpy as np
import pandas as pd
import torch

def data_generator(n_sample, n_state=3):
    index = np.random.randint(0, n_state, size=(n_sample))
    output= np.zeros((n_sample, n_state))
    for i, idx in enumerate(index):
        output[i, idx] = 1
    return output

def data_loader(dataset, device=torch.device('cpu')):
    for i in range(dataset.shape[0] - 1):
        train_data = dataset[i,:]
        #train_data = np.argmax(dataset[i:i+1,:], axis=1)
        target = np.argmax(dataset[i+1:i+2,:], axis=1)

        yield torch.from_numpy(train_data).float().view(1,1,-1).to(device), torch.from_numpy(target).to(device)


def get_direction(df, price_threshold=0.0010):
    df['Direction']= df['LastPrice'].pct_change().apply(lambda x: 2 if x > price_threshold else (1 if x < -price_threshold else 0))
    return df['Direction'].values

def to_categorical(index_label, num_classes):
    """ 1-hot encodes a tensor """
    return index_label, np.eye(num_classes, dtype='uint8')[index_label]

def to_label(categorical):
    return np.argmax(categorical, axis=1)


def predict(rnn_model, dataset, hidden_init):
    raw_result = []
    cat_result = []
    hidden = hidden_init
    for test, target in data_loader(dataset):
        pred, hidden = rnn_model(test.view(1,1,-1), hidden)
        raw_result.append(pred.view(1,-1).data.numpy().tolist())
        cat_result.append(pred.view(1,-1).data.numpy().tolist())
    raw_result = np.array(raw_result)
    cat_result = np.argmax(np.array(cat_result), axis=-1)
    return raw_result, cat_result