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
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import create_agent
from typer import prompt


# API keys =================================================================
load_dotenv()
news_API = os.getenv("news_API")
groq_API_KEY = os.getenv("groq_API_KEY")
gemini_API_KEY = os.getenv("gemini_API_KEY")
fmp_API_KEY = os.getenv("fmp_API_KEY")
TAVILY_API_KEY = os.getenv("tavily")



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

# def summarize_gemini(data, prompt="Summarize the given article, and tell What is the news about, what happened, and the keypoints:"):
#     llm = ChatOpenAI(
#     model="gemini-2.0-flash",
#     api_key=gemini_API_KEY,
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
#     response = llm.invoke(f"{prompt} {data}")
#     return response.content

def summarize_local(data, prompt="Summarize the given article, and tell What is the news about, what happened, and the keypoints:"):
    llm = ChatOllama(
        model="llama3.1:latest",
        num_ctx= 4096,
        temperature=0.2
    )
    response = llm.invoke(f"{prompt} {data}")
    return response.content


def bold(text):
    # Code to bold the text.
    # color text to red
    return f"\033[1;31m{text}\033[0m"


# def company_dna_scraping(company_name):
#     # Code to analyse the company's products, accuisitions, and partnerships. or news directly related to comapny.
#     link1 = f"https://news.google.com/rss/search?q=latest+news+related+to+company+{company_name}"
#     request = requests.get(link1,allow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
#     soup = BeautifulSoup(request.text, "xml")
#     lst_news = []
#     for i in range(1):
#         request2 = requests.get()
#         soup2 = BeautifulSoup(request2.content, "html.parser")

#         lst_news.append({("info_id"): f"n{i+1}", 
#                          ("news"): (soup2.find_all("item")[i]),
#                          ("date"): (soup.find_all("item")[i].pubDate.text)[:16],
#                          ("source"): soup.find_all("item")[i].source.text
#                         })

#     return lst_news
#     # return soup.prettify()


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
        # time.sleep(5)
        i+=1
        url = article["url"]
        request = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True)
        soup = BeautifulSoup(request.text, "html.parser")
        cnt = soup.find_all("body")[0].text
        lst_news.append({
            "info_id": f"n{i}",
            "news_title": article["title"],
            "news_description": summarize_local(cnt),
            "date": article["publishedAt"][:10],
            "source": article["source"]["name"]
        })

    return lst_news

def competitive_position_analysis(company_name,news_API, depth = 5):
    prompt = "Name the major competitors of the company {company_name}, please give the answer in a list format of python, and keep the company names in it in single quotes, eg ['company1', 'company2', 'company3'] "
    word = summarize_groq(groq_API_KEY, prompt.format(company_name=company_name))
    lst_competitors = list(eval(word))
    lst_content = []
    for competitor in lst_competitors:    
        content = company_dna_newsAPI(competitor, news_API, depth)
        for dc in content:
            dc["competitor company"] = competitor
        lst_content += content

    return lst_content



# def about_company_analysis(company_name):
#     # Code to analyse the company's competitive position in the industry
#     pass


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


def save_in_json(lst_news, company_name):
    import json
    new = {company_name: lst_news}
    with open(f"{company_name}_news.json", "w") as f:
        json.dump(new, f, indent=4)

import requests


