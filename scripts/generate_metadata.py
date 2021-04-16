import pandas as pd
import numpy as np
import io
import random

#Read excel file
df = pd.read_excel(r'data/input/Master_TMA_analyses.xlsx', sheet_name='The Mamma Database 2000-2013 FI')
df = pd.read_excel(r'data/input/Master_TMA_analyses.xlsx', sheet_name='')
#Create annotation sheet
variables = df.columns
df_annotation = pd.DataFrame(columns = ['Variables', 'Variable name cBioportal', 'Variable description', 'Data type', 'Priority', 'Sample/patient'])
df_meta = pd.DataFrame(columns = ['Variable', 'Description'])
df_meta['Variable'] = ['type of cancer:','cancer study identifier:', 'name:', 'short name:', 'description:','add global case list:', 'group:']
df_meta['Description'] = ['','','','','', 'true', 'PUBLIC']
df_meta_p = pd.DataFrame(columns = ['Variable', 'Description'])
df_meta_s = pd.DataFrame(columns = ['Variable', 'Description'])
df_annotation['Variables'] = variables

try:
    f = open("data/input/Annotation_file.xlsx")
    # Do something with the file
except IOError:
    print("Annotation file doesn't exist yet, creating...")
    with pd.ExcelWriter('data/input/Annotation_file.xlsx', mode= 'w') as writer:
        df_annotation.to_excel(writer, sheet_name='Annotation', index=False)
        df_meta.to_excel(writer, sheet_name='Meta study', index=False)
    exit()
    
print("Annotation file found, checking contents...")
df_annotated_variables = pd.read_excel (r'data/input/Annotation_file.xlsx', 'Annotation')
df_annotated_variables['Variables'] = list(map(str.upper, list(df_annotated_variables['Variables'])))
df_meta_info = pd.read_excel (r'data/input/Annotation_file.xlsx', 'Meta study')
amount_of_variables = len(df_annotated_variables["Variables"])

if df_annotated_variables.isnull().values.any() == False and df_meta_info.isnull().values.any() == False:
    print("Variable annotation found and complete, continuing...")
    print(df_annotated_variables)
else:
    print("Variable annotation incomplete, please completely annotate the variables")
    exit()

tumor_size = df['Tumorsize']
l = []
for x in tumor_size:
    l.append(str(x).replace(',','.'))
df['Tumorsize'] = l
#df = df[pd.to_numeric(df.Tumorsize, errors='coerce').notnull()]

# Open metadata and data files
meta_study= open("/home/onco/mdekorte/Documents/Cbioportal_clean/cbioportal/test_study/MMC_test/meta_study.txt", "w+")
meta_clinical_patient= open("/home/onco/mdekorte/Documents/Cbioportal_clean/cbioportal/test_study/MMC_test/meta_clinical_patient.txt", "w+")
data_clinical = open("/home/onco/mdekorte/Documents/Cbioportal_clean/cbioportal/test_study/MMC_test/data_clinical_patient.txt", "w+")
meta_clinical_sample= open("/home/onco/mdekorte/Documents/Cbioportal_clean/cbioportal/test_study/MMC_test/meta_clinical_sample.txt", "w+")
data_clinical_sample= open("/home/onco/mdekorte/Documents/Cbioportal_clean/cbioportal/test_study/MMC_test/data_clinical_sample.txt", "w+")
data_type_cancer = open("/home/onco/mdekorte/Documents/Cbioportal_clean/cbioportal/test_study/MMC_test/cancer_type.txt", "w+")
meta_type_cancer = open("/home/onco/mdekorte/Documents/Cbioportal_clean/cbioportal/test_study/MMC_test/meta_cancer_type.txt", "w+")

#Write study meta
meta_study_list = df_meta_info['Description']
meta_study.write(
"""type_of_cancer: %s
cancer_study_identifier: %s
name: %s
short_name: %s
description: %s
add_global_case_list: %s
groups: %s""" % (meta_study_list[0], meta_study_list[1], meta_study_list[2], meta_study_list[3], meta_study_list[4], meta_study_list[5], meta_study_list[6]))



meta_clinical_patient.write(
    """cancer_study_identifier: %s
genetic_alteration_type: CLINICAL
datatype: PATIENT_ATTRIBUTES
data_filename: data_clinical_patient.txt""" % (meta_study_list[1])
)

meta_clinical_sample.write(
"""cancer_study_identifier: %s
genetic_alteration_type: CLINICAL
datatype: SAMPLE_ATTRIBUTES
data_filename: data_clinical_sample.txt""" % (meta_study_list[1])
)

data_type_cancer.write("idc_test\tInvasive Ductal Carcinoma test\tbreast,breast invasive\tHotPink\tBreast\n")
meta_type_cancer.write(
"""genetic_alteration_type: CANCER_TYPE
datatype: CANCER_TYPE
data_filename: cancer_type.txt""")



sample_id_names = []
for index in range(len(df_annotated_variables['Variables'])):
    value = df_annotated_variables['Variables'][index]
    if '*' in value:
        patient_id_name = value.replace('*', '')
        df_annotated_variables['Variables'][index] = patient_id_name
        value = patient_id_name
    if '#' in value:
        sample_id_name = value.replace('#', '')
        sample_id_names.append(sample_id_name)
        df_annotated_variables['Variables'][index] = sample_id_name

patient_id_name = patient_id_name.replace('#', '')
df.columns = [cname.upper() for cname in df.columns]
df= df[list(df_annotated_variables['Variables'])]

