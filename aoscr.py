# -*- coding: utf-8 -*-
"""
Scrape the official Australian Open web site
Note:
* court information is only available for years starting from 2005
"""

import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select  # to deal with dropdown menues
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import re
import pandas as pd
from collections import namedtuple

import requests
from bs4 import BeautifulSoup

from collections import defaultdict
from datetime import datetime  # need to convert timezone
from pytz import timezone  # note that the AO timezone is called Australia/Melbourne


"""
what do you want to scrape? 
MS : Men's Singles
WS : Women's Singles
MD : Men's Doubles
WD : Women's Doubles

"""

year = 2016

comps = "MS MD"

#driver = webdriver.PhantomJS()

abbr_dict = {"MS" : "Men's Singles", 
				"WS" : "Women's Singles", 
					"MD" : "Men's Doubles", 
						"WD" : "Women's Doubles"}
list_dates = []
list_times = []
list_round = []

list_player1 = []
list_player2 = []

list_player1_set1 = []
list_player1_set2 = []
list_player1_set3 = []
list_player1_set4 = []
list_player1_set5 = []

list_player2_set1 = []
list_player2_set2 = []
list_player2_set3 = []
list_player2_set4 = []
list_player2_set5 = []

list_courts = []

mtch_list = []


ao_tz = timezone("Australia/Melbourne")
de_tz = timezone("Europe/Berlin")

wettpoint_headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"}

list_tmp_player1 = []
list_tmp_player2 = []
list_tmp_dtime= []
list_tmp_scores = []

# comp_types = "MS WS"

# comp_types_dict = {"MS" : "Men's Singles", "WS" : "Women's Singles"}
# dictionary used to create the right URL
add_to_link_dict = {"MS": "men", "WS": "women"}


driver = webdriver.Chrome('/Users/ik/Codes/aopen-scraping/chromedriver')

start_page  = "http://www.ausopen.com/en_AU/scores/completed_matches"

driver.get(start_page)

print("""-------> scraping aopen.com""")

