import flask  # Serve that flask
import flask_cors  # Serve that flask
import flask_restful.reqparse  # Serve that flask
import references

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
        refs = references.References(args['bib'])
        refs.infer_gender()
        refs.infer_ethnicity()

        return flask.jsonify({**refs.ethnicity_results, **refs.gender_results, **refs.raw_results})


api.add_resource(Evaluate, "/")

if __name__ == '__main__':
    app.run(debug=True)