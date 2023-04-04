# -*- coding: utf-8 -*-
"""
Copyright 2021 shimst3r @ https://github.com/shimst3r/sofascore
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
sofascore computes the Sepsis-related Organ Failure Assessment (SOFA) score
according to Singer et al.:
    https://doi.org/10.1001%2Fjama.2016.0287
"""


"""
This file contains a modified version of sofascore Copyright 2021 shimst3r @ https://github.com/shimst3r/sofascore
The modifications were implemented to work together with the implementation of sepsis-3 requirements.
"""

from typing import NamedTuple, Optional

__version__ = "1.2.0"


class Catecholamine(NamedTuple):
    """
    Optional dosages, only cardiovascular (for SOFA-scores 2 to 4)
    """

    name: str
    dosage: float


class Condition(NamedTuple):
    """
    Computes SOFA-Score at the time where it is called. -> Monitor this score over time for sepsis check.
    Respiration - PaO2/FiO2 (mmHg): 'partial_pressure_of_oxygen: float' & 'is_mechanically_ventilated: bool' -> 'compute_score_for_respiratory_system'
    Coagulation - Platelets (× 103/μL): 'platelets_count: int' -> 'compute_score_for_coagulation'
    Liver - Bilirubin (mg/dl): 'bilirubin_level: float' -> 'compute_score_for_liver'
    Cardiovascular: 'mean_arterial_pressure: float' & 'catecholamine: Optional[Catecholamine]' -> 'compute_score_for_cardiovascular_system'
    Central nervous system - Glasgow Coma Scale score: 'glasgow_coma_scale: int' -> 'compute_score_for_nervous_system'
    Renal - Creatinine (mg/dl) or Urine output (mL/d): 'creatinine_level: float' & 'urine_output: float' -> 'compute_score_for_kidneys'
    """

    mean_arterial_pressure: float
    catecholamine: Optional[Catecholamine]
    platelets_count: int
    creatinine_level: float
    urine_output: float
    bilirubin_level: float
    glasgow_coma_scale: int
    partial_pressure_of_oxygen: float
    is_mechanically_ventilated: bool


def compute(condition: Condition) -> int:
    try:
        cvs_score = compute_score_for_cardiovascular_system(
            mean_arterial_pressure=condition.mean_arterial_pressure,
            catecholamine=condition.catecholamine,
        )
    except Exception as e:
        cvs_score = 0
        # print("Could not compute Cardiovascular Score. -> Set to 0.\n", e)

    try:
        cg_score = compute_score_for_coagulation(
            platelets_count=condition.platelets_count
        )
    except Exception as e:
        cg_score = 0
        # print("Could not compute Coagulation Score. -> Set to 0.\n", e)

    try:
        kdny_score = compute_score_for_kidneys(
            creatinine_level=condition.creatinine_level,
            urine_output=condition.urine_output,
        )
    except Exception as e:
        kdny_score = 0
        # print("Could not compute Kidney Score. -> Set to 0.\n", e)

    try:
        livr_score = compute_score_for_liver(bilirubin_level=condition.bilirubin_level)
    except Exception as e:
        livr_score = 0
        # print("Could not compute Liver Score. -> Set to 0.\n", e)

    try:
        ns_score = compute_score_for_nervous_system(
            glasgow_coma_scale=condition.glasgow_coma_scale
        )
    except Exception as e:
        ns_score = 0
        # print("Could not compute GCS Score. -> Set to 0.\n", e)

    try:
        rs_score = compute_score_for_respiratory_system(
            partial_pressure_of_oxygen=condition.partial_pressure_of_oxygen,
            is_mechanically_ventilated=condition.is_mechanically_ventilated,
        )
    except Exception as e:
        rs_score = 0
        # print("Could not compute Respiratory Score. -> Set to 0.\n", e)

    return cvs_score + cg_score + kdny_score + livr_score + ns_score + rs_score


