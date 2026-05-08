import matplotlib.pyplot as plt
import numpy as np

models = ['llama3.1:8b','mistral:7b','qwen2:7b','deepseek-coder:6.7b']
domains = ['Math', 'Logic', 'Knowledge', 'Code']

# Replace with actual values from your results JSON
acc = np.array([
    [0.152, 0.192, 0.24, 0.56],      # llama3.1:8b
    [0.032, 0.072, 0.216, 0.184],    # mistral:7b
    [0.296, 0.24, 0.128, 0.592],     # qwen2:7b
    [0.04, 0.216, 0.008, 0.304],     # deepseek-coder:6.7b
])

x = np.arange(len(domains))
width = 0.2
fig, ax = plt.subplots(figsize=(8, 4))
for i, model in enumerate(models):
    ax.bar(x + i*width, acc[i]*100, width, label=model)
ax.set_xticks(x + width*1.5)
ax.set_xticklabels(domains)
ax.set_ylabel('Accuracy (%)')
ax.set_title('Per-Domain Accuracy by Model (Quick Mode)')
ax.legend(fontsize=8)
plt.tight_layout()
plt.savefig('figures/fig2.png', dpi=300)