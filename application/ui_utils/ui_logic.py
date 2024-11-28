import pandas as pd
from datetime import datetime

def create_update_cols(udf: pd.DataFrame, update_tags: dict) -> pd.DataFrame: 
    """
    Create new columns in udf for updating values of the defined DICOM tags. 
    
    Args:
    - udf (pd.DataFrame): DataFrame of uniquely identified cases.
    - update_tags (dict): Keys represent the DICOM tags to be updated, values represent the rules of creating default values. 
    
    Returns: 
    - The modified udf with columns in default values.
    """
    for tag, rule in update_tags.items():
        if callable(rule): 
            udf[f'Update({tag})'] = udf[tag].apply(rule)
        else: 
            udf[f'Update_{tag}'] = rule
    return udf
            

def update_data_editor(edit_df: pd.DataFrame, upload_df: pd.DataFrame, update_tags: dict):
    """
    Updates the specified columns in an existing DataFrame (edit_df) with values from an uploaded DataFrame (upload_df). 

    Args:
    - edit_df (pd.DataFrame): DataFrame containing the original data to be updated.
    - upload_df (pd.DataFrame): DataFrame with new values to apply to matching rows.
    - update_tags (dict): Column tags to update in the edit_df.

    Returns:
    - The modified edit_df with updated values where matches were found.
    """
    for _, row_udf in upload_df.iterrows():
    # Check if the current row_udf matches the edit_df
        matching_row = edit_df[(edit_df['PatientID'] == row_udf['PatientID'])]
    
        # Update only if row_udf matches
        if not matching_row.empty:
            idx = matching_row.index[0]  # Get the index of the matching row_udf
            
            for tag, _ in update_tags.items(): 
                col = f'Update_{tag}'   
                edit_df.at[idx, col] = row_udf[col]
        
    return edit_df

def check_unmatched_patient_ids(upload_df, edit_df):
    """
    Checks for PatientIDs in the edit_df that are not present in the upload_df.

    Args:
    - upload_df (pd.DataFrame): The DataFrame uploaded by the user.
    - edit_df (pd.DataFrame): The DataFrame from session state containing existing PatientIDs.

    Returns:
    - list: A list of unmatched PatientIDs.
    """
    unmatched_patient_ids = edit_df[~edit_df['PatientID'].isin(upload_df['PatientID']) & 
                                      ~edit_df['PatientID'].isin(upload_df['Update_PatientID'])]
    return unmatched_patient_ids['PatientID'].unique().tolist()