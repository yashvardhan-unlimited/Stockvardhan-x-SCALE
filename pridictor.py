# imports ==================================================================
from urllib import response
import asyncio
import llm
import openai   
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import requests
import feedparser
from bs4 import BeautifulSoup
import time

from typer import prompt


# API keys =================================================================
load_dotenv()
news_API = os.getenv("news_API")
groq_API_KEY = os.getenv("groq_API_KEY")
gemini_API_KEY = os.getenv("gemini_API_KEY")



# test data ================================================================
company_name = "NVIDIA"
investment_horizon = "5 years"
investment_amount = "10000 USD"
investment_risk_tolerance = "medium"

# I will be creating a stock analyser agent in 5 steps.
# step 1: Analyse the company's financial health and performance.
# step 2: Analyse the company's competitive position in the industry.
# step 3: Analyse the company's products, accuisitions, and partnerships. or news directly related to comapny.
# step 4: Analyse the company's utilities and industry, and then search for its related news.

def summarize_groq(data, prompt="Summarize the given article, and tell What is the news about, what happened, and the keypoints:"):
    llm = ChatOpenAI(
    model="llama-3.3-70b-versatile",
    api_key=groq_API_KEY,
    base_url="https://api.groq.com/openai/v1"
    )
    response = llm.invoke(f"{prompt} {data}")
    return response.content

def summarize_gemini(data, prompt="Summarize the given article, and tell What is the news about, what happened, and the keypoints:"):
    llm = ChatOpenAI(
    model="gemini-2.0-flash",
    api_key=gemini_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
    response = llm.invoke(f"{prompt} {data}")
    return response.content

def summarize_local(data, prompt="Summarize the given article, and tell What is the news about, what happened, and the keypoints:"):
    llm = ChatOllama(
        model="llama3.1:latest",
        temperature=0.2
    )
    response = llm.invoke(f"{prompt} {data}")
    return response.content


def bold(text):
    # Code to bold the text.
    # color text to red
    return f"\033[1;31m{text}\033[0m"


def company_dna_scraping(company_name):
    # Code to analyse the company's products, accuisitions, and partnerships. or news directly related to comapny.
    link1 = f"https://news.google.com/rss/search?q=latest+news+related+to+company+{company_name}"
    request = requests.get(link1,allow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(request.text, "xml")
    lst_news = []
    for i in range(1):
        request2 = requests.get()
        soup2 = BeautifulSoup(request2.content, "html.parser")

        lst_news.append({("info_id"): f"n{i+1}", 
                         ("news"): (soup2.find_all("item")[i]),
                         ("date"): (soup.find_all("item")[i].pubDate.text)[:16],
                         ("source"): soup.find_all("item")[i].source.text
                        })

    return lst_news
    # return soup.prettify()


def company_dna_newsAPI(company_name, news_API, depth=5):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": f"{company_name}",
        "apiKey": news_API,
        "language": "en",
        "sortBy": "relevancy"
    }
    response = requests.get(url, params=params)
    data = response.json()
    articles = data["articles"]
    
    lst_news = []
    i=0
    for article in articles[:depth]:
        time.sleep(5)
        i+=1
        url = article["url"]
        request = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True)
        soup = BeautifulSoup(request.text, "html.parser")
        cnt = soup.find_all("body")[0].text
        lst_news.append({
            "info_id": f"n{i}",
            "news_title": article["title"],
            "news_description": summarize_groq(cnt),
            "date": article["publishedAt"][:10],
            "source": article["source"]["name"]
        })

    return lst_news

def about_company_analysis(company_name,news_API):
    prompt = "Name the major competitors of the company {company_name}, please give the answer in a list format of python, and keep the company names in it in single quotes, eg ['company1', 'company2', 'company3'] "
    word = summarize_groq(groq_API_KEY, prompt.format(company_name=company_name))
    lst_competitors = list(eval(word))
    lst_content = []
    for competitor in lst_competitors:
        lst_content += company_dna_newsAPI(competitor, news_API, depth=2)

    return lst_content

def financial_health_analysis(company_name):
    # Code to analyse the company's financial health and performance
    pass


def competitive_position_analysis(company_name):
    # Code to analyse the company's competitive position in the industry
    pass


def view(lst_news):
    for news in lst_news:
        for key, value in news.items():
            print(f"{bold(key)}: {value}")
        print("-" * 50)


# start_time = time.time()
# print()
# view(company_dna_newsAPI(company_name, news_API))
# print("\n\n")
# print(f"Execution time: {time.time() - start_time} seconds")

# test case ==================================================================
# lst_news = company_direct_news_analysis(company_name)
# view(lst_news)

# url = "https://news.google.com/rss/articles/CBMihwFBVV95cUxOQ2syWGhmZU10YXdaWk9vWlpoaWlsOXp3SGg3TXZFdEFyQm9waHZfOUFIOVAtenNFM1RJTk84cXFEOU1ZNzNMZ0VVNm5vX1pPSE0zMlU4bTZRcTNtNmNTZERHR1hCbVNFM2tFNC01Z2ZTeF9qVmppa2p0clNWRUV4b1ZWck9wMUE?oc=5"
# import httpx

# from playwright.sync_api import sync_playwright

# with sync_playwright() as p:
#     browser = p.chromium.launch()
#     page = browser.new_page()

#     page.goto(url)

#     print(page.content())


# request = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True)
# request.encoding = "utf-8"
# soup = BeautifulSoup(request.text, "html.parser")
# print(soup.prettify())
# # print(request.content)
# print()
# print(request.url)


# def utilities_and_industry_analysis(company_name):
#     # Code to analyse the company's utilities and industry, and then search for its related news.
#     pass

# view(company_dna_newsAPI(company_name, news_API))


view(about_company_analysis(company_name,news_API))