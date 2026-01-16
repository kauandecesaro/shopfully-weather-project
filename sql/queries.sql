-- =========================================================
-- 1. Numero di condizioni meteo distinte in un periodo
-- (es. rain / snow / clear / clouds)
-- =========================================================
SELECT
    COUNT(DISTINCT wc.main) AS condizioni_distinte
FROM fact_weather_hourly f
JOIN dim_weather_condition wc
    ON f.weather_condition_id = wc.weather_condition_id
WHERE f.observation_timestamp BETWEEN :start_date AND :end_date;


-- =========================================================
-- 2. Ranking delle condizioni meteo più comuni per città
-- =========================================================
SELECT
    c.city_name,
    wc.main AS condizione_meteo,
    COUNT(*) AS occorrenze
FROM fact_weather_hourly f
JOIN dim_city c
    ON f.city_id = c.city_id
JOIN dim_weather_condition wc
    ON f.weather_condition_id = wc.weather_condition_id
WHERE f.observation_timestamp BETWEEN :start_date AND :end_date
GROUP BY c.city_name, wc.main
ORDER BY c.city_name, occorrenze DESC;


-- =========================================================
-- 3. Temperatura media osservata per città in un periodo
-- =========================================================
SELECT
    c.city_name,
    AVG(f.temperature) AS temperatura_media
FROM fact_weather_hourly f
JOIN dim_city c
    ON f.city_id = c.city_id
WHERE f.observation_timestamp BETWEEN :start_date AND :end_date
GROUP BY c.city_name;


-- =========================================================
-- 4. Città con la temperatura massima assoluta nel periodo
-- =========================================================
SELECT
    c.city_name,
    MAX(f.temp_max) AS temperatura_massima
FROM fact_weather_hourly f
JOIN dim_city c
    ON f.city_id = c.city_id
WHERE f.observation_timestamp BETWEEN :start_date AND :end_date
GROUP BY c.city_name
ORDER BY temperatura_massima DESC
LIMIT 1;


-- =========================================================
-- 5. Città con la maggiore variazione giornaliera
-- di temperatura nel periodo
-- =========================================================
SELECT
    c.city_name,
    DATE(f.observation_timestamp) AS giorno,
    MAX(f.temp_max) - MIN(f.temp_min) AS variazione_giornaliera
FROM fact_weather_hourly f
JOIN dim_city c
    ON f.city_id = c.city_id
WHERE f.observation_timestamp BETWEEN :start_date AND :end_date
GROUP BY c.city_name, giorno
ORDER BY variazione_giornaliera DESC
LIMIT 1;


-- =========================================================
-- 6. Città con il vento più forte nel periodo
-- =========================================================
SELECT
    c.city_name,
    MAX(f.wind_speed) AS velocita_vento_massima
FROM fact_weather_hourly f
JOIN dim_city c
    ON f.city_id = c.city_id
WHERE f.observation_timestamp BETWEEN :start_date AND :end_date
GROUP BY c.city_name
ORDER BY velocita_vento_massima DESC
LIMIT 1;
