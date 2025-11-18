from flask import Flask, render_template, request, redirect, flash, session
import requests
import base64
from flask_mysqldb import MySQL


app = Flask(__name__)
app.secret_key = '289vyugiq3be3quf'
app.config["MYSQL_HOST"] = "mysql.2425.lakeside-cs.org"
app.config["MYSQL_USER"] = "student2425"
app.config["MYSQL_PASSWORD"] = "ACSSE2425"
app.config["MYSQL_DB"] = "2425finalproject"
app.config["MYSQL_CURSORCLASS"] = "DictCursor" # a cursor is an object that lets you make queries
mysql = MySQL(app)
# information about the client
CLIENT_ID = "d33ef33c938c4a5ebc267ccb692df976"
CLIENT_SECRET = "9c2631691aec4b2c88d5de69c2d1d5d7"
# redirect uri, used for the Spotify API
REDIRECT_URI = "https://2425.lakeside-cs.org/WilliamP/finalproject/callback"
# add a SCOPE variable and use it in authURL
SCOPE = "playlist-modify-private playlist-modify-public playlist-read-private playlist-read-collaborative user-top-read user-read-email"

@app.route('/')
def index():
    return render_template("index.html.j2")

@app.route('/auth')
def auth():
    # show_dialog=true will make sure Spotify doesn't immediately authenticate,
    # since it stores information in the browser session automatically. This setting
    # will give the user an option to not accept the scopes, or change accounts.
    authURL = (
        f"https://accounts.spotify.com/authorize?client_id={CLIENT_ID}"
        f"&response_type=code&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPE}&show_dialog=true"
    )
    return redirect(authURL)

@app.route('/callback')
def callback():
    authCode = request.args.get("code")
    # add some if statement? if not authCode?

    # encode the client id and secret
    encodedCreds = base64.b64encode(str(CLIENT_ID + ":" + CLIENT_SECRET).encode()).decode()
    # set post request Header and Body
    headers = {"Authorization": f"Basic {encodedCreds}", "Content-Type": "application/x-www-form-urlencoded"}
    # this is the body
    data = {"grant_type": "authorization_code", "code": authCode, "redirect_uri": REDIRECT_URI}

    # make the post request
    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    print(response.text)
    # status code 200 means OK

    if response.status_code == 200:
        jsonResponse = response.json()
        accessToken = jsonResponse.get("access_token")
        session['williamp_accessToken'] = accessToken
        getRQHeader = {"Authorization": f"Bearer {accessToken}"}
        userID = makeGetRequest("/me", getRQHeader).get("id")
        session['williamp_userID'] = userID

        # check if user is registered in database
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM williamp_users WHERE user_id = %s"
        queryVars = (session['williamp_userID'],)
        cursor.execute(query, queryVars)
        mysql.connection.commit()
        data = cursor.fetchall()
        # if not, add the userID to database
        if not data:
            query = "INSERT INTO williamp_users (user_id) VALUES (%s)"
            queryVars = (session['williamp_userID'],)
            cursor.execute(query, queryVars)
            mysql.connection.commit()

        flash("You are now logged in.")
        return redirect(".")
        
    else:
        flash("Error while logging in.")
        popall()
        return redirect("error")   
    
@app.route('/account')
def account():
    return render_template("account.html.j2")

@app.route('/logout')
def logout():
    popall()
    flash("You are now logged out.")
    return redirect("account")

@app.route('/playlists')
def playlists():
    if 'williamp_accessToken' in session:
        header = {"Authorization": f"Bearer {session['williamp_accessToken']}"}
        userPlaylists = makeGetRequest(f"/users/{session['williamp_userID']}/playlists?limit=50", header)
    else:
        flash("Error while retrieving playlists. Consider logging in again.")
        return redirect("error")
    
    if userPlaylists == -1:  # if there was an error
        flash("Error finding playlists.")
        popall()
        return redirect("error")   
    else:
        return render_template("playlists.html.j2", playlists=userPlaylists)

@app.route('/error')
def error():
    return render_template("error.html.j2")

@app.route('/playlistModal', methods=['POST'])
def playlistModal():
    # get the data from the request
    data = request.get_json()
    endpoint = data["endpoint"].split("api.spotify.com/v1", 1)[1] + "/tracks"

    # use this endpoint to make an API request
    header = {"Authorization": f"Bearer {session['williamp_accessToken']}"}
    playlistData = makeGetRequest(endpoint, header)
    if playlistData != -1:
        return playlistData
    else:
        # TODO: change this
        return playlistData
    
@app.route('/closePlaylistModal', methods=['POST'])
def closePlaylistModal():
    return ''

