import json
import os
from schemato import Schemato
from schemato.distillery import ParselyDistiller, NewsDistiller
from flask import Flask,abort, request, redirect, Response
app = Flask(__name__, static_url_path='/static')

@app.route("/metaextract", methods=['GET'])
def mo():
    if len(request.args)==0 or request.args.get("url")=="": #if you have no parameters then redirect to the static page
        return redirect("/extracturl")
    else: 
        url = request.args.get("url")
        sch = Schemato(url)
        d = NewsDistiller(sch)
        return Response(json.dumps(d.distill()), mimetype="text/json")


@app.route('/extracturl', methods=['GET'])
@app.route('/extracturl.html', methods=['GET'])
def static_extracturl():  
    return  app.send_static_file('extracturl.html')

if __name__ == "__main__":
    app.run(debug=True)