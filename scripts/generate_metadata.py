import pandas as pd
import numpy as np
import io
import random

#Read excel file
df = pd.read_excel(r'data/input/Master_TMA_analyses.xlsx', sheet_name='Overig')
df = df.drop_duplicates(subset=['Patient_nr'])
tumor_size = df['Tumorsize']
l = []

for x in tumor_size:
    l.append(x.replace(',','.'))
df['Tumorsize'] = l
df = df[pd.to_numeric(df.Tumorsize, errors='coerce').notnull()]
randomIDlist=[]
for i in range(len(df['Patient_nr'])):
    randomID = 'P' + str(i)
    randomIDlist.append(randomID)


random.shuffle(randomIDlist)
df['Patient_nr'] = randomIDlist



# Open metadata and data files
meta_study= open("/home/onco/mdekorte/Documents/Cbioportal_clean/cbioportal/test_study/MMC_test/meta_study.txt", "w+")
meta_clinical_patient= open("/home/onco/mdekorte/Documents/Cbioportal_clean/cbioportal/test_study/MMC_test/meta_clinical_patient.txt", "w+")
data_clinical = open("/home/onco/mdekorte/Documents/Cbioportal_clean/cbioportal/test_study/MMC_test/data_clinical_patient.txt", "w+")
meta_clinical_sample= open("/home/onco/mdekorte/Documents/Cbioportal_clean/cbioportal/test_study/MMC_test/meta_clinical_sample.txt", "w+")
data_clinical_sample= open("/home/onco/mdekorte/Documents/Cbioportal_clean/cbioportal/test_study/MMC_test/data_clinical_sample.txt", "w+")
data_type_cancer = open("/home/onco/mdekorte/Documents/Cbioportal_clean/cbioportal/test_study/MMC_test/cancer_type.txt", "w+")
meta_type_cancer = open("/home/onco/mdekorte/Documents/Cbioportal_clean/cbioportal/test_study/MMC_test/meta_cancer_type.txt", "w+")

#Write study meta
meta_study.write(
"""type_of_cancer: idc_test
cancer_study_identifier: idc_test_study
name: Test study (Derksen Lab 2021)
short_name: TS (Derksen)
description: Clinical data gathered at the UMC Utrecht.
add_global_case_list: true
groups: PUBLIC""")


meta_clinical_patient.write(
    """cancer_study_identifier: idc_test_study
genetic_alteration_type: CLINICAL
datatype: PATIENT_ATTRIBUTES
data_filename: data_clinical_patient.txt"""
)

meta_clinical_sample.write(
"""cancer_study_identifier: idc_test_study
genetic_alteration_type: CLINICAL
datatype: SAMPLE_ATTRIBUTES
data_filename: data_clinical_sample.txt"""
)


#Patient    identifier  Patient Age Sex Sample  Origin   Tumor size Overall Survival Status    Overall survival (months)   Disease free survival status    Disease free (months)
#
#
#
#
data_clinical_sample.write(
"""#Sample identifier\tPatient identifier\tSample Origin\tTumor size
#Sample identifier\tPatient identifier\tSample 0rigin\tTumor size
#STRING\tSTRING\tSTRING\tNUMBER
#1\t1\t1\t1
""")

data_clinical.write(
"""#Patient identifier\tPatient Age\tSex\tOverall Survival Status\tOverall survival (months)\tDisease free survival status\tDisease free (months)\tRadio therapy\tHormone therapy\tImmuno therapy\tChemo therapy
#Patient identifier\tPatient Age\tSex\tOverall Survival Status\tOverall survival (months)\tDisease free survival status\tDisease free (months)\tRadio therapy\tHormone therapy\tImmuno therapy\tChemo therapy
#STRING\tNUMBER\tSTRING\tSTRING\tNUMBER\tSTRING\tNUMBER\tNUMBER\tNUMBER\tNUMBER\tNUMBER
#1\t1\t1\t1\t1\t1\t1\t1\t1\t1\t1
""")

data_type_cancer.write("idc_test\tInvasive Ductal Carcinoma test\tbreast,breast invasive\tHotPink\tBreast\n")
meta_type_cancer.write(
"""genetic_alteration_type: CANCER_TYPE
datatype: CANCER_TYPE
data_filename: cancer_type.txt""")

df= df[["T_nr", "Tumorblock","Patient_nr", "Age", "Sex_M1_F2", "PathData_from", "Tumorsize", "OS_status_01", "OS_months", "DFS_status_01", "DFS_months", "RT", "HT", "CT", "IT"]]

