from flask import Flask, render_template, redirect, url_for
from forms import UserForm
from models import db, User

app = Flask(__name__)

# CSRF protection.
app.config["SECRET_KEY"] = "SOpassword123$"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/", methods=['GET', 'POST'])
def home():
    form = UserForm()

    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("index"))

    return render_template("index.html", form=form)



if __name__ == "__main__":
    app.run(debug = True, host = "0.0.0.0", port = 3000)