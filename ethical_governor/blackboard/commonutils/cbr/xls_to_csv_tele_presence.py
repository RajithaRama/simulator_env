import pandas as pd
import os

# CASE_BASE = 'casebase.json'
# df = pd.read_json(CASE_BASE, orient='records', precise_float=True)
#
# df.to_excel('data.xlsx')

CASE_BASE = 'data_telepresence.xlsx'
df = pd.read_excel(CASE_BASE, header=0, index_col=None, keep_default_na=False, dtype={"other_patient_locations": list, 
    "on_call": bool, 
    "receiver_seen": bool,	
    "receiver_preference": bool, 
    "worker_seen": bool,
    "worker_preference": bool,
    "other_patient_seen": bool})
# df.astype({
#     "other_patient_locations": list, 
#     "on_call": bool, 
#     "receiver_seen": bool,	
#     "receiver_preference": bool, 
#     "worker_seen": bool,
#     "worker_preference": bool,
#     "other_patient_seen": bool
# })

df = df.replace({'': None})

print(df)
print(df.dtypes)

df.to_json('case_base_gen_telepresence.json', orient='records', indent=4)