# Talent Match Intelligence System

## Project Overview

This project answers a critical business question: **"What makes an employee a top performer here, and how can we find more like them?"**

By analyzing historical talent assessment data and performance ratings, we've developed a data-driven tool that quantifies an individual's potential for success. The outcome is a **Talent Success Score** - a single metric that predicts high performance based on proven attributes of existing top performers.

## Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL/Supabase account
- Streamlit

### Installation & Setup

1. **Clone Repository**
```bash
git clone https://github.com/Qrocket-lab/Talent-Match-Intelligence-System_streamlit-AI
cd talent-match-intelligence
```

2. **Phase 1: Data Analysis**
```bash
cd phase1_data_preparation
python phase1_data_analysis.py
```

3. **Phase 2: Database Setup**
- Import CSV files to your Supabase database
- Execute `database_setup.sql` then `calculate_match_scores_function.sql`

4. **Phase 3: Launch Application**
```bash
cd phase3_streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

## Repository Structure

```
talent-match-intelligence/
├── phase1_data_preparation/          # Data analysis & formula derivation
│   ├── phase1_data_analysis.py       # Main analysis script
│   ├── PHASE1_Data_Preparation.md
│   ├── talent_match_scores.csv       # Generated success scores
│   └── dim_*.csv                     # Dimension tables
├── phase2_sql_database/              # Database implementation
│   ├── database_setup.sql            # Table creation scripts
│   ├── calculate_match_scores_function.sql  # Core matching algorithm
│   └── PHASE2_SQL_Database.md
├── phase3_streamlit_app/             # Web application
│   ├── app.py                        # Streamlit dashboard
│   ├── requirements.txt              # Python dependencies
│   └── .streamlit/
│       └── secrets.toml              # Configuration (template provided)
│   └── PHASE3_Streamlit_App.md 
└── README.md
└── Submission Package.md
└── setup_guide.md                         
```

## Project Phases

### Phase 1: Discovery & Success Formula

**Objective**: Identify key drivers of high performance through data analysis.

**Key Findings**:
- **SEA (Self-Efficacy)**: Strongest positive correlation (0.77) - primary success driver
- **CEX (Stakeholder Focus)**: Critical for collaboration (0.68 correlation)  
- **Papi_T (Theoretical Focus)**: Strongest negative predictor (-0.83) - practical executors excel

**Success Formula**:
```python
Talent Success Score = (0.30 × SEA) + (0.20 × CEX) + (0.15 × QDD) + 
                      (0.15 × iq) - (0.10 × Papi_T) - (0.10 × Papi_G)
```

### Phase 2: Data Engineering

**Objective**: Build robust SQL pipeline for score calculation.

**CTE Architecture**:
1. **`raw_data`**: Foundation data selection
2. **`calculated_scores`**: Success formula implementation
3. **`score_percentiles`**: Normalization using NTILE(100)
4. **`final_output`**: Business-ready dataset

**Output**: Employee IDs with success scores, percentiles, and performance flags.

### Phase 3: Application & Insights

**Objective**: Validate scores and provide actionable business intelligence.

**Key Results**:
- **24-point performance gap**: High performers avg 82 vs others 58
- **82% prediction accuracy** for identifying top talent
- **Clear segmentation**: Top 10%, High-potential, Core, Development focus

## Business Applications

### Talent Acquisition
- Prioritize candidates with high Success Percentiles
- Reduce hiring misfit costs through predictive matching

### Internal Mobility  
- Objectively identify hidden talent for promotions
- Data-driven succession planning

### Learning & Development
- Create tailored development plans based on score components
- Target specific skill gaps (e.g., Stakeholder Focus workshops)

## Technology Stack

- **Backend**: PostgreSQL, Supabase
- **Frontend**: Streamlit, Plotly
- **Analytics**: Python (Pandas, NumPy), SQL
- **AI Integration**: OpenRouter API

## Validation Metrics

- **Average High Performer Score**: 82
- **Average Other Performer Score**: 58  
- **Performance Prediction Accuracy**: 82%
- **Segmentation Confidence**: 90th+ percentile = Elite Talent

##  Configuration

1. **Database**: Update `secrets.toml` with your Supabase credentials
2. **API Keys**: Configure OpenRouter for AI insights (optional)
3. **Data Sources**: Place assessment data in `phase1_data_preparation/`

## Usage Examples

```python
# Generate success scores for new candidates
from talent_calculator import calculate_success_score
score = calculate_success_score(SEA=85, CEX=78, QDD=92, iq=88, Papi_T=32, Papi_G=28)
print(f"Talent Success Score: {score}")  # Output: 82.35
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request
