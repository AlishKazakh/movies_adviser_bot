import telebot
import config
from telebot import types
import db
import numpy as np
import re



bot = telebot.TeleBot(config.TOKEN)
select_filter = {}
cursor = db.get_cursor()
genres = [a[0] for a in db.fetchall('genres',['genre_name'])]


movies_filtered = []

def define_range(some_list):
    datatype_set = set([type(a) for a in some_list])
    list_linspace = np.linspace(min(some_list),max(some_list),num=5, dtype=list(datatype_set)[0])
    final_range = []
    for i in range(len(list_linspace)):
        try:
            if list(datatype_set)[0] == int:
                if i == 0:
                    final_range.append("{}-{}".format(list_linspace[i],list_linspace[i+1]))
                else:
                    final_range.append("{}-{}".format(list_linspace[i]+1,list_linspace[i+1]))
            elif list(datatype_set)[0] == float:
                    if i == 0:
                        final_range.append("{}-{}".format(round(list_linspace[i],1),round(list_linspace[i+1],1)))
                    else:
                        final_range.append("{}-{}".format(round(list_linspace[i]+0.1,1),round(list_linspace[i+1],1)))
        except:
            continue
    return final_range

def print_final_movies(message, category, movies_filtered = None):
    if category == "genre":
        cursor.execute("SELECT m1.movie_name_eng, m1.movie_year, m1.movie_duration, m1.movie_rating, m1.movie_description_eng, m1.movie_poster, m1.actors, GROUP_CONCAT(d.director_name || ' ' || d.director_surname,', ') as directors FROM (SELECT m.movie_id, m.movie_name_eng, m.movie_year, m.movie_duration, m.movie_rating, m.movie_description_eng, m.movie_poster, GROUP_CONCAT(a.actor_name || ' ' || a.actor_surname,', ') as actors FROM MOVIES m JOIN MOVIE_GENRE mg ON m.movie_id=mg.movie_id JOIN GENRES g ON mg.genre_id=g.genre_id AND g.genre_name='{}' JOIN MOVIE_ACTOR ma ON m.movie_id = ma.movie_id INNER JOIN ACTORS a ON ma.actor_id = a.actor_id GROUP BY m.movie_id) m1 INNER JOIN MOVIE_DIRECTOR md ON m1.movie_id = md.movie_id INNER JOIN DIRECTORS d on md.director_id = d.director_id GROUP BY m1.movie_id ORDER BY m1.movie_rating DESC".format(str(message.text)))
        result = cursor.fetchall()
    else:
        if category in ["year","duration"]:
            range_from = int(message.text.split(" ")[0].split('-')[0])
            range_to = int(message.text.split(" ")[0].split('-')[1])
        else:
            range_from = float(message.text.split(" ")[0].split('-')[0])
            range_to = float(message.text.split(" ")[0].split('-')[1])

        if len(movies_filtered)>1:
            movie_id = [a[0] for a in movies_filtered]
        else:
            movie_id = movies_filtered[0]
        cursor.execute("SELECT m1.movie_name_eng, m1.movie_year, m1.movie_duration, m1.movie_rating, m1.movie_description_eng, m1.movie_poster, m1.actors, GROUP_CONCAT(d.director_name || ' ' || d.director_surname,', ') as directors FROM (SELECT m.movie_id, m.movie_name_eng, m.movie_year, m.movie_duration, m.movie_rating, m.movie_description_eng, m.movie_poster, GROUP_CONCAT(a.actor_name || ' ' || a.actor_surname,', ') as actors FROM MOVIES m JOIN MOVIE_ACTOR ma ON m.movie_id = ma.movie_id INNER JOIN ACTORS a ON ma.actor_id = a.actor_id WHERE m.movie_id in {} and m.movie_{} BETWEEN {} AND {} GROUP BY m.movie_id) m1 INNER JOIN MOVIE_DIRECTOR md ON m1.movie_id = md.movie_id INNER JOIN DIRECTORS d on md.director_id = d.director_id GROUP BY m1.movie_id ORDER BY m1.movie_rating DESC".format(tuple(movie_id),category,range_from,range_to))
        result = cursor.fetchall()
    bot.send_message(message.chat.id, "Here are the results:", parse_mode='html')
    for count,row in enumerate(result):
        poster = open("/posters/{}.jpg".format(row[5]),"rb")
        bot.send_message(message.chat.id, "<b>{}. {}</b>\n\n<b>Year:</b> {}\n<b>Duration:</b> {}\n<b>IMDB Rating:</b> {}\n<b>Actors:</b> {}\n<b>Director:</b> {}\n\n{}".format(count+1,row[0],row[1],row[2],row[3],row[6],row[7],row[4]), parse_mode='html',reply_markup=types.ReplyKeyboardRemove())
        bot.send_photo(message.chat.id, poster)
    bot.send_message(message.chat.id, "Are you satisfied with proposed movies?\n If you are not, press /start button to change filters", parse_mode='html')

