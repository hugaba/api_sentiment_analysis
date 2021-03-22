import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# header to don't be stopped from scraping website
HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
}


def scrape_category(category: str, num_of_site: int) -> list:
    """
    scrape a given category to have a list of site to use in scrape_site
    :param category: str: category to scrape
    :param num_of_site: int: number of site to scrape
    :return: list: list of site and refs to scrape in the param category
    """

    list_of_site = []
    site_to_scrape = []

    page_to_scrape = True
    num_page = 1
    while page_to_scrape:
        # url to scrape
        url = f"https://fr.trustpilot.com/categories/{category}?page={num_page}"

        try:
            req = requests.get(url, HEADERS, timeout=1)  # wait 1 second before sending error
        except:
            req = requests.get(url, HEADERS)

        soup = BeautifulSoup(req.content, 'html.parser')
        # search site name into category page
        for site in soup.find_all(["div"], attrs={"class": "styles_businessTitle__1IANo"}):
            site = site.text.strip()
            list_of_site.append(site)

        # check if there is a page after the current one
        tag = soup.find(["a"], attrs={"name": "pagination-button-next"})
        if tag:
            num_page += 1
        else:
            page_to_scrape = False

    # keep unique values from list
    list_of_site = list(dict.fromkeys(list_of_site))

    if num_of_site > len(list_of_site) or num_of_site == 0:
        num_of_site = len(list_of_site)

    site_to_remove = []

    for site in list_of_site[:num_of_site]:
        end = ['.fr', '.com']
        # check if adress already finish by '.fr' or '.com'
        # if True url2 will lead to nothing
        if any(substring in site.lower() for substring in end):
            site_to_scrape.append(site)
        elif "n'existe plus" in site.lower():
            site_to_remove.append(site)
        else:
            # scrape a new url with the site name to get full site name
            # from "Flashbay" we want "flashbay.fr"
            # from "Cadeaucity" we want "www.cadeaucity.com"
            url2 = f"https://fr.trustpilot.com/search?query={site}"
            try:
                req2 = requests.get(url2, HEADERS, timeout=1)  # wait 1 second before sending error
            except:
                req2 = requests.get(url2, HEADERS)
            soup2 = BeautifulSoup(req2.content, 'html.parser')
            for final_site in soup2.find(["a"], attrs={"class": "search-result-heading"}):
                final_site = final_site.split(' | ')[1]
                site_to_scrape.append(final_site)

    return [list_of_site, site_to_scrape]


def scrape_site(refs: list, max_page) -> pd.DataFrame:
    """
    scrape a list of sites on trustpilottrustpilot
    :param refs: list: list of site to scrape
    :param max_page: max number of page to scrape on each site
    :return: dataframe
    """
    # initialization of variable infos
    infos = []
    # iteration over list of sites
    for site in refs:
        page_to_scrape = True
        num_page = 1

        # scrape while there is page to scrape or max number of page is reached
        while page_to_scrape:

            # url to scrape
            url = f"https://fr.trustpilot.com/review/{site}?page={num_page}"

            try:
                req = requests.get(url, HEADERS, timeout=1)  # wait 1 second before sending error
            except:
                req = requests.get(url, HEADERS)
            soup = BeautifulSoup(req.content, 'html.parser')

            # get infos for every review for one site
            for opinion in soup.find_all(["div"], attrs={"class": "review-content"}):
                info = [site]

                # get number of stars
                star = opinion.find(["div"], attrs={"class": "star-rating star-rating--medium"})
                img = star.find('img')
                if img:
                    info.append(img['alt'])

                # get title
                title = opinion.find('h2', attrs={'class': 'review-content__title'})
                if title:
                    info.append(title.text.strip())

                # get review content
                content = opinion.find(["p"], attrs={"class": "review-content__text"})
                if content:
                    info.append(content.text.strip())
                else:
                    info.append('')

                # get date of post
                date_of_post = opinion.find(['div'], attrs={"class": 'review-content-header__dates'})
                if date_of_post:
                    date_of_post = str(date_of_post)
                    date_of_post = re.search('"publishedDate":"(.*)","updatedDate', date_of_post).group(1)
                    info.append(date_of_post)
                infos.append(info)

            # check if there is a page after the current one
            tag = soup.find(["a"], attrs={"class": "button button--primary next-page"})
            if tag and num_page != max_page:
                num_page += 1
            else:
                page_to_scrape = False

    df = pd.DataFrame(infos, columns=['site', 'note', 'titre', 'comment', 'date'])
    pd.set_option('display.max_columns', None)
    pd.set_option('display.expand_frame_repr', False)
    return df


def scrape(category: str, num_of_site: int, num_page: int) -> tuple:
    """
    scrape truspilot reviews
    :param category: str: category to scrape
    :param num_of_site: int: number of site to scrape (0 for all site)
    :param num_page: int: number of page to scrape on each site (0 for all pages)
    :return: tuple: tuple with refs from scrape_category and dataframe with scraped data
    """
    refs = scrape_category(category, num_of_site)
    df = scrape_site(refs[1], num_page)
    return refs, df


# ####################################
# ############## TESTS ###############
# ####################################

# ref_to_scrape = 'auroremarket.fr'
#category = 'restaurants_bars'

# refs = scrape_category(category)
#df = scrape(category, num_of_site=0, num_page=1)

#print(df)