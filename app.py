from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, Users, Ad, Response, Material, ShipMaterial
from werkzeug.utils import secure_filename
import os
from sqlalchemy import select
from glob import glob
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from sqlalchemy import func, Column
from sqlalchemy.orm import aliased

class Plug:
    pass

STATIC_FOLDER = os.path.abspath('static')
UPLOAD_FOLDER = os.path.abspath('static/images')
app = Flask(__name__,static_folder='static')

app.config['SECRET_KEY'] = '12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:pwrd@localhost/db_ads'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def add_image_paths(classes):
    for obj in classes:
        image_directory = os.path.join(UPLOAD_FOLDER, obj.id)
        all_files = glob(os.path.join(image_directory, '*'))
        image_paths = [os.path.relpath(f,STATIC_FOLDER) for f in all_files]
        image_paths = [f.replace('\\','/') for f in image_paths]
        print(image_paths)
        obj.image_paths = image_paths




db.init_app(app)
migrate = Migrate(app, db)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/')
def index():
    a = aliased(Ad)
    km = aliased(ShipMaterial)

    query = (
        select(
            a.id.label('sname'),
            a.speed,
            a.text,
            func.array_agg(km.material_id).label('reqmats'),
            func.array_agg(km.amount).label('req')

        )
        .select_from(a)
        .outerjoin(km, a.id == km.ad_id)
        .group_by(a.id)
    )
    result = db.session.execute(query).all()
    print(result)
    ads = []
    for res in result:
        plug = Plug()
        plug.id = res[0]
        plug.speed=res[1]
        plug.text=res[2]
        plug.matAmounts=zip(res[3],res[4])
        ads.append(plug)

    add_image_paths(ads)
    print(ads[0].matAmounts)

    return render_template('index.html', ads=ads)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = Users(username=username, password=hashed_password, balance=0)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Users.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('ad_form'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


@app.route('/ad/create', methods=['GET', 'POST'])
@login_required
def ad_form():
    if request.method == 'POST':
        ad_id = request.form['id']
        text = request.form['text']



        existing_ad = Ad.query.get(ad_id)
        if existing_ad:
            flash('This ID already exists. Please choose another one.', 'danger')
            return render_template('ad_form.html')


        new_ad = Ad(id=ad_id, user_id=current_user.id, text=text,speed=request.form['speed'])

        try:
            db.session.add(new_ad)

            flds = [fld[0] for fld in Material.query.with_entities(Material.name).all()]
            print(flds)
            for fld in flds:
                print(f"Processing field {fld} with value {request.form.get(fld)}")
                new_shipMat=ShipMaterial(ad_id=ad_id,material_id=fld,amount=request.form[fld])
                db.session.add(new_shipMat)
            db.session.commit()



            if 'images' in request.files:
                files = request.files.getlist('images')


                ad_folder = os.path.join(app.config['UPLOAD_FOLDER'], ad_id)
                if not os.path.exists(ad_folder):
                    os.makedirs(ad_folder)

                for index, file in enumerate(files):
                    if file and allowed_file(file.filename):
                        ext = file.filename.rsplit('.', 1)[1].lower()
                        filename = f"{ad_id}_{index + 1}.{ext}"
                        file.save(os.path.join(ad_folder, filename))

            flash('Ad created successfully!', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating ad: {str(e)}', 'danger')
            print(e)
            return render_template('ad_form.html')

    flds= [fld[0] for fld in Material.query.with_entities(Material.name).all()]

    print(flds)
    return render_template('ad_form.html',flds=flds)

@app.route('/ad/<string:ad_id>/respond', methods=['POST'])  # Изменено с int на string
@login_required
def respond_ad(ad_id):
    ad = Ad.query.get(ad_id)
    if not ad:
        flash('Ad not found.', 'danger')
        return redirect(url_for('index'))

    if ad.user_id == current_user.id:
        flash("You can't respond to your own ad.", 'danger')
        return redirect(url_for('index'))

    existing_response = Response.query.filter_by(ad_id=ad_id, user_id=current_user.id).first()
    if existing_response:
        flash('You have already responded to this ad.', 'warning')
        return redirect(url_for('index'))

    new_response = Response(ad_id=ad_id, user_id=current_user.id)
    db.session.add(new_response)
    db.session.commit()
    flash('You have responded to the ad!', 'success')
    return redirect(url_for('index'))

@app.route('/my_ads')
@login_required
def my_ads():
    ads = (Ad.query.filter_by(user_id=current_user.id)
           .outerjoin(Response)
           .group_by(Ad.id)
           .order_by(db.func.count(Response.id).desc())
           .all())
    return render_template('my_ads.html', ads=ads)

@app.route('/my_responses')
@login_required
def my_responses():
    responses = Response.query.filter_by(user_id=current_user.id).all()
    ads = [response.ad for response in responses]
    return render_template('my_responses.html', ads=ads)

if __name__ == '__main__':
    app.run(debug=True)