import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.express as px
from datetime import datetime

# Fungsi untuk koneksi ke Google Spreadsheet
def connect_to_spreadsheet():
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    # Ambil kredensial dari Streamlit secrets
    credentials_dict = {
        "type": st.secrets["gcp_service_account"]["type"],
        "project_id": st.secrets["gcp_service_account"]["project_id"],
        "private_key_id": st.secrets["gcp_service_account"]["private_key_id"],
        "private_key": st.secrets["gcp_service_account"]["private_key"],
        "client_email": st.secrets["gcp_service_account"]["client_email"],
        "client_id": st.secrets["gcp_service_account"]["client_id"],
        "auth_uri": st.secrets["gcp_service_account"]["auth_uri"],
        "token_uri": st.secrets["gcp_service_account"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["gcp_service_account"]["client_x509_cert_url"]
    }
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    client = gspread.authorize(creds)
    
    # Buka spreadsheet berdasarkan ID
    spreadsheet = client.open_by_key('1OrofvXQ5a-H27SR5YtrTkv4szzRRDQ6KUELGAVMWbVg')
    
    # Ambil worksheet
    dataset_sp = spreadsheet.worksheet('DATASET SP')
    dataset_berita = spreadsheet.worksheet('DATASET BERITA')
    
    return dataset_sp, dataset_berita

# Fungsi untuk mengonversi data spreadsheet ke DataFrame
def load_data():
    dataset_sp, dataset_berita = connect_to_spreadsheet()
    
    # Ambil semua data
    sp_data = dataset_sp.get_all_records()
    berita_data = dataset_berita.get_all_records()
    
    # Konversi ke DataFrame
    sp_df = pd.DataFrame(sp_data)
    berita_df = pd.DataFrame(berita_data)
    
    # Konversi kolom tanggal
    sp_df['Publikasi'] = pd.to_datetime(sp_df['Publikasi'], format='%d-%m-%Y')
    berita_df['Tanggal'] = pd.to_datetime(berita_df['Tanggal'], format='%d-%m-%Y')
    
    return sp_df, berita_df

# Fungsi utama Streamlit
def main():
    st.set_page_config(layout="wide", page_title="Press Monitoring Dashboard")
    st.title("Press Monitoring Dashboard")
    
    # Load data
    sp_df, berita_df = load_data()
    
    # Sidebar untuk filter
    st.sidebar.header("Filter")
    
    # Filter rentang waktu
    start_date = st.sidebar.date_input("Tanggal Mulai", min_value=sp_df['Publikasi'].min(), 
                                       max_value=sp_df['Publikasi'].max(), 
                                       value=sp_df['Publikasi'].min())
    end_date = st.sidebar.date_input("Tanggal Akhir", min_value=sp_df['Publikasi'].min(), 
                                     max_value=sp_df['Publikasi'].max(), 
                                     value=sp_df['Publikasi'].max())
    
    # Filter Siaran Pers
    selected_siaran_pers = st.sidebar.multiselect(
        "Pilih Siaran Pers", 
        options=sp_df['Judul'].unique()
    )
    
    # Filtering data
    filtered_sp = sp_df[
        (sp_df['Publikasi'].dt.date >= start_date) & 
        (sp_df['Publikasi'].dt.date <= end_date)
    ]
    
    if selected_siaran_pers:
        filtered_sp = filtered_sp[filtered_sp['Judul'].isin(selected_siaran_pers)]
    
    # Tab
    tab1, tab2 = st.tabs(["Overview", "Detail"])
    
    with tab1:
        # Scorecard
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Siaran Pers", filtered_sp['Judul'].nunique())
        col2.metric("Total Berita", len(berita_df))
        col3.metric("Total Media", berita_df['Sumber Media'].nunique())
        col4.metric("Total Narasumber", filtered_sp['Narasumber'].nunique())
    
    with tab2:
        st.write("Visualisasi detail akan dikembangkan")
    
    # Tampilkan data
    st.subheader("Data Siaran Pers")
    st.dataframe(filtered_sp)

if __name__ == "__main__":
    main()
