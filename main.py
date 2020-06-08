import bibtexparser
import nameparser
import pandas
import gender_guesser.detector
import flask
import flask_restful
import flask_restful.reqparse
import flask_cors

# Make app and API
app = flask.Flask(__name__)
api = flask_restful.Api(app)
flask_cors.CORS(app)

# Create arguments to pass
parser = flask_restful.reqparse.RequestParser()
parser.add_argument('bib')


# Create an endpoint to call
class Evaluate(flask_restful.Resource):

    def post(self):
        # Get arguments
        args = parser.parse_args()
        bib_database = bibtexparser.loads(args['bib'])

        # Extract names
        names = []
        for paper in bib_database.entries:
            authors = paper["author"].split(' and ')
            for person in authors:
                name = nameparser.HumanName(person)
                names.append({"last_name": name.last, "first_name": name.first})

        names = pandas.DataFrame(names)

        # Get ethnicity
        ethnicity_lookup = pandas.read_csv("./data/Names_2010Census.csv", index_col=0)
        most_likely_race = []
        for name in names['last_name'].to_list():
            if name.upper() in ethnicity_lookup.index:
                most_likely_race.append(ethnicity_lookup.loc[name.upper()].to_frame().replace("(S)", "0").astype(float).drop(['rank', 'count', 'prop100k', 'cum_prop100k']).idxmax().values[0])
            else:
                most_likely_race.append('race_unknown')

        print(most_likely_race)
        most_likely_race = pandas.Series(most_likely_race[0])
        ethnicity_results = most_likely_race.value_counts()

        # Get gender
        d = gender_guesser.detector.Detector()
        gender = []
        for name in names['first_name'].to_list():
            gender.append(d.get_gender(name))
        gender = pandas.Series(gender)
        gender_results = gender.value_counts()

        # Validate data
        genders = ['male', 'mostly_male', 'andy', 'mostly_female', "female", "unknown"]
        for gender in genders:
            if gender not in gender_results.index:
                n = pandas.Series([0], index=[gender])
                gender_results = gender_results.append(n)

        races = ['pctwhite', 'pctblack', 'pctapi', 'pctaian', 'pct2prace', 'pcthispanic', 'race_unknown']
        for race in races:
            if race not in ethnicity_results.index:
                n = pandas.Series([0], index=[race])
                ethnicity_results = ethnicity_results.append(n)

        print(ethnicity_results)
        print(gender_results)
        return ethnicity_results.append(gender_results).to_json()


api.add_resource(Evaluate, "/")

if __name__ == '__main__':
    app.run(debug=True)