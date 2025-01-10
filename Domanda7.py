import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

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
plt.plot(weekly_counts.index, weekly_counts.values, linestyle='-')
plt.title('Distribuzione degli attacchi nel tempo', fontsize=16)
plt.xlabel('Settimana', fontsize=12)
plt.ylabel('Numero di attacchi', fontsize=12)
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

#############################################################################

df = data

# Supponiamo che le colonne si chiamino 'date' e 'gang' (aggiorna se necessario)
date_column = 'date'
gang_column = 'gang'

# Converti la colonna delle date nel formato datetime
df[date_column] = pd.to_datetime(df[date_column], errors='coerce')

# Filtra le date a partire dal 2023 e crea una copia del DataFrame filtrato
df = df[df[date_column] >= '2023-01-01'].copy()

# Estrai i mesi e gli anni dalla colonna delle date
df['month_year'] = df[date_column].dt.to_period('M')

# Raggruppa i dati per mese-anno e gang
agg_data = df.groupby(['month_year', gang_column]).size().reset_index(name='occurrences')

# Filtra solo le gang con occorrenze > 50
agg_data = agg_data[agg_data['occurrences'] > 50]

# Riorganizza i dati in formato pivot per lo stack delle barre
pivot_data = agg_data.pivot(index='month_year', columns=gang_column, values='occurrences').fillna(0)

# Configura la palette dei colori
palette = sns.color_palette('husl', n_colors=len(pivot_data.columns))

# Crea l'istogramma a barre impilate
ax = pivot_data.plot(kind='bar', stacked=True, figsize=(14, 7), color=palette, edgecolor='black')

# Aggiungi i numeri delle occorrenze sopra le barre
for container in ax.containers:
    ax.bar_label(container, label_type='center', fontsize=10, color='black')

# Imposta i titoli e le etichette
plt.title('Ransomware Gang che hanno commesso più di 50 attacchi in un mese (dal 2023)', fontsize=14)
plt.xlabel('Mese', fontsize=12)
plt.ylabel('Numero di attacchi', fontsize=12)
plt.legend(title='Ransomware Gang')
plt.xticks(rotation=45)

# Migliora il layout
plt.tight_layout()

# Mostra il grafico
plt.show()

