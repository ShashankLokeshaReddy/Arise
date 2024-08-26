### SetupTime_Prediction ###

### Author: Arne Henning Witteborg
### Date: 01.06.2023
### Purpose: Calculation of the setup-times-matrix for the inner optimization 
###          model. Consists of the individual sequence-dependent setup-times. 
###          Gets a set of jobs and generates the corresponding setup-times-matrix.

import numpy as np
import pandas as pd
import xgboost as xgb
import pickle
import os




def Estimator(raw_data_arise):
    '''
    Pass
    
    :param dataframe: pd.DataFrame. Contains set of jobs of Schulte. The column names have to be the same as in the sample_arise dataset.
    
    :return setup_time_matrix: np.array. (N+1) x N matrix for N as number of jobs.
                               Contains the sequence-dependent setup-times for all jobs i in N with
                               first row as the initial job (setup-time before first job is ready
                               to produce).
    '''
    
    #Preprocessing the input dataframe:
    
    df = raw_data_arise.copy()
    df['FEFCO_Teil'] = df['FEFCO_Teil'].astype(str)
    df['FEFCO_Code'] = df['FEFCO_Teil'].str.extract(r'(\d{4})').fillna(df['FEFCO_Teil'].str.extract(r'(\d{3})')) #The four or three digit FEFCO-code is extracted from the cell contents
    df['FEFCO_Code'] = df['FEFCO_Code'].astype(str).apply(lambda x: x.zfill(4) if len(x) == 3 else x) #In case only three digits of the FEFCO-code are specified, it is expanded to four.
    
    #Creating the input data for the prediction model by generating a new dataframe with each FEFCO-Code combination of the input dataframe and the corresponding ID_Druck:
    
    repeated_categories = df['FEFCO_Code'].repeat(len(df)+1)
    repeated_id = df['ID_Druck'].repeat(len(df)+1)
    
    repeated_codes = []
    repeat_sequence = list(df['FEFCO_Code'])

    for item in repeat_sequence:
        modified_sequence = [item] + repeat_sequence
        repeated_codes.extend(modified_sequence)
        
        
    prediction_data_categorial = pd.DataFrame({'FEFCO_Category': repeated_categories, 'Prev_FEFCO_Category': repeated_codes , 'ID_DRUCK': repeated_id})
    
    #Loading the required files:
    
    directory = 'scripts/PL_Optimizer/PL_Optimizer/Setup_Time_Prediction'
    encoder_name = 'Encoder.pkl'
    model_name = 'SetupTime_Prediction.json'
    with open(os.path.join(directory, encoder_name), 'rb') as file:
        encoder = pickle.load(file)
    model = xgb.XGBRegressor()
    model.load_model(os.path.join(directory, model_name))
    
    #Encoding of the categorial features for the model:
    
    prediction_data_categorial_encoded = encoder.transform(prediction_data_categorial)
    
    #Applying the model on the encoded data and transform it into the (N+1) x N matrix:
    
    setup_time_matrix = model.predict(prediction_data_categorial_encoded)
    setup_time_matrix = np.reshape(setup_time_matrix, (len(df)+1, len((df))))
    np.fill_diagonal(setup_time_matrix[1:, :], 0)  
    
    return setup_time_matrix