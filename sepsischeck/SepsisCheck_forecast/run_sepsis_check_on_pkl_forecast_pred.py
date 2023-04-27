# forecast = True performs SepsisCheck with added predictions of our forecast model, False only performs SepsisCheck on up to 120 hours (max observation window) of observed data
forecast = True


if forecast == True:
   import sepsischeck_utilities_for_pkl_forecast_pred as su
   run_on = "prediction" # no-prediction (only run standard check on data) / prediction (run check on predictions over all observation windows)
else:
   import sepsischeck_utilities_for_pkl_forecast_pred_cutoff as su
   run_on = "no-prediction" # no-prediction (only run standard check on data) / prediction (run check on predictions over all observation windows)


#######################################
############# -- RUN 1 -- ###################
#######################################

#if sofa first and sep_window[0] hours no sus, or sus first and sep_window[1] hours no sofa -> no sepsis
sep_window = [48, 24]
# sus_window[0] = IV first and within sus_window[0] hours of cultures, sus_window[1] = cultures first and within sus_window[1] of IV
sus_window = [24, 72]
preds = "../../data/exp1/forecasting_preds/forecasting_preds_test/content/forecasting_preds_test.pkl"
path = "../../data/exp1/forecasting_exp1/mimic_iii_preprocessed_forecasting1.pkl" #path to pkl data in format as of 19.02.23 (data[0] contains ts_ind, variables, values, std and mean; data[1] contains ts_ind, HADM_ID, SUBJECT_ID and in_hospital_sepsis)
output = "{}_prediction_{}-{}_{}-{}.txt".format("sepsis-3", sep_window[0], sep_window[1], sus_window[0], sus_window[1], run_on) # path for results


#Features that are not subject to ffil, regardless of setting: "Blood Culture","text","Mechanically ventilated","Dopamine","Dobutamine","Norepinephrine","Epinephrine","blood_culture","mech",
su.run_sepsis_check_on_pkl(path, output, False, "sepsis-3", sus_window, sep_window, preds, run_on)


"""#######################################
############# RUN 2 ###################
#######################################

#if sofa first and sep_window[0] hours no sus, or sus first and sep_window[1] hours no sofa -> no sepsis
sep_window = [12, 12]
# sus_window[0] = IV first and within sus_window[0] hours of cultures, sus_window[1] = cultures first and within sus_window[1] of IV
sus_window = [168, 168]

#Features that are not subject to ffil, regardless of setting: "Blood Culture","text","Mechanically ventilated","Dopamine","Dobutamine","Norepinephrine","Epinephrine","blood_culture","mech",
su.run_sepsis_check_on_pkl(path, output, ffill, mode, sus_window, sep_window)


#######################################
############# RUN 3 ###################
#######################################

#if sofa first and sep_window[0] hours no sus, or sus first and sep_window[1] hours no sofa -> no sepsis
sep_window = [12, 12]
# sus_window[0] = IV first and within sus_window[0] hours of cultures, sus_window[1] = cultures first and within sus_window[1] of IV
sus_window = [120, 120]

#Features that are not subject to ffil, regardless of setting: "Blood Culture","text","Mechanically ventilated","Dopamine","Dobutamine","Norepinephrine","Epinephrine","blood_culture","mech",
su.run_sepsis_check_on_pkl(path, output, ffill, mode, sus_window, sep_window)"""