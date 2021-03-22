# api_sentiment_analysis
contributors: Imad Hennini, Hugo Algaba

## List of files:
- api.py : Main file to launch to run api.
- process.py : file with preprocessing and postprocessing function definition
- model.py : file with loading of models to do prediction
- scraping.py : file witch takes scrape data on trustpilot
- sentiment_analysis.ipynb : notebook for model creation
- sentiment_analysis_camembert.ipynb notebook for camembert model creation

## How to use api?
Download weight model files and add them to your virtual envirronment directory:
https://drive.google.com/drive/folders/1TlVXRIaed36yPEV9kliUAdufRF4FjrmY?usp=sharing

- 100features_40minwords_20context_bigram
- model_bigram.h5
- model_bigram.json
- camembert_model

Run api.py file.

Option 1:
- Click on the link in the terminal (http://127.0.0.1:5000/)
- This will redirect you to a web page and you can follow instruction on it.

Option 2:
- Use the base: http://127.0.0.1:5000/
- then add *graphs?category=* followed by the category you want on trustpilot (by default, this will scrape 5 sites and 2 pages on each site)
- You can add optional arguments:
  - num_of_site : number of site to scrape
  - num_page : number of pages to scrape on each site
  - model: model to use for prediction(only possible value 'camembert', if model not specified, this will do basic nlp prediction)
-example: http://127.0.0.1:5000/graphs?category=restaurants_bars&num_of_site=50&num_page=3&model=camembert