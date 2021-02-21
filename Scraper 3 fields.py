from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup
import urllib.request
import pprint
import sys 
import csv

class CraiglistScraper(object):
	def __init__(self, location, postal, max_price, radius, url_num):
		self.location = location
		self.postal = postal
		self.max_price = max_price
		self.radius = radius
		self.url_num = url_num

		#self.url = f"https://{location}.craigslist.org/search/apa?search_distance={radius}&postal={postal}&max_price={max_price}"
		#self.url = f"https://{location}.craigslist.org/search/apa?max_price={max_price}&availabilityMode=0&sale_date=all+dates"
		self.url = f"https://{location}.craigslist.org/search/{url_num}"
		print(self.url)
		self.driver = webdriver.Firefox()
		self.delay = 3

	def load_craigslist_url(self):
		self.driver.get(self.url)
		try:
			wait = WebDriverWait(self.driver, self.delay)
			wait.until(EC.presence_of_element_located((By.ID, "searchform")))
			print("Page is ready")
		except TimeoutException:
			print("Loading took too much time")

	def extract_post_information(self):
		all_posts = self.driver.find_elements_by_class_name("result-row")

		dates = []
		titles = []
		prices = []
		hoods = []
		housings = []

		for post in all_posts:

			price = post.find_element_by_class_name("result-price").text
			price = price.replace('$','')
			title = post.find_element_by_class_name("result-title").text
			date = post.find_element_by_class_name("result-date").text
			if post.find_elements_by_class_name("result-hood"):
				hood = post.find_elements_by_class_name("result-hood")[0].text
			else:
				hood = ''
			if post.find_elements_by_class_name("housing"):
				housing = post.find_elements_by_class_name("housing")[0].text
			else:
				housing = ''

			print("TITLE: " + title)
			print("PRICE: " + price)
			print("DATE: " + date)
			print("NEIGHBOURHOOD: " + hood)
			print("HOUSING: " + housing)

			titles.append(title)
			prices.append(price)
			dates.append(date)
			hoods.append(hood)
			housings.append(housing)

		return titles, prices, dates, hoods, housings

	def extract_post_urls(self):
		url_list = []
		html_page = urllib.request.urlopen(self.url)
		soup = BeautifulSoup(html_page, "lxml")
		for link in soup.findAll("a", {"class": "result-title hdrlnk"}):
			print(link["href"])
			url_list.append(link["href"])
		return url_list

	def quit(self):
		self.driver.close()

	def export_to_file(self, titles, prices, dates, hoods, housings, url_num):
		
		x = int(url_num[6:10])//120
		with open(f"listings{x}.csv", 'w', newline='') as csvfile:
			fieldnames = ['title', 'price', 'date posted', 'neighbourhood', 'housing']
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

			writer.writeheader()
			for x in range(len(titles)):
				writer.writerow({'title': titles[x].encode("utf-8"), 'price': prices[x].encode("utf-8"), 'date posted': dates[x].encode("utf-8"), 'neighbourhood': hoods[x].encode("utf-8"), 'housing': housings[x].encode("utf-8")})
				

def get_all (location, postal, max_price, radius, url_num):
	x = 0
	while x <= 1640:
		url_num = url_num + str(x)
		execute(location, postal, max_price, radius, url_num)
		x = x + 120	  
		print(x)
		print(url_num)
		url_num = "apa?s="


def execute(location, postal, max_price, radius, url_num):
	scraper = CraiglistScraper(location, postal, max_price, radius, url_num)
	scraper.load_craigslist_url()
	titles, prices, dates, hoods, housings = scraper.extract_post_information()
	scraper.export_to_file(titles, prices, dates, hoods, housings, url_num)
	print(titles)
	scraper.quit()

location = "Victoria"
postal = "0"
max_price = "1000"
radius = "0"
url_num = "apa?s="

get_all(location, postal, max_price, radius, url_num)
#scraper.load_craigslist_url()
#titles, prices, dates, hoods, housings = scraper.extract_post_information()
#scraper.export_to_file(titles, prices, dates, hoods, housings)


#scraper.extract_post_urls()
#scraper.quit()