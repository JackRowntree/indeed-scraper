
-- SELECT pid FROM pg_locks l JOIN pg_class t ON l.relation = t.oid AND t.relkind = 'r'WHERE t.relname = 'job_listings_scraped';
-- drop table if exists job_listings_totals;
drop table if exists job_listings_full;
-- CREATE TABLE job_listings_totals (
-- 	--make this row per domain instead
-- 	date_scraped date,
-- 	website varchar(100),
-- 	country varchar(100),
-- 	company_id varchar,
-- 	company_name varchar(100),
-- 	search_term varchar(100),
-- 	is_wagestream boolean,
-- 	total integer,
-- 	CONSTRAINT site_job UNIQUE(date_scraped,website,country,company_id,company_name,search_term,is_wagestream)
-- );

CREATE TABLE job_listings_full (
	jobid varchar(100),
	date_scraped date,
	website varchar(100),
	country varchar(100),
	company_id varchar(100),
	company_name varchar(100),
	search_term varchar(100),
	jobtitle varchar(100),
	is_wagestream boolean,
	properties jsonb,
	CONSTRAINT site_job2 UNIQUE(date_scraped,jobid,website)
);

grant all privileges on table job_listings_full to jackrowntreepg;
-- grant all privileges on table job_listings_totals to jackrowntreepg;