# README

## Files:

- Distance_Measure.py
- Inner_Optimization.py
- Main_Optimization.py
- Outer_Optimization.py

### Folder: Setup_Time_Prediction:

- Encoder.pkl
- SetupTime_Prediction.json
- SetupTime_Prediction.py

## Prerequisites

Required python packages (please consider the version numer for SciKit Learn, XGBoost):

- [SciKit Learn (1.2.1)](https://scikit-learn.org/stable/)
- [XGBoost (1.7.3 or higher)](https://xgboost.readthedocs.io/en/stable/install.html)
- [Pickle](https://docs.python.org/3/library/pickle.html)
- [Gurobipy](https://support.gurobi.com/hc/en-us/articles/360044290292-How-do-I-install-Gurobi-for-Python-)
- [MIP](https://www.python-mip.com)
- [Optuna](https://optuna.org)
- [Datetime](https://docs.python.org/3/library/datetime.html)
- [Numpy](https://numpy.org)
- [Pandas](https://pandas.pydata.org/docs/getting_started/overview.html)
- [Levenshtein](https://pypi.org/project/python-Levenshtein/)
- [SciPy](https://scipy.org)
- [Datetime](https://docs.python.org/3/library/datetime.html)
- [os](https://docs.python.org/3/library/os.html)

## SetupTime_Prediction.py

Consists of SetupTime_Prediction.py, Encoder.pkl and SetupTime_Prediction.json. The python file is called by the "Inner Optimization" and takes the jobs characteristics to generate a matrix of setup time for each job and the possible following jobs. For this prediction, the SetupTime_Prediction.json and Encoder.pkl files are used. The .json file contains the prediction model itself while the Encoder secures the correct data processing. The setup time prediction process returns a matrix that is used in "Inner_Optimization.py".

## Inner_Optimization.py

Takes the Input data, calls the "Setup Time Prediction" and starts the optimization of the production schedule via the Gurobi Solver and returns a schedule of the jobs for the defined time horizon.

## Outer_Optimization.py

Calls the "Inner Optimization" to retrieve the generated schedule from the optimization as well as the schedule for comparison from the historical data. For this purpose, the Distance_Measure.py file is called which extracts the schedule for comparison. Within these two schedules a score for comparison is calculated by using a distance measure from Distance_Measure.py.

## Distance_Measure.py:

For comparison purposes the true job schedule from the Schulte data is extracted and preprocessed. The file also contains multiple distance metrics from which the Levenshtein distance is used in the current version and called in the "Outer Optimization".

## Main_Optimization.py

The Optimizer.py can be seen as the main function. It contains the initializion of the whole optimization process with the inner and outer optimization. In the first step the outer optimization is called which triggers the inner optimization for the first time. "Main_Optimization" contains the optimization of meta-parameters using the black box optimizer Optuna and returns the best meta parameters applied on the first optimization loop. With the updated meta-parameters the "Main_Optimization" reinitialzes the inner optimization and returns the final schedule and the meta-paramter vector.