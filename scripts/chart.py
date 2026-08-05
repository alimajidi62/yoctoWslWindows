import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2 * np.pi, 300)

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
fig.suptitle("Sample Charts", fontsize=14, fontweight="bold")

# Line chart
axes[0].plot(x, np.sin(x), label="sin", color="royalblue")
axes[0].plot(x, np.cos(x), label="cos", color="tomato")
axes[0].set_title("Sine & Cosine")
axes[0].legend()
axes[0].grid(True, linestyle="--", alpha=0.5)

# Bar chart
categories = ["A", "B", "C", "D", "E"]
values = [23, 45, 12, 67, 34]
axes[1].bar(categories, values, color="steelblue", edgecolor="white")
axes[1].set_title("Bar Chart")
axes[1].set_ylabel("Value")

# Scatter plot
np.random.seed(42)
scatter_x = np.random.randn(200)
scatter_y = scatter_x * 0.8 + np.random.randn(200) * 0.5
axes[2].scatter(scatter_x, scatter_y, alpha=0.6, color="mediumseagreen", edgecolors="white", linewidths=0.5)
axes[2].set_title("Scatter Plot")

plt.tight_layout()
plt.savefig("/home/ali/chart.png", dpi=150)
print("Chart saved to /home/ali/chart.png")
plt.show()
