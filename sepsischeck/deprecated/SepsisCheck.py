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
Prerequisites: 
sofa relevant values of one timestep -> sofa score for specific timestep
compute for each patient at every timestep
"""

from typing import NamedTuple, Optional
import numpy as np
import pandas as pd

__version__ = "1.2.0"


class Catecholamine(NamedTuple):
    """
    Optional dosages, only cardiovascular (for SOFA-scores 2 to 4)
    """
    name: str
    dosage: float

class Urine(NamedTuple):
    """
    Optional feature for liver
    """
    #name:str
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



    Questions: 
    1. Does urine_output <500ml/d always mean kidney score is 3? Or is it a combination of creatinine and urine values?
    2. Where do we get Glasgow Coma Scale from? MIMIC-III
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
    cvs_score = compute_score_for_cardiovascular_system(
        mean_arterial_pressure=condition.mean_arterial_pressure,
        catecholamine=condition.catecholamine,
    )
    cg_score = compute_score_for_coagulation(platelets_count=condition.platelets_count)
    kdny_score = compute_score_for_kidneys(creatinine_level=condition.creatinine_level, urine_output=condition.urine_output)
    livr_score = compute_score_for_liver(bilirubin_level=condition.bilirubin_level)
    ns_score = compute_score_for_nervous_system(
        glasgow_coma_scale=condition.glasgow_coma_scale
    )
    rs_score = compute_score_for_respiratory_system(
        partial_pressure_of_oxygen=condition.partial_pressure_of_oxygen,
        is_mechanically_ventilated=condition.is_mechanically_ventilated,
    )
    return cvs_score + cg_score + kdny_score + livr_score + ns_score + rs_score


def compute_score_for_cardiovascular_system(
    mean_arterial_pressure: float, catecholamine: Optional[Catecholamine]
) -> int:
    """
    Computes score based on mean arterial pressure or catecholamine therapy.
    """
    if catecholamine:
        if catecholamine.name == "dopamine":
            if catecholamine.dosage <= 5:
                return 2
            if catecholamine.dosage < 15:
                return 3
            return 4
        if catecholamine.name == "dobutamine":
            return 2
        if catecholamine.name in {"epinephrine", "norepinephrine"}:
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
    Computes score based on Creatinine level (unit is mg/dl) and urine output (unit is mL/d).
    """
    if urine_output:
        if urine_output < 200:
            return 4
        if urine_output < 500:
            return 3
    if creatinine_level >= 5.0:
        return 4
    if creatinine_level >= 3.5:
        return 3
    if creatinine_level >= 2.0:
        return 2
    if creatinine_level >= 1.2:
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
    Computes score based on PaO2 (unit is mmHg).
    """
    if partial_pressure_of_oxygen < 100 and is_mechanically_ventilated:
        return 4
    if partial_pressure_of_oxygen < 200 and is_mechanically_ventilated:
        return 3
    if partial_pressure_of_oxygen < 300:
        return 2
    if partial_pressure_of_oxygen < 400:
        return 1
    return 0

"""
even though reyna et.al. compute a specific time of sepsis and we just say Sepsis=1 or No Sepsis=0, we still need to look at the whole timeseries of the patient 

Compute SepsisLabel for 1 Patient

Prerequisite:  
hourly Sofa in sofa: list, 
hourly IV administered boolean in IV_administered:list, 
hourly cultures taken boolean in cultures_taken: list, 
atleast 72 hourly bins because that is a requirement for IV check according to reyna et. al.
i am not sure yet if variables as list will work

!Testing Needed!
"""
class Sepsis(NamedTuple):
    
    sofa: list #timeseries of sofa scores
    IV_administered: list #timeseries of boolean whether IV_was administered or not
    cultures_taken: list #timeseries of boolean whether cultures were taken or not

def sepsis_check(param: Sepsis) -> int: #1 if patient is septic else 0 ToDo: Add Exceptions: if there is not t_sofa or t_IV or t_cultures or t_sus return 0 (no sepsis)
    t_sofa = get_t_sofa(sofa=param.sofa)
    t_IV = iv_check(IV=param.IV_administered)
    t_cultures = blood_check(cultures=param.cultures_taken)
    t_sus = get_t_sus(IV=t_IV, cultures=t_cultures)
    return is_septic(t_sofa, t_sus)

def get_t_sofa(sofa) -> int: 
    """
    time of Sofa, probably needs to be initialized at first value, because if the first value is >2 this may already set t_sofa 
    """
    for t, score in enumerate(sofa):
        if t < 24:
            if score >= 2 + min(sofa[:t+1]):
                return t    
        else:
            if score >= 2 + min(sofa[t-24:t]): #Testing needed!! min(sofa[t,-24])+2 is supposed to be minimum of sofa from t and 24 hours back +2. Have not tested that line of code yet, so it is probably somewhat wrong.
                return t
    return False
        
def iv_check(IV) -> int: 
    """
    time of IV ordering, under the requirements of reyna et.al. Need exception if it doesnt happen -> no sepsis
    """
    consec = 0
    max = 0
    for t, bool in enumerate(IV):
        if bool==False:
            consec = 0
        if bool==True:
            consec += 1
            if consec > max:
                max = consec
                if max == 72:
                    return t-71 #set t_IV in the patients list? the moment where it was ordered
    return False

def blood_check(cultures) -> int: 
    """
    first time of bloodcultures taken
    exception needed for when it doesnt happen -> No sepsis
    what if it happens more than once? -> List?
    """
    count = 0
    for t in cultures:
        if t == True:
            return count
        else:
            count += 1
    return False
            
def get_t_sus(IV, cultures) -> int: 
    """
    time of suspicion, needs exception for when IV and cultures are too far apart -> No sepsis
    """
    if not str(IV).isdigit() and IV==False:
        return False
    elif not str(cultures).isdigit() and cultures==False:
        return False
    elif IV==cultures:
        return IV
    elif IV<cultures and cultures-IV <= 24:
        return IV
    elif cultures<IV and IV-cultures <= 72:
        return cultures
    
    else:
        return False


def is_septic(sofa, sus) -> bool: 
    """
    as long as t_sofa occured no more than 24 hours before or 12 hours after t_suspicion
    """
    if not str(sus).isdigit() and sus==False:
        return False
    if not str(sofa).isdigit() and sofa==False:
        return False
    if sus - sofa > 24 or sofa - sus > 12: 
        return False
    else:
        return True 