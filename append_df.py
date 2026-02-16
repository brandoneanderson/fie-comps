from parser.paths import *
import pandas as pd

'''
    Just combine the datasets
'''
B_frames = []

def combine_dataframes(frames):
    combined_df = pd.concat(frames)
    return combined_df

def convert_csv_to_df():
    df_B = []
    df_M = []

    dfB1 = pd.read_csv(OUTPUTB1_CSV)
    dfB2 = pd.read_csv(OUTPUTB2_CSV)
    dfB3 = pd.read_csv(OUTPUTB3_CSV)
    dfB4 = pd.read_csv(OUTPUTB4_CSV)
    dfB5 = pd.read_csv(OUTPUTB5_CSV)
    dfB6 = pd.read_csv(OUTPUTB6_CSV)
    dfB7 = pd.read_csv(OUTPUTB7_CSV)

    df_M = pd.read_csv(OUTPUTMCHROME_CSV)

    df_B.append(dfB1)
    df_B.append(dfB2)
    df_B.append(dfB3)
    df_B.append(dfB4)
    df_B.append(dfB5)
    df_B.append(dfB6)
    df_B.append(dfB7)


    return df_B, df_M

if __name__ == "__main__":
    
    df_B, df_M = convert_csv_to_df()
    combined_df_B = combine_dataframes(df_B)

    combined_df_B.to_csv('final_B.csv', index=False)
    df_M.to_csv('final_M.csv', index=False)