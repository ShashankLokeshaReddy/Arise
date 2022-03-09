import numpy as np
import pandas as pd
from datetime import timedelta

def material_check(set_date):
    """
    Generates a function that checks whether the supplier
    material has been delivered based on the given date. 
    Returns true if delivery date is in the past or
    one day after the given date. 

    Parameters
    ----------
    set_date : date
        Date on which you wish to validate avialability of material.
        Ideally this is the current date. 
    
    Returns
    ----------
    Material_check : date --> boolean
    """

    def bool_material_check(LT):
        # wenn Liefertermin nicht bekannt, dann False
        if pd.isnull(LT): 
            return False
        # wenn der morgige Tag schon weiter in der Zukunft liegt, als das Datum des Liefertermins, dann True
        elif (set_date+timedelta(days=1))>=LT: 
            return True
        else:
            return False

    return bool_material_check


def load_Schichtplaene(start, end):
    """
    Functions loads shift plans and machine specific shift plans
    from static csv-files.

    Parameters
    ----------
    start : string
        Start date of timeframe in format '%Y-%m-%d %H:%M:%S'.
    end : string
        End date of timeframe in format '%Y-%m-%d %H:%M:%S'.

    Returns
    -------
    df_Schichtplan : pd.DataFrame
        DataFrame object with shift planning for each day.
    df_Maschinenplan : pd.DataFrame
        DataFrame object with machine specific shift planning.

    """
    # Load Schichtplan and machine specific Schichtplan
    date_columns = ['DATUM', 'START', 'ENDE', 'P1_START', 'P1_ENDE',
                    'P2_START', 'P2_ENDE', 'P3_START', 'P3_ENDE']
    filepath_Werksplan = "tmp_data/Kapazitätsplanung-20220121_Werksplanung.csv"
    df_Schichtplan = pd.read_csv(filepath_Werksplan,
                                 parse_dates=date_columns)
    date_columns = ['DATUM', 'MSTART', 'MENDE', 'MP1_START', 'MP1_ENDE',
                    'MP2_START', 'MP2_ENDE', 'MP3_START', 'MP3_ENDE']
    filepath_MPlan = "tmp_data/Kapazitätsplanung-20220121_Maschinenplanung.csv"
    df_Maschinenplan = pd.read_csv(filepath_MPlan,
                                   parse_dates=date_columns)
    return df_Schichtplan, df_Maschinenplan


def load_static_orders(start, end):
    """
    Function loads orders for the specified timeframe
    from a static csv-file.

    Parameters
    ----------
    start : string
        Start date of timeframe in format '%Y-%m-%d %H:%M:%S'.
    end : string
        End date of timeframe in format '%Y-%m-%d %H:%M:%S'.

    Returns
    -------
    df : pd.DataFrame
        DataFrame object with orders and their parameters as columns.

    """
    # Load Auftragsfolgen
    df = pd.read_csv("tmp_data/Auftragsfolgen-20211207.csv")
    # Format delivery dates as date objects
    df['LTermin'] = pd.to_datetime(df['LTermin'], format='%Y-%m-%d %H:%M:%S')
    df['LTermin'] = df['LTermin'].dt.to_pydatetime()
    # Select only rows with state production and drop duplicates
    df = df[df['ID_Maschstatus'] == 1]
    df = df.drop_duplicates()
    # Timeframe
    mask = (df['LTermin'] >= start) & (df['LTermin'] < end)
    df = df.loc[mask]
    return df


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


def run_capacity_check(start, end):
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
    df_Schichtplan, df_Maschinenplan = load_Schichtplaene(start, end)
    df_order = load_static_orders(start, end)
    df_order = calculate_production_date(df_order, df_Schichtplan)
    df_order = parse_machine_number(df_order)
    df_workload = calculate_machine_workload(df_order)
    df_capacity = get_capacity(df_workload['machine_id'].unique(),
                               df_workload['date'].unique(), df_Schichtplan,
                               df_Maschinenplan)
    df_workload_capacity = df_workload.merge(df_capacity,
                                             on=['machine_id', 'date'])
    return df_order, df_workload_capacity
