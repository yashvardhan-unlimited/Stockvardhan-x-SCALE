# imports ==================================================================
import openai   
import os
from dotenv import load_dotenv
from langchain.agents import create_agent
load_dotenv()
import requests
from bs4 import BeautifulSoup


# API keys =================================================================
news_API = os.getenv("news_API")




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

def summarize(data):
    # Code to summarize the data and extract key insights and trends.
    return data

def bold(text):
    # Code to bold the text.
    # color text to red
    return f"\033[1;31m{text}\033[0m"

def company_direct_news_analysis(company_name):
    # Code to analyse the company's products, accuisitions, and partnerships. or news directly related to comapny.
    link1 = f"https://news.google.com/rss/search?q=latest news related to company {company_name}"
    request = requests.get(link1)
    soup = BeautifulSoup(request.text, "xml")
    lst_news = []
    for i in range(10):
        lst_news.append({("info_id"): f"n{i+1}", 
                         ("news"): summarize(soup.find_all("item")[i].link.text),
                         ("date"): (soup.find_all("item")[i].pubDate.text)[:16],
                         ("source"): soup.find_all("item")[i].source.text
                        })


    return lst_news



def view(lst_news):
    for news in lst_news:
        print(f"{bold('News ID')}: {news['info_id']}")
        print(f"{bold('News')}: {news['news']}")
        print(f"{bold('Date')}: {news['date']}")
        print(f"{bold('Source')}: {news['source']}")
        print("-" * 50)
# test case ==================================================================
lst_news = company_direct_news_analysis(company_name)

request = requests.get("https://nvidianews.nvidia.com/news/nvidia-microsoft-windows-pcs-agents-rtx-spark")
soup = BeautifulSoup(request.content, "html.parser")
print(soup.find_all("body")[0].text)



def utilities_and_industry_analysis(company_name):
    # Code to analyse the company's utilities and industry, and then search for its related news.
    pass
def financial_health_analysis(company_name):
    # Code to analyse the company's financial health and performance
    pass

def competitive_position_analysis(company_name):
    # Code to analyse the company's competitive position in the industry
    pass