for column in df:

    # filter on patient number and randomise the patient numbers
    if column == "T_nr":
        sample_id_list = []
        for i in range(len(df[column])):
            sample_id = str(df.iloc[i][2]) + "-" + str(i)
            sample_id_list.append(sample_id)
        if len(sample_id_list) == len(df.index):
            df[column] = sample_id_list
            df = df.rename(columns={'T_nr':'SAMPLE_ID'})

    # rename column
    if column == 'Patient_nr':
        df = df.rename(columns={'Patient_nr':'PATIENT_ID'})
    
    # transform values to male/female
    if column == "Sex_M1_F2":
        ncolumn=[]
        for sex in df[column]:
            if int(sex) ==1:
                ncolumn.append("Male")
            if int(sex) ==2:
                ncolumn.append("Female")
            if(len(df.index)==len(ncolumn)):
                df[column] = ncolumn
                df = df.rename(columns={'Sex_M1_F2':'SEX'})

    # rename column
    if column == 'Age':
        df = df.rename(columns={column:'AGE'})
    
    
    if column == "Tumorsize":
        tcolumn = []
        for value in df[column]:
            tcolumn.append(value.replace(',','.'))
        if(len(df.index)==len(ncolumn)):
            df[column] = tcolumn
            df = df.rename(columns={'Tumorsize':'TUMOR_SIZE'})

    if column == 'OS_status_01':
        os_column = []
        for status in df[column]:
            if np.isnan(status) == True or int(status) != 0 and int(status) != 1:
                os_column.append('')
            elif int(status) == 0:
                os_column.append('0:LIVING')
            elif int(status) == 1:
                os_column.append('1:DECEASED')
            else:
                os_column.append(status)
        if(len(df.index)==len(os_column)):
            df[column] = os_column
            df = df.rename(columns={'OS_status_01':'OS_STATUS'})

    if column == 'DFS_status_01':
        dfs_column = []
        for status in df[column]:
            if np.isnan(status) == True or int(status) != 0 and int(status) != 1:
                dfs_column.append('')
            elif int(status) == 0:
                dfs_column.append('0:DiseaseFree')
            elif int(status) == 1:
                dfs_column.append('1:Recurred/Progressed')
            else:
                dfs_column.append(status)
        
        if(len(df.index)==len(dfs_column)):
            df[column] = dfs_column
            df = df.rename(columns={'DFS_status_01':'DFS_STATUS'})

    if column == 'OS_months' or column == 'DFS_months':
        df = df.rename(columns={column:column.upper()})
    df = df.rename(columns={column:column.upper()})

    list_01 = ["RT", "HT", "CT", "IT"]
    if column in list_01:
        valuelist = df[column].tolist()
        c = 0
        for v_01 in valuelist:
            if np.isnan(v_01) == True or int(v_01) != 0 and int(v_01) != 1:
                print("yes")
                valuelist[c] = ''
            else :
                valuelist[c] = int(v_01)
            c += 1
        df[column] = valuelist


df = df.rename(columns={"RT":"RADIO_THERAPY", "HT":"HORMONE_THERAPY", "IT":"IMMUNO_THERAPY", "CT": "CHEMO_THERAPY"})
df = df.round(decimals=2)
pn = list(df['SAMPLE_ID'])
random.shuffle(pn)
df['SAMPLE_ID'] = pn

print(df)
sample_df= df[["SAMPLE_ID","PATIENT_ID","PATHDATA_FROM","TUMOR_SIZE" ]]
patient_df = df[["PATIENT_ID", "AGE", "SEX", "OS_STATUS", "OS_MONTHS", "DFS_STATUS", "DFS_MONTHS", "RADIO_THERAPY", "HORMONE_THERAPY", "IMMUNO_THERAPY", "CHEMO_THERAPY"]]
print(sample_df)

sdata = io.StringIO()
sample_df.to_csv(sdata, sep='\t', index=False, na_rep= "")

pdata = io.StringIO()
patient_df.to_csv(pdata, sep='\t', index=False, na_rep= "")


data_clinical.write(pdata.getvalue())
data_clinical_sample.write(sdata.getvalue())


data_clinical.close()
meta_study.close()
meta_clinical_patient.close()
meta_clinical_sample.close()
data_clinical_sample.close()
data_type_cancer.close()
meta_type_cancer.close()