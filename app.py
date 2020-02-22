import os
import tarfile
import csv
import io
import time

from flask import Flask, render_template, send_file, redirect, url_for, Markup,send_from_directory
from flask_login import login_required, current_user
from operator import itemgetter
from zipfile import ZipFile

import instruments as ins
import experiments as exp

app = Flask(__name__)
baseDir = os.getcwd()
runCheckFile = os.path.join(baseDir,'runnig.txt')
dataDir = "/mnt/5a576321-1b84-46e6-ba92-46de6b117d92/GitHub/dataDir/"


@app.route('/index/')
def index():
    available_exp = ['rvg']
    return render_template('index.html', available_exp = available_exp)

@app.route('/index/rvgConf/')
def rvgConf():
    return render_template('rvg_config.html')

@app.route('/index/rvgRun/',methods=['POST'])
def rvgRun():
    if not os.path.exists(runCheckFile):
        runFile = open(runCheckFile,"w")
        runFile.close()
        time.sleep(20)
        data='expt data'
        os.remove(runCheckFile)
        return render_template('rvg_runFinish.html',data=baseDir)
    else:
        return redirect(url_for('expFiles'))

@app.route('/index/expFiles/')
def expFiles():
    svglist=[]
    for file in os.listdir(dataDir):
        svglist.append(file)
    return render_template('svglist.html',svglist=svglist)

@app.route('/index/expFiles/getsvg-<svgName>')
def getsvg(svgName):
    svgpath = os.path.join(dataDir,svgName)
    svg = open(svgpath).read
    return send_from_directory(dataDir,svgName, as_attachment=True)

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8000, debug=True)
