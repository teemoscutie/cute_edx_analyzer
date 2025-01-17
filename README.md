# EDX Spectrum Analyzer
## Description
This Python script provides a **graphical user interface** (GUI) for analyzing **Energy Dispersive X-ray Spectroscopy** (EDX) spectra. It enables users without python knowledge to load, process, and compare multiple EDX spectra. It aims to identify peaks in the future, but is currently only for referece purposes for manual element identification.

### Background correction is currently disabled due to implementation issues!

---

## Requirements

### Python 3.XX
```bash
python3 --version
```
Make sure to download python if not installed. Also, check if pip is installed:

```bash
pip --version
```
If not, install pip with:

```bash
python -m ensurepip --upgrade
```

### Installation of Required Libraries
Ensure the following Python libraries are installed:

```bash
pip install pandas numpy scipy matplotlib plotly tkinter
```

**Note**: If you are using Anaconda, some of these libraries may already be pre-installed. The tkinter library is typically included with the standard Python installation.

---

## Preparing Input Files

### Characteristic Energies

Ensure the file containing characteristic energies is prepared as following or use the data given:

- File structure (example):
  
  | Element | Transition  | Theory (eV) | Unc (eV) | Direct (eV)  | Unc. (eV) |
  |---------|-------------|-------------|----------|--------------|-----------|
  | Ne      | KL1         | 817.69      |0.56      |              |           |
  | Ne      | KL2         | 849.09      |0.54      |848.61        |0.26       |


---

## Using the Script

1. Save the script as edx_analyzer.py.
2. Run the script with the following command:

   ```bash
   python cute_edx_analyzer.py
   ```
   
3. A GUI will open. Select the desired spectrum files (up to 4 files) and optionally a background file.
4. Next, add the Reference data Energies_from_NIST.csv or equivalent.
5. Then, select Groups that should be shown at the plot. For biological substrates a preset is given.
6. Start analysis with the GUIs button. (Pop ups will appear without any use at this point)

**Output**:

- An interactive plot saved as an HTML file (edx_spectrum_analysis.html).
- Analysis results, including peak identification.

---

## Outlook

### Peak detection
It will be possible to include a peak detection. Currently, this detection is highly inaccurate and should only be used for reference purposes to identify peaks manually.
I aim for an adjustable resolution with printed errors.
Therefore, standards for script learing are required. Those are going to be implemented, to ensure a more accurate peak detection. Thus, EDX spectra from biologist undergraduates are used to understand given peak detection from TESCAN Clara Software. Furthermore, the sputtering material should provide limits for element detection. This is possible due to known precise element composition.

---

## Recommendations

**Data**: Ensure that the landing energy and the beam current is homogeneous for all samples / compared samples.

**Angles**: The landing beam should be 0° (or as recommended for your EDX).

**Error Handling**: The script includes basic error checks for missing files or incorrect formats. 

---
## Reporting Issues
For bug reports or feature requests, please open an issue in the GitHub repository: [GitHub Issues](https://github.com/teemoscutie/cute_edx_analyzer/issues)

If you have any questions, suggestions, or need further assistance, feel free to reach out to me:

- **Name**: Linh Ngoc Tram Zimmermann
- **Email**: teemoscutie@outlook.de
- **GitHub**: [https://github.com/teemoscutie](https://github.com/teemoscutie)
- **LinkedIn**: [LinkedIn](https://www.linkedin.com/in/linh-zimmermann)
