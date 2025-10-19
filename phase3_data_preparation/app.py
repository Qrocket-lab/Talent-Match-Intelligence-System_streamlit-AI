import streamlit as st
import pandas as pd
from supabase import create_client, Client
import requests
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any, Tuple

# Set page configuration
st.set_page_config(layout="wide", page_title="Talent Match & Vacancy Intelligence")

# ==============================================================================
# 0. CONFIGURATION & DATA CONNECTION
# ==============================================================================

@st.cache_resource
def init_connection() -> Client:
    """Initializes the Supabase client connection."""
    try:
        url: str = st.secrets["supabase"]["url"]
        key: str = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Error initializing Supabase connection: {e}")
        raise

supabase_client = init_connection()

# Success Formula
SUCCESS_FORMULA = [
    {'tv_name': 'SEA', 'tgv_name': 'Self-Efficacy & Achievement', 'direction': 'Higher is Better', 'weight': 0.30},
    {'tv_name': 'CEX', 'tgv_name': 'Stakeholder Focus', 'direction': 'Higher is Better', 'weight': 0.20},
    {'tv_name': 'QDD', 'tgv_name': 'Conscientiousness & Reliability', 'direction': 'Higher is Better', 'weight': 0.15},
    {'tv_name': 'iq', 'tgv_name': 'Cognitive Complexity', 'direction': 'Higher is Better', 'weight': 0.15},
    {'tv_name': 'Papi_G', 'tgv_name': 'Need for Group Belonging', 'direction': 'Lower is Better', 'weight': 0.10},
    {'tv_name': 'Papi_T', 'tgv_name': 'Theoretical/Strategic Focus', 'direction': 'Lower is Better', 'weight': 0.10},
]

TGV_LABELS = [item['tgv_name'] for item in SUCCESS_FORMULA]

# ==============================================================================
# 1. ENHANCED DATABASE FUNCTIONS (SINGLE TABLE SOURCE)
# ==============================================================================

@st.cache_data(ttl=600)
def fetch_talent_data() -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
    """
    Fetches ALL data from talent_match_scores table only.
    """
    try:
        # Fetch all data from single table
        response = supabase_client.from_('talent_match_scores').select("*").execute()
        
        if not response.data:
            st.error("No talent data found in talent_match_scores table.")
            return pd.DataFrame(), pd.DataFrame(), {}
            
        talent_df = pd.DataFrame(response.data)
        
        # Fetch dimension names for display
        dimensions = {}
        dim_tables = ['positions', 'divisions', 'departments', 'directorates', 'grades', 'companies']
        
        for dim in dim_tables:
            try:
                dim_response = supabase_client.from_(f'dim_{dim}').select("*").execute()
                if dim_response.data:
                    dimensions[dim] = pd.DataFrame(dim_response.data)
            except Exception as dim_error:
                st.warning(f"Could not load dim_{dim}: {dim_error}")
        
        # Create employee name mapping
        employee_name_map = talent_df.set_index('employee_id')['fullname'].to_dict()
        
        # Identify high performers
        high_performers = talent_df[talent_df['rating'] == 5]
        
        return talent_df, high_performers, employee_name_map, dimensions
        
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame(), pd.DataFrame(), {}, {}

