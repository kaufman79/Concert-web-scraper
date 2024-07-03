import requests
import selectorlib
import smtplib, ssl
import os
import time
import sqlite3


URL = "http://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

# SQL commands
"INSERT INTO events VALUES ('Metallica', 'Pittsburgh', '2025.09.17')"
"SELECT * FROM events WHERE date='2024.08.10'"
"DELETE FROM events WHERE Artist= 'Tigers'"

connection = sqlite3.connect("data.db")


def scrape(url):
    """scrape the page source (html of the page) from the URL"""
    response = requests.get(url)
    source = response.text
    return source


def extract(source):
    extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
    extracted = extractor.extract(source)["tours"]
    return extracted


def send_email(message):
    password = os.getenv("GOOGLEPASSWORD")  # need to first input environmental variable in os
    username = "ryankaufman79@gmail.com"
    receiver = "ryankaufman79@gmail.com"
    host = "smtp.gmail.com"
    port = 465
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, receiver, message)
    print("Email was sent")


def store(extracted):
    """appends extracted tour to SQL database"""
    row = extracted.split(",")
    row = [item.strip() for item in row]
    cursor = connection.cursor()
    cursor.execute("INSERT INTO events VALUES (?,?,?)", row)
    connection.commit()


def read(extracted):
    """checks if the extracted concert is in the database.
    Returns empty list if not, returns concert if so
    """
    row = extracted.split(",")
    row = [item.strip() for item in row]
    artist, city, date = row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM events WHERE Artist=? AND city=? AND date=?",
                   (artist, city, date))
    rows = cursor.fetchall()
    print(rows)
    return rows


subject = ("\
Subject: New music event")

if __name__ == "__main__":
    while True:
        scraped = scrape(URL)
        extracted = extract(scraped)
        print(extracted)

        if extracted != "No upcoming tours":
            row = read(extracted)
            if not row:
                store(extracted)
                send_email(message=subject + "\n\nHey, New Event was found")
                print("New event found")

        time.sleep(2)
