# THE INFLUENCE OF TV SHOWS ON BABY NAME TRENDS IN CANADA
This repository contains the final project for CMPT 353: Computational Data Science at Simon Fraser University (Summer 2025).

## Overview
This project investigates whether characters from popular TV shows influence baby name trends in Canada. Key question in analysis is:<br>
**Do popular TV show characters influence baby name usage in Canada?**

## Cloning the Repository
**This repository uses Git Large File Storage (Git LFS) to manage large data files.**
1. Install Git LFS (if you haven't already):
```git lfs install```

2. Clone the repository:
```git clone <your-repo-url>```<br>
```cd <your-repo-directory>```

3. Pull LFS-tracked files (If you do not see ```raw_data/```):
```git lfs pull```

## Running the Code
1. To install all necessary Python packages, run:  :<br>
```pip install -r requirements.txt```
2. Run the scripts in the order listed under [Script Files](#script-files) (1 to 5). You do NOT need to run ```config.py``` directory. Use either of the following commands to execute each script: <br>```python <filename>``` or ```python3 <filename>```.  <br>
Example: ```python get_baby_name_csv.py```

## Project Structure
### Structure Overview
```
cmpt353-project/
├── raw_data/
├── processed_data/
├── plots/
├── results/
│
├── config.py
├── get_baby_name_csv.py
├── get_main_characters_names.py
├── check_assumptions.py
├── name_trend_analysis.py
├── get_box_plots.py
│
|── requirements.txt
└── README.md
```
### Directories
1. ```raw_data``` contains:<br>
• ```baby-names-frequency_1980_2020.xlsx```<br>
• ```baby-names-frequency_2024.xlsx```<br>
• ```IMDB.csv```<br>
• ```title.principals.tsv```<br>
These are raw data I downloaded. See the report for more details.

2. ```processed_data``` contains:<br>
• ```baby_names_by_year.csv```<br>
• ```popular_shows.csv```<br>
• ```main_characters.csv```<br>
• ```clean_main_characters.csv```<br>
• ```name_trends.csv```<br>
These are processed data by cleanining and combining the raw data in ```raw_data/```

3. ```plots/``` contains histograms and box plots for visualization. They are used in the report.

4. ```results/``` contains CSV files summarizing statistical test outcomes

### Script Files
1. ```get_baby_name_csv.py```: Extracts baby name data from raw Excel files and saves it as a cleaned CSV file

2. ```get_main_characters_names.py```: Extracts names of main TV show characters from IMDb data and filters relevant TV shows. Outputs the final cleaned dataset: ```name_trends.csv```

3. ```check_assumptions.py```: Verifies t-test assumptions

4. ```name_trend_analysis.py```: Runs t-tests and Mann-Whitney U tests

5. ```get_box_plots.py```: Generates boxplots for top trend results

6. ``` config.py ``` contains shared directory paths used by other scripts. This file is imported by other scripts and does not need to be run directly

### Other files
1. ```README```: Lists overview and setup instructions,
2. ```requirements.txt```: Lists all the Python libraries and their versions needed to run the project
## Author
Maki Hosokawa
