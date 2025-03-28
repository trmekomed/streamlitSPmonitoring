import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

def connect_to_sheets():
    """
    Connect to Google Sheets with improved error handling
    """
    sheet_id = "1OrofvXQ5a-H27SR5YtrTkv4szzRRDQ6KUELGAVMWbVg"
    
    try:
        # Gunakan kredensial dari Streamlit Secrets
        credentials_dict = st.secrets.get("gcp_service_account")
        
        if not credentials_dict:
            st.error("Kredensial Google Cloud tidak ditemukan di Streamlit Secrets")
            return None, sheet_id
        
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            credentials_dict, scope)
        
        client = gspread.authorize(credentials)
        return client, sheet_id
    
    except Exception as e:
        st.error(f"Kesalahan koneksi: {e}")
        return None, sheet_id

def load_dataset(sheet_name):
    """
    Load dataset with robust error handling
    """
    try:
        client, sheet_id = connect_to_sheets()
        
        if client:
            try:
                # Buka spreadsheet dan worksheet
                spreadsheet = client.open_by_key(sheet_id)
                worksheet = spreadsheet.worksheet(sheet_name)
                
                # Ambil semua data
                data = worksheet.get_all_values()
                
                if not data:
                    st.warning(f"Tidak ada data di sheet {sheet_name}")
                    return pd.DataFrame()
                
                # Konversi ke DataFrame
                headers = data[0]
                values = data[1:]
                df = pd.DataFrame(values, columns=headers)
                
                return df
            
            except Exception as e:
                st.error(f"Gagal membaca sheet {sheet_name}: {e}")
                return pd.DataFrame()
        
        else:
            st.error("Tidak dapat terhubung ke Google Sheets")
            return pd.DataFrame()
    
    except Exception as e:
        st.error(f"Error umum: {e}")
        return pd.DataFrame()

def safe_convert_date(date_str):
    """
    Konversi tanggal dengan robust error handling
    """
    try:
        return pd.to_datetime(date_str, errors='coerce')
    except:
        st.warning(f"Tidak dapat mengonversi tanggal: {date_str}")
        return pd.NaT
