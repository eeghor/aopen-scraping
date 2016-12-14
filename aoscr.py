# -*- coding: utf-8 -*-

"""
Scrape the official Australian Open web site.

Note:

* court information is only available for years starting from 2005

"""
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select  # to deal with dropdown menues
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
import time
from selenium.common.exceptions import NoSuchElementException
import re
import pandas as pd
from collections import defaultdict
# from collections import namedtuple


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

WAIT_TIME = 40  # max waiting time for a page to load

y_from =2009
y_to = 2016

year = 2014

comps = "MS"

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

ao_tz = timezone("Australia/Melbourne")

#driver = webdriver.PhantomJS()
driver = webdriver.Chrome('/Users/ik/Codes/aopen-scraping/chromedriver')



print("""-------> scraping aopen.com""")

if year == 2016:

	# note: the same starting page regardless the year
	start_page  = "http://www.ausopen.com/en_AU/scores/completed_matches"

	driver.get(start_page)

	for competition_type in comps.split():
	
	
		dropdown_menu = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#eventSelector")))
		dropdown_menu.click()
		
		time.sleep(3)
	
		print("extracting the {} tournament ...".format(abbr_dict[competition_type]))
		
		# now go to the list of days: it's <div> with id=tournDays
		playday_list = driver.find_element_by_xpath("//div[@id='tournDays']/ul")
		
		# collect all <a> with href
		as_in_playday_list = playday_list.find_elements_by_xpath("li/a[@href]")
		total_days = len(as_in_playday_list)
	
		# the below are like Monday, 18 January; format: %A, %d %B
		match_dates = [d.strftime("%Y-%m-%d") for d in map(lambda x: ao_tz.localize(datetime.strptime(x, "%A, %d %B %Y")), [a.get_attribute("title").strip() + " " + str(year) for a in as_in_playday_list])]
	
		a = as_in_playday_list[0]
		
		a.click()
		time.sleep(3)  # go to page 1
		
		# visit each day of the chosen competition
		for i in range(total_days): 
		
			print("scraping day", i+1, "...", end="")
		
			time.sleep(3)
		
			score_tables = driver.find_elements_by_xpath("//div[@class='scoringtable' and @data-event='" + competition_type +"']")  # list of tables
		
			for t in score_tables:
				
				court, compet_type = t.find_element_by_xpath("div/div[@class='courtname']").text.split("-")
				
				tmp = compet_type.strip().split(abbr_dict[competition_type])
	
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
	
				else:
	
					flag = "singles"
					list_player1.append(t.find_elements_by_css_selector(".name." + flag)[0].find_element_by_xpath("a").text)
					list_player2.append(t.find_elements_by_css_selector(".name." + flag)[1].find_element_by_xpath("a").text)
		
			print("ok")
			
			if i < total_days - 1:
				driver.find_element_by_xpath("//div[@id='tournDays']/ul").find_elements_by_xpath("li/a[@href]")[i+1].click()
	
		assert len(list_player1) == len(list_player2), "some player names seem to be missing!"
	
		print("found {} matches in this competition".format(len(list_player1)))

