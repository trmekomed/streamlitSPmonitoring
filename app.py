import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from datetime import datetime
from data_loader import load_dataset

def clean_narasumber_name(name):
    """
    Clean narasumber name:
    - If no comma, return full name
    - If comma exists, return part after comma
    """
    name = name.strip()
    if ',' in name:
        return name.split(',')[1].strip()
    return name

def main():
    st.set_page_config(layout="wide", page_title="v1.1 Dashboard Monitoring")
    st.title("DASHBOARD MONITORING 𓀛")
    st.write("Dashboard ini dalam pengembangan, saat ini data yang disajikan adalah Siaran Pers yang didiseminasi oleh Komdigi dan Monitoring pemuatan beritanya")

    # Load data
    try:
        sp_df = load_dataset('DATASET SP')
        berita_df = load_dataset('DATASET BERITA')

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
            options=filtered_sp['JUDUL'].unique() if not filtered_sp.empty else []
        )
        if selected_siaran_pers:
            filtered_sp = filtered_sp[filtered_sp['JUDUL'].isin(selected_siaran_pers)]

        st.subheader("💡 Overview")
        # Overview - Scorecard
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Siaran Pers", filtered_sp['JUDUL'].nunique() if not filtered_sp.empty else 0)
        col2.metric("Berita", len(berita_df) if not berita_df.empty else 0)
        col3.metric("Media", berita_df['Sumber Media'].nunique() if 'Sumber Media' in berita_df.columns and not berita_df.empty else 0)
        
        # Add null check and debug information for NARASUMBER
        if 'NARASUMBER' in filtered_sp.columns:
            col4.metric("Narasumber", filtered_sp['NARASUMBER'].nunique() if not filtered_sp['NARASUMBER'].isnull().all() else 0)
        else:
            st.warning("NARASUMBER column not found in the dataset")

        # Create tabs after the overview section
        tab1, tab2 = st.tabs(["Siaran Pers", "Pemberitaan"])
        
        # Tab 1: Siaran Pers (all current visualizations)
        with tab1:
            # Visualisasi Detail
            st.subheader("🔎 Sebaran")

            if not filtered_sp.empty:
                # Check if NARASUMBER column exists
                if 'NARASUMBER' not in filtered_sp.columns:
                    st.warning("NARASUMBER column is missing from the dataset")
                    return

                try:
                    # Handle potential None or NaN values
                    filtered_sp['NARASUMBER'] = filtered_sp['NARASUMBER'].fillna('')
                    
                    # Split and explode the NARASUMBER column
                    narasumber_df = filtered_sp.copy()
                    narasumber_df['NARASUMBER'] = narasumber_df['NARASUMBER'].str.split(';')
                    narasumber_exploded = narasumber_df.explode('NARASUMBER')
                    
                    # Clean and count narasumbers
                    narasumber_exploded['NARASUMBER'] = narasumber_exploded['NARASUMBER'].str.strip()
                    narasumber_exploded['CLEAN_NARASUMBER'] = narasumber_exploded['NARASUMBER'].apply(clean_narasumber_name)
                    
                    # Calculate total count for each narasumber
                    narasumber_total_counts = narasumber_exploded[narasumber_exploded['CLEAN_NARASUMBER'] != '']['CLEAN_NARASUMBER'].value_counts()

                    # Pastikan PUBLIKASI adalah tipe datetime
                    if not pd.api.types.is_datetime64_any_dtype(narasumber_exploded['PUBLIKASI']):
                        narasumber_exploded['PUBLIKASI'] = pd.to_datetime(narasumber_exploded['PUBLIKASI'])

                    # Tambahkan kolom Week untuk mengelompokkan berdasarkan minggu
                    narasumber_exploded['Week'] = narasumber_exploded['PUBLIKASI'].dt.to_period('W')
                    narasumber_exploded['Week_start'] = narasumber_exploded['Week'].dt.start_time
                    narasumber_exploded['Week_end'] = narasumber_exploded['Week'].dt.end_time

                    # Hitung kemunculan per narasumber per minggu
                    narasumber_counts = narasumber_exploded[narasumber_exploded['CLEAN_NARASUMBER'] != ''].groupby(['CLEAN_NARASUMBER', 'Week', 'Week_start', 'Week_end']).size().reset_index(name='COUNT')

                    # Buat label kustom untuk hover
                    narasumber_counts['custom_label'] = (
                        narasumber_counts['CLEAN_NARASUMBER'] + '<br>' + 
                        'Rentang=' + narasumber_counts['Week_start'].dt.strftime('%d-%m-%Y') + ' - ' + 
                        narasumber_counts['Week_end'].dt.strftime('%d-%m-%Y') + '<br>' +
                        'Frekuensi=' + narasumber_counts['COUNT'].astype(str) + ' kali'
                    )

                    # Top 10 Narasumber Bar Chart
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Horizontal Bar Chart for Top 10 Narasumbers, sorted in descending order
                        sorted_narasumber_counts = narasumber_total_counts.sort_values(ascending=False).head(10)
        
                        fig_bar = px.bar(
                            x=sorted_narasumber_counts.values, 
                            y=sorted_narasumber_counts.index,
                            orientation='h',
                            title="Top 10 Narasumber",
                            labels={'x': 'Frekuensi', 'y': 'Narasumber'}
                        )
                        fig_bar.update_layout(
                            xaxis_title="Frekuensi",
                            yaxis_title="Narasumber",
                            height=400
                        )
                        st.plotly_chart(fig_bar, use_container_width=True)
                    
                    with col2:
                        # Timeline Series of Press Releases
                        sp_timeline = filtered_sp.groupby(filtered_sp['PUBLIKASI'].dt.date).size().reset_index(name='COUNT')
                        fig_timeline = px.line(
                            sp_timeline, 
                            x='PUBLIKASI', 
                            y='COUNT',
                            title="Timeline Siaran Pers",
                            labels={'PUBLIKASI': 'Tanggal', 'COUNT': 'Jumlah Siaran Pers'}
                        )
                        fig_timeline.update_layout(
                            xaxis_title="Tanggal",
                            yaxis_title="Jumlah Siaran Pers",
                            height=400
                        )
                        st.plotly_chart(fig_timeline, use_container_width=True)

                    # Narasumber Scatter Plot
                    fig_scatter = px.scatter(
                        narasumber_counts, 
                        x='Week_start',  # Gunakan tanggal awal minggu sebagai sumbu X
                        y='CLEAN_NARASUMBER',
                        size='COUNT',
                        color='CLEAN_NARASUMBER',
                        title="Narasumber Appearances Weekly",
                        labels={'Week_start': 'Week', 'CLEAN_NARASUMBER': 'Narasumber', 'COUNT': 'Frequency'},
                        hover_name='custom_label',  # Gunakan label kustom untuk hover
                        custom_data=['COUNT', 'Week_start', 'Week_end']  # Data tambahan untuk hover
                    )

                    # Atur format hover
                    fig_scatter.update_traces(
                        hovertemplate='%{hovertext}<extra></extra>'
                    )

                    fig_scatter.update_layout(
                        showlegend=False,
                        autosize=True,
                        height=600,
                        width=None,
                        xaxis_title='Minggu',
                        yaxis_title='Narasumber'
                    )

                    # Urutkan berdasarkan total kemunculan
                    narasumber_total_counts = narasumber_counts.groupby('CLEAN_NARASUMBER')['COUNT'].sum().sort_values(ascending=False)
                    
                    fig_scatter.update_yaxes(
                        categoryorder='array', 
                        categoryarray=narasumber_total_counts.index.tolist()[::-1]
                    )

                    # Format sumbu X untuk menampilkan tanggal dengan lebih baik
                    fig_scatter.update_xaxes(
                        tickformat='%d-%m-%Y',
                        tickmode='auto',
                        nticks=10
                    )

                    st.plotly_chart(fig_scatter, use_container_width=True)
                    
                    # Tampilkan data detail
                    st.subheader("Data Siaran Pers")
                    st.dataframe(filtered_sp)
                
                except Exception as name_error:
                    st.error(f"Error processing NARASUMBER: {name_error}")
            else:
                st.warning("Tidak ada data untuk ditampilkan.")
        
        # Tab 2: Pemberitaan (empty for now)
        with tab2:
            st.info("Konten untuk tab Pemberitaan akan segera hadir.")
    
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    main()
