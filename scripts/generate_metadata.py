import sys, getopt
import pandas as pd
import numpy as np
import io
import random



#define functions
def write_annotation(df, variables_amount):
    data_string = ''
    for column in df.columns.values:
        data_string += '#'
        c = 0
        for variable in df[column]:
            c+=1
            if variables_amount != c:
                data_string += str(variable) + '\t'
            else:
                data_string += str(variable) + '\n'
    return data_string

def write_data(df, df_annotation, variable_list, file, ispatient):
    df_annotated_split = df_annotation.loc[df_annotation['Variables'].isin(variable_list)]
    df_annotated_split = df_annotated_split.drop(['Variables', "Sample/patient", "Yes/No"], axis = 1)

    if ispatient:
        new_row = []
        new_row.insert(0, {'Variable name cBioportal':'Patient identifier', 'Variable description': 'Patient identifier', 'Data type': 'STRING', 'Priority': 1})
    else:
        new_row = []
        new_row.insert(0,{'Variable name cBioportal':'Sample identifier', 'Variable description': 'Sample identifier', 'Data type': 'STRING', 'Priority': 1})
        new_row.insert(1, {'Variable name cBioportal':'Patient identifier', 'Variable description': 'Patient identifier', 'Data type': 'STRING', 'Priority': 1})
        
    df_annotated_split = pd.concat([pd.DataFrame(new_row), df_annotated_split], ignore_index=True)


    amount_of_variables = len(df_annotated_split.index)
    clinical_string = write_annotation(df_annotated_split, amount_of_variables)
    file.write(clinical_string)

    split_df = df[df.columns[df.columns.isin(variable_list)]]

    if ispatient:
        split_df = split_df.drop_duplicates(subset=['PATIENT_ID'])
    else:
        print(sample_id_list)
        print(split_df)
        split_df.insert(loc = 0, column = 'SAMPLE_ID', value = sample_id_list)

    data_string = io.StringIO()
    split_df.to_csv(data_string, sep='\t', index=False, na_rep= "")
    
    file.write(data_string.getvalue())

def reformat_logical(df, column, c_values, r_values):
    valuelist = df[column].tolist()
    c = 0
    for v_01 in valuelist:
        try:
            if pd.isnull(v_01) == True or int(v_01) != int(c_values[0]) and int(v_01) != int(c_values[1]):
                valuelist[c] = ''
            elif int(v_01) == int(c_values[0]):
                valuelist[c] = str(int(v_01)).replace(c_values[0], r_values[0])
            elif int(v_01) == int(c_values[1]):
                valuelist[c] = str(int(v_01)).replace(c_values[1], r_values[1])
        except ValueError:
            valuelist[c] = ''
        c += 1
    print(len(valuelist))
    df[column] = valuelist
    return df

#get command line arguments
arguments = sys.argv
#arguments = ['XD', '-i', 'overview 263-4-01 - final.xlsx', '-s', 'Sheet3']
try:
    if arguments[1] == '-i':
        inputfile = arguments[2]
    if arguments[3] == '-s':
        sheetname = arguments[4]
except IndexError:
    print('There seems to be something wrong with your input arguments, format:')
    print("""generate_metadata.py -i '<inputfile>' -s '<sheetname>'""")
    exit()

input_path = 'data/input/' + inputfile

#Read excel file
try:
    df = pd.read_excel(input_path, sheet_name=sheetname)
except (FileNotFoundError, FileExistsError) as e:
    print('Something went wrong reading the input files.')
    print('Please make sure the file and sheet name are correct and the file is placed inside the input folder.')
    exit()

#Create annotation sheet
variables = df.columns
df_annotation = pd.DataFrame(columns = ['Variables', 'Variable name cBioportal', 'Variable description', 'Data type', 'Priority', 'Sample/patient', 'Yes/No'])
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

# Write patient meta file
meta_clinical_patient.write(
    """cancer_study_identifier: %s
genetic_alteration_type: CLINICAL
datatype: PATIENT_ATTRIBUTES
data_filename: data_clinical_patient.txt""" % (meta_study_list[1])
)

#Write sample meta file
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
list_01 = []
for index in range(len(df_annotated_variables['Variables'])):
    value_v = df_annotated_variables['Variables'][index]
    value_yn = df_annotated_variables['Yes/No'][index]
    
    if '*' in value_v:
        patient_id_name = value_v.replace('*', '')
        df_annotated_variables['Variables'][index] = patient_id_name
        value_v = patient_id_name
    if '#' in value_v:
        sample_id_name = value_v.replace('#', '')
        sample_id_names.append(sample_id_name)
        df_annotated_variables['Variables'][index] = sample_id_name
    if value_yn == True:
        list_01.append(value_v)

patient_id_name = patient_id_name.replace('#', '')
df.columns = [cname.upper() for cname in df.columns]
print(df.columns.values)
print(df_annotated_variables['Variables'])
df.columns = list(df_annotated_variables['Variables'])

sample_id_list = []
sample_id_generated = False

for column in df:
    # filter on patient number and randomise the patient numbers
    if column in sample_id_names and sample_id_generated == False:
        if len(sample_id_names) > 1:
            for i in range(len(df[column])):
                sample_id = str(list(df[sample_id_names[0]])[i]) + "-" + str(list(df[sample_id_names[1]])[i]).replace(' ', '_').replace(',','').replace('(', '').replace(')','')
                sample_id_list.append(sample_id)
        elif len(sample_id_names) == 1:
            sample_id_list = [sample_name.replace(' ', '_').replace(',','').replace('(', '').replace(')','') for sample_name in df[column].tolist()]
        if len(sample_id_list) == len(df.index):
            sample_id_generated = True

    # rename column
    if column == patient_id_name:
        df = df.rename(columns={patient_id_name:'PATIENT_ID'})
    
    # transform values to male/female
    if column == "SEX":
        df = reformat_logical(df, column, c_values = ['1', '2'], r_values = ['Male', 'Female'])

    if column == 'OS_STATUS':
        df = reformat_logical(df, column, c_values = ['0', '1'], r_values = ['0:LIVING', '1:DECEASED'])

    if column == 'DFS_STATUS':
        df = reformat_logical(df, column, c_values = ['0', '1'], r_values = ['0:DiseaseFree', '1:Recurred/Progressed'])

    if column in list_01:
        df = reformat_logical(df, column, c_values = ['0', '1'], r_values = ['No', 'Yes'])

df = df.round(decimals=2)

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

#write data to file
write_data(df, df_annotated_variables, patient_vlist, data_clinical, ispatient=True)
write_data(df, df_annotated_variables, sample_vlist, data_clinical_sample, ispatient=False)

f.close()
data_clinical.close()
meta_study.close()
meta_clinical_patient.close()
meta_clinical_sample.close()
data_clinical_sample.close()
data_type_cancer.close()
meta_type_cancer.close()

