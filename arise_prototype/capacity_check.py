import numpy as np
import pandas as pd


def parse_machine_number(df):
    """
    Function extracts the machine number of a expression in the format "SL 3"
    and gives back only the machines with a number expression.

    Parameters
    ----------
    df : pd.DataFrame
        dataframe with a column 'MaschNr' which contains a string expression
         for the machine

    Returns
    ---------
    pd.DataFrame
        Updated dataframe with new columns 'machine' and 'machine_id
    """

    df['machine'] = df.apply(lambda row: str(row['MaschNr'][:5]).strip(),
                             axis=1)
    df = df[df.machine.str.startswith('SL')]
    df['machine_id'] = df.apply(lambda row: str(row['machine'][3:]).strip(),
                                axis=1)
    return df


def new_production_date(date, df_Schichtplan):
    """
    Calculates a new production date from a given date and ensures
    that it is a workday.

    Parameters
    ----------
    date : numpy.datetime64
        Old production date or delivery date.
    df_Schichtplan : pd.DataFrame
        DataFrame with shift description. Column 'DATUM' with the date
        for each day and 'ARBEITSZEIT_MIN' the overall worktime of the day.

    Returns
    -------
    production_date : numpy.datetime64
        New production date that will be on a workday.

    """
    production_date = date - np.timedelta64(1, 'D')
    production_date = check_production_date(production_date, df_Schichtplan)
    return production_date


def check_production_date(date, df_Schichtplan):
    """
    Checks whehter the date is on a workday and otherwise computes
    the previous workday as production date.

    Parameters
    ----------
    date : np.datetime64
        Date for which shall be checked whether it is on a workday.
    df_Schichtplan : pd.DataFrame
        DataFrame with shift description. Column 'DATUM' with the date
        for each day and 'ARBEITSZEIT_MIN' the overall worktime of the day.

    Raises
    ------
    ValueError
       Raises error if the date cannot be found in the DataFrame.

    Returns
    -------
    production_date : np.datetime64
        Checked date if it is on a workday otherwise the previous workday.

    """
    if date in df_Schichtplan['DATUM'].unique():
        df_Schicht = df_Schichtplan[df_Schichtplan['DATUM'] == date]
        if df_Schicht['ARBEITSZEIT_MIN'].iloc[0] == 0:
            production_date = new_production_date(date, df_Schichtplan)
        else:
            production_date = date
    else:
        raise ValueError("Date ", date, " not found in shift plan.")
    return production_date


def calculate_production_date(df_order, df_Schichtplan):
    """
    Calculates the production date. The production date will
    be the day before delivery or the previous workday.

    Parameters
    ----------
    df_order : pd.DataFrame
        DataFrame with orders and column 'LTermin' with the
        delivery date in format 'YYYY-MM-DD HH:mm:SS'.
    df_Schichtplan : pd.DataFrame
        DataFrame with shift description. Column 'DATUM' with the date
        for each day and 'ARBEITSZEIT_MIN' the overall worktime of the day.

    Returns
    -------
    df_order : pd.DataFrame
        DataFrame with orders and additional column 'Production_date'
        with the planned production date.

    """
    delivery_date = df_order['LTermin']
    df_order['Production_date'] = delivery_date - np.timedelta64(1, 'D')
    for date in df_order['Production_date'].unique():
        approved_production_date = check_production_date(date, df_Schichtplan)
        if date != approved_production_date:
            mask = (df_order['Production_date'] == date)
            df_order['Production_date'].loc[mask] = approved_production_date
    return df_order


def calculate_machine_workload(df):
    """
    Calculates the planned runtime of the machines.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with orders and column 'Production_date' (Production date),
        'machine' (planned production machine), 'Laufzeit_Soll' (planned
        runtime).

    Returns
    -------
    df_workload : pd.DataFrame
        DataFrame with the planned production time for each machine on
        each day.

    """
    dates = df['Production_date'].unique()
    machines = df['machine_id'].unique()
    df_workload = pd.DataFrame(columns=['machine_id', 'date', 'workload'])
    for date in dates:
        for machine in machines:
            mask = (df['Production_date'] == date) & (
                df['machine_id'] == machine)
            df_date_machine = df[mask]
            workload = df_date_machine['Laufzeit_Soll'].sum()
            new_row = {'machine_id': machine, 'date': date,
                       'workload': workload}
            df_workload = df_workload.append(new_row, ignore_index=True)

    return df_workload


def get_capacity(id_machines, dates, df_Schichtplan, df_Maschinenschichten):
    """
    Gets the planned capacity of the machines from the shift
    plan and machine specific shift plan.

    Parameters
    ----------
    id_machines : array
        Array with machine ids.
    dates : array
        Array with dates.
    df_Schichtplan : pd.DataFrame
        DataFrame with shift description. Column 'DATUM' with the date
        for each day and 'ARBEITSZEIT_MIN' the overall worktime of the day.
    df_Maschinenschichten : pd.DataFrame
        DataFrame with the planned runtimes of the machines each day. Columns
        'ID_MASCHINE' (machine id), 'DATUM' (date), 'MZEIT_MIN'
        (planned runtime).

    Returns
    -------
    df_capacity : pd.DataFrame
        DataFrame with the planned capacity for each machine each day.

    """
    df_capacity = pd.DataFrame(columns=['machine_id', 'date', 'capacity'])
    print('TODO: Check if date and machine combination is unique in \
           Maschinenschichten')
    for date in dates:
        for machine in id_machines:
            mask = df_Maschinenschichten['ID_MASCHINE'] == int(machine)
            df_Maschine = df_Maschinenschichten[mask]
            if date in df_Maschine['DATUM'].unique():
                df_Maschine_Datum = df_Maschine[df_Maschine['DATUM'] == date]
                capacity = df_Maschine_Datum['MZEIT_MIN'].iloc[0]
            else:
                df_Schicht = df_Schichtplan[df_Schichtplan['DATUM'] == date]
                capacity = df_Schicht['ARBEITSZEIT_MIN'].iloc[0]
            new_row = {'machine_id': machine,
                       'date': date, 'capacity': capacity}
            df_capacity = df_capacity.append(new_row, ignore_index=True)

    return df_capacity


def run_capacity_check(df_order, df_Schichtplan, df_Maschinenplan):
    """
    Run functions to calculate production date and check capacities.

    Parameters
    ----------
    df_order : TYPE
        DESCRIPTION.
    df_Schichtplan : pd.DataFrame
        DataFrame with shift description. Column 'DATUM' with the date
        for each day and 'ARBEITSZEIT_MIN' the overall worktime of the day.
    df_Maschinenplan : pd.DataFrame
        DataFrame with the planned runtimes of the machines each day. Columns
        'ID_MASCHINE' (machine id), 'DATUM' (date), 'MZEIT_MIN'
        (planned runtime).

    Returns
    -------
    df_order : pd.DataFrame
        DataFrame with orders and column 'LTermin' (Delivery date),
        'MaschNr' (planned production machine), 'Laufzeit_Soll' (planned
        runtime).
    df_workload_capacity : pd.DataFrame
        DataFrame with the planned productiont time and capacity for
        each machine each day.

    """
    df_order = calculate_production_date(df_order, df_Schichtplan)
    df_order = parse_machine_number(df_order)
    df_workload = calculate_machine_workload(df_order)
    df_capacity = get_capacity(df_workload['machine_id'].unique(),
                               df_workload['date'].unique(), df_Schichtplan,
                               df_Maschinenplan)
    df_workload_capacity = df_workload.merge(df_capacity,
                                             on=['machine_id', 'date'])
    return df_order, df_workload_capacity
