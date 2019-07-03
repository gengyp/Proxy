-- 一个一个执行
CREATE DATABASE linzi;
CREATE SCHEMA jiake;
-- default database is linzi,default schema is jiake
-- create table.
CREATE TABLE jiake.proxy_ips_games(
  id_ SERIAL PRIMARY KEY,
  content varchar(30) NOT NULL,
  test_times int4 DEFAULT 1 NOT NULL,
  failure_times int4 DEFAULT 0 NOT NULL,
  success_rate float8 DEFAULT 0.0 NOT NULL,
  avg_response_time float8 DEFAULT 1.0 NOT NULL,
  score float8 DEFAULT 2.5 NOT NULL,
  create_time timestamp(6) DEFAULT CURRENT_TIMESTAMP
)WITH (OIDS=FALSE);