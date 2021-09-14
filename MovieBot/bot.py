import telebot
import config
from telebot import types
import sqlite3
import pandas as pd
import db
import numpy as np



bot = telebot.TeleBot(config.TOKEN)
select_filter = {}
genres = [a[0] for a in db.fetchall('genres',['genre_name'])]
movie_year = [int(a[0]) for a in db.fetchall('movies',['movie_year'])]
movie_rating = [float(a[0]) for a in db.fetchall('movies',['movie_rating'])]
movie_duration = [int(a[0]) for a in db.fetchall('movies',['movie_duration'])]
actors = [a[0]+' '+a[1] for a in db.fetchall('actors',['actor_name','actor_surname'])]
directors = [a[0]+' '+a[1] for a in db.fetchall('directors',['director_name','director_surname'])]

@bot.message_handler(commands=['start'])
def welcome(message):
    # keyboard 
    markup = types.InlineKeyboardMarkup()
    for row in genres:
        btn1 = types.InlineKeyboardButton(text=str(row),callback_data=str(row))
        markup.add(btn1)
    bot.send_message(message.chat.id, "Здравствуй, {0.first_name}! Я - бот, который определяет мамбича. Кто по-твоему мамбич?".format(message.from_user), parse_mode='html', reply_markup=markup)

@bot.callback_query_handler(func=lambda call:True)
def lalala(call):
    years = np.linspace(min(movie_year),max(movie_year),num=10, dtype=int)
    ratings = np.linspace(min(movie_rating),max(movie_rating),num=10, dtype=float)
    durations = np.linspace(min(movie_duration),max(movie_duration),num=10, dtype=int)
    periods = []
    rating_range = []
    duration_range = []
    for i in range(len(years)):
        try:
            if i == 0:
                periods.append("{}-{}".format(years[i],years[i+1]))
                rating_range.append("{}-{}".format(round(ratings[i],1),round(ratings[i+1],1)))
                duration_range.append("{}-{}".format(durations[i],durations[i+1]))
            else:
                periods.append("{}-{}".format(years[i]+1,years[i+1]))
                rating_range.append("{}-{}".format(round(ratings[i]+0.1,1),round(ratings[i+1],1)))
                duration_range.append("{}-{}".format(durations[i]+1,durations[i+1]))
        except:
            continue
    if call.data in genres:
        select_filter["genre_name"] = call.data
        try:
            if call.message:
                markup = types.InlineKeyboardMarkup()
                for row in periods:
                    btn1 = types.InlineKeyboardButton(text=str(row),callback_data=str(row))
                    markup.add(btn1)
                bot.send_message(call.message.chat.id, "Which year?", parse_mode='html', reply_markup=markup)
        except Exception as e:
            print(e)
    elif call.data in periods:
        select_filter["movie_year"] = call.data
        try:
            if call.message:
                markup = types.InlineKeyboardMarkup()
                for row in duration_range:
                    btn1 = types.InlineKeyboardButton(text=str(row+' min.'),callback_data=str(row))
                    markup.add(btn1)
                bot.send_message(call.message.chat.id, "Duration?", parse_mode='html', reply_markup=markup)
        except Exception as e:
            print(e)
    elif call.data in duration_range:
        select_filter["movie_duration"] = call.data
        try:
            if call.message:
                markup = types.InlineKeyboardMarkup()
                for row in rating_range:
                    btn1 = types.InlineKeyboardButton(text=str(row+' ⭐'),callback_data=str(row))
                    markup.add(btn1)
                bot.send_message(call.message.chat.id, "Rating?", parse_mode='html', reply_markup=markup)
        except Exception as e:
            print(e)
        


    

# RUN
bot.polling(none_stop=True)