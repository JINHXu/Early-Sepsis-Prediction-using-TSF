import pandas as pd
import numpy as np
import SepsisCheck as sc
from tqdm import *


def get_features_for_sepsischeck():
    """get list of features necessary for sepsis check, as well as place holder features used in the check"""
    sepsisfeatures = [
        "text",
        "Mechanically ventilated",
        "mech",
        "Blood Culture",
        "blood_culture",
        "Antibiotics",
        "anti",
        "Dopamine",
        "Dobutamine",
        "Epinephrine",
        "Norepinephrine",
        "GCS_motor",
        "GCS_eye",
        "GCS_verbal",
        "Platelet Count",
        "Bilirubin (Total)",
        "Creatinine Urine",
        "DBP",
        "SBP",
        "Urine",
        "FiO2",
        "Catecholamines",
    ]
    return sepsisfeatures


def restore_values(normalized, mean, std):
    """
    the preprocessing script normalizes values by '(ts.loc[ii, 'value']-ts.loc[ii, 'mean'])/ts.loc[ii, 'std'] -> normalized = (value - mean) / std -> value = normalized * std + mean'
    """
    return (normalized * std) + mean


def prepare_strats_for_sepsis(dataframe, features):
    """take Time, Label, Value, std and mean from the data
    then find unique timestamps, as we want to aggregate all features per timestep for the sepsis check
    """
    df = dataframe[["hour", "value", "variable", "mean", "std"]]
    hours = df["hour"].unique()
    timesteps = len(hours)
    patient_arr = np.empty(shape=(timesteps, len(features)))
    patient_arr[:] = np.nan
    df_new = pd.DataFrame(patient_arr, columns=features, index=hours)
    df_new = df_new.astype("str")

    """for each unique timestep, get all corresponding values and write them to df, reverse the normalization"""
    for i in hours:
        x = df["hour"] == i
        values = df[x]
        values.reset_index(inplace=True)
        try:
            if "Blood Culture" in str(values["variable"]):
                df_new.at[i, "blood_culture"] = "True"
            if "Antibiotics" in str(values["variable"]):
                df_new.at[i, "anti"] = "True"
            if "Mechanically ventilated" in str(values["variable"]):
                df_new.at[i, "mech"] = "True"
            if "Text" in str(values["variable"]):
                df_new.at[i, "text"] = values["value"]

            for k in range(0, len(values)):
                if values.at[k, "variable"] in features:
                    # print("Value",values.at[k, 'VALUE'], "Variable",values.at[k, 'LABEL'])
                    col = values.at[k, "variable"]
                    unnormalized = restore_values(
                        values.at[k, "value"], values.at[k, "mean"], values.at[k, "std"]
                    )
                    df_new.at[i, col] = unnormalized

        except Exception as e:
            print(e)
    df_temp = pd.DataFrame(df_new["text"])
    df_new.drop(
        [
            "text",
        ],
        axis=1,
        inplace=True,
    )
    df_new = df_new.replace(
        "ERROR", np.nan
    )  # some values are reported as 'ERROR' which makes conversion to float impossible
    d = df_new.join(df_temp)

    return d


def fill_data(dataframe, ffill_antibiotics):
    """
    data imputation: remove features we want to keep untouched, forward fill remaining features, reattach removed features
    """

    dataframe.replace(["None", "nan"], np.nan, inplace=True)
    # save columns we do not want to fill
    if ffill_antibiotics == True:
        df_temp = pd.DataFrame(
            dataframe[
                [
                    "Dopamine",
                    "Dobutamine",
                    "Norepinephrine",
                    "Epinephrine",
                    "blood_culture",
                    "mech",
                ]
            ]
        )
        # drop columns we do not want to fill
        dataframe.drop(
            [
                "Blood Culture",
                "text",
                "Mechanically ventilated",
                "Dopamine",
                "Dobutamine",
                "Norepinephrine",
                "Epinephrine",
                "blood_culture",
                "mech",
            ],
            axis=1,
            inplace=True,
        )
    if ffill_antibiotics == False:
        df_temp = pd.DataFrame(
            dataframe[
                [
                    "blood_culture",
                    "anti",
                    "text",
                    "mech",
                    "Dopamine",
                    "Dobutamine",
                    "Norepinephrine",
                    "Epinephrine",
                ]
            ]
        )
        dataframe.drop(
            [
                "Blood Culture",
                "blood_culture",
                "anti",
                "text",
                "Antibiotics",
                "Mechanically ventilated",
                "mech",
                "Dopamine",
                "Dobutamine",
                "Norepinephrine",
                "Epinephrine",
            ],
            axis=1,
            inplace=True,
        )

    # fill data
    dataframe.fillna(method="ffill", inplace=True)
    # dataframe.fillna(method="bfill", inplace=True)
    # dataframe.to_csv('after.tsv', sep='\t')

    # return saved columns
    d = dataframe.join(df_temp)
    # d = dataframe

    return d


