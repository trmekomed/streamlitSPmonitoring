import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from data_loader import load_dataset, process_dataset

# Fungsi utama Streamlit
def main():
    st.set_page_config(layout="wide", page_title="Press Monitoring Dashboard")
    st.title("Press Monitoring Dashboard")
    
    # Load data
    sp_df = load_dataset('DATASET SP')
    berita_df = load_dataset('DATASET BERITA')
    
    # Debugging: Tampilkan struktur DataFrame
    st.write("Kolom SP DataFrame:", sp_df.columns)
    st.write("Kolom Berita DataFrame:", berita_df.columns)
    
    # Konversi kolom tanggal dengan fungsi safe
    if 'Publikasi' in sp_df.columns:
        sp_df['Publikasi'] = sp_df['Publikasi'].apply(safe_convert_date)
    
    if 'Tanggal' in berita_df.columns:
        berita_df['Tanggal'] = berita_df['Tanggal'].apply(safe_convert_date)
    
    # Tambahkan pengecekan data
    st.write("Jumlah baris SP:", len(sp_df))
    st.write("Jumlah baris Berita:", len(berita_df))
    
    # Sort data dari terbaru
    sp_df = sp_df.sort_values('Publikasi', ascending=False)
    berita_df = berita_df.sort_values('Tanggal', ascending=False)
    
    # Sidebar untuk filter
    st.sidebar.header("Filter")
    
    # Filter rentang waktu
    start_date = st.sidebar.date_input("Tanggal Mulai", 
                                       min_value=sp_df['Publikasi'].min().date(), 
                                       max_value=sp_df['Publikasi'].max().date(), 
                                       value=sp_df['Publikasi'].min().date())
    end_date = st.sidebar.date_input("Tanggal Akhir", 
                                     min_value=sp_df['Publikasi'].min().date(), 
                                     max_value=sp_df['Publikasi'].max().date(), 
                                     value=sp_df['Publikasi'].max().date())
    
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