@st.cache_data(ttl=60)
def run_match_query(benchmark_ids: List[str], formula: List[Dict[str, Any]]):
    """
    Calls the secured PostgreSQL function 'calculate_match_scores'
    """
    try:
        response = supabase_client.rpc(
            'calculate_match_scores', 
            params={
                'p_benchmark_ids': benchmark_ids, 
                'p_tgv_config': formula
            }
        ).execute()
        
        if hasattr(response, 'error') and response.error:
            st.error(f"SQL Function Error: {response.error}")
            return pd.DataFrame()
             
        if not response.data:
            st.error("No results returned from matching function.")
            return pd.DataFrame()
             
        df_results = pd.DataFrame(response.data)
        
        # Enhanced profile analysis
        tgv_cols = ['sea_match_rate', 'cex_match_rate', 'qdd_match_rate', 
                   'iq_match_rate', 'papi_g_match_rate', 'papi_t_match_rate']
        
        tgv_label_map = {
            'sea_match_rate': 'Self-Efficacy & Achievement', 
            'cex_match_rate': 'Stakeholder Focus', 
            'qdd_match_rate': 'Conscientiousness & Reliability', 
            'iq_match_rate': 'Cognitive Complexity', 
            'papi_g_match_rate': 'Need for Group Belonging', 
            'papi_t_match_rate': 'Theoretical/Strategic Focus'
        }
        
        def analyze_profile(row):
            rates = row[tgv_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
            
            # Find top 2 strengths and bottom 2 gaps
            top_2 = rates.nlargest(2)
            bottom_2 = rates.nsmallest(2)
            
            strengths = [f"{tgv_label_map.get(col, 'Unknown')} ({rate:.0f}%)" 
                        for col, rate in top_2.items()]
            gaps = [f"{tgv_label_map.get(col, 'Unknown')} ({rate:.0f}%)" 
                   for col, rate in bottom_2.items()]
            
            return {
                'top_strengths': ", ".join(strengths),
                'main_gaps': ", ".join(gaps),
                'strength_count': len([r for r in rates if r >= 80]),
                'gap_count': len([r for r in rates if r <= 50])
            }
        
        # Apply enhanced analysis
        profile_analysis = df_results.apply(analyze_profile, axis=1, result_type='expand')
        df_results = pd.concat([df_results, profile_analysis], axis=1)
                
        return df_results

    except Exception as e:
        st.error(f"Matching error: {e}")
        return pd.DataFrame()

# ==============================================================================
# 2. ENHANCED VISUALIZATION FUNCTIONS
# ==============================================================================

def create_enhanced_radar_chart(df_scores, employee_name, labels, benchmark_avg=None):
    """Creates an enhanced radar chart with benchmark comparison."""
    if isinstance(df_scores, pd.Series):
        df_scores = df_scores.to_frame().T
        
    fig = go.Figure()
    
    match_scores = [
        df_scores['sea_match_rate'].iloc[0],
        df_scores['cex_match_rate'].iloc[0],
        df_scores['qdd_match_rate'].iloc[0],
        df_scores['iq_match_rate'].iloc[0],
        df_scores['papi_g_match_rate'].iloc[0],
        df_scores['papi_t_match_rate'].iloc[0],
    ]
    
    # Main candidate trace
    fig.add_trace(go.Scatterpolar(
        r=match_scores,
        theta=labels,
        fill='toself',
        name=f'Candidate: {employee_name}',
        line_color='#2E86AB',
        fillcolor='rgba(46, 134, 171, 0.6)',
        opacity=0.8,
    ))
    
    # Benchmark average trace (if provided)
    if benchmark_avg is not None:
        fig.add_trace(go.Scatterpolar(
            r=benchmark_avg,
            theta=labels,
            fill='toself',
            name='Benchmark Average',
            line_color='#A23B72',
            fillcolor='rgba(162, 59, 114, 0.4)',
            opacity=0.6,
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=[0, 25, 50, 75, 100],
                ticktext=['0%', '25%', '50%', '75%', '100%'],
                linecolor='gray',
                gridcolor='lightgray'
            ),
            angularaxis=dict(
                rotation=90,
                direction='clockwise',
                linecolor='gray'
            )
        ),
        showlegend=True,
        title="TGV Match Profile Comparison",
        height=500
    )
    return fig

def create_match_distribution(df_results):
    """Creates a distribution chart of match scores."""
    fig = px.histogram(
        df_results, 
        x='final_match_rate',
        nbins=20,
        title='Distribution of Match Scores',
        labels={'final_match_rate': 'Final Match Rate (%)'},
        color_discrete_sequence=['#2E86AB']
    )
    
    fig.update_layout(
        xaxis_title='Match Rate (%)',
        yaxis_title='Number of Employees',
        showlegend=False
    )
    
    # Add average line
    avg_match = df_results['final_match_rate'].mean()
    fig.add_vline(x=avg_match, line_dash="dash", line_color="red", 
                 annotation_text=f"Average: {avg_match:.1f}%")
    
    return fig

