from manager_old import *
from ML_manager import *
import pandas as pd


'''
    File to seperate our scanner into two parts
    1. Scan the extension and return a dataframe of the extracted features
    2. Query the ML model to produce an output
'''
if __name__ == "__main__":
    my_bibID = "phidhnmbkbkbkbknhldmpmnacgicphkf"
    ext_df = Scan_Extension(my_bibID)
    query_model(ext_df)
