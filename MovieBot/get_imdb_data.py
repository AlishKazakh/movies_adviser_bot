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
import db

# resp_rus = requests.get("https://freeproxylists.net/ru/?c=US&pt=&pr=HTTPS&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=0")
# soup_rus = bs.BeautifulSoup(resp_rus.text, features="html.parser")
# table_rus = soup_rus.find('table', {'class': 'DataGrid'})
# print(soup_rus)


def has_cyrillic(text):
    return bool(re.search('[а-яА-Я]', text))


def get_imdb_data(table_rus):  ###### это функция, которая сохраняет коды(названия) компаний
    #proxies = urllib.ProxyHandler({'http':'http://159.203.61.169'}) , proxies={"https":"//91.195.156.241:3128"}
    

    tickers = []
    for row in table_rus.findAll('div', {'class': 'lister-item-content'}):
        #dict_tmp = {}
        #dict_tmp[row.find('a').text] = row.find('p', {'class': ''}).text
        ticker = row.find_all('p', {'class': 'text-muted text-small'})[1].text
        tickers.append(ticker)

    # connect = sqlite3.connect('imdb.db')
    # cursor = connect.cursor()
    # cursor.execute(""" CREATE TABLE IF NOT EXISTS actors(
    #     actor_id INTEGER,
    #     actor_movie_id INTEGER,
    #     actor_name TEXT,
    #     actor_surname TEXT,
    #     actor_movie TEXT
    # )
    # """)
    # connect.commit()
    print(tickers)


def get_movie_name(table_rus,table_eng):
    movies_name_dict = {}
    movies_name_list_rus = []
    for count,row in enumerate(table_rus.findAll('div', {'class': 'lister-item-content'})):
        #dict_tmp = {}
        movie_name = row.find('a').text
        if has_cyrillic(movie_name):
            # dict_tmp[count] = movie_name
            movies_name_list_rus.append(movie_name)
            print("inserted from imdb {}. {}".format(count, movie_name))
        else:
            try:
                resp_tmp = requests.get("https://www.kinopoisk.ru/index.php?kp_query={}".format(movie_name))
                soup_tmp = bs.BeautifulSoup(resp_tmp.text, features="html.parser")
                table_tmp = soup_tmp.find('div', {'class': 'element most_wanted'})
                movie_rus_eng = table_tmp.find('p', {'class': 'name'}).find('a').text + ' ' + table_tmp.find('p', {'class': 'name'}).find('span', {'class': 'year'}).text
                # dict_tmp[count] = movie_rus_eng
                print(movie_name,movie_rus_eng)
                movies_name_list_rus.append(movie_rus_eng)
            except:
                print("Could not find in kinopoisk {}. {}".format(count,movie_name))
                # dict_tmp[count] = "NULL"
                movies_name_list_rus.append("NULL")

    movies_name_list_eng = []
    for count,row in enumerate(table_eng.findAll('div', {'class': 'lister-item-content'})):
        movie_name = row.find('a').text
        movies_name_list_eng.append(movie_name)    
    # print(len(movies_name_list_rus))
    # print(len(movies_name_list_eng))
    movies_name_dict["name_rus"] = movies_name_list_rus
    movies_name_dict["name_eng"] = movies_name_list_eng
    return movies_name_dict


def get_other_info(table_rus):
    info_dict = {}
    duration_list = []
    genre_list = []
    imdb_rating_list = []
    year_list = []
    for row in table_rus.findAll('div', {'class': 'lister-item-content'}):
        year = row.find('span', {'class': 'lister-item-year text-muted unbold'}).text
        year_list.append(year)
        duration = row.find('span', {'class': 'runtime'}).text.strip(' min')   
        duration_list.append(duration)
        genre = row.find('span', {'class': 'genre'}).text.strip('\n').strip(' ') 
        genre_list.append(genre)
        imdb_rating = row.find('span', {'class': 'ipl-rating-star__rating'}).text   
        imdb_rating_list.append(imdb_rating) 
    # print(len(year_list))
    # print(len(duration_list))
    # print(len(genre_list))
    # print(len(imdb_rating_list))
    info_dict["year"] = year_list
    info_dict["duration"] = duration_list
    info_dict["genre"] = genre_list
    info_dict["imdb_rating"] = imdb_rating_list

    values = [tuple(info_dict.values())]
    print(values)
    return info_dict


def get_actor_director_name(table_rus):
    info_dict = {}
    actors_list = []
    directors_list = []
    for row in table_rus.findAll('div', {'class': 'lister-item-content'}):
        # director_tmp = []
        # actors_tmp = []
        actors_directors = row.findAll('p', {'class': 'text-muted text-small'})[1].text
        actors = actors_directors.split('Stars:')[1].strip('\n').strip(' ')
        # actors_tmp.append(actors)
        #print(actors_directors.split('Director')[1])
        try:
            if actors_directors.split('Director')[1].split('|')[0][:2] == 's:':
                director = actors_directors.split('Directors:')[1].split('|')[0].strip('\n').strip(' ')
                # director_tmp.append(director)
            else:
                director = actors_directors.split('Director:')[1].split('|')[0].strip('\n').strip(' ')
        except:
            director = "NULL"
            # director_tmp.append(director)
        
        actors_list.append(actors)
        directors_list.append(director)

    # print(len(actors_list))
    # print(len(directors_list))
    info_dict["actors"] = actors_list
    info_dict["director"] = directors_list

    return info_dict


