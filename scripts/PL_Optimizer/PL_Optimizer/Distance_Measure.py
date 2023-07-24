### Distance_Measure.py ###
### Author: Philipp Hege
### Date: 09.06.2023
### Purpose: Construction of different distance measures. In addition, contains
###          a function to extract the true schedule from Schulte data.

import numpy as np
import pandas as pd
from scipy.spatial.distance import hamming as ScipyHammingDistance
from Levenshtein import distance as levenshtein_distance




def Extract_True_Schedule_From_SchulteData(SchulteData_dataframe,
                                           date_of_schedule=None):
    '''
    This function extracts the true Schedule from the Schulte data.
    For that, it takes the Schulte data and extracts the true produced schedule for a provided
    data.
    
    :param SchulteData_dataframe: pd.DataFrame. Contains the produced jobs by Schulte for many
                                  days.
    :param date_of_schedule: pd.Timestamp or datetime.datetime. The date of the day, for which
                             we want to extract the true produced schedule. If None (default)
                             it takes the whole dataframe.
                             
    :return true_schedule: np.array. The true schedule produced by Schulte on the given date.
    '''
    # bring 'Start' data to correct format if not already done
    if 'Start__YYYY_MM_DD' not in SchulteData_dataframe.columns:
        # change data types for 'Start'
        SchulteData_dataframe['Start'] = pd.to_datetime(SchulteData_dataframe['Start'])
        # create new columns with date consisting of year, month, day as datetime object
        SchulteData_dataframe['Start__YYYY_MM_DD'] = SchulteData_dataframe['Start'].apply(lambda x: x.date())
    
    # get data only for one day if we have a specific date
    if date_of_schedule is not None:
        SchulteData_dataframe = SchulteData_dataframe[SchulteData_dataframe['Start__YYYY_MM_DD'] == date_of_schedule]
    
    # generate ID as a combination of AKNR, TeilNr and SchrittNr
    SchulteData_dataframe['JOB_ID'] = SchulteData_dataframe.apply(lambda row: f'{row.AKNR}_{row.TeilNr}_{row.SchrittNr}', axis=1)
    # extract ID to np.array
    true_schedule = np.array(SchulteData_dataframe['JOB_ID'].to_list())
    
    return true_schedule




def Bring_Schedules_To_Equal_Length(schedule1, schedule2):
    '''
    Function to bring two schedules to the same length by adding zeros to the shorter schedule.
    Note: If both schedules already have the same length, nothing happens.
    
    :param schedule1: np.array. First schedule.
    :param schedule2: np.array. Second schedule.
    
    :return schedule1: np.array. First schedule after transformation.
    :return schedule2: np.array. Second schedule after transformation.
    '''
    length_difference = len(schedule1) - len(schedule2)
    if length_difference > 0:
        # schedule 1 is longer than schedule 2 -> fill schedule 2 with zeros
        schedule2 = np.append(schedule2, np.zeros(length_difference, dtype=np.int32))
    elif length_difference < 0:
        # schedule 2 is longer than schedule 1 -> fill schedule 1 with zeros
        schedule1 = np.append(schedule1, np.zeros(np.absolute(length_difference), dtype=np.int32))
    # NOTE: If length_difference == 0, do nothing
    return schedule1, schedule2




class DistanceMeasures(object):
    ''' Class that store all different kinds of Distance Measures to compare two schedules. '''
    
    def __init__(self):
        pass
    
    
    def SAE(schedule1, schedule2): # remove self from function to be able to use class without '()'
        '''
        Method that compares the total sum of absolute errors/differences between two schedules.
        I. e., we compute the difference of both first elements, take the absolute value and sum
        that for all elements of the arrays.
        
        :param schedule1: np.array. First schedule.
        :param schedule2: np.array. Second schedule.
        
        :return SSE: Float. Total sum of absolute errors/differences between schedule1 and 
                     schedule2.
        '''
        # both schedules need to have the same length
        schedule1, schedule2 = Bring_Schedules_To_Equal_Length(schedule1, schedule2)
        differences = schedule1 - schedule2 # use numpy broadcasting
        absolute_differences = np.array([np.absolute(element) for element in differences])
        return np.sum(absolute_differences)
    
    
    def SSE(schedule1, schedule2): # remove self from function to be able to use class without '()'
        '''
        Method that compares the total sum of squared errors/differences between two schedules.
        I. e., we compute the difference of both first elements, to the power of two and sum
        that for all elements of the arrays.
        
        :param schedule1: np.array. First schedule.
        :param schedule2: np.array. Second schedule.
        
        :return SSE: Float. Total sum of squared errors/differences between schedule1 and 
                     schedule2.
        '''
        # both schedules need to have the same length
        schedule1, schedule2 = Bring_Schedules_To_Equal_Length(schedule1, schedule2)
        differences = schedule1 - schedule2 # use numpy broadcasting
        squared_differences = np.array([element**2 for element in differences])
        return np.sum(squared_differences)
    
    
    def HammingDistance(schedule1, schedule2):
        '''
        Method to compute the Hamming Distance proportional to the length of the schedule.
        Based on: https://en.wikipedia.org/wiki/Hamming_distance.
        Uses Scipy: https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.hamming.html
        Note: Ranges from 0 to 1, where 0 is optimal (0 wrong positions) and 1 (equal schedules).
        
        :param schedule1: np.array. First schedule.
        :param schedule2: np.array. Second schedule.
        
        :return hamming_distance: Float. Hamming Distance divided by the length of the schedule.
        '''
        # both schedules need to have the same length
        schedule1, schedule2 = Bring_Schedules_To_Equal_Length(schedule1, schedule2)
        hamming_distance = ScipyHammingDistance(schedule1, schedule2)
        return hamming_distance
    
    
    def LevenshteinDistance(schedule1, schedule2):
        '''
        https://en.wikipedia.org/wiki/Levenshtein_distance
        '''
        distance = levenshtein_distance(schedule1, schedule2)
        return distance