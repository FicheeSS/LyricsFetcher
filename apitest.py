from flask import Flask
from flask_restful import Api, Resource, reqparse
from LyricsTools import GetLyrics

app = Flask(__name__)
api = Api(app)

class Lyrics (Resource):
    def get(self, artist , track):
        if artist == "" or track == "":
            return "One of the input is empty" , 400
        else :
            lyrics = GetLyrics(artist,track)
            if lyrics == "" :
                return "Could not find the requested lyrics" , 204
            else: 
                return  lyrics , 200 

api.add_resource(
    Lyrics,
    '/lyrics/<artist>/<track>', 
    methods=["GET"]
)
app.run()