def financial_health_analysis(company_name, fmp_api_key, groq_api_key):

    # ---------------------------
    # Get Stock Symbol using AI
    # ---------------------------

    prompt = (
        f"What is the stock symbol of {company_name}? "
        f"For example Apple -> AAPL, NVIDIA -> NVDA. "
        f"Return ONLY the stock symbol."
    )

    symbol = summarize_groq(groq_api_key, prompt).strip()

    # Handle AI responses like:
    # "NVDA", "The symbol is NVDA", etc.
    symbol = symbol.split()[0]
    symbol = symbol.replace(",", "").replace(".", "").upper()

    try:

        # ---------------------------
        # Income Statement
        # ---------------------------

        income_data = requests.get(
            f"https://financialmodelingprep.com/stable/income-statement?symbol={symbol}&limit=2&apikey={fmp_api_key}"
        ).json()

        if not income_data:
            return {
                "error": f"No income statement found for {symbol}",
                "symbol": symbol
            }

        # ---------------------------
        # Balance Sheet
        # ---------------------------

        balance_data = requests.get(
            f"https://financialmodelingprep.com/stable/balance-sheet-statement?symbol={symbol}&limit=1&apikey={fmp_api_key}"
        ).json()

        # ---------------------------
        # Cash Flow
        # ---------------------------

        cashflow_data = requests.get(
            f"https://financialmodelingprep.com/stable/cash-flow-statement?symbol={symbol}&limit=1&apikey={fmp_api_key}"
        ).json()

        # ---------------------------
        # Ratios
        # ---------------------------

        ratios_data = requests.get(
            f"https://financialmodelingprep.com/stable/ratios?symbol={symbol}&limit=1&apikey={fmp_api_key}"
        ).json()

        # ---------------------------
        # Quote / Market Data
        # ---------------------------

        quote_data = requests.get(
            f"https://financialmodelingprep.com/stable/quote?symbol={symbol}&apikey={fmp_api_key}"
        ).json()

        # ---------------------------
        # Dividend Data
        # ---------------------------

        dividends_data = requests.get(
            f"https://financialmodelingprep.com/stable/dividends?symbol={symbol}&apikey={fmp_api_key}"
        ).json()

        # ---------------------------
        # Extract Latest Records
        # ---------------------------

        income = income_data[0]

        previous_income = (
            income_data[1]
            if len(income_data) > 1
            else {}
        )

        balance = (
            balance_data[0]
            if balance_data
            else {}
        )

        cashflow = (
            cashflow_data[0]
            if cashflow_data
            else {}
        )

        ratios = (
            ratios_data[0]
            if ratios_data
            else {}
        )

        quote = (
            quote_data[0]
            if quote_data
            else {}
        )

        # ---------------------------
        # Revenue Growth
        # ---------------------------

        revenue_growth = None

        if previous_income.get("revenue", 0):

            revenue_growth = (
                (
                    income.get("revenue", 0)
                    - previous_income.get("revenue", 0)
                )
                / previous_income.get("revenue", 1)
            ) * 100

        # ---------------------------
        # Profit Growth
        # ---------------------------

        profit_growth = None

        if previous_income.get("netIncome", 0):

            profit_growth = (
                (
                    income.get("netIncome", 0)
                    - previous_income.get("netIncome", 0)
                )
                / previous_income.get("netIncome", 1)
            ) * 100

        # ---------------------------
        # ROCE Calculation
        # ---------------------------

        operating_income = income.get(
            "operatingIncome",
            0
        )

        total_assets = balance.get(
            "totalAssets",
            0
        )

        current_liabilities = balance.get(
            "totalCurrentLiabilities",
            0
        )

        capital_employed = (
            total_assets
            - current_liabilities
        )

        roce = None

        if capital_employed:
            roce = (
                operating_income
                / capital_employed
            ) * 100

        # ---------------------------
        # Dividend Yield
        # ---------------------------

        dividend_yield = None

        if dividends_data and quote:

            latest_dividend = dividends_data[0].get(
                "adjDividend",
                0
            )

            share_price = quote.get(
                "price",
                0
            )

            if share_price:
                dividend_yield = (
                    latest_dividend
                    / share_price
                ) * 100

        # ---------------------------
        # Final Dictionary
        # ---------------------------

        return {

            "company_name": company_name,
            "symbol": symbol,

            # Revenue
            "revenue": income.get("revenue"),
            "revenue_growth_percent": revenue_growth,

            # Profit
            "net_profit": income.get("netIncome"),
            "profit_growth_percent": profit_growth,

            # Earnings
            "eps": income.get("eps"),
            "ebitda": income.get("ebitda"),

            # Balance Sheet
            "total_assets": balance.get("totalAssets"),
            "total_liabilities": balance.get("totalLiabilities"),
            "cash": balance.get("cashAndCashEquivalents"),
            "total_debt": balance.get("totalDebt"),
            "shareholders_equity": balance.get(
                "totalStockholdersEquity"
            ),

            # Cash Flow
            "operating_cash_flow": cashflow.get(
                "operatingCashFlow"
            ),
            "free_cash_flow": cashflow.get(
                "freeCashFlow"
            ),
            "capital_expenditure": cashflow.get(
                "capitalExpenditure"
            ),

            # Ratios
            "roe": ratios.get("returnOnEquity"),
            "roce": roce,
            "current_ratio": ratios.get("currentRatio"),
            "debt_to_equity": ratios.get("debtEquityRatio"),
            "pe_ratio": ratios.get("priceEarningsRatio"),
            "pb_ratio": ratios.get("priceToBookRatio"),
            "interest_coverage": ratios.get(
                "interestCoverage"
            ),

            # Dividend
            "dividend_yield_percent": dividend_yield,

            # Market Data
            "market_cap": quote.get("marketCap"),
            "share_price": quote.get("price")
        }

    except Exception as e:

        return {
            "error": str(e),
            "symbol": symbol
        }

