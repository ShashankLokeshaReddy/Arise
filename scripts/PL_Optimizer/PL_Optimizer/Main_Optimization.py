### Main_Optimization.py ###
### Author: Philipp Hege
### Date: 04.07.2023
### Purpose: Total optimization of the outer optimization (including the inner
###          optimization).

from Inner_Optimization import InnerOptimization
from Outer_Optimization import OuterOptimization
import optuna # pip install optuna




def Optimization(Schulte_data):
    '''
    Function that combines the whole optimization. Gets the Schulte data and 
    returns the bet schedule as well as the best meta parameter combination
    as a result of the whole optimization process.

    :param Schulte_data: pd.DataFrame. Contains set of jobs of Schulte.
    
    :return best_schedule_df: pd.DataFrame. Contains the scheduled jobs in correct 
                              order with corresponding setup times, start and end 
                              times. Best schedule resulting from the main optimization.
    :return best_meta_params: Dict. Contains the best meta parameters resulting
                              from the outer optimization.
    '''
    
    def OPTUNA_objective(trial):
        ''' Objective for OPTUNA. Follows the conventional syntax required by OPTUNA. '''
        # define meta-parameters
        Makespan = trial.suggest_float('Makespan', 0.1, 10)
        Lateness = trial.suggest_float('Lateness', 0.1, 10)
        PointEstimatorAddOn = trial.suggest_float('PointEstimatorAddOn', 0.9, 1.5)
        meta_params = {'Makespan': Makespan,
                       'Lateness': Lateness,
                       'PointEstimatorAddOn': PointEstimatorAddOn}
        # call outer optimization with different meta-parameters
        return OuterOptimization(Schulte_data, meta_params, print_output=False)
    
    # make optimization of meta-parameters with OPTUNA
    study = optuna.create_study()
    study.optimize(OPTUNA_objective, n_trials=10)
    # extract best meta-parameters
    best_meta_params = study.best_params
    
    # get schedule from optimizer with best meta-parameters
    best_schedule_df = InnerOptimization(Schulte_data,
                                         best_meta_params,
                                         return_schedule_as_dataframe=True,
                                         print_output=False)
    
    return best_schedule_df, best_meta_params