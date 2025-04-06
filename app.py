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

def get_filtered_berita(berita_df, filtered_sp):
    """
    Helper function to get news related to the selected press releases.
    This will be used for both the scorecard and pemberitaan tab.
    """
    # Ensure date columns are datetime
    berita_df['Tanggal'] = pd.to_datetime(berita_df['Tanggal'], errors='coerce')
    
    # If no press releases selected, return empty dataframe
    if filtered_sp.empty:
        return pd.DataFrame(columns=berita_df.columns)
    
    # Filter berita yang relevan dengan siaran pers yang dipilih
    filtered_berita_indices = []
    
    for _, sp_row in filtered_sp.iterrows():
        sp_date = sp_row['PUBLIKASI']
        sp_title = sp_row['JUDUL']
        
        if pd.isna(sp_date):
            continue
            
        # Temukan berita dalam rentang 3 hari setelah siaran pers
        # IMPORTANT FIX: Add check for 'Siaran Pers' column to match the title
        relevant_news = berita_df[
            (berita_df['Tanggal'] >= sp_date) & 
            (berita_df['Tanggal'] <= sp_date + pd.Timedelta(days=7)) &
            (berita_df['Siaran Pers'] == sp_title)  # Match the exact SP title
        ]
        
        filtered_berita_indices.extend(relevant_news.index.tolist())
    
    # Hapus duplikat indeks berita
    filtered_berita_indices = list(set(filtered_berita_indices))
    
    # Filter berita berdasarkan indeks yang sudah dikumpulkan
    if filtered_berita_indices:
        return berita_df.loc[filtered_berita_indices]
    else:
        return pd.DataFrame(columns=berita_df.columns)

