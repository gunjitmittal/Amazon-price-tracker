import math
import os
import requests
from bs4 import BeautifulSoup
import lxml
import smtplib
import gspread


gc = gspread.service_account(filename="service_creds.json")
sh = gc.open("Amazon price tracker").sheet1
list_of_dicts = sh.get_all_records()

my_email = os.getenv("my-email")
password = os.getenv("password")
connection = smtplib.SMTP("smtp.gmail.com", 587)
connection.starttls()
connection.login(user=my_email, password=password)

# Searches for price drops
for item in list_of_dicts:
    amazon_url = item["Amazon"]
    headers = {
        "User-Agent": "User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
    }

    amazon_page = requests.get(url=amazon_url, headers=headers)
    amazon_contents = amazon_page.text

    amazon_soup = BeautifulSoup(amazon_contents, "lxml")
    amazon_price = amazon_soup.find(name="span", class_="a-price-whole")
    amazon_cost = float(amazon_price.getText().replace(",", ""))
    product_name = amazon_soup.find(name="span", class_="a-size-large product-title-word-break").getText().strip()

    flipkart_url = item["Flipkart"]
    if flipkart_url != "":
        flipkart_page = requests.get(url=flipkart_url, headers=headers)
        flipkart_contents = flipkart_page.text

        flipkart_soup = BeautifulSoup(flipkart_contents, "lxml")
        flipkart_price = flipkart_soup.find(name="div", class_="_30jeq3 _16Jk6d")
        flipkart_cost = float(flipkart_price.getText().replace(",", "").replace("₹", ""))
    else:
        flipkart_cost = math.inf
    if flipkart_cost < amazon_cost:
        url = flipkart_url
        cost = flipkart_cost
    else:
        url = amazon_url
        cost = amazon_cost
    if cost < item["Cost"]:
        connection.sendmail(from_addr=my_email, to_addrs="gunjitmittal2@gmail.com",
                            msg="Subject: Low price alert \n\n" + f"Price is low for {product_name} buy it now.\n{url}")

row = len(list_of_dicts) + 2
# Modifying the database
choice = input("Type 1 if you want to add items, 2 to add flipkart link, 3 to display all the entries"
               " and anything else to exit\n")
while choice.lower() == "1" or choice.lower() == "2" or choice.lower() == "3":
    if choice.lower() == "1":
        amazon_url = input("Enter Amazon URL")
        flipkart_url = input("Enter Flipkart URL (optional)")
        min_price = input("Enter the price below which you wish to be notified")
        sh.update_cell(row, 1, amazon_url)
        sh.update_cell(row, 2, flipkart_url)
        sh.update_cell(row, 3, min_price)
        row += 1
        choice = input("Type 1 if you want to add items, 2 to add flipkart link, 3 to display all the entries"
                       " and anything else to exit\n")
    if choice.lower() == "2":
        entry = int(input("Type the row you want to add to"))
        flipkart_url = input("Enter Flipkart URL")
        sh.update_cell(entry, 2, flipkart_url)
        choice = input("Type 1 if you want to add items, 2 to add flipkart link, 3 to display all the entries"
                       " and anything else to exit\n")
    if choice.lower() == "3":
        print(list_of_dicts)
        choice = input("Type 1 if you want to add items, 2 to add flipkart link, 3 to display all the entries"
                       " and anything else to exit\n")
connection.close()
