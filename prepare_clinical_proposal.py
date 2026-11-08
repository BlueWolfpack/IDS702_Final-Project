"""Rebuild the clinical proposal's descriptive audit and PDF from the frozen CSV.
Requires pandas, numpy, reportlab. No models or significance tests are fitted.
"""
from pathlib import Path
import argparse, json, math, csv
import numpy as np
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.graphics.shapes import Drawing, Rect, Line, String, Circle

HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser()
ap.add_argument('--data-dir',type=Path,required=True)
args=ap.parse_args()
out=HERE/'output'; out.mkdir(exist_ok=True)
d=pd.read_csv(args.data_dir/'trials_analysis_candidate.csv',keep_default_na=False)
all_d=pd.read_csv(args.data_dir/'trials_all_downloaded.csv',keep_default_na=False,low_memory=False)
d['enrollment_count']=pd.to_numeric(d.enrollment_count)
assert len(d)==18583 and len(d.columns)==36 and d.nct_id.is_unique
assert len(all_d)==22669 and all_d.nct_id.is_unique
assert (d.enrollment_count>0).all() and (d.enrollment_type=='ACTUAL').all()
assert set(d.phase_group)=={'PHASE2','PHASE3'}
summary=d.groupby(['phase_group','sponsor_group']).enrollment_count.agg(n='size',median='median',q1=lambda x:x.quantile(.25),q3=lambda x:x.quantile(.75),mean='mean',minimum='min',maximum='max').reset_index()
summary.to_csv(out/'clinical_eda_group_summary.csv',index=False)
audit={'rows':len(d),'columns':len(d.columns),'unique_sponsor_names':d.lead_sponsor_name.nunique(),'enrollment_summary':d.enrollment_count.describe(percentiles=[.25,.5,.75,.95,.99]).to_dict(),'group_summary':summary.to_dict(orient='records'),'models_fitted':False}
(out/'clinical_eda_summary.json').write_text(json.dumps(audit,indent=2)+'\n')
BLUE=colors.HexColor('#184B70'); TEAL=colors.HexColor('#087F8C'); GRAY=colors.HexColor('#536575'); LIGHT=colors.HexColor('#EAF1F5')

def histogram():
    g=Drawing(470,200); x0,y0,w,h=48,37,405,137
    counts,edges=np.histogram(np.log10(d.enrollment_count),bins=np.linspace(0,6,31))
    ymax=math.ceil(max(counts)/500)*500
    for v in range(0,ymax+1,500):
        y=y0+h*v/ymax; g.add(Line(x0,y,x0+w,y,strokeColor=LIGHT)); g.add(String(x0-8,y-3,str(v),textAnchor='end',fontSize=8,fillColor=GRAY))
    for i,c in enumerate(counts):
        g.add(Rect(x0+w*i/30+1,y0,w/30-2,h*c/ymax,fillColor=BLUE,strokeColor=None))
    for i,label in enumerate(['1','10','100','1,000','10,000','100,000','1,000,000']):
        g.add(String(x0+w*i/6,y0-15,label,textAnchor='middle',fontSize=8,fillColor=GRAY))
    g.add(String(x0+w/2,7,'Actual enrollment (log10 axis; all trials retained)',fontSize=9,textAnchor='middle',fillColor=GRAY))
    g.add(String(5,188,'Number of trials',fontSize=9,fillColor=GRAY))
    return g

def boxplot():
    g=Drawing(470,225); x0,y0,w,h=53,56,400,143
    def yy(value):return y0+h*math.log10(value)/6
    for k in range(7):
        y=y0+h*k/6;g.add(Line(x0,y,x0+w,y,strokeColor=LIGHT));g.add(String(x0-8,y-3,f'{10**k:,}',fontSize=8,textAnchor='end',fillColor=GRAY))
    for i,(phase,sponsor) in enumerate([('PHASE2','NONINDUSTRY'),('PHASE2','INDUSTRY'),('PHASE3','NONINDUSTRY'),('PHASE3','INDUSTRY')]):
        v=d.loc[(d.phase_group==phase)&(d.sponsor_group==sponsor),'enrollment_count'].to_numpy()
        q1,med,q3=np.quantile(v,[.25,.5,.75]); x=x0+(i+.5)*w/4
        shade=TEAL if sponsor=='INDUSTRY' else BLUE
        g.add(Line(x,yy(v.min()),x,yy(v.max()),strokeColor=shade))
        g.add(Rect(x-20,yy(q1),40,yy(q3)-yy(q1),fillColor=colors.white,strokeColor=shade,strokeWidth=1.2))
        g.add(Line(x-20,yy(med),x+20,yy(med),strokeColor=shade,strokeWidth=2))
        for y in [yy(v.min()),yy(v.max())]:g.add(Line(x-8,y,x+8,y,strokeColor=shade))
        g.add(String(x,37,'Phase '+phase[-1],fontSize=9,textAnchor='middle',fillColor=GRAY))
        g.add(String(x,24,'Industry' if sponsor=='INDUSTRY' else 'Nonindustry',fontSize=9,textAnchor='middle',fillColor=GRAY))
    g.add(String(5,213,'Actual enrollment (log10 axis)',fontSize=9,fillColor=GRAY))
    return g

styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleX',fontName='Helvetica-Bold',fontSize=21,leading=25,textColor=BLUE,spaceAfter=11))
styles.add(ParagraphStyle(name='SubX',fontName='Helvetica',fontSize=10,leading=14,textColor=GRAY,spaceAfter=13))
styles.add(ParagraphStyle(name='H1X',fontName='Helvetica-Bold',fontSize=14,leading=18,textColor=BLUE,spaceAfter=9))
styles.add(ParagraphStyle(name='H2X',fontName='Helvetica-Bold',fontSize=10.5,leading=14,textColor=TEAL,spaceBefore=8,spaceAfter=5))
styles.add(ParagraphStyle(name='BodyX',fontName='Helvetica',fontSize=10,leading=14,spaceAfter=7))
styles.add(ParagraphStyle(name='SmallX',fontName='Helvetica',fontSize=8.2,leading=11,spaceAfter=6))
styles.add(ParagraphStyle(name='CellX',fontName='Helvetica',fontSize=8.4,leading=11))
story=[]
def p(t,style='BodyX'):return Paragraph(t,styles[style])
def add(t,style='BodyX'):story.append(p(t,style))
def heading(t):add(t,'H1X')
def sub(t):add(t,'H2X')
def table(rows,widths):
    t=Table([[p(str(v),'CellX') for v in row] for row in rows],colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),LIGHT),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),.6,BLUE),('LINEBELOW',(0,1),(-1,-1),.3,LIGHT)]));story.append(t);story.append(Spacer(1,8))
folder='https://drive.google.com/drive/folders/1Zk7kmZaLdCKmmyyWo13c-JfCUxXnursR'
repo='https://github.com/BlueWolfpack/IDS702_Final-Project'

add('Clinical-Trial Enrollment','TitleX')
add('Development phase, sponsor type, and differences in trial size','H1X')
add('IDS 702 | Dataset Option 1 | Haoran Wang | November 8, 2026<br/>Proposal draft for team review; complements the existing Freddie Mac option.','SubX')
sub('1. Research questions and motivation')
add('Trial enrollment measures the scale of a study. Differences by development phase and sponsor type may help research administrators and trial planners describe the clinical research landscape. Enrollment is not a measure of drug quality, study success, or participant-level treatment benefit.')
add('<b>RQ1:</b> Among eligible completed Phase 2 and Phase 3 drug or biological trials starting in 2015-2024, is development phase associated with actual enrollment after accounting for lead-sponsor type and start year?')
add('<b>RQ2:</b> Does the Phase 3 versus Phase 2 association differ between industry and nonindustry lead sponsors, after accounting for start year?')
sub('2. Data source, dates, and study population')
add('The downloaded source is the official ClinicalTrials.gov API v2, not an AACT database snapshot. AACT is a related relational representation of registry data; its exact schema and version have not been substituted for this extract.')
add('<b>Data pull:</b> November 8, 2026 (UTC). <b>Registry data timestamp:</b> November 6, 2026, 10:00:05, as reported by API v2.0.5. This is a continuously updated registry, not a dataset with one original collection date. The 2015-2024 restriction refers to recorded study start years; completion may occur later.')
add('One observation is one registered trial identified by NCT ID. The downloaded cohort contains 22,669 completed interventional trials with a Phase 2 or 3 designation and a drug or biological intervention. The provisional analytic cohort has 18,583 trials with one exact phase (2 or 3), positive actual enrollment, and known lead-sponsor information. Records are global, not restricted to U.S. trials or a single disease.')
add(f'<b>Data:</b> <link href="{folder}" color="#184B70">Google Drive dataset folder</link><br/><b>Code and team proposal:</b> <link href="{repo}" color="#184B70">IDS702_Final-Project repository</link>','SmallX')
story.append(PageBreak())

