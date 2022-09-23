import imp
from logging.config import IDENTIFIER
from pydoc import cram
from flask import Flask, request, render_template, redirect, session, g, flash
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError


from forms import UserAddForm, LoginForm, UpdateUserProfileForm
from models import db, connect_db, User, Favorite
from api_secret import PRIVATE_KEY, PUBLIC_KEY

import requests, datetime, hashlib, json, os

"""Timestamp is used for required API param."""
timestamp = datetime.datetime.now().strftime('%Y-%m-%d%H:%M:%S')

CURR_USER_KEY = "curr_user"

fav_char = []

"""Base url for API call."""
BASE_URL = 'https://gateway.marvel.com/v1/public'

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///marvel_search_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '2456879478484004854899')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)


############################################################################
# User signup/login/logout:

@app.before_request
def add_user_to_g():
  """If we're logged in, add curr user to Flask global."""

  if CURR_USER_KEY in session:
    g.user = User.query.get(session[CURR_USER_KEY])

  else:
    g.user = None

def do_login(user):
  """Log in user."""

  session[CURR_USER_KEY] = user.id

def do_logout():
  """Logout user."""

  if CURR_USER_KEY in session:
    del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
  """Handle User signup.

  Create new User and add to DB. Redirect to home page.

  If form not valid, present form.

  If there is already a user with that username: flash message
  and re-present form.
  """

  form = UserAddForm()

  if form.validate_on_submit():
    try:
      user = User.signup(
          username=form.username.data,
          password=form.password.data,
          email=form.email.data,
          header_image_url=form.header_image_url.data or User.header_image_url.default.arg,
          image_url=form.image_url.data or User.image_url.default.arg,
      )
      db.session.commit()

    except IntegrityError as e:
      flash("Username already taken, please try again")
      return render_template('users/signup_form.html', form=form)

    do_login(user)

    return redirect("/")

  else:
    return render_template('users/signup_form.html', form=form)
  

@app.route('/login', methods=["GET", "POST"])
def login():
  """Handle user login."""
 
  form = LoginForm()

  if form.validate_on_submit():
    user = User.authenticate(form.username.data,
                             form.password.data)

    if user:
      do_login(user)
      flash(f"Cap Says: Welcome Back {user.username}!")
      return redirect("/")
    
    flash("Invalid credentials, please try again.")

  return render_template('users/login.html', form=form)

@app.route('/logout')
def logout():
  """Handle logout of user."""

  do_logout()

  flash("See you for the next mission Avenger!")
  return redirect("/login")


##############################################################################
# General user routes:


@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """Update profile for current user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = g.user
    form = UpdateUserProfileForm(obj=user)


    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.username=form.username.data,
            user.email=form.email.data,
            user.header_image_url=form.header_image_url.data or User.header_image_url.default.arg,
            user.image_url=form.image_url.data or User.image_url.default.arg,
            user.bio=form.bio.data

        
            db.session.commit()
            return redirect(f"/users/{user.id}")
        flash("Wrong password, please try again.")
    
    return render_template("users/edit.html", form=form, user=user)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""
    
    if not g.user:
          flash("Access unauthorized")
          return redirect("/")


    user = User.query.get_or_404(user_id)

    return render_template('users/detail.html', user=user)


@app.route('/users/<int:user_id>/favorites', methods=["GET", "POST"])
def show_likes(user_id):
  """Show user a page of favorited characters."""
  
  if not g.user:
          flash("Access unauthorized")
          return redirect("/")

  user = User.query.get_or_404(user_id)
  
  """Get the character id's for all characters in user favorites."""
  user_favs = [char.character_id for char in g.user.favorites]
  
  """Initialize empty arrary to stor favorited character information in."""
  fav_list = []

  """Loop through users favorites using the character id."""
  for fav in user_favs:
    res = requests.get(f"{BASE_URL}/characters/{fav}",
                        params={"apikey": PUBLIC_KEY, "ts": timestamp, "hash": api_hash()})
    res_data = res.json()

    for result in res_data['data']['results']:
      name = res_data["data"]["results"][0]['name']
      description = res_data["data"]["results"][0]['description']
      image = res_data["data"]["results"][0]['thumbnail']['path']
      char_id = res_data["data"]["results"][0]['id']

      """API requires extension be added to path"""
      image_src = image + '.jpg'
    
      """Dict to store character information in."""
      char_res = {'name': name, 'description': description, 'image': image_src, 'id': char_id}

      fav_list.append(char_res)


  return render_template('/users/favorites.html', user=user, favorites=user.favorites, favs=fav_list)

