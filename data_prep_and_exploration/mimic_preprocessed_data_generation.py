import pandas as pd
from tqdm import tqdm
import pickle
import numpy as np
import json

#add your path to the data 
mimic_data_dir = '/path/to/your/mimic-iii-clinical-database-1.4/'

# Read extracted time series data.
events = pd.read_csv('mimic_iii_events_text.csv', usecols=['HADM_ID', 'ICUSTAY_ID', 'CHARTTIME', 'VALUENUM', 'TABLE', 'NAME'])
icu = pd.read_csv('mimic_iii_icu_text.csv')
# Convert times to type datetime.
events.CHARTTIME = pd.to_datetime(events.CHARTTIME)
icu.INTIME = pd.to_datetime(icu.INTIME)
icu.OUTTIME = pd.to_datetime(icu.OUTTIME)

# Assign ICUSTAY_ID to rows without it. Remove rows that can't be assigned one.
icu['icustay_times'] = icu.apply(lambda x:[x.ICUSTAY_ID, x.INTIME, x.OUTTIME], axis=1)
adm_icu_times = icu.groupby('HADM_ID').agg({'icustay_times':list}).reset_index()
icu.drop(columns=['icustay_times'], inplace=True)
events = events.merge(adm_icu_times, on=['HADM_ID'], how='left')
idx = events.ICUSTAY_ID.isna()
tqdm.pandas()
def f(x):
    chart_time = x.CHARTTIME
    for icu_times in x.icustay_times:
        if icu_times[1]<=chart_time<=icu_times[2]:
            return icu_times[0]
events.loc[idx, 'ICUSTAY_ID'] = (events.loc[idx]).progress_apply(f, axis=1)
events.drop(columns=['icustay_times'], inplace=True)
events = events.loc[events.ICUSTAY_ID.notna()]
events.drop(columns=['HADM_ID'], inplace=True)

# uncomment the following part for generating the second set of experiments

# get the icu stays from the first experiment so both runs have the same patients
# with open("all_icu_stays_exp1.json", "r") as fp:
#     data = json.load(fp)

# exp1_ids = [int(x) for x in data["our_icu_ids"]]

# #ensure that both experiments have the same patients for comparison
# events = events.loc[events.ICUSTAY_ID.isin(exp1_ids)] 

# Filter icu table.
icu = icu.loc[icu.ICUSTAY_ID.isin(events.ICUSTAY_ID)]

# Get rel_charttime in minutes.
events = events.merge(icu[['ICUSTAY_ID', 'INTIME']], on='ICUSTAY_ID', how='left')
events['rel_charttime'] = events.CHARTTIME-events.INTIME
events.drop(columns=['INTIME', 'CHARTTIME'], inplace=True)
events.rel_charttime = events.rel_charttime.dt.total_seconds()//60

# Save current icu table.
icu_full = icu.copy()
# Get icustays which lasted for atleast 24 hours.
icu = icu.loc[(icu.OUTTIME-icu.INTIME)>=pd.Timedelta(24,'h')]

# Get icustays with patient alive for atleast 24 hours.
adm = pd.read_csv(mimic_data_dir+'ADMISSIONS.csv', usecols=['HADM_ID', 'DEATHTIME'])
icu = icu.merge(adm, on='HADM_ID', how='left')
icu.DEATHTIME = pd.to_datetime(icu.DEATHTIME)
icu = icu.loc[((icu.DEATHTIME-icu.INTIME)>=pd.Timedelta(24,'h'))|icu.DEATHTIME.isna()] #maybe remove

# Get icustays with aleast one event in first 24h.
icu = icu.loc[icu.ICUSTAY_ID.isin(events.loc[events.rel_charttime<24*60].ICUSTAY_ID)]

# Get sup and unsup icustays.
all_icustays = np.array(icu_full.ICUSTAY_ID)
sup_icustays = np.array(icu.ICUSTAY_ID)
unsup_icustays = np.setdiff1d(all_icustays, sup_icustays)
all_icustays = np.concatenate((sup_icustays, unsup_icustays), axis=-1)


# Get ts_ind.
def inv_list(x, start=0):
    d = {}
    for i in range(len(x)):
        d[x[i]] = i
    return d
icustay_to_ind = inv_list(all_icustays)

events['ts_ind'] = events.ICUSTAY_ID.map(icustay_to_ind)

# Rename some columns.
events.rename(columns={'rel_charttime':'minute', 'NAME':'variable', 'VALUENUM':'value'}, inplace=True)

# Add gender and age.
icu_full['ts_ind'] = icu_full.ICUSTAY_ID.map(icustay_to_ind)
data_age = icu_full[['ts_ind', 'AGE']]
data_age['variable'] = 'Age'
data_age.rename(columns={'AGE':'value'}, inplace=True)
data_gen = icu_full[['ts_ind', 'GENDER']]
data_gen.loc[data_gen.GENDER=='M', 'GENDER'] = 0
data_gen.loc[data_gen.GENDER=='F', 'GENDER'] = 1
data_gen['variable'] = 'Gender'
data_gen.rename(columns={'GENDER':'value'}, inplace=True)
data = pd.concat((data_age, data_gen), ignore_index=True)
data['minute'] = 0
events = pd.concat((data, events), ignore_index=True)


