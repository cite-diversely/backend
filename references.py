import bibtexparser
import nameparser
import pandas
import gender_guesser.detector


class References(object):

    def __init__(self, reference_text):
        self.reference_text = reference_text
        self.references = bibtexparser.loads(reference_text)
        self.ethnicity_lookup = pandas.read_csv("./data/Names_2010Census.csv", index_col=0)
        self.ethnicity_results = []
        self.gender_results = []
        self.gender_options = ['male', 'mostly_male', 'andy', 'mostly_female', "female", "unknown"]
        self.race_options = ['pctwhite', 'pctblack', 'pctapi', 'pctaian', 'pct2prace', 'pcthispanic', 'race_unknown']

        names = []
        for paper in self.references.entries:
            if "author" in paper:
                authors = paper["author"].split(' and ')
                for person in authors:
                    name = nameparser.HumanName(person)
                    names.append({"last_name": name.last, "first_name": name.first})

        self.names = pandas.DataFrame(names)

    def infer_ethnicity(self):
        # Get ethnicity
        most_likely_race = []
        for name in self.names['last_name'].to_list():
            if name.upper() in self.ethnicity_lookup.index:
                most_likely_race.append(self.ethnicity_lookup.loc[name.upper()].to_frame().replace("(S)", "0").astype(float).drop(['rank', 'count', 'prop100k', 'cum_prop100k']).idxmax().values[0])
            else:
                most_likely_race.append('race_unknown')

        most_likely_race = pandas.Series(most_likely_race)
        self.ethnicity_results = most_likely_race.value_counts()

    def infer_gender(self):
        # Get gender
        d = gender_guesser.detector.Detector()
        gender = []
        for name in self.names['first_name'].to_list():
            gender.append(d.get_gender(name))
        gender = pandas.Series(gender)
        self.gender_results = gender.value_counts()

    def validate_data(self):
        for gender in self.gender_options:
            if gender not in self.gender_results.index:
                n = pandas.Series([0], index=[gender])
                self.gender_results = self.gender_results.append(n)

        for race in self.race_options:
            if race not in self.ethnicity_results.index:
                n = pandas.Series([0], index=[race])
                self.ethnicity_results = self.ethnicity_results.append(n)


if __name__ == "__main__":
    with open('./test/test2.bib', 'r') as file:
        x = References(file.read())
        print(x.names)