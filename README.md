# EDX Spectrum Analyzer
## Description
This Python script provides a graphical user interface (GUI) for the analysis of EDX spectra. It enables the import of multiple spectrum files, background correction, and identification of element peaks based on their characteristic energies. This is my first script designed for non-python speakers.

---

## Requirements

### Installation of Required Libraries
Ensure the following Python libraries are installed:

```bash
pip install pandas numpy scipy matplotlib plotly tkinter
```

**Note**: If you are using Anaconda, some of these libraries may already be pre-installed. The tkinter library is typically included with the standard Python installation.

---

## Preparing Input Files

### Characteristic Energies
Ensure the file containing characteristic energies is prepared as follows:

- File name: characteristic_energies.csv
- Must be located in the same directory as the script.
- File structure (example):
  
  | Element | Line  | Energy_keV |
  |---------|-------|------------|
  | Fe      | Kα    | 6.40       |
  | Cu      | Lβ    | 8.04       |

The file must include at least the columns Element, Line, and Energy_keV.

---

## Using the Script

1. Save the script as edx_analyzer.py.
2. Run the script with the following command:

   ```bash
   python edx_analyzer.py
   ```
   
3. A GUI will open. Select the desired spectrum files (up to 4 files) and optionally a background file.
Start the analysis using the GUI's button.

**Output**:

- An interactive plot saved as an HTML file (edx_spectrum_analysis.html).
- Analysis results, including peak identification.

---

## Customization Options

### Energy Tolerance
Adjust the variable energy_tolerance to control the precision of peak-to-element assignments:

- High resolution: ±0.05 keV
- Standard: ±0.1 keV

### Peak Detection Parameters
Modify the parameters in the find_peaks function to adjust the sensitivity of peak detection:

- **height**: Minimum height of the peaks (relative or absolute).
- **distance**: Minimum distance between detected peaks.

---

## Recommendations

**Data Calibration**: Ensure that the energy axes of the spectra are properly calibrated.
**Testing with Example Data**: Use known spectra to verify the script's functionality.
**Error Handling**: The script includes basic error checks for missing files or incorrect formats.

---
## Reporting Issues
For bug reports or feature requests, please open an issue in the GitHub repository: [GitHub Issues](https://github.com/teemoscutie/cute_edx_analyzer/issues)

If you have any questions, suggestions, or need further assistance, feel free to reach out to me:

- **Name**: Linh Ngoc Tram Zimmermann
- **Email**: teemoscutie@outlook.de
- **GitHub**: [https://github.com/teemoscutie](https://github.com/teemoscutie)
- **LinkedIn**: [LinkedIn](https://www.linkedin.com/in/linh-zimmermann)

I am happy to help or receive feedback regarding this project!
