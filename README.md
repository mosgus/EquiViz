# EquiViz 📊
A Python-based equity portfolio visualizer using Streamlit and yfinance.

### Features
- **Web Interface**:
    - Users run EquiViz using a webpage interface, providing a CSV file of their portfolio.
        -  EquiViz will scan csv files in /porfolios if users DON'T provide a portfolio via commandline inputs.
          
### Dependencies
```bash
pip install yfinance --upgrade --no-cache-dir 
```
```bash
pip install flask
```
### How to run
Currently we run EquiViz locally using Flask. It will be hosted later.
```bash
python app.py
```
And then use the local server link provided.