for competition_type in comps.split():


	dropdown_menu = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#eventSelector")))
	dropdown_menu.click()
	
	menu_item = Select(WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#cmatch"))))
	menu_item.select_by_value(competition_type)
	
	time.sleep(3)

	print("extracting the {} tournament ...".format(abbr_dict[competition_type]))
	
	# now go to the list of days: it's <div> with id=tournDays
	
	playday_list = driver.find_element_by_xpath("//div[@id='tournDays']/ul")
	
	# collect all <a> with href
	
	as_in_playday_list = playday_list.find_elements_by_xpath("li/a[@href]")
	total_days = len(as_in_playday_list)

	# the below are like Monday, 18 January; format: %A, %d %B
	match_dates = [a.get_attribute("title").strip() for a in as_in_playday_list]
	
	a = as_in_playday_list[0]
	
	a.click()
	time.sleep(3)  # go to page 1
	
	
	for i in range(total_days): 
	
		print("scraping day", i+1, "...", end="")
	
		time.sleep(3)
	
		score_tables = driver.find_elements_by_xpath("//div[@class='scoringtable' and @data-event='" + competition_type +"']")  # list of tables
	
		for t in score_tables:
			
			court, comptype_and_round = t.find_element_by_xpath("div/div[@class='courtname']").text.split("-")
			
			tmp = comptype_and_round.strip().split(abbr_dict[competition_type])

			if "" in tmp:
				list_round.append(tmp[-1].strip())
				list_courts.append(court.strip())
			else:  # apparently, no right matches on that day - click on
				break

			list_dates.append(match_dates[i])  # same match date for tables on the page
	
			list_player1_set1.append(t.find_elements_by_css_selector("span.set1")[0].text)
			list_player2_set1.append(t.find_elements_by_css_selector("span.set1")[1].text)
			list_player1_set2.append(t.find_elements_by_css_selector("span.set2")[0].text)
			list_player2_set2.append(t.find_elements_by_css_selector("span.set2")[1].text)
			list_player1_set3.append(t.find_elements_by_css_selector("span.set3")[0].text)
			list_player2_set3.append(t.find_elements_by_css_selector("span.set3")[1].text)
			list_player1_set4.append(t.find_elements_by_css_selector("span.set4")[0].text)
			list_player2_set4.append(t.find_elements_by_css_selector("span.set4")[1].text)
			list_player1_set5.append(t.find_elements_by_css_selector("span.set5")[0].text)
			list_player2_set5.append(t.find_elements_by_css_selector("span.set5")[1].text)
	
			if competition_type in ["MD", "WD"]:
				flag = "doubles"
				double_name1 = t.find_elements_by_css_selector(".name." + flag)[0].find_elements_by_xpath("a")[0].text
				double_name2 = t.find_elements_by_css_selector(".name." + flag)[0].find_elements_by_xpath("a")[1].text
				list_player1.append(double_name1 + "/" + double_name2)
				double_name1 = t.find_elements_by_css_selector(".name." + flag)[1].find_elements_by_xpath("a")[0].text
				double_name2 = t.find_elements_by_css_selector(".name." + flag)[1].find_elements_by_xpath("a")[1].text
				list_player2.append(double_name1 + "/" + double_name2)
				#print("currently, list_player1=",list_player1)
				#list_player2.append(t.find_elements_by_css_selector(".name." + flag)[1]..text)
			else:
				flag = "singles"
				list_player1.append(t.find_elements_by_css_selector(".name." + flag)[0].find_element_by_xpath("a").text)
				#print("currently, list_player1=",list_player1)
				list_player2.append(t.find_elements_by_css_selector(".name." + flag)[1].find_element_by_xpath("a").text)
	
		print("ok")
		
		if i < total_days - 1:
			driver.find_element_by_xpath("//div[@id='tournDays']/ul").find_elements_by_xpath("li/a[@href]")[i+1].click()

	# by now we have scraped the results for this particula competition. what about times? we are going to go to tennis.wettpoint.com
	# and get the same competition

	print("""-------> scraping tennis.wettpoint.com""")

	wettpoint_archiv_part = "http://tennis.wettpoint.com/en/archiv/"

	if competition_type == "MD":
		season_line = wettpoint_archiv_part + "australian-open-doubles-" + str(year)
	elif competition_type == "WD":
		season_line = wettpoint_archiv_part + "australianopen-women-doubles-" + str(year)
	elif competition_type == "WS":
		season_line = wettpoint_archiv_part + "australian-open-women-" + str(year)
	elif competition_type == "MS":
		season_line = wettpoint_archiv_part + "australian-open-men-" + str(year)

	season_line += ".html"

	print("requesting the results page..", end="")
	page = requests.get(season_line, headers=wettpoint_headers)

	if page.status_code == 200:
		print("ok")
	else:
		print("error! status code {}".format(page.status_code))

	soup = BeautifulSoup(page.content, 'html.parser')

	rws = soup.find_all("tr")

	# we will keep match information in a list of named tuples; we don't really need the scores as such
	TennisMatch = namedtuple("TennisMatch", "date time players")

	for row in rws:

		# check if it's a typical match record, i.e. has 3 cells

		if len(row.find_all("td")) == 3:

			c1, c2, c3 = row.find_all("td")

			# localized data and time below look like 2015-01-23 13:00:00+11:00

			dtime_parsed_berlin = de_tz.localize(datetime.strptime(c1.text, "%d/%m/%y %H:%M"))
			dtime_parsed_melbourne = dtime_parsed_berlin.astimezone(ao_tz)
			
			p1_surname, p2_surname = map(lambda x: x.split(".")[-1].strip(), c2.text.split(" - "))  # note 2 white spaces

			# list_tmp_player1.append(p1_surname)
			# list_tmp_player2.append(p2_surname)

			# list_tmp_dtime.append(dtime_parsed_melbourne.strftime("%Y-%m-%d %H:%M"))
			# list_tmp_scores.append(c3.text.strip())

			mtch_list.append(TennisMatch(dtime_parsed_melbourne.strftime("%Y-%m-%d"), dtime_parsed_melbourne.strftime("%H:%M"), {p1_surname, p2_surname} ))
	
	# matching
	for i, p1 in enumerate(list_player1):
		player_surnames = set(list_player1[i].split(".")[1].strip(),list_player2[i].split(".")[1].strip())
		for match_w_time in mtch_list:
			if len(player_surnames.intersection(match_w_time.players)) == 2:  # complete match
				list_times.append(match_w_time.time)
	
driver.quit()

data = zip(list_round, list_dates, list_times, list_courts, list_player1, list_player1_set1, list_player1_set2, list_player1_set3, list_player1_set4, list_player1_set5,
				 list_player2, list_player2_set1, list_player2_set2, list_player2_set3, list_player2_set4, list_player2_set5)

df = pd.DataFrame(columns="round date time court player1 p1s1 p1s2 p1s3 p1s4 p1s5 player2 p2s1 p2s2 p2s3 p2s4 p2s5".split())

for i, row in enumerate(data):
	df.loc[i] = row
	
csv_fl = "scraped_data_from_aopen_" + "_".join(comps.split()) + ".csv"


df.to_csv(csv_fl, index=False)

print("successfully retrieved {} results..".format(len(df.index)))

