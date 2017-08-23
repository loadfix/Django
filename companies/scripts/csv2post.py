import json
import urllib3
import urllib.request
from urllib.parse import quote
import csv
import traceback
import datetime
from requests.utils import requote_uri
import traceback
from bs4 import BeautifulSoup
import signal


companies_url = "http://127.0.0.1:8000/companies/api/companies/"
directors_url = "http://127.0.0.1:8000/companies/api/directors/"
ticker_url = "http://localhost:8000/companies/api/ticker/"
boards_url = "http://localhost:8000/companies/api/boardmembers/"

nasdaq_url = "http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NASDAQ&render=download"
nyse_url = "http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NYSE&render=download"
amex_url = "http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=AMEX&render=download"
asx_url = "http://www.asx.com.au/asx/research/ASXListedCompanies.csv"
hkse_url = "https://www.hkex.com.hk/eng/market/sec_tradinfo/stockcode/eisdeqty.htm"


nasdaq_csv_file = 'nasdaq.csv'
amex_csv_file = 'amex.csv'
nyse_csv_file = 'nyse.csv'
asx_csv_file = 'asx.csv'
hkse_csv_file = 'hkse.csv'

error_messages = []
debug = True

independent_director_titles = [
    "Independent Chairman of the Board",
    "Independent Chairman of the Board of Trustees",
    "Independent Director",
    "Independent Non-Executive Chairman of the Board of Responsible Entity",
    "Independent Non-Executive Chairperson of the Board",
    "Independent Non-Executive Chairman of the Board",
    "Independent Non-Executive Director",
    "Independent Non-Executive Director, Company Secretary",
    "Independent Trustee",
    "Non-Executive Director",
    "Non-Executive Chairman",
    "Non-Executive Chairman of the Board",
    "Non-Executive Deputy Chairman of the Board",
    "Non-Executive Independent Chairman of the Board",
    "Non-Executive Independent Director",
    "Non-Executive Independent Director of Responsible Entity",
    "Non-Executive Member of the Board of Directors",
    "Member of the Supervisory Board",

    "Lead Independent Non-Executive Director",
    "IndependentChairman of the Board",
    "Company Secretary, Non-Executive Director, Investor Relations Contact Officer"
]

director_titles = [
    "Chairman",
    "Chairman of the Board",
    "Chairman of the Board, Chief Executive Officer",
    "Chairman of the Executive Board",
    "Deputy Chairman of the Board",
    "Director",
    "Director of Responsible Entity",
    "Executive Chairman of the Board",
    "Executive Chairman of the Board, Chief Executive Officer",
    "Executive Chairman of the Board, Company Secretary",
    "Chairman of the Supervisory Board",
    "Executive Chairman of the Board, Founder",
    "Executive Director",
    "Executive Director, Company Secretary",
    "Executive Non-independent Director",
    "Member of the Board of Directors",
    "Member of the Supervisory Board",
    "Member of the Management Board",
    "Trustee",
    "Non-Independent Non-Executive Director",
    "Acting Executive Chairman of the Board, Chief Executive Officer, Managing Director",
    "Finance Director, Managing Director, Executive Director, Company Secretary"
]
director_titles.extend(independent_director_titles)

independent_director_suffix = [
    ", Non-Executive Director",
    ", Director of Responsible Entity",
    ", Independent Non-Executive Director"
]
director_suffix = [
    ", Director",
    ", Trustee",
    ", Executive Director",
    ", Board Member"
]
director_suffix.extend(independent_director_suffix)


mens_names = [
    "James", "Michael", "Peter", "Silvio", "David",  "Robert", "Grant", "John", "Geoffrey", "Ross", "Paul", "Wayne",
    "Keith", "Christopher", "Andrew", "Adam", "Matt", "Brett", "Stuart", "Anthony", "Craig", "Frank", "Vincent",
    "Marcus", "Hamish", "Stephen", "Philip", "Bryce", "Ivan", "Alvin", "Alan", "Simon", "Geoff", "Neil", "Nathan",
    "Jeremy", "Charles", "Gregory", "Alasdair", "Ben", "Jeremy", "Peter", "Brian", "Brad", "Graeme", "Colin", "Harald",
    "Daniel", "Leonard", "Jonathan", "Barry", "Scott", "Dennis", "Rodney", "Thomas", "Darren", "Nicholas", "Raymond",
    "Malcolm", "Gavin",

]
womens_names = [
    "Natalya", "Rosemary", "Rebekah", "Elizabeth", "Jacqueline", "Belinda", "Diane", "Heather", "Linda", "Anna", "Liza",
    "Karen", "Nancy", "Phillipa", "Rebecca",
]



