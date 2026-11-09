# IDS702_Final-Project
This repository is for the stats group project 


## Data Access (Dataset Option 2)

The Freddie Mac loan-level dataset used in this project is available through Google Drive:

[Access the dataset](https://drive.google.com/drive/folders/1wcYV5-2_TSR5FxkU4TL7xdaeFkxauKCt?usp=drive_link)

Due to the large size of the dataset, the files could not be uploaded directly to GitHub. Instead, they are provided through the Google Drive link above. The folder contains the origination and monthly performance files for the 2022–2024 cohorts.

Download the required files and place them in the appropriate project directory before running the code. The provided scripts can then be used to read the data and perform exploratory data analysis (EDA).
- Read the mortgage loan proposal (pdf) 

## Clinical-trials alternative (Dataset Option 1)

Prepared November 8, 2026 for team review.

- [Read the clinical proposal (PDF)](output/ClinicalTrials_Proposal.pdf)
- [Editable clinical proposal and R EDA code](ClinicalTrials_Proposal.qmd)
- [Combined two-option proposal](702_Project_Proposal%20%281%29.qmd)
- [Clinical-trials data and documentation on Google Drive](https://drive.google.com/drive/folders/1Zk7kmZaLdCKmmyyWo13c-JfCUxXnursR)
- [PDF copy on Drive](https://drive.google.com/file/d/1lwvjUH15tzDRxK0WcEQbtt6K5VbOLvoz/view)

**Source:** an official ClinicalTrials.gov API v2 extract, downloaded November 8, 2026, not an AACT database snapshot. It contains completed interventional drug/biological studies with recorded start years 2015-2024. The full extract has 22,669 trials; the provisional candidate table has 18,583 trials and 36 variables. One row is one registered trial.

**Questions:** Is phase associated with actual enrollment after accounting for sponsor type and start year? Does the phase association differ between industry and nonindustry sponsors? The proposal specifies log-enrollment regression, a phase-by-sponsor interaction, sponsor-clustered uncertainty, diagnostics, and sensitivity analyses. Descriptive EDA is complete for the proposal; no inferential model has been fitted.

### Run the clinical EDA

Download `trials_analysis_candidate.csv` into `data/clinical_trials/` (the data folder is ignored by Git). From the repository root, use R, Quarto, and `knitr`:

```bash
quarto render ClinicalTrials_Proposal.qmd --to html
quarto render ClinicalTrials_Proposal.qmd --to pdf
```

For a different data location, set `CLINICAL_DATA_DIR`. PDF rendering also requires a working LaTeX installation. R and Quarto were unavailable on the preparation machine, so the QMD has not been executed there. The checked five-page PDF was generated independently from the frozen CSV using Python; it contains verified descriptive results.

To regenerate that PDF and its EDA summary files, download both clinical CSVs into the same folder, install `requirements-clinical.txt`, and run:

```bash
python3 prepare_clinical_proposal.py --data-dir data/clinical_trials
```

The existing Freddie Mac option is retained for the team's dataset decision. The previously uploaded `702_Project_Proposal--1-.pdf` predates the clinical update; use the new clinical PDF above to review this option. Team-charter policies and final dataset selection still need team agreement.

