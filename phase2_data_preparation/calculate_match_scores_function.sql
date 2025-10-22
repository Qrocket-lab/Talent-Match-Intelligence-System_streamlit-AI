DROP FUNCTION IF EXISTS public.calculate_match_scores (text[], tgv_config_type[]);

CREATE OR REPLACE FUNCTION public.calculate_match_scores (
  p_benchmark_ids text[],
  p_tgv_config TGV_CONFIG_TYPE[]
) RETURNS TABLE (
  employee_id TEXT,
  fullname TEXT,
  position_name TEXT,
  division_name TEXT,
  department_name TEXT,
  directorate_name TEXT,
  grade_name TEXT,
  final_match_rate NUMERIC,
  match_rank BIGINT,
  sea_match_rate NUMERIC,
  cex_match_rate NUMERIC,
  qdd_match_rate NUMERIC,
  iq_match_rate NUMERIC,
  papi_g_match_rate NUMERIC,
  papi_t_match_rate NUMERIC
) LANGUAGE SQL
SET search_path = pg_catalog, public AS $$

/*
CTE 1: EmployeeScores
Purpose: Gather all employee data with their test scores and organizational hierarchy
*/
WITH EmployeeScores AS (
    SELECT
        tms.employee_id,
        tms.fullname,
        dp.name AS position_name,
        dd.name AS division_name,
        dpt.name AS department_name,
        dct.name AS directorate_name,
        dg.name AS grade_name,
        tms."SEA" AS sea,
        tms."CEX" AS cex,
        tms."QDD" AS qdd, 
        tms."iq" AS iq,
        tms."Papi_G" AS papi_g,
        tms."Papi_T" AS papi_t
    FROM talent_match_scores tms
    LEFT JOIN dim_positions dp ON tms.position_id = dp.position_id
    LEFT JOIN dim_divisions dd ON tms.division_id = dd.division_id
    LEFT JOIN dim_departments dpt ON tms.department_id = dpt.department_id
    LEFT JOIN dim_directorates dct ON tms.directorate_id = dct.directorate_id
    LEFT JOIN dim_grades dg ON tms.grade_id = dg.grade_id
),

/*
CTE 2: BenchmarkBaselines
Purpose: Calculate median scores for the benchmark group
*/
BenchmarkBaselines AS (
    SELECT
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY sea) AS median_sea,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY cex) AS median_cex,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY qdd) AS median_qdd,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY iq) AS median_iq,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY papi_g) AS median_papi_g,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY papi_t) AS median_papi_t
    FROM EmployeeScores
    WHERE employee_id = ANY(p_benchmark_ids)
),

/*
CTE 3: TV_Match_Rate
Purpose: Calculate how closely each employee matches the benchmark medians
*/
TV_Match_Rate AS (
    SELECT
        es.employee_id,
        es.fullname,
        es.position_name,
        es.division_name,
        es.department_name,
        es.directorate_name,
        es.grade_name,
        LEAST(es.sea / NULLIF(bb.median_sea, 0), 1.0) * 100.0 AS sea_match_rate,
        LEAST(es.cex / NULLIF(bb.median_cex, 0), 1.0) * 100.0 AS cex_match_rate,
        LEAST(es.qdd / NULLIF(bb.median_qdd, 0), 1.0) * 100.0 AS qdd_match_rate,
        LEAST(es.iq / NULLIF(bb.median_iq, 0), 1.0) * 100.0 AS iq_match_rate,
        LEAST((2.0 * bb.median_papi_g - es.papi_g) / NULLIF(bb.median_papi_g, 0), 1.0) * 100.0 AS papi_g_match_rate, 
        LEAST((2.0 * bb.median_papi_t - es.papi_t) / NULLIF(bb.median_papi_t, 0), 1.0) * 100.0 AS papi_t_match_rate
    FROM EmployeeScores es
    INNER JOIN BenchmarkBaselines bb ON true
),

/*
CTE 4: ConfigWeights
Purpose: Extract and convert weights from the configuration array
- Explicitly converts weight values to NUMERIC type
- Provides a clean interface for weight lookup
*/
ConfigWeights AS (
    SELECT 
        tv_name,
        weight_val::NUMERIC AS weight_numeric  -- Convert to numeric for calculations
    FROM UNNEST(p_tgv_config) AS c(tv_name, weight_val)
),

/*
CTE 5: Weighted_Final_Score
Purpose: Calculate the final weighted score without CROSS JOIN
- Uses subqueries to lookup numeric weights from ConfigWeights
- Handles missing weights by returning 0
*/
Weighted_Final_Score AS (
    SELECT
        tvr.employee_id,
        tvr.fullname,
        tvr.position_name,
        tvr.division_name,
        tvr.department_name,
        tvr.directorate_name,
        tvr.grade_name,
        -- Calculate final score by summing weighted match rates
        -- Each subquery looks up the numeric weight for the specific test
        (
            COALESCE((SELECT cw.weight_numeric FROM ConfigWeights cw WHERE cw.tv_name = 'SEA'), 0) * tvr.sea_match_rate +
            COALESCE((SELECT cw.weight_numeric FROM ConfigWeights cw WHERE cw.tv_name = 'CEX'), 0) * tvr.cex_match_rate +
            COALESCE((SELECT cw.weight_numeric FROM ConfigWeights cw WHERE cw.tv_name = 'QDD'), 0) * tvr.qdd_match_rate +
            COALESCE((SELECT cw.weight_numeric FROM ConfigWeights cw WHERE cw.tv_name = 'iq'), 0) * tvr.iq_match_rate +
            COALESCE((SELECT cw.weight_numeric FROM ConfigWeights cw WHERE cw.tv_name = 'Papi_G'), 0) * tvr.papi_g_match_rate +
            COALESCE((SELECT cw.weight_numeric FROM ConfigWeights cw WHERE cw.tv_name = 'Papi_T'), 0) * tvr.papi_t_match_rate
        ) AS final_score_raw,
        tvr.sea_match_rate,
        tvr.cex_match_rate,
        tvr.qdd_match_rate,
        tvr.iq_match_rate,
        tvr.papi_g_match_rate,
        tvr.papi_t_match_rate
    FROM TV_Match_Rate tvr
)

/*
Final SELECT: Format and present results
*/
SELECT
    wfs.employee_id,
    wfs.fullname,
    wfs.position_name,
    wfs.division_name,
    wfs.department_name,
    wfs.directorate_name,
    wfs.grade_name,
    ROUND(wfs.final_score_raw::NUMERIC, 2) AS final_match_rate,
    RANK() OVER (ORDER BY wfs.final_score_raw DESC) AS match_rank,
    ROUND(wfs.sea_match_rate::NUMERIC, 2) AS sea_match_rate,
    ROUND(wfs.cex_match_rate::NUMERIC, 2) AS cex_match_rate,
    ROUND(wfs.qdd_match_rate::NUMERIC, 2) AS qdd_match_rate,
    ROUND(wfs.iq_match_rate::NUMERIC, 2) AS iq_match_rate,
    ROUND(wfs.papi_g_match_rate::NUMERIC, 2) AS papi_g_match_rate,
    ROUND(wfs.papi_t_match_rate::NUMERIC, 2) AS papi_t_match_rate
FROM Weighted_Final_Score wfs
ORDER BY match_rank;

$$;
