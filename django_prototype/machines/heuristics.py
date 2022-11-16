import pandas

def heuristic(df):
    df.sort_values('SchrittNr', inplace = True)
    df = df.rename(columns={'KndNr': 'AKNR', 'AKNR': 'KndNr'}) #renaming to proof the algorithm is working in the frontend
    return df



    #return queryset(df) hier müssen wir es wieder zurückverwandeln