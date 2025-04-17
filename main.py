from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL_VALUE")
API_KEY = os.getenv("API_KEY_VALUE")

app = Flask(__name__)
app.config['SECRET_KEY'] =os.getenv("SECRET_KEY_VALUE")
Bootstrap5(app)

# CREATE DB


class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI_VALUE")
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=True)
    year: Mapped[int] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    rating: Mapped[float] = mapped_column(Float, nullable=True)  # Fixed type
    ranking: Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[str] = mapped_column(String, nullable=True)
    img_url: Mapped[str] = mapped_column(String, nullable=True)

# Move the app context outside the class
with app.app_context():
    db.create_all()


# CREATE TABLE
class EditForm(FlaskForm):
    your_rating = StringField("Your rating out of 10")
    your_review = StringField("Your review")
    Done = SubmitField('Done')

class AddMovie(FlaskForm):
    title = StringField("Movie title")
    add = SubmitField("Add movie")


@app.route("/")
def home():
    result = db.session.execute(db.select(Movie))
    all_movies = result.scalars().all()
    return render_template("index.html", movies= all_movies)

#EDIT FORM
@app.route("/edit", methods=["GET", "POST"])
def edit_movie():
    form = EditForm()
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movie, movie_id)
    if form.validate_on_submit():
        movie.rating= float(form.your_rating.data)
        movie.review = form.your_review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=form, movie=movie)

@app.route("/add", methods=["GET", "POST"])
def add_movie():
    form = AddMovie()
    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(API_URL, params={"api_key": API_KEY, "query":movie_title})
        data = response.json()["results"]
        return render_template('select.html', options=data)
    return render_template("add.html", form=form)


@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movie, movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))




if __name__ == '__main__':
    app.run(debug=True)