def prepare_for_sofa(dataframe):
    """
    get Catecholamines and initiate as class
    set correct datatypes"""
    catecholamines = ["Dopamine", "Dobutamine", "Epinephrine", "Norepinephrine"]
    """ for each of the Catecholamines, go to the respective column, iterate through, take its value and bring it in Sofascore format."""

    for c in catecholamines:
        for i, value in enumerate(dataframe[c]):
            try:
                if str(value) == "nan":
                    pass
                else:
                    dataframe.at[i, "Catecholamines"] = sc.Catecholamine(
                        c, float(value)
                    )  # dataframe["Catecholamines"][i]
                    # print("found Catecholamine and wrote:","sc.Catecholamine({}, {})".format(c, int(value)))
            except Exception as e:
                # print("Did not find 'Dopamine', 'Dobutamine', 'Epinephrine', 'Norepinephrine'.", e)
                pass

    dataframe["Platelet Count"] = dataframe["Platelet Count"].astype(
        "float"
    )  # .astype("Int32")
    dataframe["Bilirubin (Total)"] = dataframe["Bilirubin (Total)"].astype("float")
    dataframe["Creatinine Urine"] = dataframe["Creatinine Urine"].astype("float")
    dataframe["anti"] = dataframe["anti"].map({"False": False, "True": True})
    dataframe["mech"] = dataframe["mech"].map({"False": False, "True": True})


def get_sofa(dataframe):
    """calculate sofascore and write into df"""
    dataframe["Sofa"] = np.nan
    """simply initiate the sofascore class with current patient data"""
    for i in dataframe.index:
        try:
            if dataframe["mech"][i] == True:
                mech = True
            else:
                mech = False
        except Exception as e:
            print("Mech could not be set: Setting to False.", e)
            mech = False

        try:
            GCS = (
                int(dataframe["GCS_motor"][i])
                + int(dataframe["GCS_eye"][i])
                + int(dataframe["GCS_verbal"][i])
            )
            MAP = int(dataframe["DBP"][i]) + (
                (int(dataframe["SBP"][i]) - int(dataframe["DBP"][i])) / 3
            )  # https://www.ncbi.nlm.nih.gov/books/NBK538226/
        except:
            GCS = 15  # if there's no GCS values, then use neutral value so that it does not influence the sofa score
            MAP = 71  # if there's no MAP values, then use neutral value so that it does not influence the sofa score
        cond = sc.Condition(
            MAP,
            dataframe["Catecholamines"][i],
            dataframe["Platelet Count"][i],
            dataframe["Creatinine Urine"][i],
            dataframe["Urine"][i],
            dataframe["Bilirubin (Total)"][i],
            GCS,
            dataframe["FiO2"][i],
            mech,
        )
        dataframe.at[i, "Sofa"] = sc.compute(cond)  # dataframe["Sofa"][i]


def get_sepsis(dataframe, mode, sus_window, sep_window):
    """initiate the Sepsis class with processed patient data"""

    sep = sc.Sepsis(
        list(dataframe["Sofa"]),
        dataframe["anti"],
        dataframe["blood_culture"],
        dataframe.index,
    )

    return sc.sepsis_check(sep, mode, sus_window, sep_window)


