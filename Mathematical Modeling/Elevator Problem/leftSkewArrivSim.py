#By Omer Toledo - This is his code not mine.

import numpy as np
from scipy.stats import skewnorm
import matplotlib.pyplot as plt
import math

# Parameters for left-skewed distribution
mean = -10
variance = 130
alpha = -3  # Shape parameter (< 0 for left-skew)
scale = math.sqrt(variance / (1 - ((2*alpha**2)/(np.pi*(1+alpha**2))))) # Scale parameter (measure of spread)
loc = mean - (scale*alpha*math.sqrt(2/np.pi) / math.sqrt(1+alpha**2))    # Location parameter (measure of center)


# Generate 100k simulated arrival samples
size = 100000
data = skewnorm.rvs(alpha, loc=loc, scale=scale, size=size)

# Calculate the 95% interval (2.5th to 97.5th percentiles)
lower_bound, upper_bound = np.percentile(data, [2.5, 97.5])
print(f"95% Simulation Interval: [{lower_bound:.2f}, {upper_bound:.2f}]")

# Set up a cleaner, higher-resolution figure
plt.figure(figsize=(10, 6))

# High-granularity histogram (100 bins instead of 30)
plt.hist(data, bins=100, density=True, alpha=0.5, color='skyblue', edgecolor='gray', label='Simulated Data (100k samples)')

# Plot smooth theoretical PDF curve for visual comparison
xmin, xmax = plt.xlim()
x = np.linspace(xmin, xmax, 300)
p = skewnorm.pdf(x, alpha, loc=loc, scale=scale)
plt.plot(x, p, 'r-', linewidth=2.5, label='Theoretical PDF Curve')

# Add vertical dashed lines for the 95% interval bounds
plt.axvline(lower_bound, color='lightgreen', linestyle='--', linewidth=2, label=f'2.5% Lower Bound ({lower_bound:.2f})')
plt.axvline(upper_bound, color='lightgreen', linestyle='--', linewidth=2, label=f'97.5% Upper Bound ({upper_bound:.2f})')
plt.title("Left-skewed arrival distribution simulation", fontsize=12, fontweight='bold')
plt.xlabel("Arrival Time (0 is the start of the work shift)", fontsize=10)
plt.ylabel("Density", fontsize=10)
plt.legend(loc='upper left', frameon=True)
plt.grid(True, linestyle=':', alpha=0.6)
plt.tight_layout()
plt.show()


# Calculate the percentage of simulated points at or before 0 (this represents percentage of people on time or early)
count_leq_zero = np.sum(data <= 0)
pct_leq_zero = (count_leq_zero / size) * 100

print(f"Simulated points at or before 0: {count_leq_zero} out of {size}")
print(f"Percentage of simulated points at or before 0: {pct_leq_zero:.4f}%")

print(f"The 95% interval is: {upper_bound - lower_bound}")