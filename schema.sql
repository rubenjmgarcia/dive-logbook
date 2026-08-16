-- Create tables
CREATE TABLE "logs" (
    "id" INTEGER,
    "user_id" INTEGER NOT NULL,
    "number" INTEGER NOT NULL,
    "datetime" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "divesite_id" INTEGER NOT NULL,
    "dive_time" INTEGER NOT NULL CHECK("dive_time" BETWEEN 1 AND 180),
    "max_depth" REAL NOT NULL CHECK("max_depth" > 0 AND "max_depth" < 200),
    "av_depth" REAL CHECK("av_depth" IS NULL OR ("av_depth" > 0 AND "av_depth" < "max_depth")),
    "start_pressure" INTEGER CHECK("start_pressure" > 0 AND "start_pressure" <= 232),
    "end_pressure" INTEGER CHECK("start_pressure" IS NULL OR "end_pressure" IS NULL OR "start_pressure" >= "end_pressure" AND "end_pressure" > 0),
    "volume" REAL DEFAULT 12 CHECK("volume" BETWEEN 1 AND 15),
    "sac" REAL,
    "water_temp" INTEGER CHECK("water_temp" BETWEEN -2 AND 40),
    "visibility" INTEGER CHECK("visibility" >= 0),
    "notes" TEXT,
    PRIMARY KEY("id"),
    FOREIGN KEY("divesite_id") REFERENCES "divesites"("id"),
    FOREIGN KEY("user_id") REFERENCES "users"("id") ON DELETE CASCADE,
    UNIQUE("user_id", "number")
);

CREATE TABLE "users" (
    "id" INTEGER,
    "name" TEXT NOT NULL,
    "username" TEXT NOT NULL UNIQUE,
    "hash" TEXT NOT NULL,
    PRIMARY KEY("id")
);

CREATE TABLE "divesites" (
    "id" INTEGER,
    "divesite" TEXT NOT NULL UNIQUE,
    PRIMARY KEY("id")
);

-- Create Views
CREATE VIEW "logbook" AS
SELECT "logs"."id" as "id",
       "user_id",
       "number",
       "datetime",
       "divesite_id",
       "divesite",
       "dive_time",
       "max_depth",
       "av_depth",
       "start_pressure",
       "end_pressure",
       "volume",
       "sac",
       "water_temp",
       "visibility",
       "notes"
FROM "logs"
JOIN "divesites" ON "divesites"."id" = "logs"."divesite_id"
ORDER BY "number" DESC;

CREATE VIEW "stats" AS
SELECT "user_id",
       MAX("number") AS "total_dives",
       COUNT(DISTINCT "divesite_id") AS "dive_sites_visited",
       MAX("max_depth") AS "max_depth",
       ROUND(AVG("max_depth"), 1) AS "average_depth",
       MAX("dive_time") AS "max_dive_time",
       ROUND(AVG("dive_time"), 1) AS "average_time",
       SUM("dive_time") AS "total_dive_time",
       ROUND(AVG("sac"), 2) AS "average_sac"
FROM "logs"
GROUP BY "user_id";

-- Create Indexes
CREATE INDEX idx_logs_datetime
ON "logs"("datetime");

CREATE INDEX idx_logs_divesite
ON "logs"("divesite_id");

CREATE UNIQUE INDEX unique_divesite_name -- Assure Unique Names for Dive Sites (Dori Wreck / Dori wreck)
ON divesites(LOWER(divesite));