def compute_score_for_cardiovascular_system(
    mean_arterial_pressure: float, catecholamine: Optional[Catecholamine]
) -> int:
    """
    Computes score based on mean arterial pressure or catecholamine therapy.
    """
    if catecholamine:
        if catecholamine.name == "Dopamine":
            if catecholamine.dosage <= 5:
                return 2
            if catecholamine.dosage < 15:
                return 3
            return 4
        if catecholamine.name == "Dobutamine":
            return 2
        if catecholamine.name in {"Epinephrine", "Norepinephrine"}:
            if catecholamine.dosage <= 0.1:
                return 3
            return 4
    if mean_arterial_pressure < 70:
        return 1
    return 0


def compute_score_for_coagulation(platelets_count: int) -> int:
    """
    Computes score based on platelets count (Platelets×10^3/μl).
    Originally values were '20_000, 50_000, 100_000, 150_000' but were adjusted for the units measured in patient data.
    """
    if platelets_count < 20:
        return 4
    if platelets_count < 50:
        return 3
    if platelets_count < 100:
        return 2
    if platelets_count < 150:
        return 1
    return 0


def compute_score_for_kidneys(creatinine_level: float, urine_output: float) -> int:
    """
    Computes score based on Creatinine level (unit is μmol/L) and urine output (unit is mL/d).
    """
    if urine_output:
        if urine_output < 200:
            return 4
        if urine_output < 500:
            return 3
    if creatinine_level >= 5.0: #mg/dl
        return 4
    if creatinine_level >= 3.5: #mg/dl
        return 3
    if creatinine_level >= 2.0: #mg/dl
        return 2
    if creatinine_level >= 1.2: #mg/dl
        return 1
    return 0


def compute_score_for_liver(bilirubin_level: float) -> int:
    """
    Computes score based on Bilirubin level (unit is mg/dl).
    """
    if bilirubin_level >= 12.0:
        return 4
    if bilirubin_level >= 6.0:
        return 3
    if bilirubin_level >= 2.0:
        return 2
    if bilirubin_level >= 1.2:
        return 1
    return 0


def compute_score_for_nervous_system(glasgow_coma_scale: int) -> int:
    """
    Computes score based on Glasgow Coma Scale, see paper by Teasdale et al.:
        https://doi.org/10.1016/S0140-6736(74)91639-0
    """
    if glasgow_coma_scale < 6:
        return 4
    if glasgow_coma_scale < 10:
        return 3
    if glasgow_coma_scale < 13:
        return 2
    if glasgow_coma_scale < 15:
        return 1
    return 0


def compute_score_for_respiratory_system(
    partial_pressure_of_oxygen: float, is_mechanically_ventilated: bool
) -> int:
    """
    Computes score based on PaO2 / FiO2 (unit is mmHg / kPa).
    """

    if partial_pressure_of_oxygen < 13.3 and is_mechanically_ventilated:  # 13.3 kPa 100
        return 4
    if partial_pressure_of_oxygen < 26.7 and is_mechanically_ventilated:  # 26.7 kPa 200
        return 3
    if partial_pressure_of_oxygen < 40:  # 40 kPa 300
        return 2
    if partial_pressure_of_oxygen < 53.3:  # 53.3 kPa 400
        return 1
    return 0


"""
Compute SepsisLabel for 1 Patient

Prerequisite:  
hourly Sofa in sofa: list, 
hourly IV administered boolean in IV_administered:list, 
hourly cultures taken boolean in cultures_taken: list, 
"""


from typing import NamedTuple, Optional
import itertools
class Sepsis(NamedTuple):

    sofa: list  # list of sofa scores
    IV_administered: list  # list of boolean whether IV_was administered or not
    cultures_taken: list  # list of boolean whether cultures were taken or not
    time_index: list  # the index (time)
    


