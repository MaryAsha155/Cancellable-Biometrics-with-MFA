import matplotlib.pyplot as plt

# Define metrics for both papers
metrics = ['Accuracy (%)', 'Preprocessing Time (s)', 'FAR (%)', 'FRR (%)', 'Efficiency Improvement (%)', 'Key Generation Time (s)']
base_paper = [90, 2.5, 5, 8, 0, 1.5]  # Simulated/estimated values for the base paper
enhanced_paper = [97, 1.25, 1, 3, 40, 0.75]  # Simulated values for your paper

# Create bar positions
x = range(len(metrics))
width = 0.35

# Plot the bars
plt.figure(figsize=(12, 7))  # Adjusting size for clarity
bars_base = plt.bar(x, base_paper, width, label='Minutiae Extraction Method', color='blue')
bars_enhanced = plt.bar([i + width for i in x], enhanced_paper, width, label='Ridge-Valley Binary based', color='orange')

# Add metric values on the bars
for i, bar in enumerate(bars_base):
    value = base_paper[i]
    if metrics[i] == 'Efficiency Improvement (%)' and value == 0:
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1, 'Baseline', 
                 ha='center', va='bottom', fontsize=14, color='black')
    else:
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{value}', 
                 ha='center', va='bottom', fontsize=14, color='black')

for bar in bars_enhanced:
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{bar.get_height()}', 
             ha='center', va='bottom', fontsize=14, color='black')

# Customize labels and appearance
plt.xlabel('Metrics', fontsize=16, fontweight='bold')
plt.ylabel('Values', fontsize=12, fontweight='bold')
plt.title('Comparison of Performance Metrics between Minutiae Extraction Method & Ridge-Valley Binary based', fontsize=18, fontweight='bold')
plt.xticks([i + width / 2 for i in x], metrics, rotation=45, fontweight='bold', fontsize=14)
plt.legend()

# Optional grid and layout improvements
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
