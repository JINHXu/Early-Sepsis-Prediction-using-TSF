import matplotlib.pyplot as plt
import pandas as pd

in_path = '/Users/xujinghua/Downloads/pretext_sepsis_large/logs/forecasting_log.txt'

train_losses = []
val_losses = []

with open(in_path, 'r') as f:
    lines = f.readlines()
    for line in lines:
        if line[:5] == 'Epoch':
            elements = line.strip().split(' ')
            train_losses.append(float(elements[3]))
            val_losses.append(float(elements[6]))


x = range(len(val_losses))
y = val_losses

plt.figure()
plt.plot(x, y)
plt.xlabel('epoch')
plt.ylabel('val loss')
# plt.xticks(x, [str(i) for i in y], rotation=90)

# set parameters for tick labels
plt.tick_params(axis='x', which='major', labelsize=10)
plt.tight_layout()

# save plot
plt.savefig('sepsis_pretext_large_val_loss.png')


x = range(len(train_losses))
y = train_losses

plt.figure()
plt.plot(x, y)
plt.xlabel('epoch')
plt.ylabel('train loss')
# plt.xticks(x, [str(i) for i in y], rotation=90)

# set parameters for tick labels
plt.tick_params(axis='x', which='major', labelsize=10)
plt.tight_layout()

# save plot
plt.savefig('sepsis_pretext_large_train_loss.png')