def sepsis_check(
    param: Sepsis, mode, sus_window, sep_window) -> int:
    t = param.time_index
    t_sofa = get_t_sofa(sofa=param.sofa)  # returns row number
    t_IV = iv_check(mod=mode, IV=param.IV_administered)  # returns row number
    t_cultures = blood_check(cultures=param.cultures_taken)  # returns row number
    
    # t_IV is a list of all possible IV administrations
    if not t_IV == False:
        t_IV = [t[i] for i in t_IV]  # get the hour corresponding to row number

    # t_cultures is a list of all possible blood cultures
    if not t_cultures == False:
        t_cultures = [t[i] for i in t_cultures]  # get the hour corresponding to row number

    t_sus = get_t_sus(sus_win=sus_window, IV=t_IV, cultures=t_cultures, t_0=t[0])  # returns hour
    
    if not t_sofa is False:
        t_sofa = [t[i] for i in t_sofa]  # get the hour corresponding to row number
    
    sepsis_label, t_sepsis = is_septic(t_sofa, t_sus, sep_win=sep_window, t_0=t[0])
    
    return sepsis_label, t_sepsis, t_sofa, t_cultures, t_IV, t_sus



def get_t_sofa(sofa) -> int:
    """
    time of Sofa
    """
    t_ = []
   
    for t, score in enumerate(sofa):
        t = int(t)
        if t < 24:
            if score >= 2 + min(sofa[: t + 1]):
                t_.append(t)
        else:
            if score >= 2 + min(sofa[t - 24 : t]):
                t_.append(t)
    if len(t_) > 0:
        return [min(t_)]
    return False


def iv_check(mod, IV) -> int:
    """
    time of IV
    """
    if mod == "sepsis-3":
        t_ = [x for x, bool in enumerate(IV) if bool == True]
        """for t, bool in enumerate(IV):
            if bool == True:
                return  t""" 
        if len(t_) > 0:
            return list(set(t_))
        return False
    
    if mod == "reyna":
        consec = 0
        max = 0
        for t, bool in enumerate(IV):
            if bool == False:
                consec = 0
            if bool == True:
                consec += 1
                if consec > max:
                    max = consec
                    if max == 72:
                        return (
                            t - 71
                        )  
        return False


def blood_check(cultures) -> int:
    """
    first time of bloodcultures taken
    """
    t_ = [x for x, bool in enumerate(cultures) if bool == "True"]
    if len(t_) > 0:
        return list(set(t_))
    return False
    """count = 0
    for t in cultures:
        if t == "True":
            return count
        else:
            count += 1
    return False"""


def get_t_sus(sus_win, IV, cultures, t_0) -> float:
    """
    time of suspicion, needs exception for when IV and cultures are too far apart -> No sepsis x24 x72
    """
    if IV is False:
        return False
    elif cultures is False:
        return False
    
    # only makes possible combinations -> greatly reduce the amount of combinations
    l = [x for x in itertools.product(IV, cultures) if (x[0] - x[1]) <= sus_win[1] or (x[1] - x[0]) <= sus_win[0]]
    t_ = []

    for x in l: 

        # if cultures and IV happen at the same time
        if x[0] == x[1]:
            t_.append(x[0])

        # IV first and within sus_window[0] hours of cultures
        elif (x[0] < x[1]) and ((x[1] - x[0]) >= t_0) and ((x[1] - x[0]) <= sus_win[0]):
            t_.append(x[0])
        # cultures first and within sus_window[1] of IV
        elif x[1] < x[0] and ((x[0] - x[1]) >= t_0) and ((x[0] - x[1]) <= sus_win[1]):
            t_.append(x[1])

    # returnign all possible t_sus (catching t_sus' compatible to t_sofa at all costs :D)
    if len(t_) > 0:
        return list(set(t_))
    else:
        return False


def is_septic(sofa, sus, sep_win, t_0) -> bool:
    """
    as long as t_sofa occured no more than x48 hours before or x24 hours after t_suspicion
    """
    t_ = []
    if sus is False:
        return False, False
    if sofa is False:
        return False, False
    l = [x for x in itertools.product(sofa, sus) if (x[0] - x[1]) <= sep_win[1] or (x[1] - x[0]) <= sep_win[0]]
    #if sofa first and sep_window[0] hours no sus, or sus first and sep_window[1] hours no sofa -> False
    for x in l:
        if ((x[1] - x[0]) > t_0) and ((x[1] - x[0]) <= sep_win[0]) or ((x[0] - x[1]) > t_0) and ((x[0] - x[1]) <= sep_win[1]):
            t_.append(min(x[0], x[1]))
    if len(t_) > 0:
        print("septic", t_)
        return True, list(set(t_))
    else:
            return False, False