@app.route('/users/delete', methods=["POST"])
def messages_destroy():
    """Delete a user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()
    
    db.session.delete(g.user)
    db.session.commit()
  
    return redirect('/signup')

#################################################################################
# Favorites routes:


@app.route('/heros/<int:char_id>/favorite', methods=['POST'])
def add_like(char_id):
    """Like/unlike a message for the currently-logged-in-user."""
    

    if not g.user:
          flash("Access unauthorized")
          return redirect("/")

    user = g.user.id

    """API call to get character info."""
    res = requests.get(f"{BASE_URL}/characters/{char_id}",
                        params={"apikey": PUBLIC_KEY, "ts": timestamp, "hash": api_hash()})
    
    res_data = res.json()

    name = res_data["data"]["results"][0]['name']
    char_id = res_data["data"]["results"][0]['id']
    
    
    user_favs = g.user.favorites
  
    """Add favorite charachter to user session."""
    try:
        user_fav_char = Favorite(character_id=char_id, user_id=user, character_name=name)
        db.session.add(user_fav_char)
        user_favs.append(user_fav_char)
        db.session.commit()
        
    except IntegrityError:
        return redirect("/")

    return redirect("/")


@app.route('/heros/<int:char_id>/delete', methods=["POST"])
def fav_char_destroy(char_id):
    """Delete a user favorited char."""
    user = g.user.id

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user_char = Favorite.query.get((char_id, user))
    
    db.session.delete(user_char)
    db.session.commit()
  
    return redirect('/')
    
    
##################################################################################
# Character routes:

def api_hash():
  """Marvel API requires call to include md5 hash
   of timestamp + public key + private key"""

  
  hashed_param = hashlib.md5((f'{timestamp}{PRIVATE_KEY}{PUBLIC_KEY}').encode('utf-8')).hexdigest()

  return hashed_param


@app.route('/hero')
def show_char():
  """Get info on a specific character and return comics featuring that character."""
  
  """Get character id from logged in users favorites."""
  user_favs = [char.character_id for char in g.user.favorites]
  
  name = request.args["name"]
  
  """API call to get the charachter."""
  res = requests.get(f"{BASE_URL}/characters",
                    params={"apikey": PUBLIC_KEY, "ts": timestamp, "hash": api_hash(), "name": name})

  res_data = res.json()

  try:
    name = res_data["data"]["results"][0]['name']
    description = res_data["data"]["results"][0]['description']
    image = res_data["data"]["results"][0]['thumbnail']['path']
    char_id = res_data["data"]["results"][0]['id']

    """API requires extension be added to path"""
    image_src = image + '.jpg'
  
    """Catch error if character name is not input correctly."""
  except (NameError, IndexError,):
    flash("Something went wrong, please input a character name")
    return redirect('/')

  """Create a dict for character data."""
  char_res = {'name': name, 'description': description, 'image': image_src, 'id': char_id}

  """Intialize empty array to store comics results"""
  comics_list = []

  """API call to get comics featuring character."""
  response = requests.get(f"{BASE_URL}/characters/{char_id}/comics",
                        params={"apikey": PUBLIC_KEY, "ts": timestamp, "hash": api_hash(), 'limit': 50})

  response_data = response.json()
 
  for result in response_data['data']['results']:
    comic_title = result['title']
    description = result['description']
    image = result['thumbnail']['path']
    comic_id = result['id']
    
    """API requires extension be added to path"""
    image_src = image + '.jpg'
    
    """Create dict for our comics."""
    comics_data = {'title': comic_title, 'description': description, 'image': image_src, 'id': comic_id}
    
    comics_list.append(comics_data)

  return render_template('heros/home.html', char=char_res, comics=comics_list, user=g.user, favorites=user_favs)


@app.route('/hero/comic/<int:comic_id>')
def show_comic_data(comic_id):
  """Return info about a specific comic featuring hero."""
  
  """Intialize empty array to store comic creators in."""
  creators_list = []
  
  """Intialize empty array to store comic characters in."""
  char_names = []
  
  user = g.user
  
  response = requests.get(f"{BASE_URL}/comics/{comic_id}",
                    params={"apikey": PUBLIC_KEY, "ts": timestamp, "hash": api_hash(), "comicId": comic_id})

  response_comic_data = response.json()

  for result in response_comic_data['data']['results']:
    comic_id = result['id']
    comics_title = result['title']
    issue_num = result['issueNumber']
    comic_description = result['description']
    page_count = result['pageCount']
    series = result['series']['name']
    image = result['thumbnail']['path']
   

    """API requires extension be added to path"""
    image_src = image + '.jpg'
    
  
  creator_res = requests.get(f"{BASE_URL}/comics/{comic_id}/creators",
                    params={"apikey": PUBLIC_KEY, "ts": timestamp, "hash": api_hash(), "comicId": comic_id})
  
  response_creator_data = creator_res.json()
  
  
  
  for result in response_creator_data["data"]["results"]:
    creator_id = result['id']
    creator_name = result['fullName']
    
    """Dict to store character info in."""
    char_data_dict = {"id": creator_id, "name": creator_name}
    
    
    creators_list.append(char_data_dict)
    

  for char in response_comic_data['data']['results'][0]['characters']['items']:
      
      char_name = char['name']

      chars = {'name': char_name }

      char_names.append(chars)
    
  """Dict to store comic data in."""
  comic_data = {'id': comic_id,'title': comics_title, 'issue_numb': issue_num, 'description': comic_description,
                  'page_count': page_count, 'series': series, 'image': image_src, 'creators': creators_list, 'name': char_names}

  
  return render_template('comics/detail.html', comics=comic_data, creators=creators_list, characters=char_names, user=user)


##################################################################################
# Creator routes:

@app.route('/comic/creator/<int:creator_id>')
def show_creator(creator_id): 
  
  user = g.user

  comics = []
 
  response = requests.get(f"{BASE_URL}/creators/{creator_id}",
                    params={"apikey": PUBLIC_KEY, "ts": timestamp, "hash": api_hash()})

  res_data = response.json()
  
  try:
    for result in res_data['data']['results']:
      creator_id = result['id']
      name = result['fullName']
      image = result['thumbnail']['path']
      comics_avail = result['comics']['available']
      series_avail = result['series']['available']
      stories_avail = result['stories']['available']
      events_avail = result['events']['available']
  
      """API requires extension be added to path"""
      image_src = image + '.jpg'

  except (IndexError, ConnectionError):
    flash("Something went wrong on our end, please try again.")
    return render_template('/')


  creator_data = {"id": creator_id, "name": name, "image": image_src,
                  "comicsavail": comics_avail, "seriesavail": series_avail, "storiesavail": stories_avail, "eventsavail": events_avail, "comics": comics}    

  for comic in res_data["data"]["results"][0]["comics"]["items"]:
      comic_name = comic["name"]

      comics.append(comic_name)

  """Intialize empty array to store comics results"""
  comics_list = []

  response = requests.get(f"{BASE_URL}/creators/{creator_id}/comics",
                        params={"apikey": PUBLIC_KEY, "ts": timestamp, "hash": api_hash(), 'creatorId': creator_id, 'limit': 50})

  response_data = response.json()
 
  for result in response_data['data']['results']:
    comic_title = result['title']
    description = result['description']
    image = result['thumbnail']['path']
    comic_id = result['id']
    
    """API requires extension be added to path"""
    image_src = image + '.jpg'
    
    """Create dict for our comics."""
    comics_data = {'title': comic_title, 'description': description, 'image': image_src, 'id': comic_id}
    
    comics_list.append(comics_data)

  return render_template('creators/show.html', creator=creator_data, comics=comics_list, user=user)

##################################################################################
# Homepage and error pages:

@app.route('/')
def homepage():
  """Show homepage."""

  if g.user:
    
    """Get character id from logged in users favorites."""
    user_favs = [char.character_id for char in g.user.favorites]
    
    
    """List of characters to display on the users homepage."""
    name_array = ['spider-man (peter parker)', 'captain america', 'hulk','wolverine', 'iron man', 'professor x',
                  'thor', 'jean grey', 'black widow', 'wasp', 'hawkeye', 'falcon',
                  'vision', 'nick fury', 'gamora', 'groot', 'captain marvel (carol danvers)']
    
    """Generate three random names from the name array."""
    names = random.sample(name_array,3)
    
    """Intialize empty array to store chararacter data in."""              
    name_list = []

    """Pass the sample names into API, get character data back."""
    for name in names:
      res = requests.get(f"{BASE_URL}/characters",
                    params={"apikey": PUBLIC_KEY, "ts": timestamp, "hash": api_hash(), "name": name})
      
      homepage_res_data = res.json()

      name = homepage_res_data["data"]["results"][0]['name']
      description = homepage_res_data["data"]["results"][0]['description']
      image = homepage_res_data["data"]["results"][0]['thumbnail']['path']
      char_id = homepage_res_data["data"]["results"][0]['id']

      """API requires extension be added to path"""
      image_src = image + '.jpg'

      """Dict for character data."""
      char_res = {'name': name, 'description': description, 'image': image_src, 'id': char_id}

      name_list.append(char_res)

  else:
    return redirect('/signup')

  return render_template('home.html', chars=name_list, favorites=user_favs, user=g.user)

@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html', user=g.user), 404


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask


@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req