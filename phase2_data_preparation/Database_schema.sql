-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.dim_areas (
  area_id bigint NOT NULL,
  name text,
  CONSTRAINT dim_areas_pkey PRIMARY KEY (area_id)
);
CREATE TABLE public.dim_companies (
  company_id bigint NOT NULL,
  name text,
  CONSTRAINT dim_companies_pkey PRIMARY KEY (company_id)
);
CREATE TABLE public.dim_departments (
  department_id bigint NOT NULL,
  name text,
  CONSTRAINT dim_departments_pkey PRIMARY KEY (department_id)
);
CREATE TABLE public.dim_directorates (
  directorate_id bigint NOT NULL,
  name text,
  CONSTRAINT dim_directorates_pkey PRIMARY KEY (directorate_id)
);
CREATE TABLE public.dim_divisions (
  division_id bigint NOT NULL,
  name text,
  CONSTRAINT dim_divisions_pkey PRIMARY KEY (division_id)
);
CREATE TABLE public.dim_education (
  education_id bigint NOT NULL,
  name text,
  CONSTRAINT dim_education_pkey PRIMARY KEY (education_id)
);
CREATE TABLE public.dim_grades (
  grade_id bigint NOT NULL,
  name text,
  CONSTRAINT dim_grades_pkey PRIMARY KEY (grade_id)
);
CREATE TABLE public.dim_majors (
  major_id bigint NOT NULL,
  name text,
  CONSTRAINT dim_majors_pkey PRIMARY KEY (major_id)
);
CREATE TABLE public.dim_positions (
  position_id bigint NOT NULL,
  name text,
  CONSTRAINT dim_positions_pkey PRIMARY KEY (position_id)
);
CREATE TABLE public.talent_match_scores (
  employee_id text NOT NULL,
  fullname text,
  rating numeric,
  years_of_service_months numeric,
  job_level text,
  SEA numeric,
  CEX numeric,
  QDD numeric,
  iq numeric,
  Papi_G numeric,
  Papi_T numeric,
  position_id bigint,
  division_id bigint,
  department_id bigint,
  directorate_id bigint,
  grade_id bigint,
  company_id bigint,
  education_id bigint,
  major_id bigint,
  area_id bigint,
  CONSTRAINT talent_match_scores_pkey PRIMARY KEY (employee_id),
  CONSTRAINT talent_match_scores_position_id_fkey FOREIGN KEY (position_id) REFERENCES public.dim_positions(position_id),
  CONSTRAINT talent_match_scores_division_id_fkey FOREIGN KEY (division_id) REFERENCES public.dim_divisions(division_id),
  CONSTRAINT talent_match_scores_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.dim_departments(department_id),
  CONSTRAINT talent_match_scores_directorate_id_fkey FOREIGN KEY (directorate_id) REFERENCES public.dim_directorates(directorate_id),
  CONSTRAINT talent_match_scores_grade_id_fkey FOREIGN KEY (grade_id) REFERENCES public.dim_grades(grade_id),
  CONSTRAINT talent_match_scores_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.dim_companies(company_id),
  CONSTRAINT talent_match_scores_education_id_fkey FOREIGN KEY (education_id) REFERENCES public.dim_education(education_id),
  CONSTRAINT talent_match_scores_major_id_fkey FOREIGN KEY (major_id) REFERENCES public.dim_majors(major_id),
  CONSTRAINT talent_match_scores_area_id_fkey FOREIGN KEY (area_id) REFERENCES public.dim_areas(area_id)
);