### Inner_Optimization.py ###
### Author: Philipp Hege
### Date: 20.04.2023
### Purpose: Construction of the inner optimization model. Gets a set of jobs 
###          and generates a production schedule.

import numpy as np
import pandas as pd
import gurobipy as gp
from Setup_Time_Prediction.SetupTime_Prediction import Estimator as SetupTimeEstimator




def time_difference(t0, t1):
    '''
    A function to compute the difference in time between to timestamps in minutes.
    Computes t1 - t0.
    
    :param t0: pd.Timestamp or datetime.datetime. First element of the difference.
    :param t1: pd.Timestamp or datetime.datetime. Second element of the difference.
    
    :return diff_minutes: Integer. Integer of time difference of t1-t0 in minutes.
    '''
    # compute difference
    diff = t1 - t0
    # extract difference in seconds first, then calculate minutes. If there is a rest, drop it.
    # -> ignore rest in seconds! (Here ok because the whole problem operates in minutes)
    diff_seconds = diff.days * 24 * 3600 + diff.seconds
    diff_minutes = diff_seconds // 60 # '//' makes integer division
    return diff_minutes




def time_difference_plus_Timestamp(timestamp, difference_minutes):
    '''
    :param timestamp: pd.Timestamp or datetime.datetime. First element of the sum.
    :param difference_minutes: Int. Time difference in minutes.
    
    :return: pd.Timestamp. New Timestamp after adding minutes to the original Timestamp.
    '''
    # ensure that timestamp is a pd.Timestamp and add difference in minutes via pd.Timedelta
    return pd.Timestamp(timestamp) + pd.Timedelta(minutes=difference_minutes)




def Preprocess_SchulteData(dataframe,
                           production_start):
    '''
    Function to preprocess the Schulte data. Takes a dataframe of Schulte data and computes
    all necessary data for the optimization problem in the needed structure.
    
    :param dataframe: pd.DataFrame. Contains the raw data provided by Schulte.
    :param production_start: pd.Timestamp or datetime.datetime. Marks the begin in production.
    
    :return job_ID: List. Contains the unique job IDs of Schulte data in whatever data format.
    :return processing_time: List. Contains all processing times of the raw dataframe as integers.
    :return release_date: List. Contains all release dates of the raw dataframe as differences
                          to parameter production_time as integers.
    :return due_date: List. Contains all due dates of the raw dataframe as differences to 
                      parameter production_time as integers.
    '''
    # build job_id of the original Schulte data
    dataframe['JOB_ID'] = dataframe.apply(lambda row: f'{row.AKNR}_{row.TeilNr}_{row.SchrittNr}', axis=1)
    
    # create lists to store data
    job_ID, processing_time, release_date, due_date = [], [], [], []
        
    # go over all rows of the dataframe
    for ID in dataframe.index:
        row = dataframe.iloc[ID, :]
        # compute values and add to list
        job_ID.append(row['JOB_ID'])
        processing_time.append(row['Laufzeit_Soll'])
        release_date.append(time_difference(production_start, row['Release_Date']))
        # ggf. max(0, time_difference(production_start, row['Release_Date'])), damit immer > 0
        due_date.append(time_difference(production_start, row['Due_Date']))
        # ggf. max(0, time_difference(production_start, row['Due_Date'])), damit immer > 0
    return job_ID, processing_time, release_date, due_date




