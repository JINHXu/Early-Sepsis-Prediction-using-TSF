## Forecasting Predictions for Spesis Check


### Data

* saved on G-drive

  * predict on validation data
  
  * predict on test data

### Load data

```python
data, var_to_ind = pickle.load(open(data_path, 'rb'))
```

### script

* [View on Colab](https://colab.research.google.com/drive/1YEtYUQzxya_pCsEtBsJau3RShwK3Snpf?usp=sharing)

* [View on GitHub](https://github.com/JINHXu/Research-Module-WS22-Natalia-Pablo-Jinghua/blob/main/sepsis_check_data/pretext/strats_sepsis_pretext_forecasting.ipynb)

### Data

```
ts_ind	obs_window	SUBJECT_ID	sepsis_label	forecasting_pred	forecasting_test_op
0	3	20	272	0	[-0.7563478350639343, -0.2769825756549835, -0....	[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ...
1	7	20	279	1	[0.3193117380142212, -0.22587063908576965, -0....	[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ...
2	9	20	281	0	[0.47262197732925415, -0.5889627933502197, -0....	[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ...
3	32	20	306	0	[-0.2669658064842224, -0.2691204249858856, 0.1...	[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ...
4	37	20	310	0	[-0.31633082032203674, -0.21901646256446838, -...	[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ...
...	...	...	...	...	...	...
131316	55274	120	43098	0	[-0.38975512981414795, -0.6735785007476807, -0...	[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ...
131317	55441	120	58826	1	[0.4758621156215668, -0.8170661926269531, -0.6...	[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, ...
131318	56391	120	23560	1	[0.4496254026889801, -0.8427609205245972, -0.6...	[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, ...
131319	56406	120	48388	1	[0.47397905588150024, -0.8081768751144409, -0....	[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, ...
131320	56712	120	7509	0	[0.478007048368454, -0.8025604486465454, -0.63...	[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, ...
```

`ts_ind`: ts_ind

`obs_window`: observation window for each prediction

```python
pred_window = 2 # hours
obs_windows = range(20, 124, 4)
```
`SUBJECT_ID`: patient ID

`sepsis_label`: eventual septic status (from `oc`)

`forecasting_pred`: predicted valus for 133 features (ordered according to `var_to_ind` mapping)

`forecasting_test_op`: masked `y_true`, `len = 133 * 2`



