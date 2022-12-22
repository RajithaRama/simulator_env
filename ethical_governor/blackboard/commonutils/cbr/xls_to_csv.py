import pandas as pd
import os

# CASE_BASE = 'casebase.json'
# df = pd.read_json(CASE_BASE, orient='records', precise_float=True)
#
# df.to_excel('data.xlsx')

CASE_BASE = 'data.xlsx'
df = pd.read_excel(CASE_BASE, header=0, index_col=None)
print(df)

df.to_json('case_base_gen.json', orient='records', indent=4)