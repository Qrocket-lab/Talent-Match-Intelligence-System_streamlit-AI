# Phase 3: Streamlit Application & Dashboard

## Objective
Create an interactive web application that enables business users to explore talent data, calculate success scores, and make data-driven talent decisions.

## Application Architecture

### Core Components
1. **Data Management**: Connection to Supabase database
2. **Score Calculator**: Real-time success score computation
3. **Visualization Dashboard**: Interactive charts and insights
4. **AI Insights**: OpenRouter integration for strategic recommendations

### Main Features

#### 1. Talent Explorer
- Browse all employees with their success scores
- Filter by department, role, or score range
- Sort by any talent variable or success percentile

#### 2. Score Calculator
```python
def calculate_individual_score(SEA, CEX, QDD, iq, Papi_T, Papi_G):
    """Calculate success score for individual assessment"""
    return (0.30 * SEA) + (0.20 * CEX) + (0.15 * QDD) + \
           (0.15 * iq) - (0.10 * Papi_T) - (0.10 * Papi_G)


## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Secrets
Create `.streamlit/secrets.toml`:
```toml
[supabase]
url = "your-supabase-url"
key = "your-supabase-service-key"

[openrouter]
api_key = "your-openrouter-key"
model = "anthropic/claude-3-sonnet"
```

### 3. Launch Application
```bash
streamlit run app.py
```

## Key Pages & Functionality

### Home Dashboard
- Executive summary of talent distribution
- Key performance metrics
- Quick access to common queries

### Individual Analysis
- Detailed employee talent profiles
- Success score breakdown by component
- Development recommendations

### Team Insights
- Department-level talent distribution
- Success pattern identification
- Team composition optimization

### Batch Processing
- Upload CSV files for multiple assessments
- Bulk score calculation
- Export results with insights

## API Integration

### OpenRouter AI Integration
```python
def get_ai_insights(talent_profile):
    """Get strategic insights for talent development"""
    prompt = f"""
    Analyze this talent profile and provide development recommendations:
    Success Score: {talent_profile['score']}
    Strengths: {talent_profile['strengths']}
    Development Areas: {talent_profile['development_areas']}
    """
    return openrouter_completion(prompt)
```

## Usage Examples

### For HR Business Partners
- Identify high-potential employees for promotion
- Create development plans based on score components
- Optimize team composition for projects

### For Hiring Managers
- Evaluate candidate fit using success scores
- Compare internal vs. external talent
- Make data-driven hiring decisions

### For Learning & Development
- Identify common skill gaps across organization
- Measure program effectiveness through score improvements
- Target training to specific development needs





