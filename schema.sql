-- =========================================
-- PhilGEPS dimension tables
-- (created first since philgeps will reference these)
-- =========================================

CREATE TABLE awardees (
    id UUID PRIMARY KEY,
    awardee_name TEXT UNIQUE,
    count INTEGER,
    total NUMERIC(18, 2),
    start_date DATE,
    end_date DATE
);

CREATE TABLE organizations (
    id UUID PRIMARY KEY,
    organization_name TEXT UNIQUE,
    count INTEGER,
    total NUMERIC(18, 2),
    start_date DATE,
    end_date DATE
);

CREATE TABLE area_of_deliveries (
    id UUID PRIMARY KEY,
    area_of_delivery TEXT UNIQUE,
    count INTEGER,
    total NUMERIC(18, 2),
    start_date DATE,
    end_date DATE
);

CREATE TABLE business_categories (
    id UUID PRIMARY KEY,
    business_category TEXT UNIQUE,
    count INTEGER,
    total NUMERIC(18, 2),
    start_date DATE,
    end_date DATE
);

-- =========================================
-- PhilGEPS fact table
-- =========================================

CREATE TABLE philgeps (
    id UUID PRIMARY KEY,
    reference_id TEXT,
    contract_no TEXT,
    award_title TEXT,
    notice_title TEXT,
    awardee_name TEXT REFERENCES awardees(awardee_name),
    organization_name TEXT REFERENCES organizations(organization_name),
    area_of_delivery TEXT REFERENCES area_of_deliveries(area_of_delivery),
    business_category TEXT REFERENCES business_categories(business_category),
    contract_amount numeric(18, 2),
    award_date DATE,
    award_status TEXT
);

-- =========================================
-- DPWH TRANSPARENCY
-- =========================================

CREATE TABLE dpwh_transparency_data (
    contract_id TEXT PRIMARY KEY,
    description TEXT,
    category TEXT,
    status TEXT,
    budget numeric(18, 2),
    amount_paid numeric(18, 2),
    progress NUMERIC(5, 2),
    contractor TEXT,
    start_date DATE,
    completion_date DATE,
    infra_year INTEGER,
    program_name TEXT,
    source_of_funds TEXT,
    is_live BOOLEAN,
    livestream_url TEXT,
    livestream_video_id TEXT,
    livestream_detected_at TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    report_count INTEGER,
    has_satellite_image BOOLEAN,
    province TEXT,
    region TEXT
);

CREATE TABLE component_category_table (
    contract_id TEXT,
    component_category TEXT,
    PRIMARY KEY (contract_id, component_category),
    CONSTRAINT fk_component_category
        FOREIGN KEY (contract_id) REFERENCES dpwh_transparency_data(contract_id)
);

-- =========================================
-- Flood control
-- =========================================

CREATE TABLE flood_control (
    global_id UUID PRIMARY KEY,
    object_id TEXT,
    infra_year INTEGER,
    region TEXT,
    province TEXT,
    municipality TEXT,
    implementing_office TEXT,
    project_id TEXT,
    project_description TEXT,
    project_component_id TEXT,
    project_component_description TEXT,
    program TEXT,
    type_of_work TEXT,
    infra_type TEXT,
    longitude DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    contract_id TEXT,
    abc numeric(18, 2),
    contract_cost numeric(18, 2),
    completion_date_original DATE,
    completion_year INTEGER,
    contractor TEXT,
    creation_date TIMESTAMP,
    creator TEXT,
    edit_date TIMESTAMP,
    editor TEXT,
    funding_year INTEGER,
    legislative_district TEXT,
    district_engineering_office TEXT,
    completion_date_actual DATE,
    start_date DATE,
    CONSTRAINT fk_flood_control
        FOREIGN KEY (contract_id) REFERENCES dpwh_transparency_data(contract_id)
);