import bs4 as bs
import numpy as np
import os
import pandas as pd
import pickle
import requests
import urllib
import sqlite3
import re
import time


directory = "MovieBot/dataset"

pd_df = pd.DataFrame()
ds_store_file_location = 'MovieBot/dataset/.DS_store'
if os.path.isfile(ds_store_file_location):
    os.remove(ds_store_file_location)
for i in range(len(os.listdir(directory))):
    df_tmp = pd.read_excel(os.path.join(directory, "movies_data_set_{}.xlsx".format(i+1)), engine='openpyxl', index_col=0)
    pd_df = pd_df.append(df_tmp, ignore_index = True)
pd_df = pd_df.rename(columns={"director":"directors", "genre":"genres", "name_rus":"movie_name_rus", "name_eng":"movie_name_eng", "year":"movie_year", "duration":"movie_duration", "imdb_rating":"movie_rating", "description":"movie_description_eng"})
#pd_df = pd.read_excel(os.path.join(directory, "movies_data_set_all.xlsx"), engine='openpyxl', index_col=0)
pd_df.dropna(axis=0,inplace=True)
#print(pd_df)


actors_distinct = set()
# for actors in pd_df["actors"]:
#     try:
#         # if index==3:
#         #     print(row["movie_name_rus"],row["movie_name_eng"],row["movie_year"],row["movie_rating"],row["movie_duration"],row["movie_description_eng"])
#         for actor in actors.split(','):
#             actors_distinct.add(actor.strip(' \n').strip('"'))
#     except:
#         continue

#print(pd_df[["movie_name_rus","movie_name_eng"]])

# movies_final = []
# for index,row in pd_df.iterrows():
#     #print([index+1,row["movie_name_rus"],row["movie_name_eng"],row["movie_year"],row["movie_rating"],row["movie_duration"],row["movie_description_eng"]])
#     movies_final.append([index+1,str(row["movie_name_rus"]).strip("'"),str(row["movie_name_eng"]).strip("'"),row["movie_year"][1:-1],row["movie_rating"],row["movie_duration"],str(row["movie_description_eng"]).strip("'").strip("\n")])

#print(movies_final)    

# actors_final = []
# for count,actor in enumerate(actors_distinct):
#     actors_final.append([count+1,actor])
    # if actor.split()[-1] in ["JR", "JR.", "Jr.", "Jr", "jr.", "jr", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "XI", "X"]:
    #     actors_final.append([count+1,' '.join(actor.split()[0:-2]), ' '.join(actor.split()[-2:])])
    # else:
    #     actors_final.append([count+1,' '.join(actor.split()[0:-1]), actor.split()[-1]])

conn = sqlite3.connect("/Users/alish/Documents/Telegram/MovieBot/db/imdb.db")
cursor = conn.cursor()
#cursor.executemany("INSERT INTO genres VALUES (?, ?)", actors_final)
#cursor.executemany("INSERT INTO movies(movie_id,movie_name_rus,movie_name_eng,movie_year,movie_rating,movie_duration,movie_description_eng) VALUES (?,?,?,?,?,?,?)", movies_final)
actors_movies_final = []
cursor.execute("SELECT * FROM actors")
actors = cursor.fetchall()
for row_actor in actors:
    #print(row_actor)
    actor_name = row_actor[1]+' '+row_actor[2]
    actor_id = row_actor[0]
    for index,row in pd_df.iterrows():
        if actor_name in row["actors"]:
            try:
                #print(row["movie_name_eng"],row["movie_year"])
                cursor.execute('SELECT movie_id FROM movies WHERE movie_name_eng = "{}" and movie_year = {}'.format(row["movie_name_eng"],row["movie_year"][1:-1]))
                movie_id = cursor.fetchone()[0]
                actors_movies_final.append([movie_id,actor_id])
                #print([movie_id,actor_id])
            except Exception as e:
                print(index,row["movie_name_eng"],row["movie_year"][1:-1])
                print(e)
                continue
        else:
            continue
print(actors_movies_final)
cursor.executemany("INSERT INTO Roles VALUES (?, ?)", actors_movies_final)

for row in cursor.execute("SELECT * FROM roles where movie_id<100"):
    print(row)




#print(actors_distinct)

