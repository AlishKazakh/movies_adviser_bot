import bs4 as bs
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
import os
import pandas as pd
import pandas_datareader.data as web
import pickle
import requests

def save_sp500_tickers():  ###### это функция, которая сохраняет коды(названия) компаний
	resp = requests.get("https://www.slickcharts.com/sp500")
	soup = bs.BeautifulSoup(resp.text, 'lxml')
	table = soup.find('table', {'class': 'table table-hover table-borderless table-sm'})
	tickers = []
	for row in table.findAll('tr')[1:]:
		ticker = row.findAll('td')[2].text
		tickers.append(ticker)
	
	with open("sp500tickers.pickle", "wb") as f:
		pickle.dump(tickers,f)
    
	return tickers

def get_data_from_marketwatch(reload_sp500 = False):  ##############  это функция, которая вытягивает финансовые показатели компаний с marketwatch  #############
	if reload_sp500:
		tickers = save_sp500_tickers()
	else:
		with open("sp500tickers.pickle","rb") as f:
			tickers = pickle.load(f)

	if not os.path.exists('stock_dfs'):
		os.makedirs('stock_dfs')
	
	for count,ticker in enumerate(tickers):
		if not os.path.exists('stock_dfs/{}'.format(ticker)):
			os.makedirs('stock_dfs/{}'.format(ticker))			
			fin_statement_categories = ['balance-sheet','cash-flow'] ###разделил на 2 категории пока
			for fin_category in fin_statement_categories:
				if not os.path.exists('stock_dfs/{}/{}'.format(ticker,fin_category)):
					os.makedirs('stock_dfs/{}/{}'.format(ticker,fin_category)) ### создаю папку с кодом компании и категорией
				resp = requests.get('https://www.marketwatch.com/investing/stock/{}/financials/{}'.format(ticker,fin_category))  ### начинаю вытянивать данные с сайта
				soup = bs.BeautifulSoup(resp.text,'lxml')
				body = soup.find('body')
				categories_soup = soup.findAll('h2')
				categories = []

				
				tables = body.findAll('table', {'class': 'crDataTable'})
				for category in categories_soup[1:]:
					categories.append(category.text) 

				for category in categories:
					table_index = categories.index(category)	
				
					if not os.path.exists('stock_dfs/{}/{}/{}_{}.csv'.format(ticker,fin_category,ticker,category)):
						desc_df = []
						for row in tables[table_index].findAll('tr')[1:]:
							desc = row.findAll('td')[0].text
							desc_df.append(desc)

						years = []	
						years_table = tables[table_index].findAll('tr')[0]
						for year_row in years_table.findAll('th')[1:-1]:
							year = year_row.text
							years.append(year)
						years_dict = {}
						#print(years)
						for year in years:
							index = years.index(year)+1
							df = []
							for row in tables[table_index].findAll('tr')[1:]:
								info = row.findAll('td')[index].text
								if (info[0] == '(') & (info[-1] == ')'):
									info = '-'+info[1:-1]
								df.append(info)
							years_dict[year] = df	
						pd_df = pd.DataFrame(years_dict,index = desc_df)
						#print(pd_df)
						main_df = pd.DataFrame(pd_df) 	
						main_df.append(pd_df)
						#print(main_df)	
						main_df.to_csv("stock_dfs/{}/{}/{}_{}.csv".format(ticker,fin_category,ticker,category))	
					else:
						print('Already have {}'.format(ticker))	
			
			if not os.path.exists('stock_dfs/{}/income-statement'.format(ticker)):
				os.makedirs('stock_dfs/{}/income-statement'.format(ticker)) ### вытягиваю данные для третьей категории
			resp = requests.get('https://www.marketwatch.com/investing/stock/{}/financials/income-statement'.format(ticker))
			soup = bs.BeautifulSoup(resp.text,'lxml')
			body = soup.find('body')
			

			tables1 = body.findAll('table', {'class': 'crDataTable'})
			
			years1 = []	
			years_table = tables1[0].findAll('tr')[0]
			for year_row in years_table.findAll('th')[1:-1]:
				year = year_row.text
				years1.append(year)

			if not os.path.exists('stock_dfs/{}/income-statement/{}.csv'.format(ticker,ticker)):
				main_df1 = pd.DataFrame()
				for table in tables1:
					desc_df1 = []
					for row in table.findAll('tr')[1:]:
						desc = row.findAll('td')[0].text
						desc_df1.append(desc)

					years_dict1 = {}
					#print(years)
					for year in years1:
						index = years1.index(year)+1
						df1 = []
						for row in table.findAll('tr')[1:]:
							info = row.findAll('td')[index].text
							if (info[0] == '(') & (info[-1] == ')'):
								info = '-'+info[1:-1]
							df1.append(info)
						years_dict1[year] = df1	
					pd_df1 = pd.DataFrame(years_dict1,index = desc_df1)
					#print(pd_df) 	
					main_df1 = pd.concat([main_df,pd_df1])
				#print(main_df)	
				main_df1.to_csv("stock_dfs/{}/income-statement/{}.csv".format(ticker,ticker))	
			else:
				print('Already have {}'.format(ticker))			


		
		print("{}. {} loaded. {}%".format(count+1,ticker,(count+1)/5))
						
					
### я должен буду объединить вытягивание данных для трех категорий и поправить код, чтобы вытягивал данные правильно

get_data_from_marketwatch()	



