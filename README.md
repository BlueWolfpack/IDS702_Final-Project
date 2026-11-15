# IDS702_Final-Project
This repository is for the stats group project 


### From Default Prediction to Expected Credit Loss ( Dataset Option 2)
#### Data Access 

The Freddie Mac loan-level dataset used in this project is available through Google Drive:

[Access the dataset](https://drive.google.com/drive/folders/1wcYV5-2_TSR5FxkU4TL7xdaeFkxauKCt?usp=drive_link)

Due to the large size of the dataset, the files could not be uploaded directly to GitHub. Instead, they are provided through the Google Drive link above. The folder contains the origination and monthly performance files for the 2022–2024 cohorts.

Download the required files and place them in the appropriate project directory before running the code. The provided scripts can then be used to read the data and perform exploratory data analysis (EDA).


## Revised clinical trials proposal (Dataset Option 1)

- [Revised proposal and R code](clinical-trials/ClinicalTrials_Proposal_Revised.qmd)
- [Frozen candidate CSV (compressed)](clinical-trials/trials_analysis_candidate.csv.gz)
- [Source data and documentation](https://drive.google.com/drive/folders/1Zk7kmZaLdCKmmyyWo13c-JfCUxXnursR)

The proposal asks whether the difference in mean actual enrollment between industry and non-industry lead sponsors varies by development phase after adjusting for start year. The included ClinicalTrials.gov extract has 18,583 eligible trials and 36 variables. The original proposal remains in the repository for reference.

### Render the revised proposal

Install R and Quarto. In R, install the rendering packages once:

```r
install.packages(c("knitr", "rmarkdown"))
```

A LaTeX installation is required for PDF output. If you don't already have one, run `quarto install tinytex` once in your terminal. From the repository root, run:

```sh
quarto render clinical-trials/ClinicalTrials_Proposal_Revised.qmd --to pdf
```

Both the QMD and its CSV are included in the checkout. R reads the compressed CSV directly. No unzipping, Drive download, or path changes are needed. Use `--to html` instead if you don't need PDF or LaTeX.
