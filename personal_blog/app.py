from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


#################################################################################################################


app = Flask("__main__")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)


#################################################################################################################


class Essay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)


    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


#################################################################################################################

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/essays")
def essays():
    essays = Essay.query.all()
    newest_essay =  Essay.query.order_by(Essay.date_posted.desc()).first()
    return render_template("essays.html", essays = essays, newest_essay = newest_essay)

@app.route("/essay/<int:essay_id>")
def essay(essay_id):
    essay = Essay.query.get_or_404(essay_id)
    return render_template("essay.html", essay=essay)

@app.route("/create", methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_post = Essay(title=title, content=content)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("create.html")


#################################################################################################################







if "__main__" == __name__:
    app.run(host="0.0.0.0", port=5000)