elif year > 2004 and year < 2016:

	for competition_type in comps.split():

		main_link = "http://www.ausopen.com/en_AU/event_guide/history/draws/" + str(year) + "_" + competition_type + "_"

		if competition_type in "MS WS".split():

			# this is for all years but 2016; {"round 1": ["link1", "link2", ..], "round 2": [..]}
			links_by_round = defaultdict(list)
			# another dict to relate round number to what is actually is
			round_numbers_to_names = {1: "Round 1", 2: "Round 2", 3: "Round 3", 4: "Round 4", 
							5: "Quarterfinals", 6: "Semifinals", 7: "Final"}


			# because Chrome web driver cannot click areas (!), here is a dumb solution: create direct links depending on round		
			
			for rnd in range(1,8):
	
				if rnd == 1:
					links_by_round[rnd].append(main_link + str(rnd) + ".html")
					for panel in range(2,5):
						links_by_round[rnd].append(main_link + str(rnd) + "_" + str(panel) + ".html")
				
				if rnd == 2:
					links_by_round[rnd].append(main_link + str(rnd) + ".html")
					links_by_round[rnd].append(main_link + str(rnd) + "_2.html")
	
				if rnd in [3,4]:
					links_by_round[rnd].append(main_link + str(rnd) + ".html")
	
				if rnd == 5:
					links_by_round[rnd].append(main_link +  "Q" + ".html")
	
				if rnd == 6:
					links_by_round[rnd].append(main_link +  "S" + ".html")
	
				if rnd == 7:
					links_by_round[rnd].append(main_link +  "F" + ".html")
	
				# done with the links
	
				print("scraping round", rnd, "...", end="")
	
				for r in links_by_round[rnd]:  
	
					driver.get(r)
	
					time.sleep(3)
		
					score_tables = driver.find_elements_by_xpath("//div[@class='scoringtable' and @data-event='" + competition_type +"']")  # list of tables
				
					for t in score_tables:
						
						# for each match attach round, we know what it is
						list_round.append(round_numbers_to_names[rnd])
						list_dates.append(str(year))  # no dates available, only the year!
	
						try:
							court_comp = t.find_element_by_xpath("div/div[@class='courtname']")
						except NoSuchElementException:
							print("error! interestingly, couldn't find the court name for this match..")
	
						if "-" in court_comp.text:
							court, compet_type = court_comp.text.split("-")
						else:
							court = compet_type = "N/A"
	
						list_courts.append(court.strip())
				
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
				
						
						list_player1.append(t.find_elements_by_css_selector(".name.singles")[0].find_element_by_xpath("a").text)
						list_player2.append(t.find_elements_by_css_selector(".name.singles")[1].find_element_by_xpath("a").text)
				
				print("ok")

			elif competition_type in "MD WD".split():

				# this is for all years but 2016; {"round 1": ["link1", "link2", ..], "round 2": [..]}
				links_by_round = defaultdict(list)
				# another dict to relate round number to what is actually is
				round_numbers_to_names = {1: "Round 1", 2: "Round 2", 3: "Round 3", 4: "Quarterfinals", 5: "Semifinals", 6: "Final"}

				for rnd in range(1,7):
	
				if rnd == 1:
					links_by_round[rnd].append(main_link + str(rnd) + ".html")
					links_by_round[rnd].append(main_link + str(rnd) + "_2.html")
				
				if rnd == [2,3]:
					links_by_round[rnd].append(main_link + str(rnd) + ".html")
	
				if rnd == 4:
					links_by_round[rnd].append(main_link +  "Q" + ".html")
	
				if rnd == 6:
					links_by_round[rnd].append(main_link +  "S" + ".html")
	
				if rnd == 7:
					links_by_round[rnd].append(main_link +  "F" + ".html")
	
				# done with the links
	
		# 	navigation_bar = WebDriverWait(driver, WAIT_TIME).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#nav")))
		# draws_in_navigation_bar = navigation_bar.find_element_by_xpath(".//ul/li/a[contains(@href, 'draws')]")

		# # ActionChains(driver).move_to_element(navigation_bar).perform()

		# hidden_archive_draws_menu = navigation_bar.find_element_by_xpath(".//ul/li[@class='nav_draws']/div/ul/li/a[contains(@href, 'history')]")

		# ActionChains(driver).move_to_element(draws_in_navigation_bar).click(hidden_archive_draws_menu).perform()

		# # now select year from the dropdow menu
		# dropdown_year_menu = driver.find_element_by_xpath("//select[@name='year']")
		# #dropdown_year_menu.click()
		
		# #time.sleep(2)

		# Select(dropdown_year_menu).select_by_value(str(year))
		# time.sleep(3)

		# # find the Go button and click it

		# driver.find_element_by_xpath("//input[contains(@src, 'go.gif')]").click()

		# time.sleep(3)

		# # find the compettition map

		# comp_map = driver.find_element_by_xpath("//map[@name='hist_events']")
		# # Men's Singles
		# #print("alt=",".//area[@alt=" + '"' + abbr_dict[competition_type] + '"' +"]")
		# #comp_map.find_element_by_xpath(".//area[@alt=" + '"' + abbr_dict[competition_type] + '"' +"]").click()
		# comp_map.find_element_by_xpath('.//area[@coords="10,8,115,39"]').click()

		# time.sleep(2)

		# # find the map

		# round_map = driver.find_element_by_xpath("//map[@name='hist_draw']")

		# time.sleep(2)

		# # start from the 1st round

		# round_map.find_element_by_xpath(".//area[@alt='1st Round, 1st quarter']").click()

		# time.sleep(2)

# all done
	
driver.quit()

data = zip(list_round, list_dates, list_courts, list_player1, list_player1_set1, list_player1_set2, list_player1_set3, list_player1_set4, list_player1_set5,
				 list_player2, list_player2_set1, list_player2_set2, list_player2_set3, list_player2_set4, list_player2_set5)

df = pd.DataFrame(columns="round date court player1 p1s1 p1s2 p1s3 p1s4 p1s5 player2 p2s1 p2s2 p2s3 p2s4 p2s5".split())

for i, row in enumerate(data):
	df.loc[i] = row
	
csv_fl = "scraped_data_from_aopen_" + "_".join(comps.split()) + ".csv"


df.to_csv(csv_fl, index=False, sep="\t")

print("successfully retrieved {} results..".format(len(df.index)))

