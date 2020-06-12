import bibtexparser
import nameparser
import gender_guesser.detector
import csv
import operator


class References(object):

    def __init__(self, reference_text):
        self.gender_options = ['male', 'mostly_male', 'andy', 'mostly_female', "female", "unknown"]
        self.gender_results = {key: 0 for key in self.gender_options}
        self.race_options = ['pctwhite', 'pctblack', 'pctapi', 'pctaian', 'pct2prace', 'pcthispanic', 'race_unknown']
        self.ethnicity_results = {key: 0 for key in self.race_options}

        # Load data
        self.ethnicity_lookup = {}
        with open('./data/Names_2010Census.csv') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                self.ethnicity_lookup[row['name']] = {}
                for race in self.race_options[:-1]:
                    try:
                        value = float(row[race])
                    except ValueError:
                        value = 0
                    self.ethnicity_lookup[row['name']][race] = value

        # Parse names from input
        self.reference_text = reference_text
        self.references = bibtexparser.loads(reference_text)
        self.first_names = []
        self.last_names = []
        for paper in self.references.entries:
            if "author" in paper:
                authors = paper["author"].split(' and ')
                for person in authors:
                    name = nameparser.HumanName(person)
                    self.first_names.append(name.first)
                    self.last_names.append(name.last)

    def infer_ethnicity(self):
        # Get ethnicity
        most_likely_race = []
        for name in self.last_names:
            if name.upper() in self.ethnicity_lookup:
                rr = max(self.ethnicity_lookup[name.upper()].items(), key=operator.itemgetter(1))[0]
                most_likely_race.append(rr)
            else:
                most_likely_race.append('race_unknown')

        for i in most_likely_race:
            self.ethnicity_results[i] = self.ethnicity_results.get(i, 0) + 1

    def infer_gender(self):
        # Get gender
        d = gender_guesser.detector.Detector()
        gender = []
        for name in self.first_names:
            gender.append(d.get_gender(name))

        for i in gender:
            self.gender_results[i] = self.gender_results.get(i, 0) + 1


if __name__ == "__main__":
    with open('./test/test2.bib', 'r') as file:
        x = References(file.read())
        x.infer_ethnicity()
        x.infer_gender()
        print(x.ethnicity_results)
        print(x.gender_results)
        print({**x.ethnicity_results, **x.gender_results})