import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from datetime import datetime
from data_loader import load_dataset

def clean_narasumber_name(name):
    name = name.strip()
    if ',' in name:
        return name.split(',')[1].strip()
    return name

def get_filtered_berita(berita_df, filtered_sp):
    berita_df['Tanggal'] = pd.to_datetime(berita_df['Tanggal'], errors='coerce')
    if filtered_sp.empty:
        return pd.DataFrame(columns=berita_df.columns)
    
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

def pemberitaan_tab(berita_df, sp_df, filtered_sp):
    st.subheader("📰 Analisis Pemberitaan")
    
    if not berita_df.empty and not sp_df.empty:
        try:
            filtered_berita = get_filtered_berita(berita_df, filtered_sp)
            st.info(f"Menampilkan {len(filtered_berita)} berita yang relevan dengan Siaran Pers yang dipilih")
            
            st.subheader("📈 Media Coverage")
            if not filtered_berita.empty:
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
                    fig_media.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
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
            
            st.subheader("Analisis Dampak Siaran Pers")
            merged_data = []
            for _, sp_row in filtered_sp.iterrows():
                sp_date = sp_row['PUBLIKASI']
                if pd.isna(sp_date):
                    continue
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
            
            impact_df = pd.DataFrame(merged_data)
            if not impact_df.empty:
                impact_df = impact_df.sort_values('Jumlah_Berita', ascending=False)
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
                    fig_impact.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
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
            
            if not filtered_berita.empty:
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
            
            st.subheader("Hubungan Siaran Pers dan Media")
            if not filtered_berita.empty and 'Siaran Pers' in filtered_berita.columns:
                sankey_df = filtered_berita[['Siaran Pers', 'Sumber Media']].copy()
                top_sp = sankey_df['Siaran Pers'].value_counts().head(5).index.tolist()
                top_media = sankey_df['Sumber Media'].value_counts().head(8).index.tolist()
                sankey_df = sankey_df[
                    (sankey_df['Siaran Pers'].isin(top_sp)) &
                    (sankey_df['Sumber Media'].isin(top_media))
                ]
                if not sankey_df.empty:
                    flow_counts = sankey_df.groupby(['Siaran Pers', 'Sumber Media']).size().reset_index(name='Count')
                    all_nodes = list(set(flow_counts['Siaran Pers'].tolist() + flow_counts['Sumber Media'].tolist()))
                    source_indices = [all_nodes.index(sp) for sp in flow_counts['Siaran Pers']]
                    target_indices = [all_nodes.index(media) for media in flow_counts['Sumber Media']]
                    fig_sankey = go.Figure(data=[go.Sankey(
                        node=dict(
                            pad=15,
                            thickness=20,
                            line=dict(color="black", width=0.5),
                            label=all_nodes
                        ),
                        link=dict(
                            source=source_indices,
                            target=target_indices,
                            value=flow_counts['Count'].tolist()
                        )
                    )])
                    fig_sankey.update_layout(title_text="Alur Siaran Pers ke Media", height=600)
                    st.plotly_chart(fig_sankey, use_container_width=True)
                else:
                    st.warning("Tidak cukup data untuk membuat diagram Sankey.")
            
            st.subheader("Detail Pemberitaan")
            selected_columns = ['Judul Berita', 'Tanggal', 'Sumber Media', 'Siaran Pers', 'Link Berita']
            if not filtered_berita.empty:
                st.dataframe(filtered_berita[selected_columns])
            else:
                st.warning("Tidak ada data berita untuk ditampilkan.")
        
        except Exception as e:
            st.error(f"Error in pemberitaan analysis: {e}")
    else:
        st.warning("Tidak ada data berita untuk ditampilkan.")

