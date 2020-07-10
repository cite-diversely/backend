# For main things
import bibtexparser
import nameparser
import gender_guesser.detector
import csv
import operator
import os
import pickle
import json
import pathlib

# For Azure things
import logging
import azure.functions as func


class References(object):

    def __init__(self, reference_text):
        self.gender_options = ['male', 'mostly_male', 'andy', 'mostly_female', "female", "unknown"]
        self.gender_results = {key: 0 for key in self.gender_options}
        self.race_options = ['pctwhite', 'pctblack', 'pctapi', 'pctaian', 'pct2prace', 'pcthispanic', 'race_unknown']
        self.ethnicity_results = {key: 0 for key in self.race_options}
        self.raw_results = {}

        pickle_path = pathlib.Path(__file__).parent / 'data' / 'ethnicity_lookup.p'
        csv_path = pathlib.Path(__file__).parent / 'data' / 'Names_2010Census.csv'

        # Load data
        if os.path.isfile(pickle_path):
            self.ethnicity_lookup = pickle.load(open(pickle_path, 'rb'))
        else:
            self.ethnicity_lookup = {}
            with open(csv_path) as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    self.ethnicity_lookup[row['name']] = {}
                    for race in self.race_options[:-1]:
                        try:
                            value = float(row[race])
                        except ValueError:
                            value = 0
                        self.ethnicity_lookup[row['name']][race] = value
            pickle.dump(self.ethnicity_lookup, open(pickle_path, 'wb'))
            
        # Parse names from input
        self.reference_text = reference_text
        self.references = bibtexparser.loads(reference_text)
        logging.info(self.reference_text)
        logging.info(self.references.entries)
        self.first_names = []
        self.last_names = []
        for paper in self.references.entries:
            if "author" in paper:
                authors = paper["author"].split(' and ')
                for person in authors:
                    name = nameparser.HumanName(person)
                    self.first_names.append(name.first)
                    self.last_names.append(name.last)
        self.raw_results['first_name'] = self.first_names
        self.raw_results['last_name'] = self.last_names

    def infer_ethnicity(self):
        # Get ethnicity
        most_likely_race = []
        for name in self.last_names:
            if name.upper() in self.ethnicity_lookup:
                rr = max(self.ethnicity_lookup[name.upper()].items(), key=operator.itemgetter(1))[0]
                most_likely_race.append(rr)
            else:
                most_likely_race.append('race_unknown')
        self.raw_results['most_likely_race'] = most_likely_race

        for i in most_likely_race:
            self.ethnicity_results[i] = self.ethnicity_results.get(i, 0) + 1

    def infer_gender(self):
        # Get gender
        most_likely_gender = []
        d = gender_guesser.detector.Detector()
        for name in self.first_names:
            most_likely_gender.append(d.get_gender(name))
        self.raw_results['most_likely_gender'] = most_likely_gender

        for i in most_likely_gender:
            self.gender_results[i] = self.gender_results.get(i, 0) + 1


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    logging.info(req.get_body())

    name = req.get_body().decode('utf8')
    logging.info(name)

    if name:
        logging.info("Starting process")
        refs = References(name)
        logging.info("Reference object created")
        refs.infer_gender()
        logging.info("Gender inferred")
        refs.infer_ethnicity()
        logging.info("Ethnicity inferred")

        name = {**refs.ethnicity_results, **refs.gender_results, **refs.raw_results}

        return func.HttpResponse(
            json.dumps(name),
            mimetype="application/json",
        )
    else:
        return func.HttpResponse(
             "A reference list was not properly identified.",
             status_code=200
        )
