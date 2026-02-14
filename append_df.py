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

    dfM1 = pd.read_csv(OUTPUTM1_CSV)
    dfM2 = pd.read_csv(OUTPUTM2_CSV)
    dfM3 = pd.read_csv(OUTPUTM3_CSV)
    dfM4 = pd.read_csv(OUTPUTM4_CSV)
    # dfM5 = pd.read_csv(OUTPUTM5_CSV)
    # dfM6 = pd.read_csv(OUTPUTM6_CSV)
    df_B.append(dfB1)
    df_B.append(dfB2)
    df_B.append(dfB3)
    df_B.append(dfB4)
    df_B.append(dfB5)
    df_B.append(dfB6)

    df_M.append(dfM1)
    df_M.append(dfM2)
    df_M.append(dfM3)
    df_M.append(dfM4)
    # df_M.append(dfM5)
    # df_M.append(dfM6)


    return df_B, df_M

if __name__ == "__main__":

    print(OUTPUTB1_CSV)
    
    df_B, df_M = convert_csv_to_df()
    combined_df_B = combine_dataframes(df_B)
    combined_df_M = combine_dataframes(df_M)

    combined_df_B.to_csv('final_B', index=False)
    combined_df_M.to_csv('final_M', index=False)