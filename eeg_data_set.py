'''
File: eeg_data_set.py
Author: listenzcc
Date: 2023-01-09

The DataSet of the EEG data.
'''

# %%
import pandas as pd
from main_setup import main_setup, logger

# %%

# Require the data within the latest 10 seconds
default_latest_length_seconds = 10
# Set data limit to 1800 seconds
data_limit_seconds = 1800

# %%
default_latest_length = int(
    default_latest_length_seconds * main_setup['sample_rate'] / main_setup['interval'])
logger.info('Default latest length is set to {} seconds'.format(
    default_latest_length_seconds))

data_limit = int(data_limit_seconds *
                 main_setup['sample_rate'] / main_setup['interval'])
data_limit_overflow = int(data_limit_seconds * 1.5 *
                          main_setup['sample_rate'] / main_setup['interval'])
logger.info('Data limit is set to {} seconds'.format(data_limit_seconds))


class DataSet(object):
    ''' Main dataset of the Pseudo EEG Device Signal '''

    def __init__(self):
        self.reset()

    def reset(self):
        ''' Reset the dataset '''
        self.dataset = []

    def append(self, n, q, q2, data):
        '''
        Append the signal into the dataset

        Args:
            :param: n: The count of the signal segment;
            :param: q: The timestamp of the signal segment;
            :param: q2: The timestamp of receiving the signal segment
            :param: data: The 2D array of the signal segment
        '''

        if self.length() > data_limit_overflow:
            self.dataset = self.dataset[-data_limit >> 1:]
            logger.warning(
                'Dataset is beyond its limit * 1.5, shrinking it back to its limit')

        self.dataset.append((n, q, q2, data))

    def length(self):
        '''
        Get the length of the dataset
        '''
        return len(self.dataset)

    def get_latest(self, latest=default_latest_length):
        '''
        Convert the dataset into the dataframe

        Args:
            :param: latest: Require the latest n segments.

        Return:
            return: df: The dataframe of the dataset.
        '''
        df = pd.DataFrame(self.dataset[-latest:],
                          columns=['idx', 'query', 'query2', 'data'])

        df = df[['idx', 'query', 'query2', 'data']]
        return df

# %%
