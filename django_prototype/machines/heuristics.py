import pandas

def heuristic(df):
    df.sort_values('SchrittNr', inplace = True)
    return df



    #return queryset(df) hier müssen wir es wieder zurückverwandeln