# Drop duplicate events.
events.drop_duplicates(inplace=True)


# Add mortality label.
# adm = pd.read_csv(mimic_data_dir+'ADMISSIONS.csv', usecols=['HADM_ID', 'HOSPITAL_EXPIRE_FLAG'])
# oc = icu_full[['ts_ind', 'HADM_ID', 'SUBJECT_ID']].merge(adm, on='HADM_ID', how='left')
# oc = oc.rename(columns={'HOSPITAL_EXPIRE_FLAG': 'in_hospital_mortality'})

# add sepsis label (the codes are based on the diease description in D_DIAGNOSIS)
sepsis_icd_codes = [
    "0380","03810", "03811", "03812", "03819","0382","0383","03840",
    "03841","03842","03843","03844","03849","0388","0389","67020","67022",
    "67024","67030","67032","67034","99591","99592" ]

diagnosis = pd.read_csv(mimic_data_dir+'DIAGNOSES_ICD.csv',
    usecols = ["HADM_ID","ICD9_CODE"])
diagnosis["label"] = diagnosis["ICD9_CODE"].isin(sepsis_icd_codes).astype(int)
gold = [1]
dia = diagnosis.loc[diagnosis.label.isin(gold)]
positive_adm_id = []
for x in dia["HADM_ID"]:
    positive_adm_id.append(x)
positive_hadm_id = list(set(positive_adm_id))
oc = icu_full[['ts_ind', 'HADM_ID', 'SUBJECT_ID']]
oc["in_hospital_sepsis"] = oc["HADM_ID"].isin(positive_hadm_id).astype(int)
# oc.drop_duplicates(inplace=True)


# Get train-valid-test split for sup task.
all_sup_subjects = icu.SUBJECT_ID.unique()
np.random.seed(0)
np.random.shuffle(all_sup_subjects)
S = len(all_sup_subjects)
bp1, bp2 = int(0.64*S), int(0.8*S)
train_sub = all_sup_subjects[:bp1]
valid_sub = all_sup_subjects[bp1:bp2]
test_sub = all_sup_subjects[bp2:]
icu['ts_ind'] = icu.ICUSTAY_ID.map(icustay_to_ind)
train_ind = np.array(icu.loc[icu.SUBJECT_ID.isin(train_sub)].ts_ind)
valid_ind = np.array(icu.loc[icu.SUBJECT_ID.isin(valid_sub)].ts_ind)
test_ind = np.array(icu.loc[icu.SUBJECT_ID.isin(test_sub)].ts_ind)

# Filter columns.
events = events[['ts_ind', 'minute', 'variable', 'value', 'TABLE']]


events['hour'] = events['minute']/60
events.drop(columns=['minute'], inplace=True)

# Aggregate data.
non_string_mask = events['variable'] != 'Text'
non_string_events = events[non_string_mask].copy()
note_events = events[~non_string_mask]
non_string_events['value'] = non_string_events['value'].astype(float)  # convert only the selected rows
non_string_events.loc[non_string_events['TABLE'].isna(), 'TABLE'] = 'N/A'

agg_func = {'value': 'mean', 'TABLE': 'unique'}
events = pd.concat([
    events[~non_string_mask],  # append rows that don't satisfy the condition
    non_string_events.groupby(['ts_ind', 'hour', 'variable']).agg(agg_func).reset_index()
], ignore_index=True)

events = events[['ts_ind', 'hour', 'variable', 'value', 'TABLE']]

def f(x):
    if len(x)==0:
        return x[0]   
    else:
        return ','.join(x)
events['TABLE'] = events['TABLE'].apply(f)

# needs to be solved better
events.loc[events["TABLE"] == "n,o,t,e,e,v,e,n,t,s", "TABLE"] = "noteevents"



# Save data.
pickle.dump([events, oc, train_ind, valid_ind, test_ind], open('mimic_iii_preprocessed_text.pkl','wb'))

# Normalize data and save. 
ts, oc, train_ind, valid_ind, test_ind = pickle.load(open('mimic_iii_preprocessed_text.pkl','rb'))


non_string_mask = ts['variable'] != 'Text'
ts_non_string = events[non_string_mask].copy()
means_stds = ts_non_string.groupby('variable').agg({'value':['mean', 'std']})
means_stds.columns = [col[1] for col in means_stds.columns]
means_stds.loc[means_stds['std']==0, 'std'] = 1
ts = ts.merge(means_stds.reset_index(), on='variable', how='left')
ii = ~ts.variable.isin(['Age', 'Gender', "Text"])
ts.loc[ii, 'value'] = (ts.loc[ii, 'value']-ts.loc[ii, 'mean'])/ts.loc[ii, 'std']
# ts.loc[events["TABLE"] == "noteevents", "mean"] = "1"
# ts.loc[events["TABLE"] == "noteevents", "std"] = "1"

print(oc)
pickle.dump([ts, oc, train_ind, valid_ind, test_ind], open('mimic_iii_preprocessed_text.pkl','wb'))