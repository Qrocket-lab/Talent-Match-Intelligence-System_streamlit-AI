-- =============================================================================
-- Talent Match Intelligence System - Database Setup
-- =============================================================================

-- Create custom type for Talent Group Variable configuration
CREATE TYPE TGV_CONFIG_TYPE AS (
    tv_name TEXT, 
    tgv_name TEXT, 
    direction TEXT, 
    weight NUMERIC 
);

-- =============================================================================
-- DIMENSION TABLES (Reference Data)
-- =============================================================================

-- Positions table
CREATE TABLE dim_positions (
    position_id BIGINT PRIMARY KEY,
    name TEXT NOT NULL
);

-- Divisions table  
CREATE TABLE dim_divisions (
    division_id BIGINT PRIMARY KEY,
    name TEXT NOT NULL
);

-- Departments table
CREATE TABLE dim_departments (
    department_id BIGINT PRIMARY KEY,
    name TEXT NOT NULL
);

-- Directorates table
CREATE TABLE dim_directorates (
    directorate_id BIGINT PRIMARY KEY,
    name TEXT NOT NULL
);

-- Grades table
CREATE TABLE dim_grades (
    grade_id BIGINT PRIMARY KEY,
    name TEXT NOT NULL
);

-- Companies table
CREATE TABLE dim_companies (
    company_id BIGINT PRIMARY KEY,
    name TEXT NOT NULL
);

-- Education levels table
CREATE TABLE dim_education (
    education_id BIGINT PRIMARY KEY,
    name TEXT NOT NULL
);

-- Majors table
CREATE TABLE dim_majors (
    major_id BIGINT PRIMARY KEY,
    name TEXT NOT NULL
);

-- Areas table
CREATE TABLE dim_areas (
    area_id BIGINT PRIMARY KEY,
    name TEXT NOT NULL
);

-- =============================================================================
-- MAIN DATA TABLE (Talent Match Scores)
-- =============================================================================

CREATE TABLE talent_match_scores (
    -- Employee Identification
    employee_id TEXT PRIMARY KEY,
    fullname TEXT NOT NULL,
    
    -- Performance Data
    rating NUMERIC NOT NULL,
    years_of_service_months NUMERIC,
    job_level TEXT,
    
    -- Talent Variables (Core Assessment Scores)
    SEA NUMERIC,        -- Self-Efficacy & Achievement
    CEX NUMERIC,        -- Stakeholder Focus
    QDD NUMERIC,        -- Conscientiousness & Reliability
    iq NUMERIC,         -- Cognitive Complexity
    Papi_G NUMERIC,     -- Need for Group Belonging (Lower is Better)
    Papi_T NUMERIC,     -- Theoretical/Strategic Focus (Lower is Better)
    
    -- Dimension Foreign Keys
    position_id BIGINT REFERENCES dim_positions(position_id),
    division_id BIGINT REFERENCES dim_divisions(division_id),
    department_id BIGINT REFERENCES dim_departments(department_id),
    directorate_id BIGINT REFERENCES dim_directorates(directorate_id),
    grade_id BIGINT REFERENCES dim_grades(grade_id),
    company_id BIGINT REFERENCES dim_companies(company_id),
    education_id BIGINT REFERENCES dim_education(education_id),
    major_id BIGINT REFERENCES dim_majors(major_id),
    area_id BIGINT REFERENCES dim_areas(area_id)
);

-- =============================================================================
-- INDEXES for Performance
-- =============================================================================

-- Index on rating for high-performer queries
CREATE INDEX idx_talent_match_scores_rating ON talent_match_scores(rating);

-- Index on talent variables for matching performance
CREATE INDEX idx_talent_match_scores_sea ON talent_match_scores(SEA);
CREATE INDEX idx_talent_match_scores_cex ON talent_match_scores(CEX);
CREATE INDEX idx_talent_match_scores_qdd ON talent_match_scores(QDD);
CREATE INDEX idx_talent_match_scores_iq ON talent_match_scores(iq);
CREATE INDEX idx_talent_match_scores_papi_g ON talent_match_scores(Papi_G);
CREATE INDEX idx_talent_match_scores_papi_t ON talent_match_scores(Papi_T);

-- Indexes on foreign keys for join performance
CREATE INDEX idx_tms_position_id ON talent_match_scores(position_id);
CREATE INDEX idx_tms_division_id ON talent_match_scores(division_id);
CREATE INDEX idx_tms_department_id ON talent_match_scores(department_id);

-- =============================================================================
-- SAMPLE DATA (Optional - for testing)
-- =============================================================================

-- Sample dimension data
INSERT INTO dim_positions (position_id, name) VALUES
(1, 'Brand Executive'),
(2, 'Supply Planner'),
(3, 'HRBP'),
(4, 'Sales Supervisor'),
(5, 'Data Analyst'),
(6, 'Product Manager');

INSERT INTO dim_divisions (division_id, name) VALUES
(1, 'Digital Marketing'),
(2, 'Operations'),
(3, 'Product Dev'),
(4, 'Sales'),
(5, 'Talent Management');

INSERT INTO dim_departments (department_id, name) VALUES
(1, 'Finance'),
(2, 'HR'),
(3, 'Marketing'),
(4, 'Operations'),
(5, 'R&D'),
(6, 'Sales');

-- Sample talent data (5 employees)
INSERT INTO talent_match_scores (
    employee_id, fullname, rating, years_of_service_months, job_level,
    SEA, CEX, QDD, iq, Papi_G, Papi_T,
    position_id, division_id, department_id
) VALUES
('EMP100001', 'John Smith', 5, 36, 'Senior', 85, 78, 92, 115, 42, 38, 3, 5, 2),
('EMP100002', 'Maria Garcia', 5, 24, 'Middle', 88, 85, 79, 108, 35, 41, 5, 3, 5),
('EMP100003', 'David Chen', 4, 18, 'Middle', 72, 68, 85, 112, 58, 45, 1, 1, 3),
('EMP100004', 'Sarah Johnson', 3, 12, 'Junior', 65, 72, 88, 105, 62, 52, 2, 2, 4),
('EMP100005', 'James Wilson', 5, 48, 'Senior', 92, 81, 87, 118, 31, 29, 6, 3, 5);

-- =============================================================================
-- SECURITY SETUP (Row Level Security - Optional)
-- =============================================================================

-- Enable Row Level Security on main table
ALTER TABLE talent_match_scores ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (adjust based on your security needs)
CREATE POLICY "Allow all operations for authenticated users" ON talent_match_scores
FOR ALL USING (true);

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================

-- Verify table creation
SELECT 
    table_name, 
    column_name, 
    data_type 
FROM information_schema.columns 
WHERE table_schema = 'public' 
ORDER BY table_name, ordinal_position;

-- Verify sample data
SELECT 
    tms.employee_id,
    tms.fullname,
    tms.rating,
    dp.name as position_name,
    dd.name as division_name,
    dpt.name as department_name
FROM talent_match_scores tms
LEFT JOIN dim_positions dp ON tms.position_id = dp.position_id
LEFT JOIN dim_divisions dd ON tms.division_id = dd.division_id
LEFT JOIN dim_departments dpt ON tms.department_id = dpt.department_id
LIMIT 5;