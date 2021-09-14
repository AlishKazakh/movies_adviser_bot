drop table if exists Actors;
create table Actors(
    actor_id integer primary key AUTOINCREMENT,
    actor_name text,
    actor_surname text
);

drop table if exists Genres;
create table Genres(
    genre_id integer primary key AUTOINCREMENT,
    genre_name text
);

drop table if exists Directors;
create table Directors(
    director_id integer primary key AUTOINCREMENT,
    director_name text,
    director_surname text
);

drop table if exists Movies;
create table Movies(
    movie_id integer primary key AUTOINCREMENT,
    movie_name_rus text,
    movie_name_eng text not null,
    movie_year integer not null,
    movie_rating real,
    movie_duration integer,
    movie_description_rus text,
    movie_description_eng text,
    movie_poster text
);

drop table if exists Movie_Actor;
create table Movie_Actor(
    movie_id integer not null,
    actor_id integer not null,
    FOREIGN KEY(movie_id)
        REFERENCES Movies(movie_id),
    FOREIGN KEY(actor_id)
        REFERENCES Actors(actor_id),
    PRIMARY KEY(movie_id, actor_id)
);

drop table if exists Movie_Genre;
create table Movie_Genre(
    movie_id integer not null,
    genre_id integer not null,
    FOREIGN KEY(movie_id)
        REFERENCES Movies(movie_id),
    FOREIGN KEY(genre_id)
        REFERENCES Genres(genre_id),
    PRIMARY KEY(movie_id, genre_id)
);

drop table if exists Movie_Director;
create table Movie_Director(
    movie_id integer not null,
    director_id integer not null,
    FOREIGN KEY(movie_id)
        REFERENCES Movies(movie_id),
    FOREIGN KEY(director_id)
        REFERENCES Directors(director_id),
    PRIMARY KEY(movie_id, director_id)
);