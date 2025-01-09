import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Caricare i dati dal file CSV
file_path = 'Dataset.csv'
data = pd.read_csv(file_path, delimiter=';')

# Convert the 'date' column to datetime format
data['date'] = pd.to_datetime(data['date'], format='%d/%m/%Y', errors='coerce')

# Drop rows with invalid dates (if any)
data = data.dropna(subset=['date'])

# Group the data by week and count occurrences
data['week'] = data['date'].dt.to_period('W').apply(lambda r: r.start_time)
weekly_counts = data['week'].value_counts().sort_index()

# Custom function to format x-axis labels (vertical and only year in January)
def custom_date_formatter_vertical(x, pos):
    date = mdates.num2date(x)
    if date.month == 1:  # Show only the year in January
        return date.strftime('%Y')
    else:  # Show only the month for other months
        return date.strftime('%b')

# Plot the line graph with slightly lighter vertical grid lines for the start of each year
plt.figure(figsize=(12, 6))
plt.plot(weekly_counts.index, weekly_counts.values, marker='o', linestyle='-')
plt.title('Occorrenze Settimanali', fontsize=16)
plt.xlabel('Settimana', fontsize=12)
plt.ylabel('Occorrenze', fontsize=12)
plt.grid(visible=True, linestyle='--', alpha=0.6)

# Add vertical grid lines with a lighter color for the start of each year
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(plt.FuncFormatter(custom_date_formatter_vertical))

# Loop through all unique years in the data to highlight the start of each year
unique_years = weekly_counts.index.to_series().dt.year.unique()
for year in unique_years:
    start_of_year = pd.Timestamp(f'{year}-01-01')
    plt.axvline(x=start_of_year, color='red', linestyle='--', alpha=0.5, linewidth=1.0)

plt.xticks(rotation=90, fontsize=10)
plt.tight_layout()
plt.show()

