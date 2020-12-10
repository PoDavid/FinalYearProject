import string
import pandas as pd
import csv
import operator

def test_df(infile):
    df = pd.read_csv(infile, engine='python')
    print(type(df))
    print(df.head(5))
    frames = [df,df,df,df,df]
    result = pd.concat(frames)
    print(result.head(5))
    print(result.shape)
    print(result.index)
def formatting():
    text = "5844-9821-f3ad"
    text = text.replace('-','')
    newtext = ':'.join(text[i:i + 2] for i in range(0, 12, 2))
    print(newtext)
def main():
    #csv_file = "../sortlog/h3c-wx7-20161118/h3c-wx7-20161118-warning-clean/h3c-wx7-20161118-hh3cDot11APMtChlIntfDetected.csv"
    #test_df(csv_file)
    formatting()

if __name__ == '__main__':
    main()