header = {
    'Content-Type': 'application/json'
    }

company_file = "companies.csv"
director_file = "directors.csv"


# Catch Control-C
start_time = datetime.datetime.now()
def signal_handler(signal, frame):
   end_time = datetime.now()
   print(str(end_time - start_time) + " seconds elapsed")
   sys.exit(0)


# Catch Control-C, flush buffer to CSV
signal.signal(signal.SIGINT, signal_handler)

class Company:

    def __init__(self):
        company_id = -1
        name = ""
        founded = ""
        market_cap = -1
        website = ""
        sector = ""
        industry = ""
        last_updated = datetime.datetime.now()
        is_current = True

class Director:

    def __init__(self):
        director_id = -1
        name = ""
        age = -1
        sex = ""
        birth_date = ""
        title = ""
        start_date = ""
        is_independent = False



def getJSONData(url):
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    return json.loads(r.data.decode('utf-8'))

def get_csv_files():

    print("In get files")
    urllib.request.urlretrieve(asx_url, asx_csv_file)
    urllib.request.urlretrieve(nyse_url, nyse_csv_file)
    urllib.request.urlretrieve(nasdaq_url, nasdaq_csv_file)
    urllib.request.urlretrieve(amex_url, amex_csv_file)

    # Do something special for HKSE as it is a web page
    with open(hkse_csv_file, 'w') as csvfile:
        fieldnames = ['symbol', 'name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        http = urllib3.PoolManager()
        r = http.request('GET', hkse_url)
        soup = BeautifulSoup(r.data, "html.parser")
        stock_table = soup.find_all('table')[0]('td')[0]('tr')[0]('tr')[3]('tr')
        for x in range(1, len(stock_table)):
            symbol = stock_table[x]('td')[0].text.strip()
            stock = stock_table[x]('td')[1].text.strip()
            writer.writerow({'symbol': symbol, 'name': stock})

def ConvertMC(market_cap):

    if market_cap.startswith("$") and market_cap.endswith("M"):
        try:
            market_cap = float(market_cap.split("$")[1].split("M")[0]) * 1000000
        except Exception as e:
            print
            str(e)

    elif market_cap.startswith("$") and market_cap.endswith("B"):
        try:
            market_cap = float(market_cap.split("$")[1].split("B")[0]) * 1000000000
        except Exception as e:
            print
            str(e)
    else:
        market_cap = 0

    return float(market_cap)

#################################
# Add the companies and tickers #
#################################
def add_companies():

    with open(company_file, 'rt', encoding='utf8') as f:
        reader = csv.reader(f)
        company_list = list(reader)

    http = urllib3.PoolManager()

    for company in company_list:

        company_name = company[1].strip()

        # Check if company exists
        try:
            url = requote_uri(companies_url + "?format=json&search=" + company_name)
            r = http.request('GET', url)

            jsondata = json.loads(r.data.decode('utf-8'))

            if len(jsondata) == 0:
                print("Adding company: " + company_name)

                # Set Exchagne ID
                if company[8] == "AMEX":
                    exchange = "1"

                elif company[8] == "NYSE":
                    exchange = "2"

                elif company[8] == "NASDAQ":
                    exchange = "3"

                elif exchange is None:
                    print("Could not find exchange")
                    break

                print("Exchange: " + exchange)

                # Create json payload
                payload = {
                    'name': company[1].strip(),
                    'market_cap': ConvertMC(company[3]),
                    'sector': company[5],
                    'industry': company[6],
                    'exchange': exchange,
                    'founded': "0000",
                    'website': "None"
                }

                try:
                    r = http.urlopen('POST', companies_url, headers=header, body=json.dumps(payload))

                    # Get Company ID
                    jsondata = json.loads(r.data.decode('utf-8'))
                    company_id = str(jsondata['id'])
                    print("Created company: " + company_name + "   ID: " + company_id)

                except Exception as e:
                    print("An error occurred: " + str(e))

            else:
                # Get company ID
                company_id = str(jsondata[0]['id'])
                print("Company exists: " + company_name + "  (ID: " + company_id + ")")

            # Get Ticker List
            url = requote_uri(ticker_url + "?format=json&ticker=" + company[0].strip())
            r = http.request('GET', url)

            # If ticker does not exist
            tickers = json.loads(r.data.decode('utf-8'))

            if len(tickers) == 0:
                print("Ticker not found, adding ticker " + company[0].strip() + " to company " + company_name)
                # Add ticker
                payload = {
                    'ticker': company[0].strip(),
                    'exchange': exchange,
                    'company': company_id,
                }
                r = http.urlopen('POST', ticker_url, headers=header, body=json.dumps(payload))
            else:
                print("Found tickers: " + company[0].strip())

        except Exception as e:
            print(str(e))


################################
# Add the directors and boards #
################################
def add_directors():
    with open(director_file, 'rt', encoding='utf8') as f:
        reader = csv.reader(f)
        director_list = list(reader)


    http = urllib3.PoolManager()

    for director in director_list:

        director_name = director[2].strip()
        director_company = director[1].strip()
        director_ticker = director[0].strip()
        director_title = director[3].strip()

        if director[4].strip() == 0:
            director_independent = False
        else:
            director_independent = True

        if director[5].strip() == "":
            if debug:
                print("No age found, blanking")
            director_age = ""
        else:
            director_age = str(director[5].strip())

        director_startdate = director[6].strip() + "-01-01"
        director_id = None

        # Check if director exists
        try:
            # This logic assumes that there is only one director with the same name and the same age
            url = requote_uri(directors_url + "?format=json&name=" + director_name + "&age=" + director_age)
            r = http.request('GET', url)

            jsondata = json.loads(r.data.decode('utf-8'))

            if len(jsondata) == 0:
                print("Adding director: " + director_name + " (" + director_age + ")")

                # Create json payload
                payload = {
                    'name': director[2].strip(),
                    'age': director_age
                }

                # Add Director
                r = http.urlopen('POST', directors_url, headers=header, body=json.dumps(payload))

                # Get Director ID
                jsondata = json.loads(r.data.decode('utf-8'))
                director_id = str(jsondata['id'])

            else:
                print("Found director: " + director_name + " - " + director_age)
                # Get Director ID
                director_id = str(jsondata[0]['id'])

        except Exception as e:
            print("Somthing bad happened")
            traceback(e)

        # Search for director on company board
        if director_id is None:
            print("Could not find director_id")
            break

        try:
            # Get Company ID
            url = requote_uri(companies_url + "?format=json&name=" + director_company)
            jsondata = getJSONData(url)

            # Found the company
            if len(jsondata) != 0:
                company_id = str(jsondata[0]['id'])
                print("Found ID: " + company_id + " for company " + director_company)
            else:
                print("ERROR: Company not found!")
                continue

            url = requote_uri(boards_url + "?format=json&company=" + company_id + "&director=" + director_id)
            jsondata = getJSONData(url)

            if len(jsondata) == 0:
                # Director is not on the board
                payload = {
                    'company': company_id,
                    'director': director_id,
                    'start_date': director_startdate,
                    'is_current': "True",
                    'is_independent': director_independent,
                    'title': director_title
                }
                r = http.urlopen('POST', boards_url, headers=header, body=json.dumps(payload))

                if r.status == 201:
                    print("Added director " + director_name + " to company " + director_company)
                else:
                    print("An error ocurred added boardmember")


        except Exception as e:
            print(str(e))


###############
# New Section #
# #############
def getCompanyFromReuters(symbol, exchange):

    if exchange == "AMEX":
        suffix = ".A"
    if exchange == "ASX":
        suffix = ".AX"
    if exchange == "NYSE":
        suffix = ".N"
    if exchange == "NASDAQ":
        suffix = ".O"

    reuters_url = "http://www.reuters.com/finance/stocks/overview?symbol="
    url = requote_uri(reuters_url + symbol + suffix)

    http = urllib3.PoolManager()
    r = http.request('GET', url)
    soup = BeautifulSoup(r.data, 'html.parser')

    try:
        name = soup.find_all('h1')[0].text.split('(')[0]
    except Exception as e:
        print(str(e))
        print("Could not find company " + symbol + " at Reuters")
        return None

    try:
        market_cap = soup.find('tbody').find_all('td')[3].text
    except Exception as e:
        print(str(e))
        print("Could not retrieve market cap for comapany: " + symbol + "." + suffix)

    # Create a new company object
    company = Company()

    # Remove semi commas from company nammes
    company.name = name.replace(';','')

    # Reuters expresses market capitalisation as $38,206.23 (millions)
    try:
        company.market_cap = float(market_cap.strip().split('$')[1].replace(',','')) * 1000000
    except Exception as e:
        print("Could not calcualte market cap for " + company.name)
        company.market_cap = -1

    print("Found company at Reuters: " + company.name)

    return company

##################################
# Adds a company to the database #
##################################
def add_company(company):

    payload = {
        'name': company.name,
        'market_cap': company.market_cap,
        'sector': "unknown",
        'industry': "unknown",
        'founded': "0000",
        'website': "None"
    }

    http = urllib3.PoolManager()
    r = http.urlopen('POST', companies_url, headers=header, body=json.dumps(payload))
    jsondata = json.loads(r.data.decode('utf-8'))

    company.company_id = str(jsondata['id'])
    print("Created company: " + company.name + "   ID: " + company.company_id)

    # Return the newly created company with new company_id
    return company


def getCompanyIDByName(company):

    http = urllib3.PoolManager()
    url = requote_uri(companies_url + "?format=json&name=" + quote(company.name))
    r = http.request('GET', url)
    jsondata = json.loads(r.data.decode('utf-8'))

    if len(jsondata) == 0:
        # Company name not found
        company.company_id = -1
    else:
        # More than one company with the same name found
        company.company_id = jsondata[0]['id']

    return company

def postJSONData(url, payload):
    http = urllib3.PoolManager()
    return http.urlopen('POST', url, headers=header, body=json.dumps(payload))

def add_ticker(ticker, exchange, company):

    if exchange == "AMEX":
        ex = "1"
    if exchange == "NYSE":
        ex = "2"
    if exchange == "NASDAQ":
        ex = "3"
    if exchange == "ASX":
        ex = "4"

    # Check if this ticker is already associated with the company
    url = requote_uri(ticker_url + "?format=json&ticker=" + ticker + "&exchange=" + ex)
    jsondata = getJSONData(url)

    if len(jsondata) == 0:
        # Ticker does not exist, add it to the company
        payload = {
            'ticker': ticker,
            'exchange': ex,
            'company': company.company_id
        }
        r = postJSONData(ticker_url, payload)
        jsondata = json.loads(r.data.decode('utf-8'))

        print(jsondata)

        print("Added ticker " + ticker + " to company " + company.name)
    else:
        print("Ticker " + ticker + " already associated to company " + str(company.company_id))


def getDirectorSexFromName(name):

    for male_name in mens_names:
        if name.startswith(male_name + " "):
            return "M"

    for female_name in womens_names:
        if name.startswith(female_name + " "):
            return "F"

    return "U"

def isDirector(title):
    if title in director_titles:
        return True

    for suffix in director_suffix:
        if title.endswith(suffix):
            return True

    return False


def isIndependentDirector(title):
    if title in independent_director_titles:
        return True

    for suffix in independent_director_suffix:
        if title.endswith(suffix):
            return True

    return False

def getDiretorsFromReuters(ticker, exchange):

    """ Returns an array of directors """

    # Initialise array of directors
    director_array = []

    if exchange == "AMEX":
        suffix = ".A"
    if exchange == "ASX":
        suffix = ".AX"
    if exchange == "NYSE":
        suffix = ".N"
    if exchange == "NASDAQ":
        suffix = ".O"

    reuters_url = "http://www.reuters.com/finance/stocks/companyOfficers?symbol="
    url = requote_uri(reuters_url + ticker + suffix)

    http = urllib3.PoolManager()
    r = http.request('GET', url)
    soup = BeautifulSoup(r.data, 'html.parser')

    try:
        officer_table = soup.find('table')
        no_of_rows = len(officer_table.find_all('tr')) - 1

        if "Shares Traded" in officer_table.find_all('tr')[0].text:
            print("No officers found, skipping...")
            return None

    except Exception as e:
        print("Error getting directors for " + ticker + "." + exchange)
        return None

    for y in range(1, no_of_rows + 1):

        try:
            # Check company officers for director positions
            title = str(officer_table.find_all('tr')[y].find_all('td')[3].text.strip())
            #print("assigned title to: " + title)
        except Exception as e:
            print(str(e))
            continue

        if isDirector(title) is True:

            # Create a new director
            this_director = Director()

            #print("Found Director: " + title)
            this_director.title = title

            # Get name, age and sex of director
            this_director.name = str(officer_table.find_all('tr')[y].find_all('td')[0].text.strip()).replace('\xa0',' ')
            this_director.age = officer_table.find_all('tr')[y].find_all('td')[1].text.strip()
            if this_director.age == "":
                this_director.age = ""
            this_director.sex = getDirectorSexFromName(this_director.name)

            # Get start date
            if officer_table.find_all('tr')[y].find_all('td')[2].text.strip() != "":
                this_director.start_date = officer_table.find_all('tr')[y].find_all('td')[2].text.strip() + "-01-01"
            else:
                this_director.start_date = ""

            # Is this director independent?
            this_director.is_independent = isIndependentDirector(title)

            director_array.append(this_director)
        else:
            error_messages.append(title)


    return director_array


def getDirectorIDByName(director):

    print("DEBUG:")
    print("Age:" + str(director.age))

    if str(director.age) == "":
        url = requote_uri(directors_url + "?name=" + director.name)
    else:
        url = requote_uri(directors_url + "?name=" + director.name + "&age=" + str(director.age))


    jsondata = getJSONData(url)

    if len(jsondata) == 0:
        # Director not found
        director.director_id = -1

    elif len(jsondata) == 1:
        director.director_id = jsondata[0]['id']

    else:
        # More than one director was returned!!
        # Return the number of duplicates as a negative director_id
        director.director_id = 0 - len(jsondata)

    return director

def add_directors(company, ticker, exchange):
    if company.company_id is -1:
        print("Company ID is not set")
        return

    # Get first ticker from company
    url = requote_uri(boards_url + "?format=json&company=" + company.company_id)
    jsondata = getJSONData(url)

    # Check for exting board members
    if len(jsondata) is not 0:
        print("Company has existing board")
        for director in jsondata:
            print(jsondata[director]['title'])

        return

    # Else add the board members
    # Get list of directors from Reuters
    director_array = getDiretorsFromReuters(ticker, exchange)

    if director_array is not None:
        print("-----------------------------")
        print("Number of directors: " + str(len(director_array)))
        print("-----------------------------")

        # Search for the directors, add them if not found
        for director in director_array:
            print("Name: " + director.name)
            print("Age: " + director.age)

            # See if director already exists
            director = getDirectorIDByName(director)

            if director.director_id == -1:
                # Director not found, adding

                if str(director.age) == "":
                    payload = {
                        'name': director.name,
                        'sex': director.sex
                    }
                else:
                    payload = {
                        'name': director.name,
                        'age': director.age,
                        'sex': director.sex
                    }

                # Todo: Check return status
                r = postJSONData(directors_url, payload)
                jsondata = json.loads(r.data.decode('utf-8'))

                if debug:
                    print("Post Response:")
                    print(jsondata)

                director.director_id = str(jsondata['id'])

                # Check if object was created
                if debug:
                    print("created new director with ID:" + director.director_id + " for company ID: " + company.company_id)

                # Add director to board
                if str(director.start_date) == "":
                    payload = {
                        'company': company.company_id,
                        'director': director.director_id,
                        'title': director.title,
                        'is_independent': director.is_independent
                    }
                else:
                    payload = {
                        'company': company.company_id,
                        'director': director.director_id,
                        'title': director.title,
                        'start_date': director.start_date,
                        'is_independent': director.is_independent
                    }

                if debug:
                    print("Sending payload:")
                    print(payload)

                r = postJSONData(boards_url, payload)
                jsondata = json.loads(r.data.decode('utf-8'))
                print(jsondata)
                print("Added " + director.name + " to board of " + company.name )

            else:
                print("One or more directors exist with Name: " + director.name + " and Age: " + director.age)
    else:
        print("No directors found at " + company.name)

    if len(error_messages) is not 0:
        print("Non Director roles")
        for position in set(error_messages):
            print("===> " + position)

def process_company(ticker, exchange):
    # Get the correct name and market cap from Reuters
    this_company = getCompanyFromReuters(ticker, exchange)

    # Check if company already exists in the DB and set company ID
    this_company = getCompanyIDByName(this_company)

    if this_company is None:
        return

    if this_company.company_id is -1:
        # Company is not in database, add it
        print("Company not found in database, adding...")

        # Add the company
        this_company = add_company(this_company)

        # Add the company tickers
        add_ticker(ticker, exchange, this_company)

        # Add the company directors
        add_directors(this_company, ticker, exchange)

    else:
        print("Company " + this_company.name + " already exists, (" + str(this_company.company_id) + ")")

#######################################
# Lookup and add listed companies #
#######################################
def process_csv(csv_file, exchange):
    with open(csv_file, 'rt', encoding='utf8') as f:
        reader = csv.reader(f)
        company_list = list(reader)

    # SPECIFIC EXCHANGE FILE FORMATS
    if exchange == "AMEX":
        company_list = company_list[1:]
        ticker_column = 0

    if exchange == "ASX":
        company_list = company_list[3:]
        ticker_column = 1

    if exchange == "NYSE":
        company_list = company_list[1:]
        ticker_column = 0

    if exchange == "NASDAQ":
        company_list = company_list[1:]
        ticker_column = 0

    for company in company_list:
        process_company(company[ticker_column].strip(), exchange)


###################################
#             Runtime             #
###################################
#add_companies()
#add_directors()
#get_csv_files()

#process_csv(asx_csv_file,"ASX")
#process_csv(amex_csv_file,"AMEX")
process_csv(nyse_csv_file,"NYSE")
#process_csv(nasdaq_csv_file,"NASDAQ")