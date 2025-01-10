import pandas as pd
import matplotlib.pyplot as plt

# Lettura del dataset
file_path = "Dataset.csv"  # Sostituisci con il percorso del tuo file
data = pd.read_csv(file_path, delimiter=";")

# Conversione della colonna "date" in datetime
data['date'] = pd.to_datetime(data['date'], format='%d/%m/%Y', errors='coerce')

# Pulizia dei dati
# Rimuovere colonne completamente vuote
data_cleaned = data.dropna(how="all", axis=1)

# Rimuovere righe con date non valide
data_filtered = data_cleaned.dropna(subset=["date"])

# Creare una colonna per il mese e l'anno
data_filtered = data_filtered.copy()
data_filtered["year_month"] = data_filtered["date"].dt.to_period("M")


# Aggregare le attività delle gang per mese
activity_by_month = data_filtered.groupby("year_month").size()

# Convertire a DataFrame per la visualizzazione
activity_by_month_df = activity_by_month.reset_index(name="activity_count")

# Eventi geopolitici chiave
updated_key_events = {
    "2022-02": "Inizio guerra Russia-Ucraina",
    "2022-08": "Visita di Pelosi a Taiwan",
    "2022-09": "Proteste in Iran (morte di Mahsa Amini)",
    "2023-04": "La Finlandia entra nella NATO",
    "2023-07": "Vertice NATO a Vilnius",
    "2023-10": "Attacco di Hamas a Israele",
    "2024-11": "Elezioni presidenziali USA",
}

# Creazione del grafico con aggiunta della griglia grigia per migliorare la leggibilità
plt.figure(figsize=(15, 10))
plt.plot(
    activity_by_month_df["year_month"].astype(str),
    activity_by_month_df["activity_count"],
    label="Attività delle gang",
    color="blue",
    linewidth=2,
)

# Aggiunta delle linee verticali per gli eventi con il testo ingrandito
for event_date, event_name in updated_key_events.items():
    plt.axvline(x=event_date, color="red", linestyle="--", alpha=0.7)
    plt.text(
        event_date,
        max(activity_by_month_df["activity_count"]) / 2,  # Posizionare le scritte al centro
        event_name,
        rotation=90,
        horizontalalignment="center",
        fontsize=12,  # Testo più grande
        fontweight="bold",  # Aggiunto grassetto per leggibilità
        color="black",
    )

# Aggiunta della griglia grigia
plt.grid(color="gray", linestyle="--", linewidth=0.5, alpha=0.7)

# Dettagli del grafico
plt.title("Attività delle ransomware gang in relazione ai principali eventi geopolitici", fontsize=18)
plt.xlabel("Anno-Mese", fontsize=14)
plt.ylabel("Numero di attacchi", fontsize=14)
plt.xticks(rotation=90, fontsize=12)
plt.yticks(fontsize=12)
plt.legend(fontsize=12)
plt.tight_layout()

# Mostrare il grafico
plt.show()


###############################################################################################
















