import streamlit as st
import json
import pandas as pd

from anonymizer_utils.anonymize_dicom import *
from ui_utils.ui_logic import *

def streamlit_app(): 
    # Inititalize pre-defined values
    ## DICOM tags: used as Unique identifiers (list)
    unique_ids = [
        'PatientName', 
        'PatientID', 
        'AccessionNumber'
    ]

    ## DICOM tags: to be Shown in template for user's reference (list)
    ref_tags = [
        'PatientBirthDate', 
        'PatientSex', 
        'PatientAge', 
        'StudyDate'
    ]
    
    ## DICOM tags: to be Anonymized default values or user's inputs (dict)
    update_tags = {
        'PatientName':      '',                                     # for user's inputs
        'PatientID':        '',                                     # for user's inputs
        'InstitutionName':  '',                                     # for user's inputs
        'PatientBirthDate': '19700101',                             # reset patient's birth date to 0
        'AccessionNumber':  lambda x: x[3:]                         # remove the first 3 characters        
    }

    ## DICOM tag: used as identifier in user-uploaded file (str)
    upload_df_id = 'PatientID'
    
    ## DICOM tags: to be Anonymized as empty string (None-default or list)
    ## >> Example: tags_2_anon = [(0x0010, 0x0010), (0x0010, 0x0020)]
    tags_2_anon = None

    ## DICOM tags: Not anonymized (list)
    tags_2_spare = []