def InnerOptimization(SchulteData,
                      meta_params={'Makespan': 1,
                                   'Lateness': 1,
                                   'PointEstimatorAddOn': 1},
                      production_start=None,
                      return_schedule_as_dataframe=False,
                      print_output=True):
    '''
    Function that contains the whole inner optimization proccess.
    Takes the Schulte Data, converts it to the format needed and optimizes.
    Optimization results are returned.

    :param SchulteData: pd.DataFrame. Contains all  necessary data which is
                        provided by Schulte.
    :param meta_params: Dict. Contains all meta-parameters, that influence the
                        inner optimization. Default: All 1 yields no weighting.
    :param production_start: pd.Timestamp or datetime.datetime. Default: None. If none, the
                             production_start used is the minimum of the Release_Date of the 
                             dataframe provided. Marks the begin in production.  
    :param return_schedule_as_dataframe: Bool. If true, the schedule is returned
                                         as an entire schedule. Otherwise only
                                         an array of the ordered job IDs is returned.
    :param print_output: Bool. If True, output is printed, if False none of the
                         outputs is printed.
                         
    :return:
        ...either...
    schedule: np.array. Contains the job ids in the order of production. Hence, 
                        for JobOrder_result = np.array([3, 1, 2]) we produce
                        Job 3, then Job 1 followed by Job 2.
        ...or...
    schedule_df: pd.DataFrame. Contains the scheduled jobs in correct order with
                corresponding setup times, start and end times.
    '''
    # based on: http://yetanothermathprogrammingconsultant.blogspot.com/2018/09/scheduling-sequence-dependent-setup.html
    # --> GIT: https://github.com/google/or-tools/blob/master/examples/python/single_machine_scheduling_with_setup_release_due_dates_sat.py
    
    # define model
    model = gp.Model('SM-JSSP-SDST') # Simple Machine Job-Shop Scheduling with Sequence-Dependent Setup-Times
    
    # compute default production start, if none is given
    if production_start is None:
        production_start = np.min(SchulteData.Release_Date)
    assert production_start <= np.min(SchulteData.Release_Date), 'Procution start is not before \
earliest release date!'

    ### PARAMETERS ### (extract from data)
    setup_time = SetupTimeEstimator(SchulteData)
    job_ID, processing_time, release_date, due_date = Preprocess_SchulteData(SchulteData,
                                                                             production_start)
    # precedence = [(0, 2), (1, 2)]
    
    # calculate number of jobs and set of jobs as range object
    NUM_JOBS = len(processing_time)
    JOBS = np.arange(NUM_JOBS)
    
    # define big M for constraint (6)
    bigM = 100_000
    
    
    ### VARIABLES ###
    # First job; 1 if jj is first job, zero else
    First = [model.addVar(name=f'First_{jj}', vtype=gp.GRB.BINARY) for jj in JOBS]
    # Last job; 1 if jj is last job, zero else
    Last = [model.addVar(name=f'Last_{jj}', vtype=gp.GRB.BINARY) for jj in JOBS]
    # Job order; 1 if job jj follows job ii, zero else
    X = [[model.addVar(name=f'First_{ii}_{jj}', vtype=gp.GRB.BINARY) for jj in JOBS]for ii in JOBS]
    # Start time of job jj after setup
    StartTime = [model.addVar(name=f'StartTime_{jj}', vtype=gp.GRB.CONTINUOUS, lb=0) for jj in JOBS]
    # End time/completion time of last job (note: not a duration but a point in time)
    LastTime = model.addVar(name='LastTime', vtype=gp.GRB.CONTINUOUS, lb=0)
    # Delay/Lateness of each Job (if negative, job is finished earlier than deadline)
    Lateness = [model.addVar(name=f'Lateness_{jj}', vtype=gp.GRB.CONTINUOUS, lb=-np.inf) for jj in JOBS]


    ### OBJECTIVE ###
    # Make add on to point estimations of sequence-depentend setup-times by factor
    setup_time *= meta_params['PointEstimatorAddOn']
    # Minimization of the end time of the last job produced
    model.setObjective(meta_params['Makespan']*LastTime + meta_params['Lateness']*sum(Lateness), gp.GRB.MINIMIZE)
    # model.setObjective(meta_params['Makespan']*LastTime + sum(meta_params['Lateness']*Lateness[jj] for jj in JOBS), gp.GRB.MINIMIZE) ODER SO??
    if print_output != True:
        model.Params.OutputFlag = 0 # mute all outputs/console prints
    model.Params.MIPFocus = 1 # forces fast solving
    model.Params.TimeLimit = 10 # timelimit in seconds
    #model.Params.SolutionLimit = 5 # number of solutions found
    
    
    ### CONSTRAINTS ###
    # (1) Exactly one first job
    model.addConstr(sum(First[jj] for jj in JOBS) == 1)
    # (2) Exactly one last job
    model.addConstr(sum(Last[jj] for jj in JOBS) == 1)
    # (3) Job ii is either the last job or ii has exactly one successor
    for ii in JOBS:
        model.addConstr(Last[ii] + sum(X[ii][jj] for jj in JOBS if jj != ii) == 1)
    # (4) Job jj is either the first job or jj has exactly one predecessor
    for jj in JOBS:
        model.addConstr(First[jj] + sum(X[ii][jj] for ii in JOBS if ii != jj) == 1)
    # (5) Calculate StartTime of first job (if jj is not first job, constraint vanishes since
    #     in that case right side of it equals zero).
    for jj in JOBS:
        model.addConstr(StartTime[jj] >= setup_time[0][jj] * First[jj]) # NOTE: setup_time is not N x N but (N+1) x N !!! -> First index must be treated differently
    # (6) Calculate StartTime, if job jj is produced after job ii (if not, big M makes constraint
    #     non-binding).
    print("StartTime[jj]:",StartTime[jj])
    print("StartTime[ii]:",StartTime[ii])
    print("processing_time:",processing_time[ii], type(processing_time[ii]))
    print("setup_time[ii+1][jj]:",setup_time[ii+1][jj], type(setup_time[ii+1][jj]))
    print("bigM:",bigM)
    print("X:",X[ii][jj])
    print("End")
    for jj in JOBS:
        for ii in JOBS:
            if ii != jj:
                # NOTE: setup_time has different first index (due to initial setup times stored in the first row, which is why we have to use ii+1 instead of ii !!!
                model.addConstr(StartTime[jj] >= StartTime[ii] + processing_time[ii]\
                               + setup_time[ii+1][jj] - bigM * (1 - X[ii][jj]))
    # (7) Calculate end time (Only for last job interesting, but constraint holds for all jobs jj.)
    for jj in JOBS:
        model.addConstr(LastTime >= StartTime[jj] + processing_time[jj])
        #model.addConstr(LastTime >= (StartTime[jj] + processing_time[jj])*Last[jj])
    # (8) Each job jj is started producing after its release date.
    for jj in JOBS:
        model.addConstr(StartTime[jj] >= release_date[jj])
    # (9) Each job jj is finished producing before its due date/deadline.
    # for jj in JOBS:
    #     model.addConstr(StartTime[jj] <= due_date[jj] - processing_time[jj])
    # (9) Lateness constraint: Lateness is allowed (=finishing after deadline) but with penalty
    for jj in JOBS:
        model.addConstr(Lateness[jj] == (StartTime[jj] + processing_time[jj]) - due_date[jj])
        # model.addConstr(Lateness[jj] - Earlyness[jj] == (StartTime[jj] + processing_time[jj]) - due_date[jj])
    # [(10) Precedence constraints]
    # for ii, jj in precedence:
    #     model.addConstr(StartTime[jj] >= StartTime[ii] + processing_time[ii])
     
    
    # optimize model
    model.optimize()
    
    # compute end results and show solution
    #First_result = [First[jj].x for jj in JOBS]
    #Last_result = [Last[jj].x for jj in JOBS]
    #X_result = [[X[ii][jj].x for jj in JOBS] for ii in JOBS]
    StartTime_result = [StartTime[jj].x for jj in JOBS]
    LastTime_result = LastTime.x # =model.objVal
    
    # compute list of job jj
    JOB_LIST = np.array([job for job in range(NUM_JOBS)])
    # compute ordered job with index jj (JobOrder_result) and with job_IDs (schedule)
    JobOrder_result = JOB_LIST[np.argsort(StartTime_result)]
    schedule = np.array(job_ID)[np.argsort(StartTime_result)]
    
        
    if print_output:
        print(f'\n\nThe total makespan of {NUM_JOBS} jobs is {LastTime_result:.2f}.\n')
        for jj in JOBS:
            print(f'Job {schedule[jj]} is produced at position {jj+1:2.0f} starting at \
{StartTime_result[JobOrder_result[jj]]:8.2f}.')
    
    if return_schedule_as_dataframe == False:
        return schedule
    
    else: # return_schedule_as_dataframe==True
        # compute final setup times, start and end times for all scheduled jobs (start and end as timestamps)
        # get final setup times
        setup_time_result_sorted = []
        prev = 0
        for ID in JobOrder_result:
            setup_time_result_sorted.append(round(setup_time[prev][ID], 2))
            prev = ID+1
        setup_time_result_sorted = np.array(setup_time_result_sorted)
        # get final start times
        StartTime_Timestamp_result = [time_difference_plus_Timestamp(production_start, round(start_time, 2)) for start_time in StartTime_result]
        StartTime_Timestamp_result_sorted = np.sort(StartTime_Timestamp_result)
        # get final end times
        EndTime_result = StartTime_result + np.array(processing_time)
        EndTime_Timestamp_result = [time_difference_plus_Timestamp(production_start, round(end_time, 2)) for end_time in EndTime_result]
        EndTime_Timestamp_result_sorted = np.sort(EndTime_Timestamp_result)
        
        # take original Schulte data as output dataframe and add final setup times, start and end times
        schedule_df = SchulteData.set_index('JOB_ID').loc[schedule, ['FEFCO_Teil', 
                                                                     'ArtNr_Teil', 
                                                                     'AKNR', 
                                                                     'TeilNr',
                                                                     'SchrittNr', 
                                                                     'Maschine',
                                                                     'Start', 
                                                                     'Ende', 
                                                                     'Ruestzeit_Ist',
                                                                     'Ruestzeit_Soll',
                                                                     'Laufzeit_Soll',
                                                                     'Lieferdatum_Rohmaterial', 
                                                                     'Due_Date']]
        schedule_df['Start'] = StartTime_Timestamp_result_sorted
        schedule_df['Ende'] = EndTime_Timestamp_result_sorted
        schedule_df['Ruestzeit_Ist'] = setup_time_result_sorted
        # return final schedule as dataframe of jobs with corresponding setup times, start and end times
        return schedule_df




