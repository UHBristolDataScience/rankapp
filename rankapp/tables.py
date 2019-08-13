import pandas as pd
import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, session
)
from werkzeug.exceptions import abort

from rankapp.auth import login_required, logout
from rankapp.db import get_db
from rankapp.patient_db import DummyPatientData, IccaPatientData

bp = Blueprint('tables', __name__)

## using global variables for table data
##   A class would be more elegant but requires url endpoint rules
##   rather than decorators as currently used here.
df = pd.DataFrame()
#nrfd = dict()


@bp.route('/')
@login_required
def index():
    global df
    if current_app.config['PATIENTDATA']=='dummy':
        patientData = DummyPatientData()
    elif current_app.config['PATIENTDATA']=='icca':
        patientData = IccaPatientData()

    df = patientData.returnPatientDf()
    #nrfd = {name:False for name in df['Name']}
    table_d = json.loads(df.to_json(orient='index'))
    columns = df.columns
                
    return render_template('tables/table1.html', columns=columns, 
                            table_data=table_d)

# Removing table 2 and condensing response into single page...
#@bp.route('/table2')
#@login_required
#def table2():
#    global df
#    drop_rows = [i for i,name in enumerate(df['Name']) if nrfd[name]] 
#    df_selected = df.drop(drop_rows, axis=0)
#    df_selected['Rank'] = [i for i in range(len(df_selected))]
#    df_selected = df_selected[['Rank', 'Name', 'Bed', 'T_number', 'Age', 'Admission']]
#    table_d = json.loads(df_selected.to_json(orient='index'))
#    columns = df_selected.columns
#            
#    return render_template('tables/table2.html', columns=columns, 
#                            table_data=table_d)

@bp.route('/logout_msg')
def finish():
    logout()
    return render_template('tables/logout_msg.html')

@bp.route('/submit_table1', methods=('GET', 'POST'))
@login_required
def submit_table1():
    if request.method == 'POST':
        global df #, nrfd
        user_id = session.get('user_id')
        db = get_db()
        
        error = None
        if db.execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone() is None:
            error = 'User with id {} not in database.'.format(user_id)

        if error is None:
            db.execute(
                'INSERT INTO response (author_id) VALUES (?)',
                (user_id,)
            )
            db.commit()
        response_id = db.execute('SELECT LAST_INSERT_ROWID() as r_id').fetchone()['r_id']
        print(response_id)
        
        for name in df['Name']:    
            status = request.form[name]
            db.execute(
                'INSERT INTO status (response_id, author_id, status, name, bed_number) VALUES (?,?,?,?,?)',
                (response_id, user_id, status, name, int(df[df['Name']==name]['Bed'].iloc[0]),)
            )
            db.commit()
        #    if selected=="selected":
        #        nrfd[name] = True
        #    elif selected=="unselected":
        #        nrfd[name] = False
        testdata = db.execute('SELECT * FROM status WHERE response_id==?', (response_id,)).fetchall()
        for row in testdata:
            print([row[key] for key in row.keys()])
        #print(nrfd)
    #return redirect(url_for('tables.table2'))
    return redirect(url_for('tables.finish'))

#@bp.route('/submit_table2', methods=('GET', 'POST'))
#@login_required
#def submit_table2():
#    if request.method == 'POST':
#        global df, nrfd
#        for name in df['Name']:    
#            if not nrfd[name]:
#                rank = request.form[name]
#                print("%s : %s" %(name,rank))
#        
#    return redirect(url_for('tables.finish'))
