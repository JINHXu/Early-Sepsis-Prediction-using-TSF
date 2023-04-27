### Introduction

The following folder contains scripts which are related to the data. This project builbs upon the architecture of [STRaTS](https://arxiv.org/pdf/2107.14293.pdf), therefore, their pre-processing script was used as a base. The goal of STRaTs architecture is to predict mortality. However, our project focuses on early sepsis prediction. In order to do the [sepsis check]( https://github.com/JINHXu/Research-Module-WS22-Natalia-Pablo-Jinghua/tree/main/sepsischeck) specific physiological features need to be present. Therefore, the pre-processing scripts have been modified to include three additional featues: Antibiotics, Mechanically ventilated and Blood cultures. Moreover, the clinical notes have also been added as a feature for the second set of experiments. 

### Usage

In order to generate the data for the experiments, two scripts need to be excecuted. For borth script to run, one just needs to provide the path to the mimic folder in their directory. 
Firstly:
```
python3 mimic_events_icu_generation.py

```
The following script needs to be run to generate the desired events and icu .csv files. 
Afterwards:
```
python3 mimic_preprocessed_data_generation.py

```
This script can be run to generate the final .pkl file with all the desired data.

### Data Exploration

In order to get some insights of the data and to understand how the MIMIC-III database is structed, mimic-III data exploration.py can be used. It provides some explantations about the database and shows from which tables the sepsis-features that are missing from the original feature list can be extracted. 

In addition, one can see some visualizations of the data in regards to the duration of patients stay and the number of clinical notes that were given to those patients. 


Lastly, `ts_ind_pos_annotations.xlsx` includes annotations of the clinical notes. These annotations capture the first mentions of sepsis in the clinical notes and provide a time stamp that was present in the letter. This information could be used to compare the forecasted prediction of sepsis development vs the suspected sepsis in the notes. 


add reference to strats 
mention that strats deals with mortality and we with sepsis. which features have been added? 