def create_tgv_comparison_chart(df_results, top_n=10):
    """Creates a bar chart comparing TGV scores for top candidates."""
    top_candidates = df_results.head(top_n)
    
    # Prepare data for plotting
    plot_data = []
    for _, row in top_candidates.iterrows():
        for tgv, label in zip(
            ['sea_match_rate', 'cex_match_rate', 'qdd_match_rate', 
             'iq_match_rate', 'papi_g_match_rate', 'papi_t_match_rate'],
            TGV_LABELS
        ):
            plot_data.append({
                'Candidate': row['fullname'],
                'TGV': label,
                'Match Rate': row[tgv],
                'Overall Match': row['final_match_rate']
            })
    
    plot_df = pd.DataFrame(plot_data)
    
    fig = px.bar(
        plot_df,
        x='Candidate',
        y='Match Rate',
        color='TGV',
        title=f'TGV Breakdown for Top {top_n} Candidates',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_layout(
        xaxis_title='Candidate',
        yaxis_title='Match Rate (%)',
        xaxis_tickangle=-45,
        legend_title='Talent Attributes'
    )
    
    return fig

def create_strength_gap_heatmap(df_results, top_n=15):
    """Creates a heatmap showing strengths and gaps across TGVs."""
    top_candidates = df_results.head(top_n)
    
    # Prepare heatmap data
    heatmap_data = []
    for tgv_col, tgv_name in zip(
        ['sea_match_rate', 'cex_match_rate', 'qdd_match_rate', 
         'iq_match_rate', 'papi_g_match_rate', 'papi_t_match_rate'],
        TGV_LABELS
    ):
        row_data = {'TGV': tgv_name}
        for _, candidate in top_candidates.iterrows():
            row_data[candidate['fullname']] = candidate[tgv_col]
        heatmap_data.append(row_data)
    
    heatmap_df = pd.DataFrame(heatmap_data).set_index('TGV')
    
    fig = px.imshow(
        heatmap_df,
        aspect="auto",
        color_continuous_scale='RdYlGn',
        title=f'Strength & Gap Analysis - Top {top_n} Candidates',
        labels=dict(color="Match Rate")
    )
    
    fig.update_layout(
        xaxis_title='Candidates',
        yaxis_title='Talent Attributes'
    )
    
    return fig

# ==============================================================================
# 3. AI GENERATION FUNCTION
# ==============================================================================

def generate_job_profile(job_role_details: str, competencies: str, qualifications: str, tgv_traits: str) -> str:
    """Calls OpenRouter to generate a dynamic job profile."""
    api_key = st.secrets.get("openrouter", {}).get("api_key")
    model_name = st.secrets.get("openrouter", {}).get("model")

    if not api_key or not model_name:
        return "AI Profile generation unavailable. Please check OpenRouter configuration."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    As an HR Strategist, create a compelling job profile for: '{job_role_details}'.
    
    Key Requirements:
    - Core Competencies: {competencies}
    - Qualifications: {qualifications}
    - Success Traits: {tgv_traits}
    
    Format as one engaging paragraph focusing on mindset, skills, and behaviors.
    """

    data = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", 
                               headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"AI generation temporarily unavailable: {str(e)}"

# ==============================================================================
# 4. ENHANCED EMPLOYMENT PROFILE FUNCTION
# ==============================================================================

def create_employment_profile(row):
    """Creates comprehensive employment info using direct SQL function results"""
    profile_parts = []
    
    # Use the direct names from SQL function
    if pd.notna(row.get('position_name')) and row['position_name']:
        profile_parts.append(f"Role: {row['position_name']}")
    
    if pd.notna(row.get('division_name')) and row['division_name']:
        profile_parts.append(f"Division:{row['division_name']}")
    
    if pd.notna(row.get('department_name')) and row['department_name']:
        profile_parts.append(f"Dept: {row['department_name']}")
    
    if pd.notna(row.get('directorate_name')) and row['directorate_name']:
        profile_parts.append(f"Directorate: {row['directorate_name']}")
    
    if pd.notna(row.get('grade_name')) and row['grade_name']:
        profile_parts.append(f"Grade: {row['grade_name']}")
    
    return " | ".join(profile_parts) if profile_parts else "Position information available"

# ==============================================================================
# 5. MAIN STREAMLIT APP
# ==============================================================================

def main():
    st.title("AI-Powered Talent Match & Vacancy Intelligence")
    st.markdown("---")

    # Load data from SINGLE table
    talent_df, high_performers, employee_name_map, dimensions = fetch_talent_data()
    
    if talent_df.empty:
        st.warning("Please ensure talent_match_scores table is properly populated.")
        return

    # Sidebar
    with st.sidebar:
        st.header("1. Role Information")
        job_role = st.text_input("Role Name", "Data Analyst")
        job_level = st.selectbox("Job Level", ["Junior", "Middle", "Senior", "Executive"], index=2)
        role_purpose = st.text_area("Role Purpose", "Analyze data to drive business decisions and insights")
        competencies = st.text_area("Core Competencies", "SQL, Python, Data Visualization, Statistical Analysis")
        qualifications = st.text_area("Required Qualifications", "Bachelor's in STEM, 3+ years experience, Analytics background")
        
        st.header("2. Employee Benchmarking")
        valid_options = talent_df['employee_id'].tolist()
        default_benchmark_ids = high_performers['employee_id'].head(3).tolist()
        default_benchmark_ids = [id for id in default_benchmark_ids if id in employee_name_map]
        
        selected_benchmarks = st.multiselect(
            "Select High Performers as Benchmark (max 3)",
            options=valid_options,
            default=default_benchmark_ids,
            max_selections=3,
            format_func=lambda x: f"{employee_name_map.get(x, 'Unknown')} ({x})"
        )
        
        st.markdown("---")
        run_button = st.button("🚀 Generate Talent Matches", type="primary", use_container_width=True)

    # Main content
    if run_button and selected_benchmarks:
        
        job_vacancy_id = f"{job_role.replace(' ', '_')}_{job_level}_V1"
        st.header(f"Analysis for Job Vacancy: {job_vacancy_id}")
        
        with st.spinner("Analyzing talent matches and generating insights..."):
            match_results_df = run_match_query(selected_benchmarks, SUCCESS_FORMULA)

            if match_results_df.empty:
                st.error("No talent matches found. The benchmark group may be too small or the SQL function failed.")
                return

            # AI Profile Generation
            tgv_list_str = ", ".join([f"{item['tgv_name']} (Weight: {int(item['weight']*100)}%)" for item in SUCCESS_FORMULA])
            full_role_details = f"{job_role} ({job_level} level). Role Purpose: {role_purpose}"
            
            ai_profile = generate_job_profile(
                full_role_details, competencies, qualifications, tgv_list_str
            )

        # Display Results
        st.header("AI-Generated Success Profile Narrative")
        st.info(ai_profile)
        st.markdown("---")

        # Top Match Overview
        top_match = match_results_df.iloc[0]
        st.subheader(f"Top Match: **{top_match['fullname']}** (Score: {top_match['final_match_rate']:.1f}%)")
        
        # Rich Employment Profile - NO MORE "None"!
        employment_profile = create_employment_profile(top_match)
        st.markdown(f"Employment Profile: {employment_profile}")
        
        # Enhanced metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Overall Match", f"{top_match['final_match_rate']:.1f}%")
        with col2:
            st.metric("Key Strengths", top_match.get('strength_count', 0))
        with col3:
            st.metric("Areas for Growth", top_match.get('gap_count', 0))
        
        # Profile summary
        st.markdown(f"Profile Summary:{top_match['top_strengths']}")
        st.markdown(f"Development Areas: {top_match['main_gaps']}")

        # Visualizations Section
        st.header("Talent Analytics Dashboard")
        
        # Row 1: Radar Chart and Distribution
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Calculate benchmark averages for comparison
            benchmark_avg = [
                match_results_df['sea_match_rate'].mean(),
                match_results_df['cex_match_rate'].mean(),
                match_results_df['qdd_match_rate'].mean(),
                match_results_df['iq_match_rate'].mean(),
                match_results_df['papi_g_match_rate'].mean(),
                match_results_df['papi_t_match_rate'].mean(),
            ]
            
            radar_fig = create_enhanced_radar_chart(
                top_match.to_frame().T, 
                top_match['fullname'], 
                TGV_LABELS,
                benchmark_avg
            )
            st.plotly_chart(radar_fig, use_container_width=True)
        
        with col2:
            dist_fig = create_match_distribution(match_results_df)
            st.plotly_chart(dist_fig, use_container_width=True)

        # Row 2: TGV Comparison and Heatmap
        tab1, tab2 = st.tabs([" TGV Comparison", " Strength Gap Analysis"])
        
        with tab1:
            comparison_fig = create_tgv_comparison_chart(match_results_df, top_n=8)
            st.plotly_chart(comparison_fig, use_container_width=True)
        
        with tab2:
            heatmap_fig = create_strength_gap_heatmap(match_results_df, top_n=10)
            st.plotly_chart(heatmap_fig, use_container_width=True)

        # Enhanced Results Table
        st.header(" Ranked Talent Matches")
        
        # Create rich employment profiles for ALL results
        match_results_df['Employment Profile'] = match_results_df.apply(
            lambda row: create_employment_profile(row), 
            axis=1
        )
        
        display_df = match_results_df.head(15).copy()
        
        st.dataframe(
            display_df.set_index('match_rank')[
                ['fullname', 'Employment Profile', 'final_match_rate', 'top_strengths', 'main_gaps']
            ],
            column_config={
                "fullname": "Employee Name",
                "Employment Profile": st.column_config.TextColumn("Current Position & Details", width="large"),
                "final_match_rate": st.column_config.ProgressColumn("Match Rate", format="%.1f%%", min_value=0, max_value=100),
                "top_strengths": "Key Strengths", 
                "main_gaps": "Development Areas"
            },
            use_container_width=True
        )

        # Insights Section
        st.header(" Key Insights")
        
        insights_col1, insights_col2 = st.columns(2)
        
        with insights_col1:
            st.subheader("Top Performer Patterns")
            high_matches = match_results_df[match_results_df['final_match_rate'] >= 80]
            if not high_matches.empty:
                common_strengths = high_matches['top_strengths'].str.split(', ').explode().value_counts().head(3)
                st.write("**Common strengths in top matches:**")
                for strength, count in common_strengths.items():
                    st.write(f"- {strength} ({count} employees)")
            else:
                st.write("No employees with match rate ≥80%")
        
        with insights_col2:
            st.subheader("Recommendations")
            st.write(" **Hire Ready:** Candidates with match rates >85% and 4+ strong TGVs")
            st.write(" **Developmental:** Candidates with match rates 70-85% - consider with training plan")
            st.write(" **Bench Strength:** Multiple strong candidates indicates good talent pipeline")

    else:
        # Initial state
        st.info("👈 Configure the role and select benchmark employees in the sidebar, then click 'Generate Talent Matches'")
        
        # Show data overview
        if not talent_df.empty:
            st.subheader(" Data Overview")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Employees", len(talent_df))
            with col2:
                st.metric("High Performers", len(high_performers))
            with col3:
                avg_rating = talent_df['rating'].mean()
                st.metric("Avg Rating", f"{avg_rating:.1f}")
            with col4:
                data_quality = "✅ Complete" if talent_df['fullname'].notna().all() else "⚠️ Check Names"
                st.metric("Data Quality", data_quality)

            # Quick preview of available data
            with st.expander(" Preview Available Data"):
                st.dataframe(talent_df[['employee_id', 'fullname', 'position_id', 'rating']].head(10))

if __name__ == "__main__":
    main()