def main():
    st.set_page_config(layout="wide", page_title="v1.2 Dashboard Monitoring")
    st.title("DASHBOARD MONITORING 𓀛")
    st.write("Dashboard ini dalam pengembangan, uhuuy")
    
    try:
        sp_df = load_dataset('DATASET SP')
        berita_df = load_dataset('DATASET BERITA')
        
        sp_df['PUBLIKASI'] = pd.to_datetime(sp_df['PUBLIKASI'], errors='coerce')
        berita_df['Tanggal'] = pd.to_datetime(berita_df['Tanggal'], errors='coerce')
        
        sp_df = sp_df.sort_values('PUBLIKASI', ascending=False)
        berita_df = berita_df.sort_values('Tanggal', ascending=False)
        
        st.sidebar.header("Filter")
        
        if st.sidebar.button("Reset Filters", key="reset_filters"):
            st.experimental_rerun()
        
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
        
        filtered_sp = sp_df[
            (sp_df['PUBLIKASI'].dt.date >= start_date) &
            (sp_df['PUBLIKASI'].dt.date <= end_date)
        ]
        
        selected_siaran_pers = st.sidebar.multiselect(
            "Pilih Siaran Pers",
            options=filtered_sp['JUDUL'].unique() if not filtered_sp.empty else []
        )
        
        if selected_siaran_pers:
            filtered_sp = filtered_sp[filtered_sp['JUDUL'].isin(selected_siaran_pers)]
        
        filtered_berita = get_filtered_berita(berita_df, filtered_sp)
        
        st.subheader("💡 Overview")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Siaran Pers", filtered_sp['JUDUL'].nunique() if not filtered_sp.empty else 0)
        col2.metric("Berita", len(filtered_berita) if not filtered_berita.empty else 0)
        col3.metric("Media", filtered_berita['Sumber Media'].nunique() if 'Sumber Media' in filtered_berita.columns and not filtered_berita.empty else 0)
        
        if 'NARASUMBER' in filtered_sp.columns:
            col4.metric("Narasumber", filtered_sp['NARASUMBER'].nunique() if not filtered_sp['NARASUMBER'].isnull().all() else 0)
        else:
            st.warning("NARASUMBER column not found in the dataset")
        
        if not filtered_berita.empty and 'Siaran Pers' in filtered_berita.columns:
            st.subheader("📊 Analisis Dasar Pemberitaan")
            sp_with_news = filtered_berita['Siaran Pers'].unique()
            total_sp_with_news = len(sp_with_news)
            total_sp = len(filtered_sp) if not filtered_sp.empty else 0
            percentage_sp_with_news = (total_sp_with_news / total_sp * 100) if total_sp > 0 else 0
            sp_news_counts = filtered_berita.groupby('Siaran Pers').size().to_dict()
            avg_news_per_sp = filtered_berita.groupby('Siaran Pers').size().mean() if total_sp_with_news > 0 else 0
            sp_media_counts = filtered_berita.groupby('Siaran Pers')['Sumber Media'].nunique().to_dict()
            avg_media_per_sp = filtered_berita.groupby('Siaran Pers')['Sumber Media'].nunique().mean() if total_sp_with_news > 0 else 0
            max_news_sp = max(sp_news_counts.items(), key=lambda x: x[1]) if sp_news_counts else ("Tidak ada", 0)
            max_media_sp = max(sp_media_counts.items(), key=lambda x: x[1]) if sp_media_counts else ("Tidak ada", 0)
            
            st.markdown(f"""
            #### Analisis Dasar Pemberitaan

            Monitoring pemberitaan dilakukan terhadap **{total_sp_with_news} siaran pers atau {percentage_sp_with_news:.1f}%** dari total **{total_sp} siaran pers
            "} \n\nfig_bar.update_layout(\n height=500,\n yaxis=dict(categoryorder='total ascending'), # To sort correctly\n)\n st.plotly_chart(fig_bar, use_container_width=True)\n\n # Time Series Analysis\n with col2:\n # Ensure data is sorted by week for accurate timeline visualization\n narasumber_counts = narasumber_counts.sort_values(by='Week_start')\n # Create line chart\n fig_line = px.line(\n narasumber_counts,\n x='Week_start',\n y='COUNT',\n color='CLEAN_NARASUMBER',\n title='Tren Mingguan Top Narasumber',\n hover_data=['custom_label'],\n labels={\n 'Week_start': 'Minggu (Mulai)',\n 'COUNT': 'Frekuensi',\n 'CLEAN_NARASUMBER': 'Narasumber'\n },\n )\n # Add lines for only the top narasumbers\n top_narasumbers = narasumber_total_counts.head(5).index.tolist()\n fig_line.data = [\n trace for trace in fig_line.data if trace.name in top_narasumbers\n ]\n # Update layout for line chart\n fig_line.update_layout(\n height=500,\n xaxis=dict(title='Minggu (Mulai)'),\n yaxis=dict(title='Frekuensi')\n )\n # Show the chart\n st.plotly_chart(fig_line, use_container_width=True)\n except Exception as e:\n st.error(f"Error dalam menganalisis narasumber: {e}")\n else:\n st.warning("Tidak ada data Siaran Pers yang sesuai dengan filter untuk ditampilkan.")\n # Tab 2: Pemberitaan (visualizations and analysis specific to news articles)\n with tab2:\n # Call the pemberitaan_tab function, passing the news and press release data\n pemberitaan_tab(berita_df, sp_df, filtered_sp)\nexcept Exception as e:\n st.error(f"Error dalam memuat data: {e}")\nif name == "main":\n main()\n\n\n"}"
