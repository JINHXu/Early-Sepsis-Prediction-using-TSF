import sepsischeck_utilities_for_pkl as su

path = "./data/patient/mimic_iii_preprocessed_finetuning2.pkl" #path to pkl data in format as of 19.02.23 (data[0] contains ts_ind, variables, values, std and mean; data[1] contains ts_ind, HADM_ID, SUBJECT_ID and in_hospital_sepsis)
output = "results_ffill.txt" # path for results

""" 
Features that are not subject to ffil, regardless of setting: "Blood Culture","text","Mechanically ventilated","Dopamine","Dobutamine","Norepinephrine","Epinephrine","blood_culture","mech","""
ffill = True #whether to ffill antibiotics or not
su.run_sepsis_check_on_pkl(path, output, ffill)