import requests
import bs4
import matplotlib.pyplot as plt
import smtplib
from email.mime.multipart import MIMEMultipart   # for emailing reports
from email.mime.text      import MIMEText
from alpha_vantage.timeseries import TimeSeries # API for real-time quote
from pprint import pprint

API_URL = "https://www.alphavantage.co/query"



def isValidNews(input):
    """

    function looks for specific markers of news considered valid such as report filing
    in order to determine if the news is credible

    """
    if ("Current Report Filing" in input):
        return False
    elif ("Securities Registration Statement" in input):
        return False
    elif ("Statement of Ownership" in input):
        return False
    else:
        return True



class Company:
    '''
        Each instance of a company object will know it's ticker,
        it's price, and the headline of the article that was released
        that specific day.
    '''
    ticker = ""
    price = 0
    newsHeadline = ""


    #Intializer for Company object
    def __init__(self, t, p, n):
        self.ticker = t
        self.price = p
        self.newsHeadline = n

    def string(self):
        "returns the ticker, price and headline as a report"


        return self.ticker + ": $" + str(self.price) + "\nHeadline: " + self.newsHeadline



API_URL = "https://www.alphavantage.co/query"

ticks= ["TSLA","MSFT"] # list for custom report searches
for ticker in ticks:
    """
    Dictionary that contains the API data from alpha vantage. It takes in a list of
    Tickers and for every ticker, reveals the information. 
    """
    data={
        "function": "TIME_SERIES_INTRADAY",
        "symbol":ticker,
        "interval": "15min",
        "datatype":"json",
        "apikey": "A29TNL9G73HYIBAQ"
    }
    response= requests.get(API_URL,data) # get response from the api url
    data= response.json()
    print(ticker)
    ts = TimeSeries(key='A29TNL9G73HYIBAQ', output_format='pandas')
    data, meta_data = ts.get_intraday(symbol=ticker,interval='90 min', outputsize='full')
    pprint(data.head(2))
    data['4. close'].plot() # plots closing price from alpha vantage through matplot lib
    plt.title('Intraday Times Series for the'+ ticker +' stock (60 days)') # title of the visualization
    plt.show()



listCompanies = []

a = 1

# used idea for scraper from github project.

while (a < 3): # controls the amount of pages I want during the report generation
    print ("Fetching data from page " + str(a) + "...")
    #Download the page
    news = requests.get('http://investorshub.advfn.com/boards/recentnews.aspx?page=' + str(a))
    news.raise_for_status()
    #Passes html content to BeautifulSoup and creates a new object
    stockNews = bs4.BeautifulSoup(news.text, "lxml")
    #Selects the <a> tagged elements of the website within the table
    #The table is where the news feed is
    elems = stockNews.select('table a')

        #Remove first two empty links
    if (len(elems) > 0):
        elems.remove(elems[0])
        elems.remove(elems[0])

        '''Loop through the company tickers, prices, and news headline, and create
            new objects'''
        x = 0
        while (x < len(elems) - 3):
            #print x
            if (x % 3 == 0):
                try:
                    if ((float(elems[x+1].getText().strip()) < 10.0)):
                        if (isValidNews(elems[x+2].getText().strip())):
                            listCompanies.append(Company(elems[x].getText().strip(),
                            float(elems[x+1].getText().strip()),
                            elems[x+2].getText().strip()))
                except ValueError:
                    elems.insert(x+1, elems[x])
            x = x + 1
        a = a + 1
    else:
        a = a + 1

myCompanies = []

#Use the list to remove all the tickers that I do not want

for b in range(len(listCompanies) - 1):
    if (0.1 < listCompanies[b].price < 10.0):
        myCompanies.append(listCompanies[b])


for x in myCompanies:
    print (x.string())
    print ("")

"""
Code below controls where the message will be sent with credentials to email

"""
from_address= "xxxxxxxxxxxxxxxxx"  # from and to sends an email back to me
to_address= "xxxxxxxxxxxxxxxxxxx"
subject_heading="Investment Report"
msg= MIMEMultipart()
msg["from"]= from_address
msg["to"]= to_address
msg["subject"]= subject_heading

body_of_message= myCompanies  # sends a message with the report to my email


msg.attach(MIMEText(body_of_message,'plain'))

server= smtplib.SMTP('smtp.gmail.com',587)
server.starttls()
server.login(from_address,'xxxxxxxxxxx') # log in, to gmail cannot. password is voided out.
text= msg.as_string()
server.sendmail(from_address,to_address,text)
server.quit()