heading('Variables and data cleaning')
sub('3. Outcome, exposures, and other variables')
table([
['Variable','Role and definition','Coding / use'],
['enrollment_count','Primary outcome: actual reported enrollment.','Positive integer; primary model uses natural log.'],
['phase_group','Primary exposure: exact recorded phase.','PHASE2 reference; PHASE3 indicator P. Combined phases excluded.'],
['sponsor_group','Primary exposure / effect modifier: lead-sponsor type.','NONINDUSTRY reference; INDUSTRY indicator I. Not all study funding.'],
['start_year','Adjustment variable: recorded start year.','2015-2024; categorical, 2015 reference.'],
['lead_sponsor_name','Clustering identifier.','Recorded sponsor name; inspect aliases before clustering.'],
['nct_id','Trial identifier and deduplication key.','One unique NCT ID per row; not a predictor.'],
['allocation; masking; intervention type','Descriptive / sensitivity variables.','Preserve source categories, missingness, and drug/biological flags.']
],[105,195,168])
sub('4. Prespecified cleaning rules')
add('Retain both the full frozen extract and the candidate table. Confirm unique NCT IDs, valid phases, positive actual enrollment, and dates within the start-year window. Exclude mixed Phase 1/2 and Phase 2/3 studies rather than arbitrarily assigning them to a single phase. Do not interpret completed status as efficacy success.')
add('Map INDUSTRY to industry; NIH, FED, OTHER_GOV, NETWORK, OTHER, and INDIV to nonindustry. Unknown or unmapped classes remain missing. This comparison concerns the recorded lead sponsor; the nonindustry category is heterogeneous.')
add('A total of 4,086 downloaded records were excluded. Nonexclusive reasons were combined phases (4,015), enrollment not actual (88), missing enrollment (3), and unknown/unmapped sponsor class (5). Reasons overlap and should not be added to obtain the excluded total.')
add('Preserve partial dates and source date types. Empty fields are missing; the allocation value NA means not applicable. Parse JSON-array columns without expanding the trial-level table. No numerical imputation, automatic winsorization, or outlier deletion has been applied.')
add('Inspect the largest trials against their registry records. If an error is confirmed, document the correction and source; otherwise retain it and evaluate influence. Missingness in supplementary design variables will be reported separately, with a complete-case sensitivity analysis if those variables enter a model.')
story.append(PageBreak())

heading('Statistical analysis plan')
sub('5. Model and inferential targets')
add('For trial i, let Y be positive actual enrollment, P indicate Phase 3, I indicate an industry lead sponsor, and S be start year. The proposed model is:')
add('<b>log(Y<sub>i</sub>) = beta<sub>0</sub> + beta<sub>P</sub>P<sub>i</sub> + beta<sub>I</sub>I<sub>i</sub> + beta<sub>PI</sub>P<sub>i</sub>I<sub>i</sub> + sum<sub>y=2016,...,2024</sub> gamma<sub>y</sub>1(S<sub>i</sub>=y) + error<sub>i</sub>.</b>')
add('Fit ordinary least squares to log enrollment. Year indicators allow flexible differences across start cohorts. Phase and sponsor enter jointly with their interaction. Use sponsor-clustered robust standard errors, after checking the number, sizes, and naming consistency of clusters; the current extract contains 4,790 distinct recorded sponsor names.')
add('<b>RQ1:</b> jointly test beta<sub>P</sub> = beta<sub>PI</sub> = 0. Report Phase 3/Phase 2 geometric-mean ratios: exp(beta<sub>P</sub>) for nonindustry and exp(beta<sub>P</sub> + beta<sub>PI</sub>) for industry, each with a 95% confidence interval. <b>RQ2:</b> test beta<sub>PI</sub> = 0 and report exp(beta<sub>PI</sub>), the ratio of the two phase ratios. Use two-sided tests; apply Holm adjustment across the two planned question-level tests and emphasize estimates and intervals.')
sub('6. Rationale, assumptions, and assessment')
add('Enrollment is a count but spans several orders of magnitude. Modeling its logarithm is a transparent starting point for relative differences and reduces the influence of scale. Exponentiated coefficients describe conditional geometric-mean ratios, not arithmetic-mean or median ratios. A logarithmic transformation alone does not guarantee an adequate model.')
add('Check residual-versus-fitted plots, residual distributions, group-specific residual spread, leverage and Cook\'s distance, and phase-by-sponsor-by-year cell sizes. Inspect sponsor cluster size concentration. Robust uncertainty estimates allow within-sponsor dependence and heterogeneous variance, but do not repair misspecified conditional means or unmeasured confounding.')
add('Prespecify a negative-binomial log-link model as a sensitivity analysis for overdispersed counts, with the same covariates and sponsor-robust uncertainty where supported. It targets arithmetic conditional mean ratios, so agreement will be assessed qualitatively. Repeat the log model excluding the largest 1% of enrollments as a labeled sensitivity analysis, not as primary cleaning. No model is selected by whichever produces a smaller p-value.')
sub('7. Scope and interpretation')
add('This is an observational analysis of a selected registry cohort. Disease, trial design, geography, and registry coverage may explain some differences. Completed-only inclusion gives recent cohorts less time to enter the sample. Confidence intervals are model-based; this is not a probability sample of all trials. Results will describe adjusted associations, not causal effects or recommended enrollment targets. No model or hypothesis test has been fitted for this proposal.')
story.append(PageBreak())

