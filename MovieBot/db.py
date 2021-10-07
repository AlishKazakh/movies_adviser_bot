import os
from typing import Dict, List, Tuple
import sqlite3
import pandas as pd

directory = "/dataset"
pd_df = pd.DataFrame()
ds_store_file_location = '/dataset/.DS_store'
if os.path.isfile(ds_store_file_location):
    os.remove(ds_store_file_location)
for i in range(len(os.listdir(directory))):
    df_tmp = pd.read_excel("/dataset/movies_data_set_{}.xlsx".format(i+1), engine='openpyxl', index_col=0)
    pd_df = pd_df.append(df_tmp, ignore_index = True)
pd_df = pd_df.rename(columns={"director":"directors", "genre":"genres", "name_rus":"movie_name_rus", "name_eng":"movie_name_eng", "year":"movie_year", "duration":"movie_duration", "imdb_rating":"movie_rating", "description":"movie_description_eng"})
#pd_df = pd.read_excel(os.path.join(directory, "movies_data_set_all.xlsx"), engine='openpyxl', index_col=0)
pd_df.dropna(axis=0,how='all',inplace=True)


conn = sqlite3.connect("/db/imdb.db", check_same_thread=False)
cursor = conn.cursor()

def insert_act_dir(table):
    act_dir_distinct = set()
    for actors in pd_df[table]:
        try:
            for actor in actors.split(','):
                act_dir_distinct.add(actor.strip(' \n'))
        except:
            continue

    actors_final = []
    for count,actor in enumerate(act_dir_distinct):
        if actor.split()[-1] in ["JR", "JR.", "Jr.", "Jr", "jr.", "jr", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "XI", "X"]:
            actors_final.append([count+1,' '.join(actor.split()[0:-2]), ' '.join(actor.split()[-2:])])
        else:
            actors_final.append([count+1,' '.join(actor.split()[0:-1]), actor.split()[-1]])

    cursor.executemany("INSERT OR REPLACE INTO {} VALUES (?, ?, ?)".format(table), actors_final)
    
def insert_genres():
    genres_distinct = set()
    for count,genres in enumerate(pd_df["genres"]):
        try:
            for genre in genres.split(','):
                genres_distinct.add(genre.strip(' \n').strip('"'))
        except:
            continue

    genre_final = []
    for count,genre in enumerate(genres_distinct):
        genre_final.append([count+1,genre])
    cursor.executemany("INSERT OR REPLACE INTO genres VALUES (?, ?)", genre_final)

def insert_movies():
    movies_final = []
    count = 1
    for index,row in pd_df.iterrows():
        movies_final.append([count,str(row["movie_name_rus"]).strip("'"),str(row["movie_name_eng"]).strip("'"),row["movie_year"][1:-1],row["movie_rating"],row["movie_duration"],str(row["movie_description_eng"]).strip("'").strip("\n"), str(count)])
        count += 1
    cursor.executemany("INSERT OR REPLACE INTO movies(movie_id,movie_name_rus,movie_name_eng,movie_year,movie_rating,movie_duration,movie_description_eng,movie_poster) VALUES (?,?,?,?,?,?,?,?)", movies_final)


def insert_movie_actor_director(table):
    actors_movies_final = []
    cursor.execute("SELECT * FROM {}".format(table))
    actors = cursor.fetchall()
    for row_actor in actors:
        actor_name = row_actor[1]+' '+row_actor[2]
        actor_id = row_actor[0]
        for index,row in pd_df.iterrows():
            try:
                if actor_name in row[table]:
                    cursor.execute('SELECT movie_id FROM movies WHERE movie_name_eng = "{}" and movie_year = {}'.format(row["movie_name_eng"],row["movie_year"][1:-1]))
                    movie_id = cursor.fetchone()[0]
                    actors_movies_final.append([movie_id,actor_id])
                else:
                    continue
            except Exception as e:
                print(e)
                continue
            
    if table == "actors":
        cursor.executemany("INSERT INTO Movie_Actor VALUES (?, ?)", actors_movies_final)
    else:
        cursor.executemany("INSERT INTO Movie_Director VALUES (?, ?)", actors_movies_final)


def insert_movie_genre():
    actors_movies_final = []
    cursor.execute("SELECT * FROM genres")
    actors = cursor.fetchall()
    for row_actor in actors:
        genre_name = row_actor[1]
        genre_id = row_actor[0]
        for index,row in pd_df.iterrows():
            try:
                if genre_name in row["genres"]:
                    cursor.execute('SELECT movie_id FROM movies WHERE movie_name_eng = "{}" and movie_year = {}'.format(row["movie_name_eng"],row["movie_year"][1:-1]))
                    movie_id = cursor.fetchone()[0]
                    actors_movies_final.append([movie_id,genre_id])
                else:
                    continue
            except Exception as e:
                print(e)
                continue
            
    
    cursor.executemany("INSERT INTO Movie_Genre VALUES (?, ?)", actors_movies_final)

def fetchall(table, columns):
    columns_joined = ", ".join(columns)
    cursor.execute(f"SELECT {columns_joined} FROM {table}")
    result = cursor.fetchall()
    return result

def fetch_filtered(table, columns, condition):
    columns_joined = ", ".join(columns)
    cursor.execute(f"SELECT {columns_joined} FROM {table} WHERE {condition}")
    result = cursor.fetchall()
    return result

def get_cursor():
    return cursor

def _init_db():
    """Инициализирует БД"""
    with open("/createdb.sql", "r") as f:
        sql = f.read()
    cursor.executescript(sql)
    insert_act_dir("actors")
    insert_act_dir("directors")
    insert_genres()
    insert_movies()
    insert_movie_actor_director("actors")
    insert_movie_actor_director("directors")
    insert_movie_genre()
    conn.commit()


def check_db_exists():
    """Проверяет, инициализирована ли БД, если нет — инициализирует"""
    cursor.execute("SELECT name FROM sqlite_master "
                   "WHERE type='table' AND name='Movies'")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    _init_db()

check_db_exists()