import pandas as pd
from sys import argv

# combine a list of xlsx files into one
def combine_xlsx_files(output_file, files):
    df = pd.DataFrame()
    for file in files:
        print("Reading", file)
        df = pd.concat([df, pd.read_excel(file)], ignore_index=True)
    # remove all rows where text is an empty string
    df = df[df['text'] != '']
    df.to_excel(output_file, index=False)
    print("Length of combined file", len(df))

if __name__ == "__main__":
    files = argv[1:]
    combine_xlsx_files("combined_wsj.xlsx", files)