def pemberitaan_tab(berita_df, sp_df, filtered_sp):
    st.subheader("📰 Analisis Pemberitaan")
    
    if not berita_df.empty and not sp_df.empty:
        try:
            # Ensure date columns are datetime
            berita_df['Tanggal'] = pd.to_datetime(berita_df['Tanggal'], errors='coerce')
            
            # Get filtered news based on the selected press releases
            filtered_berita = get_filtered_berita(berita_df, filtered_sp)
            
            # Tampilkan jumlah berita yang telah difilter
            st.info(f"Menampilkan {len(filtered_berita)} berita yang relevan dengan Siaran Pers yang dipilih")
            
            # 1. Media Coverage Metrics
            st.subheader("📈 Media Coverage")
            if not filtered_berita.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Top Media Sources by Volume
                    media_counts = filtered_berita['Sumber Media'].value_counts().head(10)
                    fig_media = px.bar(
                        x=media_counts.values,
                        y=media_counts.index,
                        orientation='h',
                        title="Top 10 Media Sources by Coverage Volume",
                        labels={'x': 'Jumlah Artikel', 'y': 'Media'}
                    )
                    # FIX: Sort bars in descending order
                    fig_media.update_layout(
                        height=400,
                        yaxis={'categoryorder': 'total ascending'}  # This puts highest values at the top
                    )
                    st.plotly_chart(fig_media, use_container_width=True)
                
                with col2:
                    # Media Coverage Timeline
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
            else:
                st.warning("Tidak cukup data untuk menampilkan Media Coverage Metrics")
            
            # 2. Press Release Impact Analysis
            st.subheader("Analisis Dampak Siaran Pers")
            
            # Match press releases with news coverage
            merged_data = []
            
            # Hanya analisis SP yang telah difilter
            for _, sp_row in filtered_sp.iterrows():
                sp_date = sp_row['PUBLIKASI']
                if pd.isna(sp_date):
                    continue
                    
                sp_title = sp_row['JUDUL']
                
                # IMPORTANT FIX: Add check for 'Siaran Pers' column to match the title
                news_count = len(berita_df[
                    (berita_df['Tanggal'] >= sp_date) & 
                    (berita_df['Tanggal'] <= sp_date + pd.Timedelta(days=3)) &
                    (berita_df['Siaran Pers'] == sp_title)  # Match the exact SP title
                ])
                
                merged_data.append({
                    'Tanggal_SP': sp_date,
                    'Judul_SP': sp_title,
                    'Jumlah_Berita': news_count
                })
                
            impact_df = pd.DataFrame(merged_data)
            
            if not impact_df.empty:
                # Sort by impact (news count)
                impact_df = impact_df.sort_values('Jumlah_Berita', ascending=False)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Top Press Releases by Media Coverage
                    fig_impact = px.bar(
                        impact_df.head(10),
                        x='Jumlah_Berita',
                        y='Judul_SP',
                        orientation='h',
                        title="Top 10 Siaran Pers berdasarkan Jumlah Pemberitaan",
                        labels={'Jumlah_Berita': 'Jumlah Artikel', 'Judul_SP': 'Siaran Pers'}
                    )
                    # FIX: Sort bars in descending order
                    fig_impact.update_layout(
                        height=500,
                        yaxis={'categoryorder': 'total ascending'}  # This puts highest values at the top
                    )
                    st.plotly_chart(fig_impact, use_container_width=True)
                
                with col2:
                    # Time to Coverage Analysis
                    # Create a scatter plot showing relationship between press release date and volume of coverage
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
            else:
                st.warning("Tidak ada data impact untuk ditampilkan.")
            
            # 3. Media Source Distribution - CHANGE FROM TREEMAP TO PIE CHART
            if not filtered_berita.empty:
                st.subheader("Distribusi Sumber Media")
                
                # Create a pie chart visualization of media sources
                media_counts = filtered_berita['Sumber Media'].value_counts()
                
                # Get top 10 and sum the rest as "Other"
                top_media = media_counts.head(10)
                others_count = media_counts[10:].sum() if len(media_counts) > 10 else 0
                
                if others_count > 0:
                    pie_data = pd.concat([top_media, pd.Series({'Others': others_count})])
                else:
                    pie_data = top_media
                
                fig_pie = px.pie(
                    values=pie_data.values,
                    names=pie_data.index,
                    title="Distribusi Pemberitaan berdasarkan Sumber Media",
                    color_discrete_sequence=px.colors.sequential.Blues_r  # Use blues to match theme
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
                
                # 4. Add Sankey diagram to show relationship between SP and Media
                st.subheader("Hubungan Siaran Pers dan Media")
                
                if not filtered_berita.empty and 'Siaran Pers' in filtered_berita.columns:
                    # Create Sankey data
                    sankey_df = filtered_berita[['Siaran Pers', 'Sumber Media']].copy()
                    
                    # Get top 5 SP and top 8 media for clarity
                    top_sp = sankey_df['Siaran Pers'].value_counts().head(5).index.tolist()
                    top_media = sankey_df['Sumber Media'].value_counts().head(8).index.tolist()
                    
                    # Filter data to top items
                    sankey_df = sankey_df[
                        (sankey_df['Siaran Pers'].isin(top_sp)) & 
                        (sankey_df['Sumber Media'].isin(top_media))
                    ]
                    
                    if not sankey_df.empty:
                        # Count flows
                        flow_counts = sankey_df.groupby(['Siaran Pers', 'Sumber Media']).size().reset_index(name='Count')
                        
                        # Create lists of unique source and target nodes
                        all_nodes = list(set(flow_counts['Siaran Pers'].tolist() + flow_counts['Sumber Media'].tolist()))
                        
                        # Create source-target mapping
                        source_indices = [all_nodes.index(sp) for sp in flow_counts['Siaran Pers']]
                        target_indices = [all_nodes.index(media) for media in flow_counts['Sumber Media']]
                        
                        # Create Sankey diagram
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
                
                # 5. Data Table with News Details
                st.subheader("Detail Pemberitaan")

                # Pilih kolom yang ingin ditampilkan
                selected_columns = ['Judul Berita', 'Tanggal', 'Sumber Media', 'Siaran Pers', 'Link Berita']
                
                # Show dataframe with filtered columns
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

        # Add reset button
        if st.sidebar.button("Reset Filters", key="reset_filters"):
            # This will trigger a rerun of the app with default parameters
            st.experimental_rerun()

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

        # Get filtered news based on the selected press releases - IMPORTANT TO GET CORRECT FILTERING
        filtered_berita = get_filtered_berita(berita_df, filtered_sp)

        st.subheader("💡 Overview")
        # Overview - Scorecard - UPDATED to use filtered_berita
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Siaran Pers", filtered_sp['JUDUL'].nunique() if not filtered_sp.empty else 0)
        col2.metric("Berita", len(filtered_berita) if not filtered_berita.empty else 0)
        col3.metric("Media", filtered_berita['Sumber Media'].nunique() if 'Sumber Media' in filtered_berita.columns and not filtered_berita.empty else 0)
        
        # Add null check and debug information for NARASUMBER
        if 'NARASUMBER' in filtered_sp.columns:
            col4.metric("Narasumber", filtered_sp['NARASUMBER'].nunique() if not filtered_sp['NARASUMBER'].isnull().all() else 0)
        else:
            st.warning("NARASUMBER column not found in the dataset")

        # Analisis dasar untuk text box
        if not filtered_berita.empty and 'Siaran Pers' in filtered_berita.columns:
            st.subheader("📊 Analisis Dasar Pemberitaan")
    
            # 1. Hitung siaran pers yang memiliki berita (nilai unik di kolom Siaran Pers)
            sp_with_news = filtered_berita['Siaran Pers'].unique()
            total_sp_with_news = len(sp_with_news)
    
            # Total siaran pers di dataset yang telah difilter
            total_sp = len(filtered_sp) if not filtered_sp.empty else 0
    
            # Persentase siaran pers yang mendapat pemberitaan
            percentage_sp_with_news = (total_sp_with_news / total_sp * 100) if total_sp > 0 else 0
    
            # 2. Hitung jumlah berita per siaran pers
            sp_news_counts = filtered_berita.groupby('Siaran Pers').size().to_dict()
    
            # 3. Rata-rata pemberitaan per siaran pers (hanya yang memiliki berita)
            avg_news_per_sp = filtered_berita.groupby('Siaran Pers').size().mean() if total_sp_with_news > 0 else 0
    
            # 4. Hitung jumlah media unik per siaran pers
            sp_media_counts = filtered_berita.groupby('Siaran Pers')['Sumber Media'].nunique().to_dict()
    
            # Rata-rata media per siaran pers
            avg_media_per_sp = filtered_berita.groupby('Siaran Pers')['Sumber Media'].nunique().mean() if total_sp_with_news > 0 else 0
    
            # Temukan SP dengan pemberitaan tertinggi
            if sp_news_counts:
                max_news_sp = max(sp_news_counts.items(), key=lambda x: x[1])
            else:
                max_news_sp = ("Tidak ada", 0)
    
            # Temukan SP dengan coverage media tertinggi
            if sp_media_counts:
                max_media_sp = max(sp_media_counts.items(), key=lambda x: x[1])
            else:
                max_media_sp = ("Tidak ada", 0)
    
            # Tampilkan analisis dalam text box
            st.markdown(f"""
            #### Analisis Dasar Pemberitaan
    
            Monitoring pemberitaan dilakukan terhadap **{total_sp_with_news} siaran pers atau {percentage_sp_with_news:.1f}%** dari total **{total_sp} siaran pers** yang difilter. 
    
            Setiap siaran pers memiliki rata-rata pemberitaan sebanyak **{avg_news_per_sp:.1f} berita** dari **{avg_media_per_sp:.1f} media** yang berbeda.
            
            Siaran pers dengan pemberitaan tertinggi:
            "**{max_news_sp[0]}**"
            dengan total **{max_news_sp[1]} berita** yang ditulis oleh berbagai media.
    
            Siaran pers dengan liputan terluas:
            "**{max_media_sp[0]}**"
            dengan **{max_media_sp[1]} media** berbeda yang memberitakannya.
            """)
        else:
            st.warning("Tidak ada data berita yang sesuai dengan filter untuk ditampilkan.")

        # Create tabs after the overview section
        tab1, tab2 = st.tabs(["Siaran Pers", "Pemberitaan"])
        
        # Tab 1: Siaran Pers (all current visualizations)
        with tab1:
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
                        # FIX: Sort bars in descending order
                        fig_bar.update_layout(
                            xaxis_title="Frekuensi",
                            yaxis_title="Narasumber",
                            height=400,
                            yaxis={'categoryorder': 'total ascending'}  # This puts highest values at the top
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

                    # FIX: Adjust scatter plot to make it more readable - sort by total appearances
                    narasumber_total_counts = narasumber_counts.groupby('CLEAN_NARASUMBER')['COUNT'].sum().sort_values(ascending=False)
                    
                    # Show only top 15 narasumbers for clarity
                    top_narasumbers = narasumber_total_counts.head(15).index.tolist()
                    filtered_scatter_data = narasumber_counts[narasumber_counts['CLEAN_NARASUMBER'].isin(top_narasumbers)]
                    
                    # Create new scatter plot with only top narasumbers
                    if not filtered_scatter_data.empty:
                        fig_scatter = px.scatter(
                            filtered_scatter_data, 
                            x='Week_start',
                            y='CLEAN_NARASUMBER',
                            size='COUNT',
                            color='CLEAN_NARASUMBER',
                            title="Top 15 Narasumber Appearances Weekly",
                            labels={'Week_start': 'Week', 'CLEAN_NARASUMBER': 'Narasumber', 'COUNT': 'Frequency'},
                            hover_name='custom_label'
                        )
                        
                        fig_scatter.update_traces(
                            hovertemplate='%{hovertext}<extra></extra>'
                        )
                        
                        fig_scatter.update_layout(
                            showlegend=False,
                            autosize=True,
                            height=600,
                            width=None,
                            xaxis_title='Minggu',
                            yaxis_title='Narasumber',
                            yaxis={'categoryorder': 'array', 'categoryarray': top_narasumbers[::-1]}
                        )
                        
                        # Format sumbu X untuk menampilkan tanggal dengan lebih baik
                        fig_scatter.update_xaxes(
                            tickformat='%d-%m-%Y',
                            tickmode='auto',
                            nticks=10
                        )
                        
                        st.plotly_chart(fig_scatter, use_container_width=True)
                    else:
                        st.warning("Tidak cukup data untuk membuat scatter plot narasumber")
                    
                    # Narasumber Sankey Diagram - Shows flow from Narasumbers to Siaran Pers
                    st.subheader("Hubungan Narasumber dan Siaran Pers")
                    
                    # Get top 10 narasumbers for the Sankey diagram
                    top_narasumbers = narasumber_total_counts.head(10).index.tolist()
                    top_sp = filtered_sp['JUDUL'].value_counts().head(8).index.tolist()
                    
                    # Filter data for the Sankey diagram
                    sankey_data = narasumber_exploded[
                        (narasumber_exploded['CLEAN_NARASUMBER'].isin(top_narasumbers)) &
                        (narasumber_exploded['JUDUL'].isin(top_sp))
                    ]
                    
                    if not sankey_data.empty:
                        # Count flows
                        flow_counts = sankey_data.groupby(['CLEAN_NARASUMBER', 'JUDUL']).size().reset_index(name='Count')
                        
                        # Create lists of unique source and target nodes
                        all_nodes = list(set(flow_counts['CLEAN_NARASUMBER'].tolist() + flow_counts['JUDUL'].tolist()))
                        
                        # Create source-target mapping
                        source_indices = [all_nodes.index(ns) for ns in flow_counts['CLEAN_NARASUMBER']]
                        target_indices = [all_nodes.index(sp) for sp in flow_counts['JUDUL']]
                        
                        # Create Sankey diagram
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
                        
                        fig_sankey.update_layout(title_text="Alur Narasumber ke Siaran Pers", height=600)
                        st.plotly_chart(fig_sankey, use_container_width=True)
                    else:
                        st.warning("Tidak cukup data untuk membuat diagram Sankey.")
                    
                    # Tampilkan tabel siaran pers
                    st.subheader("Daftar Siaran Pers")
                    st.dataframe(filtered_sp[['JUDUL', 'PUBLIKASI', 'NARASUMBER']])
                    
                except Exception as e:
                    st.error(f"Error in Siaran Pers analysis: {e}")
            else:
                st.warning("Tidak ada siaran pers yang sesuai dengan filter yang dipilih.")
        
        # Tab 2: Pemberitaan analysis with Sankey from SP → Media → Volume
        with tab2:
            pemberitaan_tab(berita_df, sp_df, filtered_sp)
            
            # Create Sankey diagram for SP → Media → Volume
            st.subheader("Alur Siaran Pers ke Media ke Volume")
            
            # Get filtered news based on selected press releases
            filtered_berita = get_filtered_berita(berita_df, filtered_sp)
            
            if not filtered_berita.empty and 'Siaran Pers' in filtered_berita.columns:
                # Get top siaran pers for clarity
                top_sp = filtered_berita['Siaran Pers'].value_counts().head(5).index.tolist()
                
                # Get top media sources
                top_media = filtered_berita['Sumber Media'].value_counts().head(8).index.tolist()
                
                # Filter data for the Sankey diagram
                sankey_data = filtered_berita[
                    (filtered_berita['Siaran Pers'].isin(top_sp)) & 
                    (filtered_berita['Sumber Media'].isin(top_media))
                ]
                
                if not sankey_data.empty:
                    # Count SP to Media flows
                    flow_sp_media = sankey_data.groupby(['Siaran Pers', 'Sumber Media']).size().reset_index(name='Count')
                    
                    # Create volume category nodes for media
                    volume_categories = ['Low (1-2)', 'Medium (3-5)', 'High (6+)']
                    flow_media_volume = []
                    
                    for media in top_media:
                        media_count = sankey_data[sankey_data['Sumber Media'] == media].shape[0]
                        if media_count <= 2:
                            volume_cat = 'Low (1-2)'
                        elif media_count <= 5:
                            volume_cat = 'Medium (3-5)'
                        else:
                            volume_cat = 'High (6+)'
                        
                        flow_media_volume.append({
                            'Sumber Media': media,
                            'Volume': volume_cat,
                            'Count': media_count
                        })
                    
                    flow_media_volume_df = pd.DataFrame(flow_media_volume)
                    
                    # Create complete node list
                    all_nodes = list(set(
                        flow_sp_media['Siaran Pers'].tolist() + 
                        flow_sp_media['Sumber Media'].tolist() + 
                        volume_categories
                    ))
                    
                    # Create source-target mappings for SP -> Media
                    source_sp_media = [all_nodes.index(sp) for sp in flow_sp_media['Siaran Pers']]
                    target_sp_media = [all_nodes.index(media) for media in flow_sp_media['Sumber Media']]
                    values_sp_media = flow_sp_media['Count'].tolist()
                    
                    # Create source-target mappings for Media -> Volume
                    source_media_volume = [all_nodes.index(row['Sumber Media']) for _, row in flow_media_volume_df.iterrows()]
                    target_media_volume = [all_nodes.index(row['Volume']) for _, row in flow_media_volume_df.iterrows()]
                    values_media_volume = flow_media_volume_df['Count'].tolist()
                    
                    # Combine all links
                    sources = source_sp_media + source_media_volume
                    targets = target_sp_media + target_media_volume
                    values = values_sp_media + values_media_volume
                    
                    # Create Sankey diagram
                    fig_sankey = go.Figure(data=[go.Sankey(
                        node=dict(
                            pad=15,
                            thickness=20,
                            line=dict(color="black", width=0.5),
                            label=all_nodes,
                            color="blue"  # Use blue color theme
                        ),
                        link=dict(
                            source=sources,
                            target=targets,
                            value=values,
                            color="rgba(100, 149, 237, 0.6)"  # Use light blue with transparency
                        )
                    )])
                    
                    fig_sankey.update_layout(
                        title_text="Alur Siaran Pers → Media → Volume", 
                        height=700,
                        font=dict(size=12)
                    )
                    st.plotly_chart(fig_sankey, use_container_width=True)
                else:
                    st.warning("Tidak cukup data untuk membuat diagram Sankey.")
            else:
                st.warning("Tidak ada data berita yang sesuai untuk ditampilkan.")
            
    except Exception as e:
        st.error(f"Error loading or processing data: {e}")
        import traceback
        st.error(traceback.format_exc())

if __name__ == "__main__":
    main()
