import os
import tarfile
import csv
import io
import time
from datetime import datetime as dt

from flask import Flask,jsonify, render_template, send_file, redirect, url_for, Markup,send_from_directory
#from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, DateTime, Time, create_engine
from operator import itemgetter
from zipfile import ZipFile

import instruments as ins
import experiments as exp

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import seaborn as sns
sns.set()
sns.set_context("notebook", font_scale=1.5, rc={"lines.linewidth": 2.5})
sns.set_style("ticks", {"xtick.major.size": 8, "ytick.major.size": 8,'axes.facecolor': '#EAEAF2'})

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
baseDir = os.getcwd()
runCheckFile = os.path.join(baseDir,'runnig.txt')
dataDir = r"D:\Swapnil\OneDrive - Indian Institute of Science\001_Project_Data\003_PhD_Presentations\07_Thesis_Chapters\07_DRGN\DRGN_03\26_Annealing_Backside_2Bar_front_2E-4_-10Vdc"
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(dataDir, 'data.db')
#engine = create_engine('sqlite:///'+os.path.join(dataDir, 'data.db'), echo=False)
#db = SQLAlchemy(app)

if os.path.exists(runCheckFile):
    os.remove(runCheckFile)

# if os.path.exists(os.path.join(dataDir, 'experiments.db')):
#     os.remove(os.path.join(dataDir, 'experiments.db'))


# class Rvg(db.Model):
#     __tablename__ = 'rvg'
#     #id = Column(Integer, primary_key=True)
#     Rsd = Column(Float)
#     Rg = Column(Float)
#     Vs = Column(Float)
#     Is = Column(Float)
#     Vg = Column(Float)
#     Ig = Column(Float)
#     timeStamp = Column(DateTime,primary_key=True)

#db.create_all()

def db_seed():
    #time.sleep(0.001)
    row = Rvg(Rsd = np.random.randint(0,100),
            Rg = np.random.randint(0,100),
            Vs = np.random.randint(0,100),
            Is = np.random.randint(0,100),
            Vg = np.random.randint(0,100),
            Ig = np.random.randint(0,100),
            timeStamp = np.datetime64(dt.now()).astype(dt))
    db.session.add(row)
    db.session.commit()

# experiment

paramDict = {'instClass':'KT2461',
             'address':'169.254.0.1',
             'source_channel':'a',
             'sourceVolt':0.05,
             'gate_channel':'b',
             'gateVolt':5   ,
             'dataPoints':100,
             'dataLocation':dataDir,
             'experintName':'CurrentAnneal'}

rvg = exp.CurrentAnneal(paramDict,verbose = False)


# Routes
@app.route('/index/')
def index():
    available_exp = [rvg.paramDict['experintName']]
    return render_template('index.html', available_exp = available_exp)

@app.route('/index/rvgConf/')
def rvgConf():
    return render_template('rvg_config.html')

# @app.route('/index/rvgRun/',methods=['POST'])
# def rvgRun():
#     if not os.path.exists(runCheckFile):
#         runFile = open(runCheckFile,"w")
#         runFile.close()
#
#
#         rvg.setExperiment()
#         (df,fileName) = rvg.startExperiment(saveData=True)
#         rvg.closeExperiment()
#         f, ax = plt.subplots(figsize=(10, 8))
#         ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
#         df.plot(x="timeStamp",y="Rsd(Ohm)",ax=ax,colormap='gist_rainbow')
#         figPath = os.path.join(dataDir,'{}.svg'.format(fileName.split('csv')[0][:-1]))
#         plt.savefig(os.path.join(dataDir,'rvg.png'))
#         # quer = 'SELECT * FROM {}'.format("rvg")
#         # df = pd.read_sql_query(quer,str(engine.url),parse_dates={'timeStamp':"%Y-%m-%d %H:%M:%S.%f"})
#         # df.plot(x='timeStamp',y='Rsd')
#         # plt.savefig(os.path.join(dataDir,'rvg.png'))
#
#         os.remove(runCheckFile)
#         return redirect(url_for('expFiles'))
#     else:
#         return redirect(url_for('plotData',experiment_name='rvg'))

@app.route('/index/expFiles/')
def expFiles():
    svglist=[]
    for file in os.listdir(dataDir):
        svglist.append(file)
    return render_template('svglist.html',svglist=svglist)

@app.route('/index/expFiles/getsvg-<svgName>')
def getsvg(fileName):
    return send_file(os.path.join(dataDir,fileName), as_attachment=True)


@app.route("/index/getData-<experiment_name>/")
def getData(experiment_name):
    quer = 'SELECT * FROM {}'.format(experiment_name)
    df = pd.read_sql_query(quer,str(rvg.dbEngine.url),parse_dates={'timeStamp':"%Y-%m-%d %H:%M:%S.%f"})
    dataDict = {col: list(df[col]) for col in df.columns}
    dataDict['timeStamp'] = [i.strftime("%Y-%m-%d %H:%M:%S.%f") for i in dataDict['timeStamp']]
    response = jsonify(dataDict)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/index/plotData-<experiment_name>/')
def plotData(experiment_name):
    return render_template('plotData.html',experiment_name=experiment_name)


if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8000, debug=True)
