#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from flask import render_template, request, url_for, redirect, session, flash
import json
import os
import sys
import random
import pickle
import hashlib

@app.route('/', methods=['GET', 'POST'])
@app.route('/index.html', methods=['GET', 'POST'])
def index():
    films = None
    if request.method == 'POST':
        # Get the search result
        title = request.form.get('title')
        category = request.form.get('category')

        if (not title) and category == 'Ninguno':
            return redirect(url_for('index'))

        with open(os.path.join(app.root_path,'catalogue/catalogo.json'), encoding="utf-8") as data_file:
            catalogue = json.loads(data_file.read())
            films = catalogue['peliculas']
            if category != 'Ninguno':
                films = list(filter(lambda f: category in f['categorias'], films))
            films = list(filter(lambda f: title.lower() in f['titulo'].lower(), films))

        if not title:
            title = 'Peliculas en la catergoría: '+category
        return render_template('index.html', title='Búsqueda', films=films, search_query=title)

    else:
        # Get the last films
        with open(os.path.join(app.root_path,'catalogue/catalogo.json'), encoding="utf-8") as data_file:
            catalogue = json.loads(data_file.read())
            films = catalogue['peliculas']
            films = sorted(films, key=(lambda m : m['anio']), reverse=True)[:10]

        return render_template('index.html', title='Home', films=films, search_query=None)


@app.route('/product/<id>', methods=['GET'])
def product(id):
    with open(os.path.join(app.root_path,'catalogue/catalogo.json'), encoding="utf-8") as data_file:
        catalogue = json.loads(data_file.read())
        films = catalogue['peliculas']
        film = list(filter(lambda f: int(id) == f['id'], films))[0]

    return render_template('product.html', title=film['titulo'], film=film)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Getting data from form
        nick = request.form.get('nickname')
        passwd = request.form.get('password')
        mail = request.form.get('mail')
        ccard = request.form.get('ccard')
        # Validate fields
        if not (nick and passwd and mail and ccard):
            flash('Por favor, rellene todos los campos')
            return render_template('register.html')
        # Check user is available
        users = next(os.walk(os.path.join(app.root_path, 'usuarios/')))[1]
        if nick in users:
            flash('Usuario no disponible')
            return render_template('register.html')
        # The username is available, so we store all the data
        # Hashing the password with md5
        md5 = hashlib.md5()
        md5.update(passwd.encode('utf-8'))
        encpwd = md5.hexdigest()
        # Preparing data to be stored
        data = [nick, encpwd, mail, ccard, random.randint(0, 100)]
        # Writing user data file
        slug_nick = nick.lower()
        os.mkdir(os.path.join(app.root_path, 'usuarios', slug_nick))
        with open(os.path.join(app.root_path, 'usuarios', slug_nick, 'datos.dat'), 'wb') as file:
            pickle.dump(data, file)
        # Initializing user history file
        with open(os.path.join(app.root_path, 'usuarios', slug_nick, 'historial.json'), 'w') as file:
            history = {'historial': []}
            json.dump(history, file)

        return redirect(url_for('index'))
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Getting data from form
        nick = request.form.get('nickname')
        passwd = request.form.get('password')
        # Checking user data
        # Validate fields
        if not (nick and passwd):
            flash('Por favor, rellene todos los campos')
            return render_template('login.html')
        # Checking if the user is already registered
        slug_nick = nick.lower()
        users = next(os.walk(os.path.join(app.root_path, 'usuarios/')))[1]
        if slug_nick not in users:
            flash('Usuario no registrado')
            return render_template('login.html')
        # Checking the password
        md5 = hashlib.md5()
        md5.update(passwd.encode('utf-8'))
        encpwd = md5.hexdigest()
        with open(os.path.join(app.root_path, 'usuarios', slug_nick, 'datos.dat'), 'rb') as file:
            userdata = pickle.load(file)
        if encpwd != userdata[1]:
            flash('Contraseña incorrecta')
            return render_template('login.html')
        # Sessions
        session['nickname'] = userdata[0]
        session['mail'] = userdata[2]
        session['ccard'] = userdata[3]

        return redirect(url_for('index'))
    else:
        return render_template('login.html')