# strategies are standard, grouped (catch all possible t_sofa and t_sus) and catchsus (catch first t_sofa but all possible t_sus)
strategy = "grouped"


if strategy == "standard":
    from SepsisCheck import sepsischeck_utilities_for_pkl as su

if strategy == "grouped":
    from SepsisCheck_grouped import sepsischeck_utilities_for_pkl_grouped as su

if strategy == "catchsus":
    from SepsisCheck_catchsus import sepsischeck_utilities_for_pkl_catchsus as su


#######################################
############# -- RUN 1 -- ###################
#######################################

# whether to ffill antibiotics or not
ffill = True 
# "sepsis-3" only checks if IV was administered / "reyna" checks if IV is administered atleast 72 hours -> set ffill to true for better chances
mode = "sepsis-3" 
#if sofa first and sep_window[0] hours no sus, or sus first and sep_window[1] hours no sofa -> no sepsis
sep_window = [24, 12]
# sus_window[0] = IV first and within sus_window[0] hours of cultures, sus_window[1] = cultures first and within sus_window[1] of IV
sus_window = [240, 240]

path = "../../data/patient/mimic_iii_preprocessed_finetuning2.pkl" #path to pkl data in format as of 19.02.23 (data[0] contains ts_ind, variables, values, std and mean; data[1] contains ts_ind, HADM_ID, SUBJECT_ID and in_hospital_sepsis)
output = "1_reyna_ffill_{}_{}-{}_{}-{}.txt".format(mode, sep_window[0], sep_window[1], sus_window[0], sus_window[1]) # path for results


#Features that are not subject to ffil, regardless of setting: "Blood Culture","text","Mechanically ventilated","Dopamine","Dobutamine","Norepinephrine","Epinephrine","blood_culture","mech",
su.run_sepsis_check_on_pkl(path, output, ffill, mode, sus_window, sep_window)


#######################################
############# RUN 2 ###################
#######################################

#if sofa first and sep_window[0] hours no sus, or sus first and sep_window[1] hours no sofa -> no sepsis
sep_window = [48, 24]
# sus_window[0] = IV first and within sus_window[0] hours of cultures, sus_window[1] = cultures first and within sus_window[1] of IV
sus_window = [168, 168]

output = "1_reyna_ffill_{}_{}-{}_{}-{}.txt".format(mode, sep_window[0], sep_window[1], sus_window[0], sus_window[1]) # path for results

#Features that are not subject to ffil, regardless of setting: "Blood Culture","text","Mechanically ventilated","Dopamine","Dobutamine","Norepinephrine","Epinephrine","blood_culture","mech",
su.run_sepsis_check_on_pkl(path, output, ffill, mode, sus_window, sep_window)


#######################################
############# RUN 3 ###################
#######################################

#if sofa first and sep_window[0] hours no sus, or sus first and sep_window[1] hours no sofa -> no sepsis
sep_window = [6, 3]
# sus_window[0] = IV first and within sus_window[0] hours of cultures, sus_window[1] = cultures first and within sus_window[1] of IV
sus_window = [1, 3]

output = "1_reyna_ffill_{}_{}-{}_{}-{}.txt".format(mode, sep_window[0], sep_window[1], sus_window[0], sus_window[1]) # path for results


#Features that are not subject to ffil, regardless of setting: "Blood Culture","text","Mechanically ventilated","Dopamine","Dobutamine","Norepinephrine","Epinephrine","blood_culture","mech",
su.run_sepsis_check_on_pkl(path, output, ffill, mode, sus_window, sep_window)

#######################################
############# RUN 4 ###################
#######################################

#if sofa first and sep_window[0] hours no sus, or sus first and sep_window[1] hours no sofa -> no sepsis
sep_window = [48, 24]
# sus_window[0] = IV first and within sus_window[0] hours of cultures, sus_window[1] = cultures first and within sus_window[1] of IV
sus_window = [24, 72]

output = "1_reyna_ffill_{}_{}-{}_{}-{}.txt".format(mode, sep_window[0], sep_window[1], sus_window[0], sus_window[1]) # path for results


#Features that are not subject to ffil, regardless of setting: "Blood Culture","text","Mechanically ventilated","Dopamine","Dobutamine","Norepinephrine","Epinephrine","blood_culture","mech",
su.run_sepsis_check_on_pkl(path, output, ffill, mode, sus_window, sep_window)