@bot.message_handler(commands=['start'])
def welcome(message):
    # keyboard 
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for row in genres:
        btn1 = types.KeyboardButton(str(row))
        markup.add(btn1)
    bot.send_message(message.chat.id, "Hello, {0.first_name}! I am Movie Adviser Bot. I am here to help you to choose the movie to watch. I'll ask you some questions for that. So let's begin.\n \n What genre do you prefer? ".format(message.from_user), parse_mode='html', reply_markup=markup)


@bot.message_handler(func = lambda message: message.text in genres)
def genre_filter(message):
    cursor = db.get_cursor()
    global movies_filtered
    movies_filtered.clear()
    periods = []
    if message.chat.type == "private":
        select_filter["genre_name"] = message.text
        cursor.execute("SELECT m.movie_id, m.movie_year FROM MOVIES m JOIN MOVIE_GENRE mg ON m.movie_id=mg.movie_id JOIN GENRES g ON mg.genre_id=g.genre_id AND g.genre_name='{}'".format(str(message.text)))
        movies_filtered += cursor.fetchall()
        if len(movies_filtered)>10:
            movie_year = [int(a[1]) for a in movies_filtered]
            periods += define_range(movie_year)
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for row in periods:
                btn1 = types.KeyboardButton(str(row))
                markup.add(btn1)
            bot.send_message(message.chat.id, "Nice choice! Now let's choose the movie year.", parse_mode='html', reply_markup=markup)
        else:
            print_final_movies(message,"genre")

        

@bot.message_handler(func = lambda message: re.match( r'\d{4}-\d{4}|\d{4}',message.text, re.I))
def year_filter(message):
    duration_range = []
    global movies_filtered
    if message.chat.type == "private":
        select_filter["genre_name"] = message.text
        year_from = int(message.text.split('-')[0])
        year_to = int(message.text.split('-')[1])
        movie_id = [a[0] for a in movies_filtered]
        cursor.execute("SELECT m.movie_id, m.movie_duration FROM MOVIES m WHERE m.movie_id in {} and m.movie_year BETWEEN {} AND {}".format(tuple(movie_id),year_from,year_to))
        filtered_result = cursor.fetchall()
        if len(filtered_result)>10:
            year_from = int(message.text.split('-')[0])
            year_to = int(message.text.split('-')[1])
            movie_id = [a[0] for a in movies_filtered]
            cursor.execute("SELECT m.movie_id, m.movie_duration FROM MOVIES m WHERE m.movie_id in {} and m.movie_year BETWEEN {} AND {}".format(tuple(movie_id),year_from,year_to))
        
            movies_filtered.clear()
            movies_filtered += cursor.fetchall()
            movie_duration = [int(a[1]) for a in movies_filtered]
            duration_range += define_range(movie_duration)
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for row in duration_range:
                btn1 = types.KeyboardButton(str(row)+' min.')
                markup.add(btn1)
            bot.send_message(message.chat.id, "We almost chose the movie for you! \n\n What duration do you prefer?", parse_mode='html', reply_markup=markup)
        else:
            print_final_movies(message,"year",movies_filtered)

@bot.message_handler(func = lambda message: re.match( r'\d{2,3}-\d{2,3}|\d{2,3}',message.text, re.I))
def year_filter(message):
    rating_range = []
    global movies_filtered
    if message.chat.type == "private":
        select_filter["genre_name"] = message.text
        duration = message.text.split()[0]
        duration_from = int(duration.split('-')[0])
        duration_to = int(duration.split('-')[1])
        movie_id = [a[0] for a in movies_filtered]
        cursor.execute("SELECT m.movie_id, m.movie_rating FROM MOVIES m WHERE m.movie_id in {} and m.movie_duration BETWEEN {} AND {} ORDER BY m.movie_rating".format(tuple(movie_id),duration_from,duration_to))
        filtered_result = cursor.fetchall()
        if len(filtered_result)>10:
            duration_from = int(duration.split('-')[0])
            duration_to = int(duration.split('-')[1])
            movie_id = [a[0] for a in movies_filtered]
            cursor.execute("SELECT m.movie_id, m.movie_rating FROM MOVIES m WHERE m.movie_id in {} and m.movie_duration BETWEEN {} AND {} ORDER BY m.movie_rating".format(tuple(movie_id),duration_from,duration_to))

            movies_filtered.clear()
            movies_filtered += cursor.fetchall()
            movie_rating = [a[1] for a in movies_filtered]
            rating_range += define_range(movie_rating)
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for row in rating_range:
                btn1 = types.KeyboardButton(str(row)+' ⭐')
                markup.add(btn1)
            bot.send_message(message.chat.id, "Nooice, the last step!\n\n Let's choose rating for the movie.", parse_mode='html', reply_markup=markup)
        else:
            print_final_movies(message,"duration",movies_filtered)

@bot.message_handler(func = lambda message: re.match( r'\d{1}.\d{1}-\d{1}.\d{1}|\d{1}.\d{1}',message.text, re.I))
def year_filter(message):
    rating_range = []
    global movies_filtered
    if message.chat.type == "private":
        select_filter["genre_name"] = message.text
        rating = message.text.split()[0]
        print_final_movies(message,"rating",movies_filtered)
    

# RUN
bot.polling(none_stop=True)