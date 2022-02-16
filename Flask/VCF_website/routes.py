from flask import render_template, url_for, flash, redirect, request, session, make_response
from io import StringIO
from werkzeug.wrappers import Response
from VCF_website import app
from VCF_website.forms import ContactForm, SearchPos, SearchRs, SearchGene, PopulationStatistics
from VCF_website.models import query_search
import ast
import csv
import allel
import numpy as np
import json


# @app.before_first_request
# def create_tables():
# db.create_all()


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')





@app.route("/about")
def about():
    return render_template('about.html', title='About Us')






@app.route("/search", methods=['GET', 'POST'])
def search():
    form1 = SearchPos()
    form2 = SearchRs()
    form3 = SearchGene()

    if form1.submit.data and form1.validate_on_submit():
        chromosome_position = {
            "chr": form1.select.data,
            "start_pos": form1.start_pos.data,
            "end_pos": form1.end_pos.data
        }
        return loading(search=chromosome_position)
    elif form2.rs_search.data and form2.validate_on_submit():
        form2_rs = f"'{form2.rs_val.data}'"
        return loading(search=form2_rs)
    elif form3.gene_search.data and form3.validate_on_submit():
        form3_gene = f"'{form3.gene.data}'"
        return loading(search=form3_gene)
    return render_template('search.html', title='About', form1=form1, form2=form2, form3=form3)






def pop_data(results, *end_pos):
    mxl = []
    gbr = []
    jpt = []
    pjl = []
    yri = []
    if end_pos != None:
        for x in results:
            mxl = mxl + (x.mxl)
            gbr = gbr + x.gbr
            jpt = jpt + x.jpt
            pjl = pjl + x.pjl
            yri = yri + x.yri
    else:
        for x in results:
            mxl = x.mxl
            gbr = x.gbr
            jpt = x.jpt
            pjl = x.pjl
            yri = x.yri
        for x in mxl:
            hom_alt = ast.literal_eval(x.geno_freq)

    return mxl, gbr, jpt, pjl, yri


@app.route("/loading", methods=['GET', 'POST'])
def loading(search):
    variable = search
    print(variable)
    print(type(variable))

    print('HIIIIII')
    if isinstance(variable, dict):
        if variable["end_pos"] == None:
            results = query_search.query.filter(query_search.pos.like(variable['start_pos'])).filter(query_search.chrom == '{}'.format(variable["chr"])).all()
            mxl, gbr, jpt, pjl, yri = pop_data(results, variable["end_pos"])
            print('HIIIIII 1.1')
            return redirect(url_for('results', title='Results', Results=results))
        else:
            results = query_search.query.filter(query_search.pos >= int(variable['start_pos'])).filter(query_search.pos <= int(variable['end_pos'])).filter(query_search.chrom == '{}'.format(variable['chr'])).all()
            print('HIIIIII 1.2')
            mxl, gbr, jpt, pjl, yri = pop_data(results, variable["end_pos"])
            # session['results'] = json.dumps([i.to_dict() for i in results])
            # session['mxl'] = json.dumps([i.to_dict() for i in mxl])
            return redirect(url_for('results', title='Results'))

    elif variable.startswith('rs'):
        print(' This is working')
    else:
        # if variable.startswith('rs') == True:
        #     print('hi var')
        #     var = True
        # else:
        #     var = False
        # if var:
        #     print('Hi')
        #     results = query_search.query.filter(query_search.rs_val.like(variable)).all()
        #     print(results)
        #     print('HIIIIII 2.1')
        #     if not results:
        #         flash("No result found, please search for another ID", 'info')
        #         return redirect(url_for('search'))
        #     mxl, gbr, jpt, pjl, yri = pop_data(results)
        #     # session['results'] = json.dumps([i.to_dict() for i in results])
        #     # session['mxl'] = json.dumps([i.to_dict() for i in mxl])
        #     # print(session['results'])
        #     return redirect(url_for('results', title='Results'))
        print('HIIIIII 2.2')
    #     results = query_search.query.filter(
    #         query_search.gene_name.like(variable)).all()
    #     mxl, gbr, jpt, pjl, yri = pop_data(results)
        return redirect(url_for('results', title='Results', Results=results, MXL=mxl, GBR=gbr, JPT=jpt, PJL=pjl, YRI=yri))







@app.route("/results", methods=['GET', 'POST'])
def results():
    results = json.loads(session['results'])
    mxl = json.loads(session['mxl'])
    pop_array = []
    # temp = []
    # for x in mxl:
    #     temp.append(x['genotypes'])

    # print(temp)
    # gen_arr = allel.GenotypeArray(np.array(pop_array))
    form = PopulationStatistics()
    if request.method == "POST":
        if form.validate_on_submit():
            return stats(pop_sel=form.populations.data, stats_sel=form.stats.data)
    return render_template('results.html', Results=results, MXL=mxl, form=form)





@app.route("/stats")
def stats(pop_sel, stats_sel):
    results = session['results']
    print(len(pop_sel))
    print(type(pop_sel))
    print(len(stats_sel))
    print(type(stats_sel))
    # if "results" in session:
    #     if len(pop_sel) >= 2 and stats_sel != None:
    #         print(results)
    #     else:
    return render_template('stats.html', stats=stats_sel, populations=pop_sel, results=results)


"""
Temp Download page with dummy data

"""
test_down = [{'chrom': '22', 'rs_val': 'rs587698813', 'pos': '16051164',
              'gene_name': None, 'ref_allele': 'G', 'alt_allele': 'A'}]


@app.route('/download')
def download():
    si = StringIO()
    fields = [
        'chrom',
        'rs_val',
        'pos',
        'gene_name',
        'ref_allele',
        'alt_allele'
    ]
    cw = csv.DictWriter(si, fieldnames=fields)
    cw.writeheader()
    for stats in test_down:
        cw.writerow(stats)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=stats.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        flash(f'You Query has been submmited', 'success')
        return redirect(url_for('home'))
    return render_template('contact.html', title='Contact', form=form)


# def save_picture(form_picture):
#     random_hex = secrets.token_hex(8)
#     _, f_ext = os.path.splitext(form_picture.filename)
#     picture_fn = random_hex+f_ext
#     picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
#     form_picture.save(picture_path)
#     return picture_fn