def restore_predictions(predictions, mapping, mean_stds):
    pr = []
    for pred in predictions:
        p = []
        for k, value in enumerate(pred):
            var = mapping[k]
            mean = mean_stds["mean"].loc[mean_stds["variable"] == var].item()
            std = mean_stds["std"].loc[mean_stds["variable"] == var].item()
            p.append(restore_values(value, mean, std))

        pr.append(p)

    return pd.DataFrame(pr, columns=mapping)


def get_trim_predict(trimmed_df, predicted_vals, map):
    index = list(trimmed_df.index)
    index.append(trimmed_df.index.max() + 1)
    df = trimmed_df
    l = []

    # iterate through columns of trimmed df and get predicted value -> append to list, which is then in correct order, add list as last row
    for col in trimmed_df.columns:
        if col == "Catecholamines":
            l.append("")
            continue

        if col == "Dobutamine":
            l.append("")
            continue

        if col == "text":
            l.append("")
            continue

        if col == "Sofa":
            l.append("")
            continue

        if col == "anti":
            if predicted_vals[map.index("Antibiotics")] >= (
                2.001330 * 1.0025
            ):  # TH version: 2.001330: #kmeans of all Antibiotics predictions, thresshold... basically just guessing..
                l.append("True")
                continue
            else:
                l.append("False")
                continue

        if col == "mech":
            if predicted_vals[map.index("Mechanically ventilated")] >= (
                2.0006310 * 1.0025
            ):  # TH version: 2.0006310: #kmeans of all Mech vent predictions, thresshold... basically just guessing..
                l.append("True")
                continue
            else:
                l.append("False")
                continue

        if col == "blood_culture":
            if predicted_vals[map.index("Blood Culture")] >= (
                2.002810 * 1.0025
            ):  # TH version: 2.002810: #kmeans of all Mech vent predictions, thresshold... basically just guessing..
                l.append("True")
                continue
            else:
                l.append("False")
                continue

        else:
            l.append(predicted_vals[map.index(col)])

    df = pd.concat([df, pd.DataFrame([l], columns=df.columns)], ignore_index=False)
    df.index = index

    return df


def run_Sepsis(
    patient_data,
    subject_ID,
    hadm_ID,
    ts_ind,
    features,
    ffill,
    mode,
    sus_window,
    sep_window,
    predicted,
    mapping,
    meanstd,
    run_on,
):
    """run sepsis check return the result"""

    # make patient df, renormalize values, fill data
    df = prepare_strats_for_sepsis(patient_data, features)
    df = fill_data(df, ffill)
    # get_IV_from_json(df)

    obs_windows = predicted["obs_window"].values
    predictions = restore_predictions(
        predicted["forecasting_pred"].values, mapping=mapping, mean_stds=meanstd
    )

    if run_on == "prediction":
        # make patient df, renormalize values, fill data
        df = prepare_strats_for_sepsis(patient_data, features)
        df = fill_data(df, ffill)

        obs_windows = predicted["obs_window"].values
        predictions = restore_predictions(
            predicted["forecasting_pred"].values, mapping=mapping, mean_stds=meanstd
        )

        # run sepsis check on trimmed df with predictions -> if it is never true run on full df without prediction?
        for i, window in enumerate(obs_windows):
            # trim df to obs_window length
            observed = df.loc[df.index < window]
            # df with place for the predictions, renormalize predictions, and add to end of trimmed df using mapping
            new_df = get_trim_predict(observed, predictions.loc[i], mapping)
            prepare_for_sofa(new_df)
            get_sofa(new_df)
            # run get_sepsis. if positive return, else return last run

            sepsis_label, t_sepsis, t_sofa, t_cultures, t_IV, t_sus = get_sepsis(
                new_df, mode, sus_window, sep_window
            )

            # if true for any window, return
            if sepsis_label is True:
                s = dict(
                    {
                        "Subject ID": subject_ID,
                        "Hadm_ID": hadm_ID,
                        "ts_ind": ts_ind,
                        "Sepsis": sepsis_label,
                        "t_sepsis": t_sepsis,
                        "t_sofa": t_sofa,
                        "t_cultures": t_cultures,
                        "t_IV": t_IV,
                        "t_sus": t_sus,
                    }
                )
                return str(s)
        # if all windows are exhausted, return last -> False
        s = dict(
            {
                "Subject ID": subject_ID,
                "Hadm_ID": hadm_ID,
                "ts_ind": ts_ind,
                "Sepsis": sepsis_label,
                "t_sepsis": t_sepsis,
                "t_sofa": t_sofa,
                "t_cultures": t_cultures,
                "t_IV": t_IV,
                "t_sus": t_sus,
            }
        )
        return str(s)

    if run_on == "no-prediction":
        # make patient df, renormalize values, fill data
        df = prepare_strats_for_sepsis(patient_data, features)
        df = fill_data(df, ffill)
        print("standard mode")
        prepare_for_sofa(df)
        get_sofa(df)
        sepsis_label, t_sepsis, t_sofa, t_cultures, t_IV, t_sus = get_sepsis(
            df, mode, sus_window, sep_window
        )
        s = dict(
            {
                "Subject ID": subject_ID,
                "Hadm_ID": hadm_ID,
                "ts_ind": ts_ind,
                "Sepsis": sepsis_label,
                "t_sepsis": t_sepsis,
                "t_sofa": t_sofa,
                "t_cultures": t_cultures,
                "t_IV": t_IV,
                "t_sus": t_sus,
            }
        )
        return str(s)