@app.route('/favsongs')
def favsongs():
    if 'williamp_userID' in session:
        cursor = mysql.connection.cursor()
        query = """SELECT song FROM williamp_favoritesongs f
            JOIN williamp_users u ON u.id = f.db_user_id
            WHERE u.user_id = %s"""
        queryVars = (session['williamp_userID'],)
        cursor.execute(query, queryVars)
        mysql.connection.commit()
        dbData = cursor.fetchall()
        data = []

        header = {"Authorization": f"Bearer {session['williamp_accessToken']}"}
        ids = ""
        for map in dbData:
            ids += map['song'].split("/tracks/", 1)[1]
            if map != dbData[-1]:
                ids += ","
        data = makeGetRequest("/tracks?ids="+str(ids), header)
        if data != -1:
            return render_template("favsongs.html.j2", data=data)
        else:
            return render_template("favsongs.html.j2")
    else:
        return redirect("error")


@app.route('/search')
def search():
    if 'williamp_userID' in session:
        query = ""
        data = ""
        yearBef = request.values.get("yearbef")
        if yearBef:
            yearBef = int(yearBef)
        else:
            yearBef = 1800
        yearAft = request.values.get("yearaft")
        if yearAft:
            yearAft = int(yearAft)
        else:
            yearAft = 2026
        if request.values.get("q"):
            query = request.values.get("q")
            header = {"Authorization": f"Bearer {session['williamp_accessToken']}"}
            data = makeGetRequest(f"/search?q={query}%20year:{yearBef}-{yearAft}&type=track&limit=10", header)
        return render_template("search.html.j2", data=data, query=query)
    else:
        return redirect('error')

@app.route('/addFavorite', methods=['POST'])
def addFavorite():
    # first, get the user's database ID
    cursor = mysql.connection.cursor()
    query = "SELECT id FROM williamp_users WHERE user_id = %s"
    queryVars = (session['williamp_userID'],)
    cursor.execute(query, queryVars)
    mysql.connection.commit()
    dbuserID = cursor.fetchall()[0]['id']

    # then, insert the favorite song to the database
    sentData = request.get_json()
    songEndpoint = sentData["songEndpoint"].split("api.spotify.com/v1", 1)[1]
    # check if the song is already in favorites
    query = """SELECT song FROM williamp_favoritesongs f
        JOIN williamp_users u ON f.db_user_id = u.id
        WHERE u.user_id = %s"""
    queryVars = (session['williamp_userID'],)
    cursor.execute(query, queryVars)
    mysql.connection.commit()
    data = cursor.fetchall()
    print(songEndpoint)
    print("DATA:")
    print(data)

    if not any(entry['song'] == songEndpoint for entry in data):
        query = "INSERT INTO williamp_favoritesongs (db_user_id, song) VALUES (%s, %s)"
        queryVars = (dbuserID, songEndpoint)
        cursor.execute(query, queryVars)
        mysql.connection.commit()

    return ''

@app.route('/removeFavorite', methods=['POST'])
def removeFavorite():
    sentData = request.get_json()
    songEndpoint = sentData["songEndpoint"].split("api.spotify.com/v1", 1)[1]

    cursor = mysql.connection.cursor()
    query = "DELETE FROM williamp_favoritesongs WHERE song = %s"
    queryVars = (songEndpoint,)
    cursor.execute(query, queryVars)
    mysql.connection.commit()

    return ''

@app.route('/playlistFavSongs', methods=['POST'])
def playlistFavSongs():
    
    ## CREATE A PLAYLIST ##
    headers = {"Authorization": f"Bearer {session['williamp_accessToken']}", "Content-Type": "application/json"}
    # this is the body
    data = {"name":"Favorite Songs"}

    # make the post request
    response = requests.post(f"https://api.spotify.com/v1/users/{session['williamp_userID']}/playlists", headers=headers, json=data)

    jsonResponse = response.json()

    ## GET THE NEW PLAYLIST'S ID
    playlistID = jsonResponse["id"]


    ## GET FAVORITE SONGS ##
    cursor = mysql.connection.cursor()
    query = """SELECT song FROM williamp_favoritesongs f
        JOIN williamp_users u ON f.db_user_id = u.id
        WHERE u.user_id = %s"""
    queryVars = (session['williamp_userID'],)
    cursor.execute(query, queryVars)
    mysql.connection.commit()
    dbData = cursor.fetchall()

    ## ADD FAVORITE SONGS TO THE NEW PLAYLIST ##
    uris = []
    for map in dbData:
        # manually putting the "spotify:track:" since I know everything is a track
        uris.append("spotify:track:" + map['song'].split("/tracks/", 1)[1])
    data = {"uris": uris}
    response = requests.post(f"https://api.spotify.com/v1/playlists/{playlistID}/tracks", headers=headers, json=data)
    return ''

def makeGetRequest(endpoint, headers):
    response = requests.get(f"https://api.spotify.com/v1{endpoint}", headers=headers, timeout=5) # 5 seconds
    print(f"Request failed. Status Code: {response.status_code}, Response: {response.text}")

    if response.status_code == 200:
        jsonResponse = response.json()
        return jsonResponse
    else:
        print(f"Request failed. Status Code: {response.status_code}, Response: {response.text}")
        return -1
        
def popall():
    session.pop('williamp_userID')
    session.pop('williamp_accessToken')