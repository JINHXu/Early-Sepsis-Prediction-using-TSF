### Introduction

The following folder contains scripts which are related to the data. 

In order to generate the data for the experiments, two scripts need to be excecuted. Firstly, `mimic_events_icu_generation.py` needs to be run to generate the desired events and icu .csv files. Afterwards, `mimic_preprocessed_data_generation.py` can be run to generate the final pkl file with all the desired data. For this script to run, one just needs to provide the path to the mimic folder in their directory. 


In order to get some insights of the data, mimic-III data exploration.py can be used. It provides some explantations about the database and shows from which tables the sepssis-features that are missing from the original feature list can be extracted. 

In addition, one can see some visualizations of the data in regards to the duration of patients stay and the number of clinical notes that were given to those patients. 


Lastly, `ts_ind_pos_annotations.xlsx` includes annotations of the clinical notes. These annotations capture the first mentions of sepsis in the clinical notes and provide a time stamp that was present in the letter. This information could be used to compare the forecasted prediction of sepsis development vs the suspected sepsis in the notes. 


add reference to strats 
mention that strats deals with mortality and we with sepsis. which features have been added? 