def get_unique_admissions(data):
    """get all unique ts_indexes"""
    return data[0]["ts_ind"].unique()


def filter_data(data, str_column, value):
    """given data, string of column and string of value, return masked data that meets the requirements"""
    m = data[str_column] == value
    t = data[m]
    return t


def run_sepsis_check_on_pkl(
    path, output, ffill, mode, sus_window, sep_window, predictions, run_on
):
    """loop the sepsis check over all ts_indexes and write results to file"""
    data = pd.read_pickle(path)
    # get predictions
    preds = pd.read_pickle(predictions)
    mapping = list(preds[1].keys())
    mean_stds = data[0][["variable", "mean", "std"]].drop_duplicates("variable")
    print(
        "Unique ts_indexes in both tables: ",
        len(data[1]["ts_ind"].unique()),
        len(data[0]["ts_ind"].unique()),
        "\nMatching ts_indexes in both tables: ",
        len(set(data[1]["ts_ind"].unique()).intersection(data[0]["ts_ind"].unique())),
        "running sepsischeck on",
        len(preds[0]["ts_ind"].unique()),
        "predictions and their seperate observation windows\nThis is the threshhold*** version.",
    )

    feats = get_features_for_sepsischeck()
    # only run on ids that we have predictions for
    IDs = get_unique_admissions(preds)
    results = []

    for ts_ind in tqdm(IDs, leave=True):
        # get patient data
        df = data[0].loc[data[0]["ts_ind"] == ts_ind]
        subject_ID = int(data[1]["SUBJECT_ID"].loc[data[1]["ts_ind"] == ts_ind])
        hadm_ID = int(data[1]["HADM_ID"].loc[data[1]["ts_ind"] == ts_ind])

        # get prediction
        pre = preds[0].loc[preds[0]["ts_ind"] == ts_ind]
        # get all observation windows and forecasting predictions
        predicted = pre[["obs_window", "forecasting_pred"]]

        # result = run_Sepsis(df, subject_ID, hadm_ID, ts_ind, feats, ffill)
        results.append(
            run_Sepsis(
                df,
                subject_ID,
                hadm_ID,
                ts_ind,
                feats,
                ffill,
                mode,
                sus_window,
                sep_window,
                predicted,
                mapping,
                mean_stds,
                run_on,
            )
        )
        # with open (output, 'a') as file:
        # file.write(result+"\n")
    file = open(output, "w")
    for result in results:
        file.write(result + "\n")
    file.close()
