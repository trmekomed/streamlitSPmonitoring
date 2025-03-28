import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

def connect_to_sheets():
    """
    Koneksi ke Google Sheets dengan error handling lebih baik
    """
    try:
        # Ambil kredensial dari Streamlit Secrets
        credentials_dict = st.secrets.get("gcp_service_account")
        
        if not credentials_dict:
            st.error("Kredensial Google Cloud tidak ditemukan!")
            return None, None
        
        # Definisikan scope
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Buat kredensial
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            credentials_dict, scope)
        
        # Authorize
        client = gspread.authorize(credentials)
        
        # ID spreadsheet dari konfigurasi sebelumnya
        spreadsheet_id = "1OrofvXQ5a-H27SR5YtrTkv4szzRRDQ6KUELGAVMWbVg"
        
        return client, spreadsheet_id
    
    except Exception as e:
        st.error(f"Kesalahan koneksi: {e}")
        return None, None

def load_dataset(sheet_name):
    """
    Load dataset dengan error handling komprehensif
    """
    try:
        client, spreadsheet_id = connect_to_sheets()
        
        if not client:
            st.error("Tidak dapat terhubung ke Google Sheets")
            return pd.DataFrame()
        
        try:
            # Buka spreadsheet
            spreadsheet = client.open_by_key(spreadsheet_id)
            
            # Ambil worksheet
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
        
        except gspread.exceptions.WorksheetNotFound:
            st.error(f"Sheet {sheet_name} tidak ditemukan")
            return pd.DataFrame()
        
        except Exception as e:
            st.error(f"Kesalahan membaca sheet {sheet_name}: {e}")
            return pd.DataFrame()
    
    except Exception as e:
        st.error(f"Kesalahan umum: {e}")
        return pd.DataFrame()

def safe_convert_date(date_str):
    """
    Konversi tanggal dengan robust error handling
    """
    try:
        return pd.to_datetime(date_str, errors='coerce')
    except:
        return pd.NaT
