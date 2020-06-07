import ethnicolr
import bibtexparser
import nameparser
import pandas
import gender_guesser.detector
import numpy
import flask
import flask_restful
import flask_restful.reqparse

# Make app and API
app = flask.Flask(__name__)
api = flask_restful.Api(app)

# Create arguments to pass
parser = flask_restful.reqparse.RequestParser()
parser.add_argument('bib')


# Create an endpoint to call
class Evaluate(flask_restful.Resource):

    def post(self):
        # Get arguments
        args = parser.parse_args()
        print(args['bib'])
        bib_database = bibtexparser.loads(args['bib'])

        # Get ethnicity
        names = []
        for paper in bib_database.entries:
            authors = paper["author"].split(' and ')
            for person in authors:
                name = nameparser.HumanName(person)
                names.append({"last_name": name.last, "first_name": name.first})

        df = pandas.DataFrame(names)
        ethnicity = ethnicolr.census_ln(df, 'last_name')
        most_likely_race = ethnicity[['pctwhite', 'pctblack', 'pctapi', 'pctaian', 'pct2prace', 'pcthispanic']].replace("(S)", numpy.nan).astype(float).idxmax(axis=1).fillna('Unknown')
        print(most_likely_race)

        # Get gender
        d = gender_guesser.detector.Detector()
        gender = []
        for name in df['first_name'].to_list():
            gender.append(d.get_gender(name))
        gender = pandas.DataFrame(gender, columns=['gender'])

        # Combine the results
        results = pandas.concat([ethnicity, gender], axis=1, sort=False)
        results = results.replace("(S)", numpy.nan)

        # Give summary stats
        races = ['pctwhite', 'pctblack', 'pctapi', 'pctaian', 'pct2prace', 'pcthispanic', 'Unknown']
        genders = ['male', 'mostly_male', 'andy', 'mostly_female', "female", "unknown"]
        gender_results = results["gender"].value_counts()
        ethnicity_results = most_likely_race.value_counts()
        # ethnicity_results = results[['pctwhite', 'pctblack', 'pctapi', 'pctaian', 'pct2prace', 'pcthispanic']].mean(skipna=True)

        # Validate data
        for gender in genders:
            if gender not in gender_results.index:
                n = pandas.Series([0], index=[gender])
                gender_results = gender_results.append(n)

        for race in races:
            if race not in ethnicity_results.index:
                n = pandas.Series([0], index=[race])
                ethnicity_results = ethnicity_results.append(n)

        print(results.to_string())
        print(gender_results.to_string())
        print(ethnicity_results.to_string())

        return ethnicity_results.append(gender_results).to_json()

        # return flask.render_template("results.html",
        #                              vlmale=gender_results['male'],
        #                              lmale=gender_results['mostly_male'],
        #                              gn=gender_results['andy'],
        #                              lfemale=gender_results['mostly_female'],
        #                              vlfemale=gender_results['female'],
        #                              unknown=gender_results['unknown'],
        #                              white=ethnicity_results['pctwhite'],
        #                              black=ethnicity_results['pctblack'],
        #                              api=ethnicity_results['pctapi'],
        #                              aian=ethnicity_results['pctaian'],
        #                              mr=ethnicity_results['pct2prace'],
        #                              hispanic=ethnicity_results['pcthispanic'],
        #                              unknown2=ethnicity_results['Unknown'])


api.add_resource(Evaluate, "/")

if __name__ == '__main__':
    app.run(debug=True)