sample_id_list = []
sample_id_generated = False
for column in df:
    # filter on patient number and randomise the patient numbers
    if column in sample_id_names and sample_id_generated == False:
        if len(sample_id_names) > 1:
            for i in range(len(df[column])):
                sample_id = str(list(df[sample_id_names[0]])[i]) + "-" + str(list(df[sample_id_names[1]])[i]).replace(' ', '_').replace(',','').replace('(', '').replace(')','')
                sample_id_list.append(sample_id)

        if len(sample_id_list) == len(df.index):
            sample_id_generated = True

    # rename column
    if column == patient_id_name:
        df = df.rename(columns={patient_id_name:'PATIENT_ID'})
    
    # transform values to male/female
    if column == "SEX_M1_F2":
        ncolumn=[]
        for sex in df[column]:
            if int(sex) ==1:
                ncolumn.append("Male")
            if int(sex) ==2:
                ncolumn.append("Female")
            if(len(df.index)==len(ncolumn)):
                df[column] = ncolumn
                df = df.rename(columns={'SEX_M1_F2':'SEX'})

    # rename column
    if column == 'AGE':
        df = df.rename(columns={column:'AGE'})
    


    if column == 'OS_STATUS_01':
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
            df = df.rename(columns={'OS_STATUS_01':'OS_STATUS'})

    if column == 'DFS_STATUS_01':
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
            df = df.rename(columns={'DFS_STATUS_01':'DFS_STATUS'})

    list_01 = ["RT", "HT", "CT", "IT", "ER", "PR", "HER2stat_01", "SynchrBreastTumors_01", "SynchrTumorType_01", "SynchrBilateral_01", "AsynchrBreastTumors_01", "AsynchrBilateral_01", "AsynchrInSitu_01"]
    if column in list_01:
        valuelist = df[column].tolist()
        c = 0
        for v_01 in valuelist:
            if np.isnan(v_01) == True or int(v_01) != 0 and int(v_01) != 1:
                valuelist[c] = ''
            elif int(v_01)==0:
                valuelist[c] = str(int(v_01)).replace('0', 'No')
            elif int(v_01)==1:
                valuelist[c] = str(int(v_01)).replace('1', 'Yes')
            c += 1
        df[column] = valuelist


df = df.round(decimals=2)
replacements = {'SEX_M1_F2':'SEX', 'OS_STATUS_01': 'OS_STATUS', 'DFS_STATUS_01': 'DFS_STATUS'}
df_annotated_variables['Variables'] = [replacements.get(n, n) for n in df_annotated_variables['Variables']]

patient_vlist = []
sample_vlist = []
sample_vlist.append("PATIENT_ID")
counter = 0
for spv in df_annotated_variables['Sample/patient']:
    if spv == 'patient':
        patient_vlist.append(df.columns.values[counter])
    if spv == 'sample':
        sample_vlist.append(df.columns.values[counter])
    counter += 1


df_annotated_samples = df_annotated_variables.loc[df_annotated_variables['Variables'].isin(sample_vlist)]
df_annotated_samples = df_annotated_samples.drop(['Variables', "Sample/patient"], axis = 1)
df_annotated_patients = df_annotated_variables.loc[df_annotated_variables['Variables'].isin(patient_vlist)]
df_annotated_patients = df_annotated_patients.drop(['Variables', "Sample/patient"], axis = 1)

new_sample_row = []

new_sample_row.insert(0,{'Variable name cBioportal':'Sample identifier', 'Variable description': 'Sample identifier', 'Data type': 'STRING', 'Priority': 1})
new_sample_row.insert(1, {'Variable name cBioportal':'Patient identifier', 'Variable description': 'Patient identifier', 'Data type': 'STRING', 'Priority': 1})
df_annotated_samples = pd.concat([pd.DataFrame(new_sample_row), df_annotated_samples], ignore_index=True)
new_patient_row = []
new_patient_row.insert(0, {'Variable name cBioportal':'Patient identifier', 'Variable description': 'Patient identifier', 'Data type': 'STRING', 'Priority': 1})
df_annotated_patients =  pd.concat([pd.DataFrame(new_patient_row), df_annotated_patients], ignore_index=True)

clinical_data_string = ''
sample_data_string = ''
amount_of_variables_samples = len(df_annotated_samples.index)
amount_of_variables_patients = len(df_annotated_patients.index)

for column in df_annotated_samples.columns.values:
    sample_data_string += '#'
    c = 0
    for variable in df_annotated_samples[column]:
        c+=1
        if amount_of_variables_samples != c:
            sample_data_string += str(variable) + '\t'
        else:
            sample_data_string += str(variable) + '\n'


for column in df_annotated_patients.columns.values:
    clinical_data_string += '#'
    c = 0
    for variable in df_annotated_patients[column]:
        c+=1
        if amount_of_variables_patients != c:
            clinical_data_string += str(variable) + '\t'
        else:
            clinical_data_string += str(variable) + '\n'


data_clinical_sample.write(sample_data_string)
data_clinical.write(clinical_data_string)


sample_df = df[df.columns[df.columns.isin(sample_vlist)]]
sample_df.insert(loc = 0, column = 'SAMPLE_ID', value = sample_id_list)
patient_df = df[df.columns[df.columns.isin(patient_vlist)]]

patient_df = patient_df.drop_duplicates(subset=['PATIENT_ID'])

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