def get_description(table_rus):
    info_dict = {}
    desc_list = []
    for row in table_rus.findAll('div', {'class': 'lister-item-content'}):
        try:
            desc = row.find_all('p')[1].text
            movie_id = row.find_all('a', href = True)[0]['href']
            if 'See full summary' in desc:
                resp = requests.get("https://www.imdb.com{}plotsummary?ref_=ttls_pl".format(movie_id))
                soup = bs.BeautifulSoup(resp.text, features="html.parser")
                soup_ul = soup.find('ul', {'class': 'ipl-zebra-list'})
                summary = soup_ul.find('p').text
                desc_list.append(summary)
            else:
                desc_list.append(desc)
        except:
            desc_list.append("NULL")

    # print(len(desc_list))
    info_dict["description"] = desc_list

    return info_dict


def get_data_together():
    #main_df = pd.DataFrame()
    #rus_proxies = {"//188.166.162.1:3128","//195.34.241.124:8080","//188.187.4.113:1256","//178.62.223.151:8080","//79.143.87.138:9090","//94.228.192.197:8087","//109.167.134.253:30710","//31.184.201.40:8080","//89.20.48.118:8080","//91.224.182.49:8080"}
    #us_proxies = ["//140.227.8.56:58888","//154.64.211.145:999","//206.62.161.4:999","//140.227.68.230:58888","//140.227.65.159:6000","//140.227.32.79:6000","//35.239.150.193:8080","//140.227.28.39:6000","//96.9.72.180:46487","//140.227.65.129:58888"]
    
    resp_rus = requests.get("https://www.imdb.com/list/ls005750764/?sort=list_order,asc&st_dt=&mode=detail&page=16", proxies={"https":"//94.181.48.181:1256"})
    soup_rus = bs.BeautifulSoup(resp_rus.text, features="html.parser")
    table_rus = soup_rus.find('div', {'class': 'lister-list'})

    print("Connected to rus proxy")

    resp_eng = requests.get("https://www.imdb.com/list/ls005750764/?sort=list_order,asc&st_dt=&mode=detail&page=16", proxies={"https":"//20.81.62.32:3128"})
    soup_eng = bs.BeautifulSoup(resp_eng.text, features="html.parser")
    table_eng = soup_eng.find('div', {'class': 'lister-list'})

    print("Connected to us proxy")

    final_dict = {}
    final_dict.update(get_movie_name(table_rus,table_eng))
    final_dict.update(get_other_info(table_rus))
    final_dict.update(get_actor_director_name(table_rus))
    final_dict.update(get_description(table_rus))
    pd_df = pd.DataFrame(final_dict)
    #main_df.append(pd_df, ignore_index = True)
    pd_df.to_excel("movies_data_set_16.xlsx")


def get_eng_name():
    resp_eng = requests.get("https://www.imdb.com/list/ls005750764/?sort=list_order,asc&st_dt=&mode=detail&page=16", proxies={"https":"//128.199.20.88:8080"})
    soup_eng = bs.BeautifulSoup(resp_eng.text, features="html.parser")
    table_eng = soup_eng.find('div', {'class': 'lister-list'})

    print("Connected to us proxy")

    movies_name_dict = {}
    movies_name_list_eng = []
    for count,row in enumerate(table_eng.findAll('div', {'class': 'lister-item-content'})):
        movie_name = row.find('a').text
        movies_name_list_eng.append(movie_name) 
        print(str(count)+'. ',movie_name)
    movies_name_dict["name_eng"] = movies_name_list_eng
    pd_df = pd.DataFrame(movies_name_dict)
    pd_df.to_excel("movies_eng_16.xlsx")


def get_movie_images():
    for i in range(16):
        resp_eng = requests.get("https://www.imdb.com/list/ls005750764/?sort=list_order,asc&st_dt=&mode=detail&page={}".format(i+1))
        soup_eng = bs.BeautifulSoup(resp_eng.text, features="html.parser")
        table_eng = soup_eng.find('div', {'class': 'lister-list'})
        for count,movie in enumerate(table_eng.find_all('div', {'class': 'lister-item-image ribbonize'})):
            print(str(i*100+count+1)+'. '+movie.find('img')['loadlate'])
            urllib.request.urlretrieve(movie.find('img')['loadlate'],str(i*100+count+1)+".jpg")

            # time.sleep(5)

    #print(table_eng.find('img')['loadlate'])



