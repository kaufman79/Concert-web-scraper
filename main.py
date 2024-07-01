import requests
import selectorlib
import smtplib, ssl
import os
import time

URL = "http://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


def scrape(url):
    """scrape the page source (html of the page) from the URL"""
    response = requests.get(url)
    source = response.text
    return source


def extract(source):
    extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
    value = extractor.extract(source)["tours"]
    return value


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
    """appends extracted tour to txt file"""
    with open('data.txt', 'a') as file:
        file.write(extracted + "\n")


def read(extracted):
    with open("data.txt", 'r') as file:
        return file.read()


subject = ("\
Subject: New music event")

if __name__ == "__main__":
    while True:
        scraped = scrape(URL)
        extracted = extract(scraped)
        print(extracted)

        content = read(extracted)
        if extracted != "No upcoming tours":
            if extracted not in content:
                store(extracted)
                send_email(message=subject + "\n\nHey, New Event was found")
        time.sleep(200)