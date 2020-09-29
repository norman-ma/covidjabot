import requests
import datetime
from bs4 import BeautifulSoup


def extract(line):
    line = line[1:]
    if len(line) == 1:
        data = {"24 Hours": to_val(line[0])}
        return data
    if len(line) == 2 or line[2] == "":
        data = {"24 Hours": to_val(line[0]), "Overall": to_val(line[1])}
        return data
    if len(line) == 3:
        data = {"24 Hours": to_val(line[0]), "Overall": to_val(line[1]), "Notes": to_val(line[2])}
        return data
    else:
        return line


def search_extract(table_data, keyword):
    for row in table_data:
        if row[0] == keyword:
            return extract(row)


def is_value(val):
    return val.replace(',', '').isnumeric() or '*' in val or "day" in val or "year" in val


def to_val(val):
    if val.replace(',', '').replace('*', '').isnumeric():
        return int(val.replace(',', '').replace('*', ''))
    elif val == "":
        return 0
    else:
        return val


class CovidData:

    def __init__(self, date, raw):
        self.date = date
        self.data = {}
        header = ""

        for line in raw:
            # header
            if not is_value(line[1]) and not is_value(line[2]):
                header = line[0]
                self.data[header] = {}
            # data
            else:
                subheader = line[0]
                self.data[header][subheader] = extract(line)

    def record_to_text(self, title, data):
        out = title + "\n"
        vals = [("24 Hours", data.get("24 Hours")), ("Overall", data.get("Overall")), ("Notes", data.get("Notes"))]

        for i in range(len(vals)):
            val = vals[i]
            if val[1] is not None:
                out += "\t" + str(val[0]) + ": " + str(val[1])
                if i < len(data) - 1:
                    out += "\t|"

        return out + "\n"

    def find_attr(self, keyword):
        for key in self.data.keys():
            if keyword.upper() in key.upper():
                return self.data[key]
        return None

    def attr_to_text(self, attr):
        out = ""
        attr = self.find_attr(attr)
        if attr is not None:
            for title in attr.keys():
                out += self.record_to_text("<b>"+title+"</b>", attr[title])
            return out
        return ""

    def report(self):
        out = "<b>COVID-19 Clinical Management Summary for " + self.date.strftime("%A, %B %d, %Y") + "</b>\n\n"

        out += self.attr_to_text("cases")

        out += "\n<b>Sex Classification</b>\n"
        out += self.attr_to_text("sex")

        out += "\n<b>Parishes</b>\n"
        out += self.attr_to_text("parish")

        out += "\n<b>Testing</b>\n"
        out += self.attr_to_text("testing")

        out += "\n<b>Deaths</b>\n"
        out += self.attr_to_text("deaths")

        out += "\n<b>Recoveries and Active Cases</b>\n"
        out += self.attr_to_text("recoveries")

        out += "\n<b>Quarantine Management</b>\n"
        out += self.attr_to_text("quarantine")

        out += "\n<b>Hospital Management</b>\n"
        out += self.attr_to_text("hospitals")

        out += "\n<b>Transmission Status</b>\n"
        out += self.attr_to_text("transmission")

        return out

    def summary(self):
        out = "<b>Short COVID-19 Clinical Management Summary for " + self.date.strftime("%A, %B %d, %Y") + "</b>\n\n"

        out += self.record_to_text("<b>Confirmed Cases</b>", self.find_attr("cases")["Confirmed Cases"])
        out += self.record_to_text("<b>Deaths</b>", self.find_attr("deaths")["Deaths"])
        out += self.record_to_text("<b>Recovered</b>", self.find_attr("recoveries")["Recovered"])

        return out

    def get_attr(self, attr):
        title = {
            'cases': "<b>COVID-19 Confirmed Cases for " + self.date.strftime("%A, %B %d, %Y") + "</b>\n\n",
            'sex': "<b>COVID-19 Case Sex Classification for " + self.date.strftime("%A, %B %d, %Y") + "</b>\n\n",
            'parishes': "<b>COVID-19 Parish Data for " + self.date.strftime("%A, %B %d, %Y") + "</b>\n\n",
            'testing': "<b>COVID-19 Testing Data for " + self.date.strftime("%A, %B %d, %Y") + "</b>\n\n",
            'deaths': "<b>COVID-19 Deaths for " + self.date.strftime("%A, %B %d, %Y") + "</b>\n\n",
            'recoveries': "<b>COVID-19 Recoveries and Active Cases for " + self.date.strftime("%A, %B %d, %Y") + "</b>\n\n",
            'active': "<b>COVID-19 Recoveries and Active Cases Cases for " + self.date.strftime("%A, %B %d, %Y") + "</b>\n\n",
            'quarantine': "<b>COVID-19 Quarantine Management Data for " + self.date.strftime("%A, %B %d, %Y") + "</b>\n\n",
            'hospitals': "<b>COVID-19 Hospital Management Data for " + self.date.strftime("%A, %B %d, %Y") + "</b>\n\n",
            'transmission': "<b>COVID-19 Transmission Data for " + self.date.strftime("%A, %B %d, %Y") + "</b>\n\n"
        }

        return title[attr] + self.attr_to_text(attr)


def scrape(date):

    date_str = date.strftime("%A-%B-%d-%Y").lower()
    url = "https://www.moh.gov.jm/covid-19-clinical-management-summary-for-" + date_str + "/"
    print("Scraping " + url + " ...")

    page = requests.get(url)
    if page.status_code == 404:
        return None

    text = page.text.replace("<p>", "").replace("</p>", "")
    soup = BeautifulSoup(text, 'html.parser')

    return soup


def parse(date, soup):

    out = []

    for tr in soup.find_all('tr'):
        line = []
        tds = tr.find_all('td')
        for td in tds:
            line.append(td.text.replace('\n', "").replace('\xa0', ""))
        if line[0] != '':
            out.append(line)

    return CovidData(date, out)


date = datetime.datetime.today() - datetime.timedelta(days=1)