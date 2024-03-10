from yahoofinancials import YahooFinancials as yf
import pandas as pd
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from typing import Type
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("darkgrid")
matplotlib.rcParams['font.size'] = 14
matplotlib.rcParams['figure.figsize'] = (15, 5)
matplotlib.rcParams['figure.facecolor'] = '#00000000'

from secret_api_key import openaikey

def get_company_data(company_ticker, start_date, end_date, time_interval):
    'Used to get financial data from Yahoo Finance' 
    company_df = pd.DataFrame(yf(company_ticker).get_historical_price_data(
    start_date=start_date, end_date=end_date, time_interval=time_interval)[company_ticker]['prices'])[['adjclose', 'formatted_date']]
    return company_df

def plot_company_data(company_ticker, start_date, end_date, time_interval):
    'Used to plot financial data from Yahoo Finance when the user asks it' 
    company_df = pd.DataFrame()
    for company in company_ticker:
        c_df = pd.DataFrame(yf(company).get_historical_price_data(
        start_date=start_date, end_date=end_date, time_interval=time_interval)[company]['prices'])[['adjclose', 'formatted_date']]
        c_df['company_name'] = company
        company_df = pd.concat([company_df, c_df])
    sns.lineplot(data=company_df, x='formatted_date', y='adjclose', hue='company_name')
    plt.xticks(rotation=75)
    plt.title(f'{company_ticker} Performance on {time_interval} Basis')
    plt.xlabel('Date')
    plt.ylabel('Adj Close Price')


class StockData(BaseModel):
    company_ticker: str = Field(description="The company name on the stock market. 'AAPL' is Apple for example") 
    start_date: str = Field(description="The start date from which gathering data")
    end_date: str = Field(description="The end data to gather data. It is not included in the research.")
    time_interval: str = Field(description="The time interval of dates, it can be: 'daily', 'monthly', 'weekly'") 

class PlotStockData(BaseModel):
    company_ticker: list = Field(description="A list containing the companies name on the stock market. 'AAPL' is Apple for example") 
    start_date: str = Field(description="The start date from which gathering data")
    end_date: str = Field(description="The end data to gather data. It is not included in the research.")
    time_interval: str = Field(description="The time interval of dates, it can be: 'daily', 'monthly', 'weekly'") 

class CompanyData(BaseTool):
    name = 'company_data'
    description = '''Tool used to get financial data about adjusted closing price of one or more companies in a defined period.
    This tool must be used when the user asks for financial information.'''
    args_schema: Type[BaseModel] = StockData 

    def _run(self, company_ticker: str, start_date: str, end_date: str, time_interval: str):
        "Use the tool"
        final_df = get_company_data(company_ticker, start_date, end_date, time_interval)
        return final_df 
    def _arun(self, company_ticker: str, st_date: str, e_date: str, time_interval: str):
        "Use the tool asynchronously"
        return NotImplementedError('get_company_data does not support async') 
    
class PlotCompanyData(BaseTool):
    name = 'plot_company_data'
    description = '''Tool used to plot financial data about adjusted closing price of one or more companies in a defined period only when explicitly asked by the user.
    Use it only if the user uses terms to display a graph, like "show", "plot" and similar.
    It must return the Python code to create the chart only. 
    DO NOT add anything else in the answer, like "here is the plot". Return the graph only. It is fundamental.'''
    args_schema: Type[BaseModel] = PlotStockData 

    def _run(self, company_ticker: str, start_date: str, end_date: str, time_interval: str):
        "Use the tool"
        return plot_company_data(company_ticker, start_date, end_date, time_interval)
    def _arun(self, company_ticker: str, st_date: str, e_date: str, time_interval: str):
        "Use the tool asynchronously"
        return NotImplementedError('get_company_data does not support async') 