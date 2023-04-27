# SepsisCheck Implementation
This folder contains the SepsisCheck code, its variants, results and additional helper files.

## Folder: SepsisCheck
Given a preprocessed .pkl patient data file (and forecast predictions for SepsisCheck_forecast) the contents of this folder perform sepsis classification on each unique ts_ind. 

The general hierarchy is the same in all SepsisCheck* folders, however, different strategies within the SepsisCheck code and its utilities were employed and will be explained separately.

With data paths set up correctly, run any given strategy by navigating to the desired folder and running the corresponding run*.py, e.g.:
```bash
python run_sepsis_check_on_pkl.py
```
### SepsisCheck.py
The SepsisCheck code which comprises of a modified version of [sofascore](https://github.com/shimst3r/sofascore) and implementation of rule-based sepsis classification according to [The Third International Consensus Definitions for Sepsis and Septic Shock (Sepsis-3)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4968574/). Additionally, functionality for sepsis classification according to the guidelines of the [physionet 2019 challenge](https://physionet.org/content/challenge-2019/1.0.0/) are provided.

### run_sepsis_check_on_pkl.py
Run this to perform SepsisCheck on observed data. Should be set to Standard strategy (the other folders contain code for the different strategies), which finds time of suspicion, sofa and sepsis label according to Sepsis-3 / physionet guidelines. 
* path is the path to the preprocessed .pkl patient data
* preds is the path to the predictions of the forecast model
* sus_window: [sus_window[0], sus_window[1]]
1. If Antibiotics were admninistered first and within sus_window[0]-hours of blood cultures, then time of IV = time of suspicion. 
2. If blood cultures were taken first and within sus_window[1]-hours of Antibiotics, then time of cultures = time of suspicion.
* sep_window: [sep_window[0], sep_window[1]]
1. If time of SOFA was first and there was no time of suspicion within sep_window[0]-hours, or time of suspicion was first and there was no time of SOFA within sep_window[1]-hours the patient is not septic.
2. Else, the patient is septic, and the time of sepsis is the earlier of time of suspicion and time of SOFA.
* Mode is either "sepsis-3" or "reyna". 
* "ffill" is important for experiments in reyna mode - to have a higher chance of 72 consecutive hours of IV administration - but not important in sepsis-3 mode, as only the first occurrence of IV is important.

### sepsischeck_utilities_for_pkl.py
This takes the preprocessed .pkl files, extracts and renormalizes features relevant to SepsisCheck and then transforms the data into an hourly format, where each row corresponds to one set of features of one hour. It also fills the data, and then computes the sofa score corresponding to each set of features, which is used together with the features for antibiotics, blood cultures and time to compute the patient's sepsis label and time of sepsis (and additional information, which may or may not be useful).

## Folder: SepsisCheck_catchsus
As results on the standard implementation indicated that the most common reason for erroneous sepsis classification in patients that have all relevant features was a lack of a time of suspicion, this strategy aims to find a time of suspicion in a greedier way. The standard strategy uses the first time of blood cultures, and the first time of antibiotics and the supplied suspicion window to compute the time of suspicion. The catchsus strategy takes into consideration all times blood cultures were taken (not just the first time) and all times antibiotics were administered and then checks if any of the possible combinations (of time of IV and time of blood cultures) fall within the specified suspicion window. For each of the possible combinations that fall within the specified suspicion window, the earlier time is considered as a time of suspicion. This can yield multiple times of suspicions, which are then compared to the time of sofa and the sepsis window to generate a sepsis label.

## Folder: SepsisCheck_grouped
This strategy takes the idea of catchsus even further and expands it onto the time of sofa. As a result, multiple times of suspicion (as is the case with catchsus) and multiple times of sofa are considered when generating a sepsis label.

## Folder: SepsisCheck_forecast
This folder contains the code that utilizes the predictions of our timeseries forecasting model by appending said results to the data that was observed prior to the predictions. For a given patient, and per observation window, the observed patient data is trimmed at the time the observation window ends and the model predictions are added instead. Then SepsisCheck is performed as usual on 'observation window hours of observed data + 1 hour of predictions' (prefixed TH*). Due to the nature of the model, the three binary features 'Antibiotics', 'Blood Culture' and 'Mechanically ventilated' are predicted in a continuous fashion. To interpret these predictions a threshold was set that assigns everything above / below it a binary label. The method to find said threshold is improvable, so far, a combination of clustering and careful trial and error was used.
To get a better comparison, a separate set of experiments performs SepsisCheck on 120 hours (max observation window) of patient data (prefixed "cutoff"). 

## Folder: features/possible_predictions
Pre computed .csv's that contain the ts_indices of patients that have both Antibiotics and Blood Culture features within their observed data. "possible*.csv" is for the initial experiments which were conducted on patients of finetuning data (as that was available at the time). "forecast*.csv" is for SepsisCheck_forecast experiments, which were conducted on a subset of the forecast patient data (test set).

## Folder: results
Within the folders are .zip files with the uncompressed result files, but also the uncompressed reports that can be viewed within sepsischeck_results.ipynb and
sepsischeck_forecast_results.ipynb.

On fine tune data:
* 1 = Experiments with physionet requirements for time of suspicion
* 2 = Experiments with sepsis-3 requirements
* 3 = Experiments with grouped strategy and sepsis-3 requirements
* 4 = Experiments with catchsus strategy and sepsis-3 requirements
forecast/test:
The final results of SepsisCheck on the test subset, further explored in 'sepsischeck_forecast_results.ipynb'.

## sepsischeck_results.ipynb
The results of the first experiments. Even though the most common source for erroneous classification given all relevant features (so not due to missing IV or blood culture feature) was missing suspected infection, no strategy was superior, which is why further experiments are conducted using the standard Sepsis-3 guidelines; this allows for better comparison in the future. In general, a wide suspicion window (e.g., 10 days) is more impactful on performance than different strategies, meaning monitoring the occurrence of both blood cultures taken and antibiotics within e.g., 10 days of each other achieved surprisingly good results.

## sepsischeck_forecast_results.ipynb
Depending on the threshold for the interpretation of the binary features, the classification using up to 120 hours of observed data and 1 hour of our model predictions performed on par with classification on only observed data. Of course, 1 hour of predictions is a rather small window, and makes for only a small percentage of data used for generating a label, however, taking a look at true positives it's promising to see that the addition of our model predictions enabled SepsisCheck to classify true positives that were classified as negatives before. Still, the F1 scores are rather close, and one might argue that, unfortunately, not enough to come to a meaningful conclusion. After all, the real interesting experiments would explore results on multiple hours of predictions - which yet needs to be implemented.

### comparing results
A small excerpt of results
* cutoffsepsis* is on 120 hours of observed data
* TH1.0025* is on patient data which was cut off after each obseravtion window with the corresponding prediction (next hour) appended. Meaning multiple checks per patient, where the first check is on 20 hours of patient data + prediction of data in the 20th hour, and the last check on 120 hours of patient data + prediction of data in the 121st hour - in steps of 4 hours. If any of those checks yields a positive sepsis label, it is returned.
* 24-12_240-240 means the sepsis window was [24, 12] and the suspicion window was [240, 240]
* cm: True Negative, False Positive, False Negative, True Positive

|    | experiment                                 |   f1_raw | cm                    |
|---:|:-------------------------------------------|---------:|:----------------------|
|  2 | cutoffsepsis-3_no-prediction_24-12_240-240 | 0.875187 | [8278  480  674  284] |
|  3 | cutoffsepsis-3_no-prediction_24-12_48-72   | 0.874505 | [8335  423  707  251] |
| 10 | TH1.0025_sepsis-3_prediction_24-12_48-72   | 0.873794 | [8255  503  672  286] |
|  8 | TH1.0025_sepsis-3_prediction_24-12_24-96   | 0.873677 | [8295  463  693  265] |
|  9 | TH1.0025_sepsis-3_prediction_24-12_240-240 | 0.873287 | [8189  569  641  317] |
|  1 | cutoffsepsis-3_no-prediction_24-12_24-96   | 0.87309  | [8351  407  724  234] |
