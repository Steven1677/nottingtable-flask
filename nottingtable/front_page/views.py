from flask import Blueprint
from flask import render_template

bp = Blueprint('front', __name__, template_folder='templates')


@bp.route('/', methods=('GET',))
def index():
    return render_template('index.html')


@bp.route('/year-1', methods=('GET',))
def show_year_1():
    return render_template('year-1.html')


@bp.route('/public-api', methods=('GET',))
def show_api():
    return render_template('api.html')
