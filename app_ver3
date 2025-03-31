import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from datetime import datetime

# Fungsi untuk membersihkan nama narasumber
def clean_narasumber_name(name):
    name = name.strip()
    if ',' in name:
        return name.split(',')[1].strip()
    return name

# Fungsi untuk memfilter berita berdasarkan siaran pers yang dipilih
def get_filtered_berita(berita_df, filtered_sp):
    if berita_df.empty or filtered_sp.empty:
        return pd.DataFrame(columns=berita_df.columns)
    
    berita_df['Tanggal'] = pd.to_datetime(berita_df['Tanggal'], errors='coerce')
    filtered_berita_indices = []

    for _, sp_row in filtered_sp.iterrows():
        sp_date = sp_row['PUBLIKASI']
        sp_title = sp_row['JUDUL']
        if pd.isna(sp_date):
            continue

        relevant_news = berita_df[
            (berita_df['Tanggal'] >= sp_date) &
            (berita_df['Tanggal'] <= sp_date + pd.Timedelta(days=3)) &
            (berita_df['Siaran Pers'] == sp_title)
        ]
        filtered_berita_indices.extend(relevant_news.index.tolist())

    filtered_berita_indices = list(set(filtered_berita_indices))
    return berita_df.loc[filtered_berita_indices] if filtered_berita_indices else pd.DataFrame(columns=berita_df.columns)

# Fungsi utama untuk tab pemberitaan
def pemberitaan_tab(berita_df, sp_df, filtered_sp):
    st.subheader("📰 Analisis Pemberitaan")
    
    if berita_df.empty or sp_df.empty:
        st.warning("Tidak ada data untuk dianalisis.")
        return
    
    try:
        filtered_berita = get_filtered_berita(berita_df, filtered_sp)
        
        # Validasi jika tidak ada data setelah filter
        if filtered_berita.empty:
            st.warning("Tidak ada data berita yang relevan dengan filter.")
            return
        
        st.info(f"Menampilkan {len(filtered_berita)} berita yang relevan dengan Siaran Pers yang dipilih")
        
        # Media Coverage Metrics
        st.subheader("📈 Media Coverage")
        col1, col2 = st.columns(2)
        
        with col1:
            media_counts = filtered_berita['Sumber Media'].value_counts().head(10)
            fig_media = px.bar(
                x=media_counts.values,
                y=media_counts.index,
                orientation='h',
                title="Top 10 Media Sources by Coverage Volume",
                labels={'x': 'Jumlah Artikel', 'y': 'Media'}
            )
            fig_media.update_layout(
                height=400,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig_media, use_container_width=True)
        
        with col2:
            timeline = filtered_berita.groupby(filtered_berita['Tanggal'].dt.date).size().reset_index(name='COUNT')
            fig_timeline = px.line(
                timeline,
                x='Tanggal',
                y='COUNT',
                title="Media Coverage Timeline",
                labels={'Tanggal': 'Tanggal', 'COUNT': 'Jumlah Artikel'}
            )
            fig_timeline.update_layout(height=400)
            st.plotly_chart(fig_timeline, use_container_width=True)

        # Press Release Impact Analysis
        st.subheader("Analisis Dampak Siaran Pers")
        
        merged_data = []
        for _, sp_row in filtered_sp.iterrows():
            sp_date = sp_row['PUBLIKASI']
            sp_title = sp_row['JUDUL']
            
            news_count = len(berita_df[
                (berita_df['Tanggal'] >= sp_date) &
                (berita_df['Tanggal'] <= sp_date + pd.Timedelta(days=3)) &
                (berita_df['Siaran Pers'] == sp_title)
            ])
            
            merged_data.append({
                'Tanggal_SP': sp_date,
                'Judul_SP': sp_title,
                'Jumlah_Berita': news_count
            })
        
        impact_df = pd.DataFrame(merged_data).sort_values('Jumlah_Berita', ascending=False)
        
        col1, col2 = st.columns(2)
        with col1:
            fig_impact = px.bar(
                impact_df.head(10),
                x='Jumlah_Berita',
                y='Judul_SP',
                orientation='h',
                title="Top 10 Siaran Pers berdasarkan Jumlah Pemberitaan",
                labels={'Jumlah_Berita': 'Jumlah Artikel', 'Judul_SP': 'Siaran Pers'}
            )
            fig_impact.update_layout(
                height=500,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig_impact, use_container_width=True)

        with col2:
            fig_time = px.scatter(
                impact_df,
                x='Tanggal_SP',
                y='Jumlah_Berita',
                size='Jumlah_Berita',
                hover_name='Judul_SP',
                title="Dampak Siaran Pers dan Waktu",
                labels={'Tanggal_SP': 'Tanggal Siaran Pers', 'Jumlah_Berita': 'Jumlah Pemberitaan'}
            )
            fig_time.update_layout(height=500)
            st.plotly_chart(fig_time, use_container_width=True)

        # Distribusi Sumber Media
        st.subheader("Distribusi Sumber Media")
        
        media_counts = filtered_berita['Sumber Media'].value_counts()
        top_media = media_counts.head(10)
        others_count = media_counts[10:].sum() if len(media_counts) > 10 else 0
        
        pie_data = pd.concat([top_media, pd.Series({'Others': others_count})]) if others_count > 0 else top_media
        
        fig_pie = px.pie(
            values=pie_data.values,
            names=pie_data.index,
            title="Distribusi Pemberitaan berdasarkan Sumber Media",
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    except Exception as e:
        st.error(f"Error dalam analisis pemberitaan: {e}")

# Fungsi utama aplikasi Streamlit
def main():
    st.set_page_config(layout="wide", page_title="Dashboard Monitoring Enhanced")
    st.title("DASHBOARD MONITORING ENHANCED")
    
    try:
        # Load dataset
        sp_df = load_dataset('DATASET SP')
        berita_df = load_dataset('DATASET BERITA')

        # Konversi tanggal dengan robust handling
        sp_df['PUBLIKASI'] = pd.to_datetime(sp_df['PUBLIKASI'], errors='coerce')
        berita_df['Tanggal'] = pd.to_datetime(berita_df['Tanggal'], errors='coerce')

        # Sidebar untuk filter
        st.sidebar.header("Filter")
        
        start_date = st.sidebar.date_input("Tanggal Mulai", value=datetime.now().date())
        end_date = st.sidebar.date_input("Tanggal Akhir", value=datetime.now().date())
        
        selected_siaran_pers = st.sidebar.multiselect(
            "Pilih Siaran Pers",
            options=sp_df['JUDUL'].unique() if not sp_df.empty else []
        )
        
        # Filter data berdasarkan input pengguna
        filtered_sp = sp_df[
            (sp_df['PUBLIKASI'].dt.date >= start_date) &
            (sp_df['PUBLIKASI'].dt.date <= end_date) &
            (sp_df['JUDUL'].isin(selected_siaran_pers))
        ]
        
        pemberitaan_tab(berita_df, sp_df, filtered_sp)

    except Exception as e:
        st.error(f"Error dalam memuat data: {e}")

if __name__ == "__main__":
    main()