# ===========================================================================================================================================
# ===========================================================================================================================================
# ===========================================================================================================================================
# ===========================================================================================================================================
# ===========================================================================================================================================
# ===========================================================================================================================================
# ===========================================================================================================================================


# Main Agent function declaration 

def stock_ai_research_agent(
    company_name: str,
    investment_horizon: str,
    investment_amount: float,
    risk_tolerance: str,
    financial_data: dict,
    latest_news: list,
    competitor_news: list
):

    # -----------------------------
    # 1. Gemini Model
    # -----------------------------
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.4,
    google_api_key=gemini_API_KEY
    )

    # -----------------------------
    # 2. Web Search Tool (ONLY if needed)
    # -----------------------------
    search_tool = TavilySearchResults(api_key=TAVILY_API_KEY)

    tools = [search_tool]

    # -----------------------------
    # 3. Agent
    # -----------------------------
    agent = create_agent(
        tools=tools,
        llm=llm,
        verbose=True
    )

    # -----------------------------
    # 4. Prompt
    # -----------------------------
    prompt = f"""
You are a senior equity research analyst at a hedge fund.

You are given COMPLETE DATA. Most answers should be based on it.

ONLY use web search if:
- something important is missing
- or you need recent breaking news

Otherwise rely on provided data.

=====================
USER INPUT
=====================
Company: {company_name}
Investment Horizon: {investment_horizon}
Investment Amount: {investment_amount}
Risk Tolerance: {risk_tolerance}

=====================
FINANCIAL DATA
=====================
{json.dumps(financial_data, indent=2)}

=====================
LATEST COMPANY NEWS
=====================
{json.dumps(latest_news, indent=2)}

=====================
COMPETITOR NEWS
=====================
{json.dumps(competitor_news, indent=2)}


=====================
TASK
=====================

1. Analyze financial strength (growth, debt, cash flow)
2. Analyze news sentiment (positive / negative / neutral)
3. Compare with competitors
4. Identify risks and opportunities
5. Decide if external web search is needed
6. Provide final investment decision

=====================
OUTPUT FORMAT
=====================

Write a HUMAN-READABLE REPORT (NOT JSON)

Include:

- Summary
- Financial Analysis
- News Impact Analysis
- Competitor Comparison
- Risk Analysis
- Opportunity Analysis
- Final Recommendation (BUY / HOLD / SELL)
- Expected performance range (NOT exact price)
- Clear reasoning step-by-step

Be realistic and not overly optimistic.
If uncertain, say so clearly.
"""

    # -----------------------------
    # 5. Run Agent
    # -----------------------------
    response = agent.run(prompt)

    return response

# test data ================================================================
company_name = "NVIDIA"
investment_horizon = "5 years"
investment_amount = "10000 USD"
risk_tolerance = "medium"

# test case ================================================================

financial_data = financial_health_analysis(company_name, fmp_API_KEY, groq_API_KEY)
latest_news = company_dna_newsAPI(company_name, news_API, 15)
competitor_news = competitive_position_analysis(company_name, news_API, 5)


result = stock_ai_research_agent(
    company_name,
    investment_horizon,
    investment_amount,
    risk_tolerance,
    financial_data,
    latest_news,
    competitor_news
)

print("Stockvardhan.com","="*50)
print()
print(result)