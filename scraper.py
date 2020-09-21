import requests
from bs4 import BeautifulSoup


def extract(line):
    line = line[1:]
    if len(line) == 1:
        data = {"24 Hours": line[0]}
        return data
    if len(line) == 2:
        data = {"24 Hours": line[0], "Overall": line[1]}
        return data
    if len(line) == 3:
        data = {"24 Hours": line[0], "Overall": line[1], "Notes": line[2]}
        return data
    else:
        return line


def search_extract(table_data, keyword):
    for row in table_data:
        if row[0] == keyword:
            return extract(row)


class CovidData:

    def __init__(self, date, table_data):
        self.date = date
        self.new_cases = {
            "Meta": ["Confirmed Cases"],
            "Confirmed Cases": extract(table_data[1])
        }
        self.sex_classification = {
            "Meta": ["Males", "Females", "Under Investigation"],
            "Males": extract(table_data[3]),
            "Females": extract(table_data[4]),
            "Under Investigation": extract(table_data[5])
        }
        self.age_range = extract(table_data[6])
        self.parishes = {
            "Meta": ["St. Catherine", "Kingston & St. Andrew", "St. Thomas", "Portland", "St. Mary", "St. Ann", "Trelawny", "St. James", "Hanover", "Westmoreland", "St. Elizabeth", "Manchester", "Clarendon"],
            "St. Catherine": extract(table_data[8]),
            "Kingston & St. Andrew":  extract(table_data[9]),
            "St. Thomas":  extract(table_data[10]),
            "Portland": extract(table_data[11]),
            "St. Mary": extract(table_data[12]),
            "St. Ann": extract(table_data[13]),
            "Trelawny": extract(table_data[14]),
            "St. James": extract(table_data[15]),
            "Hanover": extract(table_data[16]),
            "Westmoreland":  extract(table_data[17]),
            "St. Elizabeth":  extract(table_data[18]),
            "Manchester":  extract(table_data[19]),
            "Clarendon":  extract(table_data[20])
        }
        self.testing = {
            "Meta": ["Samples Tested", "Discharge samples tested in the last 24 hours", "Results Positive", "Results Negative", "Results Pending"],
            "Samples Tested":  extract(table_data[22]),
            "Discharge samples tested in the last 24 hours":  extract(table_data[23]),
            "Results Positive":  extract(table_data[24]),
            "Results Negative":  extract(table_data[25]),
            "Results Pending":  extract(table_data[26])
        }
        self.deaths = {
            "Meta": ["Deaths", "Coincidental Deaths", "Deaths under Investigation"],
            "Deaths":  extract(table_data[28]),
            "Coincidental Deaths":  extract(table_data[29]),
            "Deaths under Investigation":  extract(table_data[30]),
            "Details": ""
        }
        self.recoveries_active = {
            "Meta": ["Recovered", "Active Cases"],
            "Recovered":  extract(table_data[32]),
            "Active Cases":  extract(table_data[33])
        }
        self.quarantine = {
            "Meta": ["Number in Facility Quarantine", "Number in Home Quarantine"],
            "Number in Facility Quarantine":  extract(table_data[35]),
            "Number in Home Quarantine":  extract(table_data[36])
        }
        self.hospitals = {
            "Meta": ["Number Hospitalised", "Patients Moderately Ill", "Patients Critically Ill"],
            "Number Hospitalised":  extract(table_data[38]),
            "Patients Moderately Ill":  extract(table_data[39]),
            "Patients Critically Ill":  extract(table_data[40])
        }
        self.transmission = {
            "Meta": ["Imported", "Local Transmission (Not Epidemiologically linked)", "Contacts of Confirmed Cases", "Cases Related to the St. Catherine Workplace Cluster", "Under Investigation"],
            "Imported": extract(table_data[42]),
            "Local Transmission (Not Epidemiologically linked)": extract(table_data[43]),
            "Contacts of Confirmed Cases": extract(table_data[44]),
            "Cases Related to the St. Catherine Workplace Cluster": extract(table_data[45]),
            "Under Investigation": extract(table_data[46])
        }

    def record_to_text(self, title, data):
        out = title + "\n"
        vals = [("24 Hours", data.get("24 Hours")), ("Overall", data.get("Overall")), ("Notes", data.get("Notes"))]

        for i in range(len(vals)):
            val = vals[i]
            if val[1] is not None:
                out += "\t" + val[0] + ": " + val[1]
                if i < len(data) - 1:
                    out += "\t|"

        return out + "\n"

    def attr_to_text(self, attr):
        out = ""
        for title in attr["Meta"]:
            out += self.record_to_text("<b>"+title+"</b>", attr[title])
        return out

    def report(self):
        out = "<b>COVID-19 Clinical Management Summary for " + self.date.strftime("%A, %B %d, %Y") + "</b>\n\n"

        out += self.attr_to_text(self.new_cases)

        out += "\n<b>Sex Classification</b>\n"
        out += self.attr_to_text(self.sex_classification)

        out += "\n<b>Parishes</b>\n"
        out += self.attr_to_text(self.parishes)

        out += "\n<b>Testing</b>\n"
        out += self.attr_to_text(self.testing)

        out += "\n<b>Deaths</b>\n"
        out += self.attr_to_text(self.deaths)

        out += "\n<b>Recoveries and Active Cases</b>\n"
        out += self.attr_to_text(self.recoveries_active)

        out += "\n<b>Quarantine Management</b>\n"
        out += self.attr_to_text(self.quarantine)

        out += "\n<b>Hospital Management</b>\n"
        out += self.attr_to_text(self.hospitals)

        out += "\n<b>Transmission Status</b>\n"
        out += self.attr_to_text(self.transmission)

        return out

    def summary(self):
        out = "<b>Short COVID-19 Clinical Management Summary for " + self.date.strftime("%A, %B %d, %Y") + "</b>\n\n"

        out += self.record_to_text("<b>Confirmed Cases</b>", self.new_cases["Confirmed Cases"])
        out += self.record_to_text("<b>Deaths</b>", self.deaths["Deaths"])
        out += self.record_to_text("<b>Recovered</b>", self.recoveries_active["Recovered"])
        out += self.record_to_text("<b>Recovered</b>", self.recoveries_active["Recovered"])


        return out

    def get_attr(self, attr):
        mapping = {
            'cases': {
                'title': "<b>COVID-19 Confirmed Cases for " + self.date.strftime("%A, %B %d, %Y") + "</b>\n\n",
                "data": self.attr_to_text(self.new_cases)
            },
            'sex': {
                'title': "<b>COVID-19 Case Sex Classification for " + self.date.strftime("%A, %B %d, %Y") + "</b>\n\n",
                "data": self.attr_to_text(self.sex_classification)
            },
            'parishes': {
                'title': "<b>COVID-19 Parish Data for " + self.date.strftime("%A, %B %d, %Y") + "</b>\n\n",
                "data": self.attr_to_text(self.parishes)
            },
            'testing':{
                'title': "<b>COVID-19 Testing Data for " + self.date.strftime("%A, %B %d, %Y") + "</b>\n\n",
                "data": self.attr_to_text(self.testing)
            },
            'deaths': {
                'title': "<b>COVID-19 Deaths for " + self.date.strftime("%A, %B %d, %Y") + "</b>\n\n",
                "data": self.attr_to_text(self.deaths)
            },
            'recovered': {
                'title': "<b>COVID-19 Recoveries and Active Cases for " + self.date.strftime("%A, %B %d, %Y") + "</b>\n\n",
                "data": self.attr_to_text(self.recoveries_active)
            },
            'active': {
                'title': "<b>COVID-19 Recoveries and Active Cases Cases for " + self.date.strftime("%A, %B %d, %Y") + "</b>\n\n",
                "data": self.attr_to_text(self.recoveries_active)
            },
            'quarantine': {
                'title': "<b>COVID-19 Quarantine Management Data for " + self.date.strftime("%A, %B %d, %Y") + "</b>\n\n",
                "data": self.attr_to_text(self.quarantine)
            },
            'hospitals': {
                'title': "<b>COVID-19 Hospital Management Data for " + self.date.strftime("%A, %B %d, %Y") + "</b>\n\n",
                "data": self.attr_to_text(self.hospitals)
            },
            'transmission': {
                'title': "<b>COVID-19 Transmission Data for " + self.date.strftime("%A, %B %d, %Y") + "</b>\n\n",
                "data": self.attr_to_text(self.transmission)
            }
        }

        data = mapping[attr]
        return data["title"] + data["data"]


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
