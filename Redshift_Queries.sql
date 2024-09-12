Create schema movies;

CREATE TABLE movies.imdb_movies_rating (
    Poster_link VARCHAR(MAX),
    Series_Title VARCHAR(MAX),
    Released_year VARCHAR(10),
    Certificate VARCHAR(50),
    Runtime Varchar(50),
    Genre VARCHAR(200),
    IMDB_Rating DECIMAL(10,2),
    Overview VARCHAR(MAX),
    Meta_score INT,
    Director VARCHAR(200),
    Star1 VARCHAR(200),
    Star2 VARCHAR(200),
    Star3 VARCHAR(200),
    Star4 VARCHAR(200),
    No_of_Votes INT,
    Gross VARCHAR(20)
);

drop table movies.imdb_movies_rating;

select * from movies.imdb_movies_rating limit 5;
select * from stl_load_errors;

CREATE MATERIALIZED VIEW movies.year_aggregated AS
SELECT released_year as year,
        genre,
        count(*) as total_movies
FROM movies.imdb_movies_rating
GROUP BY released_year, genre;


SELECT * FROM movies.year_aggregated;

SELECT count(*) FROM movies.year_aggregated;

REFRESH MATERIALIZED VIEW movies.year_aggregated;
