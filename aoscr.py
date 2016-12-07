# -*- coding: utf-8 -*-
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select  # to deal with dropdown menues
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import re
import pandas as pd

"""
what do you want to scrape? 
MS : Men's Singles
WS : Women's Singles
MD : Men's Doubles
WD : Women's Doubles

"""

comps = "MS MD"

#driver = webdriver.PhantomJS()

abbr_dict = {"MS" : "Men's Singles", 
				"WS" : "Women's Singles", 
					"MD" : "Men's Doubles", 
						"WD" : "Women's Doubles"}
list_dates = []
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

	# combine matches in one list of tuples, something like matches of the day
	
driver.quit()

data = zip(list_round, list_dates, list_courts, list_player1, list_player1_set1, list_player1_set2, list_player1_set3, list_player1_set4, list_player1_set5,
				 list_player2, list_player2_set1, list_player2_set2, list_player2_set3, list_player2_set4, list_player2_set5)

df = pd.DataFrame(columns="round date court player1 p1s1 p1s2 p1s3 p1s4 p1s5 player2 p2s1 p2s2 p2s3 p2s4 p2s5".split())

for i, row in enumerate(data):
	df.loc[i] = row
	
csv_fl = "scraped_data_from_aopen_" + "_".join(comps.split()) + ".csv"


df.to_csv(csv_fl, index=False)

print("successfully retrieved {} results..".format(len(df.index)))