# Initialize session states
    if 'user_folder' not in st.session_state:       # user input directory
        st.session_state['user_folder'] = ''
    if 'folder' not in st.session_state:            # folder path to glob files
        st.session_state['folder'] = ''
    if 'user_fformat' not in st.session_state:      # user input file format
        st.session_state['user_fformat'] = ''
    if 'fformat' not in st.session_state:           # file format to glob
        st.session_state['fformat'] = ''
    if 'dcm_info' not in st.session_state:          # all dcm files
        st.session_state['dcm_info'] = None 
    if 'uids' not in st.session_state:              # list of unique IDs
        st.session_state['uids'] = None
    if 'edit_df' not in st.session_state:           # data editor
        st.session_state['edit_df'] = None

    # Page user interface
    st.set_page_config(page_title = 'DICOM Anonymizer')
    st.write('# DICOM Anonymizer:hospital::card_file_box:')
    
    # A container of user instruction
    with st.expander(':bulb: **Click Here for User Tips on Best Practices**'): 
        st.markdown(
            '''
            ### Folder Preparation
            - :red[Large Folders]: If your folder contains more than 10,000 DICOM files, consider splitting it into smaller batches to optimize processing time.
            - :red[Scan Position]: It is recommended to include only one body part scanned per folder for consistency.
            
            ### Modification of DICOM Tag values
            - :red[Update Input Template]: Update your inputs using the automatically generated template.
            - :red[Avoid Empty Fields]: When uploading the updated template, ensure that there are NO empty inputs in the columns that start with "Update" (e.g. `Update_PatientName`). The values under these columns will be directly applied to the anonymized files. 
            - :red[Default values]: You can modify the following DICOM tags. For your convenience, default values have been pre-set for certain tags to streamline the anonymization process.
            
            | DICOM Tag           | Default value                                                                                    |
            |---------------------|--------------------------------------------------------------------------------------------------|
            | Patient Name        | No default value. We advise using case numbers / random characters.                              |
            | Patient ID          | No default value. We advise using case numbers / random characters.                              |
            | Institution Name    | No default value. We advise using your initial.                                                  |
            | Patient Birth Date  | `1970/01/01` (Format: YYYY/MM/DD)                                                                  |
            | Accession Number    | The first three characters representing the institution is removed. (e.g. `PXH12345` becomes `12345`) |
            
            - The other DICOM tags are anonymized by wiping out the original values.
            
            ### Folder Output
            - The anonymized files will be saved in a new folder named `"[your file path]-Anonymized"`. For example, if you file path is `"C:/Documents/dicom"`, the destination will be `"C:/Documents/dicom-Anonymized"`.

            '''
        )
    
    # Capture user's input of folder directory
    user_folder = st.text_input(
        'Please copy and paste the full directory of the folder with DICOM files.', 
        placeholder='Enter the full file directory, e.g., "C:/Users/Documents"'
    )

    user_fformat = st.text_input(
        'File extension', 
        placeholder='e.g., "dcm"'
    )

    # When 'fetch' button is triggered, save user's inputs and reset last dcm_info in st.session_states
    if st.button('Fetch files', type='primary'): 
        if not user_folder == st.session_state['user_folder']: 
            st.session_state['user_folder'] = user_folder
            st.session_state['folder'] = user_folder.replace('\\', '/')
            st.session_state['dcm_info'] = None

        if not user_fformat == st.session_state['user_fformat']:
            st.session_state['user_fformat'] = user_fformat
            st.session_state['fformat'] = user_fformat.replace('.', '')
            st.session_state['dcm_info'] = None

    # Error handling: When user's inputs are empty, show error msg
    if (st.session_state['folder'] and st.session_state['fformat']) == '': 
        st.error(':warning: Please input file directory and file format.')
        
    # Error handling: to avoid rerun of fetch file function in every refresh
    elif st.session_state['dcm_info'] is not None and user_folder == st.session_state['user_folder']:
        pass
        
    # Feed user inputted folder dir and file format to fetch files
    else: 
        with st.spinner(text='Fetching files...'):
            try: 
                st.session_state['dcm_info'] = create_dcm_df(
                    folder=st.session_state['folder'], 
                    fformat=st.session_state['fformat'], 
                    unique_ids=unique_ids, 
                    ref_tags=ref_tags
                )
                st.session_state['uids'] = st.session_state['dcm_info'][(unique_ids + ref_tags)].drop_duplicates()
            except: 
                st.error(':warning: We cannot find any files in the file format in the directory.')

    # When fetch file function is not triggered, display nothing
    if st.session_state['dcm_info'] is None: 
        pass

    # When files are found, display unique ID df
    else:     
        edit_df = create_update_cols(st.session_state['uids'], update_tags)
        st.session_state['edit_df'] = edit_df
        
        st.success('''
                We have found the following unique cases - :card_file_box:  
                :point_down: You may download the auto-generated template by clicking the "Download" button below.
                ''')
        
        # A placeholder for download function
        download_function = st.empty()
        
        # A placeholder for display data editor
        display_data = st.empty()
        
        # Upload button for user to upload their csv/xls file
        upload_function = st.empty()
        
        # A placeholder for upload error message
        upload_error = st.empty()
        
        # Read user uploaded file
        upload_file = upload_function.file_uploader(
            label='Choose a csv/excel file, which must contain column "PatientID" as identifer.', 
            type=['csv', 'xsl', 'xslx']
        )

        if upload_file is not None: 
            file_extension = Path(upload_file.name).suffix
            readfile_error = False

            try: 
                if file_extension == '.csv':
                    upload_df = pd.read_csv(upload_file)
                elif file_extension in ['.xls', '.xlsx']:
                    upload_df = pd.read_excel(upload_file)
                else: 
                    upload_error.error(':warning: Error in uploaded file: Unsupported file type.')
            except: 
                upload_error.error(':warning: Error: Unable to read uploaded file. Please input your updates in the template and upload again.')
                readfile_error = True

            if readfile_error: 
                pass
            else: 
                # Error checking
                error_message = validate_upload(st.session_state['edit_df'], upload_df, update_tags, upload_df_id)

                if error_message:
                    st.error(error_message)
                
                # Match the uploaded file with data editor
                else:
                    upload_df = upload_df.fillna('').astype(str)
                    try: 
                        edit_df = update_data_editor(st.session_state['edit_df'], upload_df, update_tags)
                    except Exception as e: 
                        upload_error.error(':warning: Error: Unable to read uploaded file. Please input your updates in the template and upload again.')

        # Save latest version of edit_df to session state
        st.session_state['edit_df'] = edit_df
        
        display_data.dataframe(
            st.session_state['edit_df'], 
            use_container_width=True, 
            hide_index=True
        )

        # Download button for csv template (edit_df)
        csv = st.session_state['edit_df'].reset_index(drop=True).to_csv(index=False).encode('utf-8')
        download_function.download_button(
            label='Download template as CSV', 
            data=csv, 
            file_name='unique_ids.csv'
        )
        
        # Capture user's input to write anonymized files 
        if st.button("Anonymize files", type='primary'): 
            anon_dcm_df = st.session_state['dcm_info'].copy().filter(like='dir', axis=1)
            anon_dcm_df = anon_dcm_df.join(st.session_state['edit_df'].filter(like='Update_', axis=1))
            
            with st.spinner(text='Writing files...'): 
                for _, row in anon_dcm_df.iterrows():
                    file_dir = row['file_dir']
                    output_dir = row['output_dir']
                    update = consolidate_tags(row, update_tags)
                    
                    anonymize(
                        file_dir=file_dir, 
                        output_dir=output_dir, 
                        tags=tags_2_anon,
                        update=update,
                        tags_2_spare=tags_2_spare
                    )
        
            st.write(f'''
                    :star2: Anonymized files are written in:  
                    :open_file_folder: :blue[{st.session_state['folder']}-Anonymized]
                    ''')