heading('Preliminary EDA | 1 of 2')
add('These results were computed from the frozen November 8 extract. Each row is a trial, with no patient records or repeated trial rows. The candidate table has 18,583 rows and 36 columns; phase, sponsor group, enrollment, and start year are complete by the eligibility rules. This completeness does not describe the unfiltered registry.','SubX')
table([['Cohort / characteristic','Observed value'],['All downloaded / candidate trials','22,669 / 18,583'],['Phase 2 / Phase 3 trials','10,993 / 7,590'],['Industry / nonindustry trials','10,261 / 8,322'],['Enrollment median [Q1, Q3]','100 [40, 260]'],['Enrollment mean / maximum','416.2 / 500,000'],['Missing start-date type / completion date','1,365 / 15']],[265,203])
sub('Figure 1. Distribution of actual enrollment')
story.append(histogram())
add('Equal-width bins are shown on the log10 enrollment scale, with counts on the vertical axis. Every eligible trial is included. The arithmetic mean exceeds the median, and the extreme upper tail motivates the proposed transformation and influence diagnostics. Large values may be valid public-health studies and are not automatically errors.','SmallX')
add('The recorded largest trial is NCT05148845 (500,000), followed by NCT04838795 (477,102). These values are reported registry enrollments, not independently verified participant counts. Their source records should be checked during final cleaning.','SmallX')
story.append(PageBreak())

heading('Preliminary EDA | 2 of 2')
sub('Table 2. Enrollment by phase and lead-sponsor type')
rows=[['Phase','Sponsor','Trials','Median','Mean']]
for phase,sponsor in [('PHASE2','NONINDUSTRY'),('PHASE2','INDUSTRY'),('PHASE3','NONINDUSTRY'),('PHASE3','INDUSTRY')]:
    r=summary[(summary.phase_group==phase)&(summary.sponsor_group==sponsor)].iloc[0]
    rows.append(['Phase '+phase[-1],sponsor.title(),f'{r["n"]:,}',f'{r["median"]:g}',f'{r["mean"]:,.1f}'])
table(rows,[62,104,90,106,106])
sub('Figure 2. Group distributions on a common scale')
story.append(boxplot())
add('Boxes show the 25th-75th percentiles and the line within each box is the median. Whiskers show the full observed minimum-maximum range, not the conventional 1.5-IQR rule. No individual observations or extremes are omitted from the range.','SmallX')
add('Phase 3 medians exceed Phase 2 medians in both sponsor groups. However, the Phase 3 nonindustry mean is much larger than its median because of the upper tail. These unadjusted summaries motivate the interaction and robust diagnostics; they do not establish an adjusted association or statistical significance.','SmallX')
sub('Next steps and final deliverables')
add('Agree on the dataset option with the team; audit extreme enrollments and sponsor labels; fit the prespecified model and sensitivity analyses; then write the 5-7 page report and 2-3 page stakeholder memo. The final QMD will hide code and present formatted tables, figures, confidence intervals, and limitations. Team meeting and communication policies still require team agreement.','SmallX')
sub('References')
add('U.S. National Library of Medicine. (2026). ClinicalTrials.gov [Registry data; API v2 extract retrieved November 8, 2026]. https://clinicaltrials.gov/data-api/api<br/>Clinical Trials Transformation Initiative. (n.d.). AACT: Aggregate Analysis of ClinicalTrials.gov. https://aact.ctti-clinicaltrials.org/landing (background only; not the downloaded snapshot).','SmallX')

def footer(c,doc):
    c.setStrokeColor(LIGHT);c.line(54,43,558,43)
    c.setFont('Helvetica',8);c.setFillColor(GRAY);c.drawString(54,30,'IDS 702 | Clinical-trials proposal | Draft for team review');c.drawRightString(558,30,str(doc.page))
pdf=out/'ClinicalTrials_Proposal.pdf'
doc=SimpleDocTemplate(str(pdf),pagesize=(612,792),rightMargin=72,leftMargin=72,topMargin=47,bottomMargin=56)
doc.build(story,onFirstPage=footer,onLaterPages=footer)
from pypdf import PdfReader
reader=PdfReader(str(pdf));assert len(reader.pages)==5, len(reader.pages)
print(json.dumps({'pdf':str(pdf),'pages':len(reader.pages),'audit':audit},indent=2))
