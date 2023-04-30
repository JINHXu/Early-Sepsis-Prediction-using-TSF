import matplotlib.pyplot as plt
import pandas as pd

in_path = '/Users/xujinghua/training_log.txt'
out_path = '/Users/xujinghua/training_results.txt'

roc_auc = []
pr_auc = []
min_rp = []

with open(out_path, 'w') as outfile, open(in_path, 'r') as infile:
    lines = infile.readlines()
    for line in lines:
        if line[:9] == 'Test res ':
            metrics = line.strip().split(' ')
            roc_auc.append(float(metrics[2]))
            pr_auc.append(float(metrics[3]))
            min_rp.append(float(metrics[4]))

# output to log.csv
data = pd.DataFrame(
    {'ROC-AUC': roc_auc,
     'PR-AUC': pr_auc,
     'min(Re,Pr)': min_rp
     })

data.to_csv('log.csv', encoding='utf-8', index=False)

# visualization
# get avg
LEN = 10


def avg(data):
    datasum = cnt = 0
    for num in data:
        datasum += num
        cnt += 1
        if cnt == LEN:
            yield datasum / LEN
            datasum = cnt = 0
    if cnt:
        yield datasum / cnt


roc_auc = list(avg(roc_auc))
pr_auc = list(avg(pr_auc))
min_rp = list(avg(min_rp))

x = range(10, 51, 10)

# plot roc_auc
plt.plot(x, roc_auc, color='r', marker='^')
plt.xlabel('% labeled data')
plt.ylabel('ROC-AUC')
plt.savefig('ROC-AUC.png')
plt.clf()

# plot roc_auc
plt.plot(x, pr_auc, color='r', marker='^')
plt.xlabel('% labeled data')
plt.ylabel('PR-AUC')
plt.savefig('PR-ROC.png')
plt.clf()

# plot roc_auc
plt.plot(x, min_rp, color='r', marker='^')
plt.xlabel('% labeled data')
plt.ylabel('min(Re,Pr)')
plt.savefig('MIN-RP.png')
plt.clf()