### Outer_Optimization.py ###
### Author: Philipp Hege
### Date: 16.06.2023
### Purpose: Construction of the outer optimization model. Includes the outer
###          optimization loop, meta-parameter vector and the combination with
###          distance measure and inner optimization.

from Inner_Optimization import InnerOptimization
from Distance_Measure import DistanceMeasures, Extract_True_Schedule_From_SchulteData


 

def OuterOptimization(Schulte_data,
                      meta_params,
                      print_output=True):
    '''
    Optimization of the meta parameters. Therefore: Compares schedule generated
    by Inner Optimization with the true schedule produced by Schulte.
    
    :param Schulte_data: pd.DataFrame. Contains all  necessary data which is
                         provided by Schulte.
    :param meta_params: Dict. Contains all meta-parameters, that influence the
                        inner optimization. Default: All 1 yields no weighting.
    :param print_output: Bool. Default: True. If True, output is printed, if 
                         False none of the outputs is printed.
                         
    :return score: Float. Score of the distance measure which indicates, how 
                   similar the generated schedule and the true schedule are.
    '''
    generated_schedule = InnerOptimization(Schulte_data,
                                           meta_params,
                                           print_output=print_output)
    true_Schulte_schedule = Extract_True_Schedule_From_SchulteData(Schulte_data)
    score = DistanceMeasures.HammingDistance(generated_schedule, true_Schulte_schedule)
    return score