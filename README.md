# Transistor IDS/IGS analysis

A tool for analyzing transistor behavior through IDS/IGS current ratio, on/off ratio, and transfer curves across multiple gate voltage sweep cycles.

## Requirements
- Python 
- Pandas
- Numpy
- Matplotlib
- Streamlit
- Plotly

Install dependencies:
```bash
pip install -r requirements.txt
```

## How to use

1. Run the app:
```bash
streamlit run app.py
```

2. Upload your `.txt` data file
3. Use the checkboxes to filter between forward and reverse sweeps
4. Select cycles to compare in the chart

## File structure

- `app.py` — interactive Streamlit dashboard
- `calcular_IDSIGS.py` — data processing script
- `requirements.txt` — project dependencies
