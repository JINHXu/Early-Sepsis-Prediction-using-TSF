### Introduction

The following folder contains scripts which are related to the data. This project builbs upon the architecture of [STRaTS](https://arxiv.org/pdf/2107.14293.pdf), therefore, their pre-processing script was used as a base. The goal of STRaTs architecture is to predict mortality. However, our project focuses on early sepsis prediction. In order to do the [sepsis check]( https://github.com/JINHXu/Research-Module-WS22-Natalia-Pablo-Jinghua/tree/main/sepsischeck) specific physiological features need to be present. Therefore, the pre-processing scripts have been modified to include three additional featues: Antibiotics, Mechanically ventilated and Blood cultures. Moreover, the clinical notes have also been added as a feature for the second set of experiments. 

### Usage

In order to generate the data for the experiments, two scripts have to be excecuted. For both scripts to run, one just needs to provide inside the script the path to the mimic folder in their directory. 
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

In order to get some insights of the data and to roughly understand how the MIMIC-III database is structed, `mimic-III data exploration.py` can be used. It provides some explantations about the database and shows from which tables the sepsis-features that are missing from the original feature list can be extracted. 

In addition, one can see some visualizations of the data in regards to the duration of patients stay and the number of clinical notes that were given to those patients. 
The figure below shows the duration of stay for patients that developed sepsis. The bar chart shows us that many patients stay more than 3 days, on average 15 days, so there should be enough data for the forecasting model.
![Figure 1.](https://github.com/JINHXu/Research-Module-WS22-Natalia-Pablo-Jinghua/blob/main/data_prep_and_exploration/images/period_of_stay.png) <br>
Figure 1. Duration of stay for septic patients

The figure below gives a rough estimate for the amount of clinical notes the patient have received during their stay in the icu. From the graph we can that most patients received under 200 notes, but there are also some cases with over 500 notes. 
![Figure 2.](https://github.com/JINHXu/Research-Module-WS22-Natalia-Pablo-Jinghua/blob/main/data_prep_and_exploration/images/number_of_letter.png)<br>
Figure 2. The amount of clinical letters received during patient's stay. 

### Data Annotations

Lastly, `ts_ind_pos_annotations.xlsx` includes annotations of the clinical notes. These annotations capture the first mentions of sepsis in the clinical notes and provide a time stamp that was present in the letter. This information could be used to compare the forecasted prediction of sepsis development vs the suspected sepsis in the notes. Overall, about 100 patients have been annotated.

Here is an example of the annotations:


| ts_ind        | SUBJECT_ID    | HADM_ID       | CHARTDATE       | CHARTTIME | TEXT | AdmissionDate |
| ------------- | ------------- | -------------  | -------------  |-------------  |-------------  | -------------  |
| 2778          | 3716          | 122999.0      |    2169-12-24  |24.12.69 16:24 |a-unknown source of hypoxia but responding nicely to CPAP. sepsis picture | [**2169-12-23**] |


### References 

Sindhu Tipirneni and Chandan K. Reddy. 2022. Self-Supervised Transformer for Sparse and Irregularly Sampled Multivariate Clinical Time-Series. ACM Trans. Knowl. Discov. Data 16, 6, Article 105 (December 2022), 17 pages. https://doi.org/10.1145/3516367



