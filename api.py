import flask
from flask import request
from datetime import datetime

# importation of linked python file
import scraping
import process
import model

import warnings
warnings.filterwarnings(action='ignore')

# instantiate Flask
app = flask.Flask(__name__)
app.config["DEBUG"] = False


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Bienvenue sur l'API d'analyse de sentiments</h1>
<p>Pour effectuer une recherche, ajoutez '/graphs?category=' suivi de la catégorie visée à la barre de recherche</p>
<p>Vous pouvez également ajouter des paramètres: 
    <ul>
        <li> le nombre de site à intégrer dans votre recherche '&num_of_site=' (0 pour tous les sites, défaut = 5)</li>
        <li> le nombre de page à rechercher pour chaque site '&num_page=' (0 pour toutes les pages, défaut = 2)</li>
    </ul>
</p>
<p>Exemple:  
    <a href="http://127.0.0.1:5000/graphs?category=restaurants_bars&num_of_site=3&num_page=3">http://127.0.0.1:5000/graphs?category=restaurants_bars&num_of_site=3&num_page=3</a>
</p>
<p>Liste des catégories à insérer dans la barre de recherche: 
    <ul>
        <li>food_beverages_tobacco</li>
        <li>animals_pets</li>
        <li>money_insurance</li>
        <li>beauty_wellbeing</li>
        <li>construction_manufactoring</li>
        <li>education_training</li>
        <li>electronics_technology</li>
        <li>events_entertainment</li>
        <li>hobbies_crafts</li>
        <li>home_garden</li>
        <li>media_publishing</li>
        <li>restaurants_bars</li>
        <li>health_medical</li>
        <li>utilities</li>
        <li>home_services</li>
        <li>business_services</li>
        <li>legal_services_government</li>
        <li>public_local_services</li>
        <li>shopping_fashion</li>
        <li>sports</li>
        <li>travel_vacation</li>
        <li>vehicles_transportation</li>
    </ul>
</p>
'''


@app.route('/graphs', methods=['GET'])
def graphs():
    initial_time = datetime.now()
    # 1. Get desired category and number of page to scrape in each site from request
    category = request.args.get('category')

    if request.args.get('num_page'):
        num_page = int(request.args.get('num_page'))
    else:
        num_page = 2

    if request.args.get('num_of_site'):
        num_of_site = int(request.args.get('num_of_site'))
    else:
        num_of_site = 5

    model_to_test = ''
    if request.args.get('model'):
        model_to_test = 'camembert'

    print(category, num_page, num_of_site)
    print('\n', '#'*50)
    print(f' Start Analyse on {category} '.center(50, '#'))
    print('#'*50, '\n')

    # 2. Scrape trustpilot to get dataframe
    init_time = datetime.now()
    print(' Start scraping '.center(30, '#'))
    refs, df = scraping.scrape(category, num_of_site, num_page)
    time_elapsed = datetime.now() - init_time
    print(f'Scraping time : {time_elapsed}')

    # 3. Preprocess dataframe before prediction
    init_time = datetime.now()
    print(' Start preprocess '.center(30, '#'))
    df = process.preprocess_df(df)
    df.to_csv(r'test.csv')
    time_elapsed = datetime.now() - init_time
    print(f'Preprocess time : {time_elapsed}')

    # 4. Predict sentiment and add it to dataframe
    init_time = datetime.now()
    print(' Start prediction '.center(30, '#'))
    if model_to_test == 'camembert':
        df = model.predict_camembert(df)
    else:
        df = model.predict(df)
    time_elapsed = datetime.now() - init_time
    print(f'Prediction time : {time_elapsed}')

    # 5. Apply postprocess to transform data into json
    init_time = datetime.now()
    print(' Start postprocess '.center(30, '#'))
    json_review = process.postprocess(df, refs)
    time_elapsed = datetime.now() - init_time
    print(f'Postprocess time : {time_elapsed}')
    time_elapsed = datetime.now() - initial_time
    print(f'Total time elapsed : {time_elapsed}')
    return json_review


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


app.run()
