import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from data_loader import load_dataset

def main():
    st.set_page_config(layout="wide", page_title="Press Monitoring Dashboard")
    st.title("Press Monitoring Dashboard")

    # Load data
    try:
        sp_df = load_dataset('DATASET SP')
        berita_df = load_dataset('DATASET BERITA')

        # Debug: Tampilkan struktur awal
        st.write("Kolom SP DataFrame:", sp_df.columns)
        st.write("Kolom Berita DataFrame:", berita_df.columns)

        # Konversi tanggal dengan robust
        sp_df['PUBLIKASI'] = pd.to_datetime(sp_df['PUBLIKASI'], errors='coerce')
        berita_df['Tanggal'] = pd.to_datetime(berita_df['Tanggal'], errors='coerce')

        # Sort data dari terbaru
        sp_df = sp_df.sort_values('PUBLIKASI', ascending=False)
        berita_df = berita_df.sort_values('Tanggal', ascending=False)

        # Sidebar untuk filter
        st.sidebar.header("Filter")

        # Filter rentang waktu
        start_date = st.sidebar.date_input(
            "Tanggal Mulai",
            min_value=sp_df['PUBLIKASI'].min().date() if not sp_df.empty else datetime.now().date(),
            max_value=sp_df['PUBLIKASI'].max().date() if not sp_df.empty else datetime.now().date(),
            value=sp_df['PUBLIKASI'].min().date() if not sp_df.empty else datetime.now().date()
        )

        end_date = st.sidebar.date_input(
            "Tanggal Akhir",
            min_value=sp_df['PUBLIKASI'].min().date() if not sp_df.empty else datetime.now().date(),
            max_value=sp_df['PUBLIKASI'].max().date() if not sp_df.empty else datetime.now().date(),
            value=sp_df['PUBLIKASI'].max().date() if not sp_df.empty else datetime.now().date()
        )

        # Filter Siaran Pers berdasarkan rentang waktu
        filtered_sp = sp_df[
            (sp_df['PUBLIKASI'].dt.date >= start_date) &
            (sp_df['PUBLIKASI'].dt.date <= end_date)
        ]

        # Filter Siaran Pers berdasarkan pilihan judul
        selected_siaran_pers = st.sidebar.multiselect(
            "Pilih Siaran Pers",
            options=filtered_sp['Judul'].unique() if not filtered_sp.empty else []
        )

        if selected_siaran_pers:
            filtered_sp = filtered_sp[filtered_sp['Judul'].isin(selected_siaran_pers)]

        # Tab
        tab1, tab2 = st.tabs(["Overview", "Detail"])

        with tab1:
            # Scorecard
            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Total Siaran Pers", filtered_sp['Judul'].nunique() if not filtered_sp.empty else 0)
            col2.metric("Total Berita", len(berita_df) if not berita_df.empty else 0)
            col3.metric("Total Media", berita_df['Sumber Media'].nunique() if 'Sumber Media' in berita_df.columns and not berita_df.empty else 0)
            col4.metric("Total Narasumber", filtered_sp['Narasumber'].nunique() if 'Narasumber' in filtered_sp.columns and not filtered_sp.empty else 0)

        with tab2:
            st.subheader("Visualisasi Detail")
            
            if not filtered_sp.empty:
                # Contoh visualisasi scatter plot narasumber vs publikasi
                fig = px.scatter(filtered_sp, x='PUBLIKASI', y='Narasumber', title="Scatter Plot Narasumber")
                st.plotly_chart(fig)
                
                # Tampilkan data detail
                st.subheader("Data Siaran Pers")
                st.dataframe(filtered_sp)
            else:
                st.warning("Tidak ada data untuk ditampilkan di tab Detail.")

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    main()
