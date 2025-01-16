import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import find_peaks
import plotly.graph_objs as go
from plotly.offline import plot
import csv

class EDXAnalyzerApp:
    def __init__(self, master):
        self.master = master
        master.title("cute EDX Spectra Analysis")

        self.canvas = tk.Canvas(master, width=800, height=600, bg='white')
        self.canvas.grid(row=0, column=0, columnspan=2, rowspan=10, sticky='nsew')

        self.canvas.create_text(
            400, 300,
            text="cute EDX Analyzer",
            font=("Helvetica", 50, "bold"),
            fill="lightgrey",
            angle=30
        )

        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)

        self.add_widgets()

    def add_widgets(self):
        tk.Label(self.master, text="spectrum data (max. 4 files):").grid(row=1, column=0, sticky='w')
        self.spectra_btn = tk.Button(self.master, text="select files", command=self.load_spectra_files)
        self.spectra_btn.grid(row=1, column=1)

        tk.Label(self.master, text="select background file (optional):").grid(row=2, column=0, sticky='w')
        self.background_btn = tk.Button(self.master, text="Datei auswählen", command=self.load_background_file)
        self.background_btn.grid(row=2, column=1)

        tk.Label(self.master, text="select reference file (NIST file):").grid(row=3, column=0, sticky='w')
        self.reference_btn = tk.Button(self.master, text="select data", command=self.load_reference_file)
        self.reference_btn.grid(row=3, column=1)

        self.analyze_btn = tk.Button(self.master, text="Analyse starten", command=self.analyze_spectra)
        self.analyze_btn.grid(row=4, column=0, pady=10)

        self.group_selection_btn = tk.Button(self.master, text="select elements", command=self.show_group_selection)
        self.group_selection_btn.grid(row=4, column=1, pady=10)

        self.status_label = tk.Label(self.master, text="Select files and start analysis.")
        self.status_label.grid(row=5, column=0, columnspan=2)

    def load_spectra_files(self):
        files = filedialog.askopenfilenames(title="Select up to 4 spectrum files.", filetypes=[("CSV file", "*.csv")])
        if files:
            if len(files) > 4:
                messagebox.showwarning("Warning", "You can select a maximum of 4 files.")
            else:
                self.spectra_files = files
                self.status_label.config(text=f"{len(files)} file(s) selected for analysis")

    def load_background_file(self):
        file = filedialog.askopenfilename(title="Select background file", filetypes=[("CSV file", "*.csv")])
        if file:
            self.background_file = file
            self.status_label.config(text="background file selected.")

    def load_reference_file(self):
        file = filedialog.askopenfilename(title="Select reference file (NIST file)", filetypes=[("CSV-Dateien", "*.csv")])
        if file:
            self.reference_file = file
            self.status_label.config(text="reference file selected.")

    def analyze_spectra(self):
        if not hasattr(self, 'spectra_files') or not self.spectra_files:
            messagebox.showwarning("Warning", "Please select files for spectrum.")
            return
        if not hasattr(self, 'reference_file') or not self.reference_file:
            messagebox.showwarning("Warning", "Select a reference file.")
            return
        try:
            reference_data = pd.read_csv(self.reference_file, sep=',', encoding='utf-8')
            reference_data['Energy (eV)'] = pd.to_numeric(reference_data['Theory (eV)'], errors='coerce')
        except Exception as e:
            messagebox.showerror("Error", f"Reference file could not be read: {e}")
            return

        self.compare_spectra(self.spectra_files, reference_data, 'EDX Spectrum Analysis')

    def compare_spectra(self, filenames, reference_data, title):
        spectra = []
        min_energy = np.inf
        max_energy = -np.inf
        # Bestimmen des gemeinsamen Energiebereichs
        for filename in filenames:
            data, metadata = self.read_spectrum(filename)
            if data is None:
                messagebox.showwarning("Warnung", f"File {filename} does not contain valid energies.")
                continue
            data = self.normalize_spectrum(data, metadata)
            min_energy = min(min_energy, data['Energy_keV'].min())
            max_energy = max(max_energy, data['Energy_keV'].max())

        if min_energy == np.inf or max_energy == -np.inf:
            messagebox.showwarning("Warning", "no valid spectrum data found.")
            return

        common_energy = np.linspace(min_energy, max_energy, num=1000)

        # Einlesen und Interpolation des Hintergrunds
        if hasattr(self, 'background_file'):
            background_data, background_metadata = self.read_spectrum(self.background_file)
            if background_data is not None:
                background_data = self.normalize_spectrum(background_data, background_metadata)
                background_counts = self.interpolate_spectrum(background_data, common_energy)
            else:
                background_counts = np.zeros_like(common_energy)
        else:
            background_counts = np.zeros_like(common_energy)

        # Interpolation und Speicherung der Spektren
        for filename in filenames:
            data, metadata = self.read_spectrum(filename)
            if data is None:
                continue
            data = self.normalize_spectrum(data, metadata)
            counts = self.interpolate_spectrum(data, common_energy)

            # Subtraktion des Hintergrunds
            corrected_counts = self.subtract_background(counts, background_counts)

            spectra.append({'filename': filename, 'counts': corrected_counts})

        # Peak-Detektion und Elementidentifikation
        tolerance = 0.126  # in keV
        min_peaks_required = 2

        element_to_energies = reference_data.groupby('Element')['Energy (eV)'].apply(list).to_dict()

        fig = go.Figure()
        summary_table = []
        os_threshold = None

        # Bestimme die Grenze für Os-Peak-Höhe
        for element, energies in element_to_energies.items():
            if element == 'Os':
                os_energies = [e / 1000.0 for e in energies]
                os_threshold = max(os_energies) if os_energies else None
                break

        # Nur nach ausgewählten Gruppen suchen
        group_elements = [group for group, var in self.group_vars.items() if var.get()]
        filtered_element_to_energies = {k: v for k, v in element_to_energies.items() if k in group_elements}

        for spec in spectra:
            peaks, properties = find_peaks(spec['counts']) #, height=os_threshold if os_threshold else 0.05 * max(spec['Counts per Counts'])) #q#1#1#1#
            peak_energies = common_energy[peaks]

            detected_elements = []
            element_scores = []

            for element, energies in filtered_element_to_energies.items():
                matched_peaks = 0
                for energy_ref in energies:
                    energy_ref_keV = energy_ref / 1000.0
                    if np.any(np.abs(peak_energies - energy_ref_keV) < tolerance):
                        matched_peaks += 1
                total_peaks = len(energies)
                score = matched_peaks / total_peaks
                if matched_peaks >= min_peaks_required:
                    detected_elements.append(element)
                    element_scores.append({
                        'Element': element,
                        'Matched Peaks': matched_peaks,
                        'Total Peaks': total_peaks,
                        'Score': score
                    })

            spec['elements'] = detected_elements

            # Ausgabe in eine CSV-Datei
            csv_filename = spec['filename'].replace('.csv', '_analyzed.csv')
            with open(csv_filename, mode='w', newline='') as csv_file:
                fieldnames = ['Element', 'Matched Peaks', 'Total Peaks', 'Score']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                for row in element_scores:
                    writer.writerow(row)
                    summary_table.append(row)

            # Plotten der Spektren
            fig.add_trace(go.Scatter(x=common_energy, y=spec['counts'], mode='lines', name=spec['filename'], showlegend=True))
            for element_info in element_scores:
                element = element_info['Element']
                energies_keV = [e / 1000.0 for e in filtered_element_to_energies[element]]
                for energy in energies_keV:
                    fig.add_trace(go.Scatter(
                        x=[energy],
                        y=[spec['counts'][np.argmin(np.abs(common_energy - energy))]],
                        mode='markers+text',
                        name=element,
                        text=[element],
                        textposition='top center',
                        showlegend=False
                    ))

        # Markiere zusätzliche spezifische Energien mit 'X'
        additional_energies = {
            'Al': [1.486, 1.557],
            'Fe': [6.400, 7.058],
            'Ni': [7.471, 8.265],
            'Cu': [8.048, 8.905],
            'Zn': [8.639, 9.571],
            'Pt': [9.441, 11.072],
            'Pd': [2.838, 2.986],
            'Rh': [2.697, 2.834],
            'Os': [8.907, 10.449],
            'Ir': [9.175, 10.574],
            'Ti': [4.508, 4.931],
            'Cr': [5.415, 5.946],
            'Mn': [5.899, 6.490],
            'Ca': [3.691, 4.012],
            'S': [2.307, 2.464],
            'P': [2.013, 2.139],
            'Si': [1.739, 1.835],
            'Cl': [2.622, 2.815],
            'K': [3.312, 3.590],
            'Mg': [1.254, 1.302]
        }

        for element, energies in additional_energies.items():
            for energy in energies:
                fig.add_trace(go.Scatter(
                    x=[energy],
                    y=[max([spec['counts'][np.argmin(np.abs(common_energy - energy))] for spec in spectra])],
                    mode='markers',
                    name=f'{element} ({energy} keV)',
                    marker=dict(symbol='x', size=10, color='red'),
                    showlegend=False
                ))

        # Legende nur für Spektrenlinien anzeigen
        fig.update_layout(
            title=title,
            xaxis_title='Energie (keV)',
            yaxis_title='Normierte Counts',
            showlegend=True
        )
        plot(fig, filename='spectrum_comparison.html')
        self.status_label.config(text="Analyse abgeschlossen. HTML-Plot und CSV-Dateien gespeichert.")

        # Zeigen der zusammengefassten Tabelle mit detektierten Elementen
        if summary_table:
            summary_window = tk.Toplevel(self.master)
            summary_window.title("Zusammenfassung der detektierten Elemente")
            table_text = tk.Text(summary_window, wrap='none')
            table_text.insert('1.0', "Element\tMatched Peaks\tTotal Peaks\tScore\n")
            for row in summary_table:
                table_text.insert('end', f"{row['Element']}\t{row['Matched Peaks']}\t{row['Total Peaks']}\t{row['Score']:.2f}\n")
            table_text.config(state='disabled')
            table_text.pack()

        # Anzeige der Gruppen Pd, Pt, Rh, Al, Ir, Ni, Os
        self.show_group_intensities(spectra, common_energy, filtered_element_to_energies)

    def show_group_selection(self):
        # Fenster zur Auswahl der Gruppen öffnen
        group_window = tk.Toplevel(self.master)
        group_window.title("Gruppen auswählen")

        frame = tk.Frame(group_window)
        frame.pack(pady=10, padx=10)

        # Annahme: Die Gruppennamen werden aus der Referenzdatei extrahiert
        try:
            reference_data = pd.read_csv(self.reference_file, sep=',', encoding='utf-8')
            unique_groups = reference_data['Element'].unique()
        except Exception as e:
            messagebox.showerror("Fehler", f"Die Referenzdatei konnte nicht eingelesen werden: {e}")
            return

        self.group_vars = {}
        num_columns = 4
        for idx, group in enumerate(unique_groups):
            var = tk.BooleanVar(value=True)
            self.group_vars[group] = var
            chk = tk.Checkbutton(frame, text=group, variable=var)
            chk.grid(row=idx // num_columns, column=idx % num_columns, sticky='w')

        btn_select_all = tk.Button(group_window, text="Alle auswählen", command=self.select_all_groups)
        btn_select_all.pack(side=tk.LEFT, padx=5, pady=5)

        btn_deselect_all = tk.Button(group_window, text="Alle abwählen", command=self.deselect_all_groups)
        btn_deselect_all.pack(side=tk.LEFT, padx=5, pady=5)

        btn_select_bio_elements = tk.Button(group_window, text="Nach Elementen biologischer Substrate suchen", command=self.select_bio_elements)
        btn_select_bio_elements.pack(side=tk.LEFT, padx=5, pady=5)

    def select_all_groups(self):
        for var in self.group_vars.values():
            var.set(True)

    def deselect_all_groups(self):
        for var in self.group_vars.values():
            var.set(False)

    def select_bio_elements(self):
        bio_elements = [
            "Na", "Mg", "Al", "Si", "P", "S", "Cl", "K", "Ca", "Ti", "Cr", "Mn", "Fe", "Ni", "Cu", "Zn", "Se", "Mo", "Ag", "Sn", "Pb"
        ]
        for element, var in self.group_vars.items():
            if element in bio_elements:
                var.set(True)
            else:
                var.set(False)

    def show_group_intensities(self, spectra, common_energy, element_to_energies):
        group_elements = [group for group, var in self.group_vars.items() if var.get()]
        group_window = tk.Toplevel(self.master)
        group_window.title("Intensität der Gruppen")

        group_text = tk.Text(group_window, wrap='none')
        group_text.insert('1.0', "Datei\tElement\tIntensität\n")

        for spec in spectra:
            counts = spec['counts']
            for element in group_elements:
                if element in spec['elements']:
                    element_energies = [e / 1000.0 for e in element_to_energies[element]]
                    intensity = sum([counts[np.argmin(np.abs(common_energy - energy))] for energy in element_energies])
                    group_text.insert('end', f"{spec['filename']}\t{element}\t{intensity:.2f}\n")

        group_text.config(state='disabled')
        group_text.pack()

    def read_spectrum(self, filename):
        try:
            df = pd.read_csv(filename, sep=';', encoding='utf-8', skiprows=0, header=None)
            voltage = df.iloc[0, 1]  # Spannung in Zeile 0, zweite Spalte
            total_counts = pd.to_numeric(df.iloc[2, 1], errors='coerce')  # Total Counts in Zeile 2, zweite Spalte

            # Überspringen der Header-Zeilen (0-7) und Einlesen der relevanten Daten ab Zeile 8
            data = pd.read_csv(filename, sep=';', encoding='utf-8', skiprows=8, names=["Energy [eV]", "Counts"])
            if data.iloc[0, 0] == "Energy [eV]":
                data = data.iloc[1:].reset_index(drop=True)

            data['Counts'] = pd.to_numeric(data['Counts'], errors='coerce')
            data['Counts per Total Counts'] = data['Counts'] / total_counts
            return data, {'Voltage': voltage, 'Total Counts': total_counts}
        except Exception as e:
            messagebox.showwarning("Warnung", f"Die Datei {filename} konnte nicht eingelesen werden oder enthält keine gültigen Daten: {e}")
            return None, None

# Counts per second jetzt nicht mehr

    def normalize_spectrum(self, data, metadata):
        data['Energy_keV'] = pd.to_numeric(data['Energy [eV]'], errors='coerce') / 1000.0
        data['Counts'] = pd.to_numeric(data['Counts'], errors='coerce')
        #live_time = float(metadata.get('Live time', 1)) ###
        live_time = float(metadata.get('Total Counts', 1))
        data['Counts_per_sec'] = data['Counts'] / live_time
        return data

    def interpolate_spectrum(self, data, common_energy):
        interp_func = interp1d(data['Energy_keV'], data['Counts_per_sec'], kind='linear', bounds_error=False, fill_value=0)
        return interp_func(common_energy)

    def subtract_background(self, sample_counts, background_counts):
        corrected_counts = sample_counts - background_counts
        corrected_counts[corrected_counts < 0] = 0
        return corrected_counts

# Starten der Anwendung
if __name__ == "__main__":
    root = tk.Tk()
    app = EDXAnalyzerApp(root)
    root.mainloop()
