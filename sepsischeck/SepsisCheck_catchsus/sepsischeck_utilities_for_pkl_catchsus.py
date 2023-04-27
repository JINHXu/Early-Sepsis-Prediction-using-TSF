import pandas as pd
import numpy as np
import SepsisCheck_catchsus as sc
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
):
    """run sepsis check return the result"""
    df = prepare_strats_for_sepsis(patient_data, features)
    # df.to_csv('./data_outputs/test/{}-{}_raw.tsv'.format(subject_ID,hadm_ID), sep='\t')
    # df = explode_into_hourly(df)
    df = fill_data(df, ffill)
    # get_IV_from_json(df)
    prepare_for_sofa(df)
    # df.to_csv('./data_outputs/test/{}-{}_b4_sofa.tsv'.format(subject_ID,hadm_ID), sep='\t')
    get_sofa(df)
    # df.to_csv('./data_outputs/test/{}-{}_before_sepsis_check.tsv'.format(subject_ID,hadm_ID), sep='\t')
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


def run_sepsis_check_on_pkl(path, output, ffill, mode, sus_window, sep_window):
    """loop the sepsis check over all ts_indexes and write results to file"""
    data = pd.read_pickle(path)
    print(
        "Unique ts_indexes in both tables: ",
        len(data[1]["ts_ind"].unique()),
        len(data[0]["ts_ind"].unique()),
        "\nMatching ts_indexes in both tables: ",
        len(set(data[1]["ts_ind"].unique()).intersection(data[0]["ts_ind"].unique())),
    )
    feats = get_features_for_sepsischeck()
    IDs = get_unique_admissions(data)
    results = []

    for ts_ind in tqdm(IDs, leave=True):
        """mask = data[0]["ts_ind"] == ts_ind
        mask2 = data[1]["ts_ind"] == ts_ind

        df = data[0][mask]
        subject_ID = int(data[1][mask2]["SUBJECT_ID"])
        hadm_ID = int(data[1][mask2]["HADM_ID"])"""

        df = data[0].loc[data[0]["ts_ind"] == ts_ind]
        subject_ID = int(data[1]["SUBJECT_ID"].loc[data[1]["ts_ind"] == ts_ind])
        hadm_ID = int(data[1]["HADM_ID"].loc[data[1]["ts_ind"] == ts_ind])

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
            )
        )
        # with open (output, 'a') as file:
        # file.write(result+"\n")
    file = open(output, "w")
    for result in results:
        file.write(result + "\n")
    file.close()
