from flask import Blueprint
from flask import render_template

from nottingtable.crawler.models import Y1Group
from nottingtable.crawler.models import MasterPlan

bp = Blueprint('front', __name__, template_folder='templates')


@bp.route('/', methods=('GET',))
def index():
    return render_template('index.html')


@bp.route('/year-24', methods=('GET',))
def show_year_24():
    return render_template('year-24.html')


@bp.route('/year-1', methods=('GET',))
def show_year_1():
    """
    Render page for year1 selection page
    :return: rendered page with selection list
    """

    group_list = Y1Group.query.all()
    return render_template('year-1.html', group_list=group_list)


@bp.route('/plan', methods=('GET',))
def show_plan():
    """
    Render page for master students
    :return: rendered page with selection list
    """

    plan_list = MasterPlan.query.all()
    return render_template('plan.html', plan_list=plan_list)


@bp.route('/public-api', methods=('GET',))
def show_api():
    return render_template('api.html')
