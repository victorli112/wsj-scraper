import pandas as pd
# combine two xlsx files into one
def combine_xlsx_files(file1, file2, output_file):
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)
    df = pd.concat([df1, df2], ignore_index=True)
    # remove all rows where text is an empty string
    df = df[df['text'] != '']
    df.to_excel(output_file, index=False)
    print(len(df))

combine_xlsx_files("wsj_data.xlsx", "wsj_data2.xlsx", "wsj_data_combined.xlsx")