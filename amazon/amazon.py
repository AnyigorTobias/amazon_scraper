import requests 
import re
import pandas as pd
from bs4 import BeautifulSoup

proxy_host = "vienna1.thesocialproxy.com"
proxy_port = "10000"
proxy_url = f"http://{proxy_host}:{proxy_port}"
proxy_username = "09bk1yv3mtxahdnpas3"
proxy_password = "4mtanfsqeczh9l2jw31"
proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"

proxies = { "http": proxy_url, "https": proxy_url }


header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }

url = ("https://www.amazon.com/HINOMI-Ergonomic-Foldable-Suitable-Computer/dp/B0CHRQWNCH/"
       "?_encoding=UTF8&pd_rd_w=ehyH1&content-id=amzn1.sym.4bba068a-9322-4692-abd5-0bbe652907a9&pf_rd_p=4bba068a-9322-4692-abd5-0bbe652907a9"
       "&pf_rd_r=7VDVZANP4F104RGPP3ZT&pd_rd_wg=piGQB&pd_rd_r=fe8c79ea-20d0-46b2-bbba-af6e30e2c1aa"
       "&ref_=pd_hp_d_btf_nta-top-picks&th=1"
    )

# Set up a session
session = requests.Session()
session.proxies = proxies

page = session.get(url, headers=header)
assert page.status_code == 200
soup = BeautifulSoup(page.content, 'html.parser')

#start:delete after first run
title = soup.find('span', attrs={'id': 'productTitle'}).get_text(strip=True)
print(title)
price = soup.find('span', attrs={'class': 'a-offscreen'}).get_text(strip=True)
print(price)

feature_bullets = soup.find('div', id='feature-bullets')
if feature_bullets:
    ul = feature_bullets.find('ul', class_='a-unordered-list')
    if ul:
        # Extract text from each 'li' tag within the 'ul'
        for li in ul.find_all('li', class_='a-spacing-mini'):
            bullet_text = li.get_text(strip=True)
            print(bullet_text)
            
#end 
            

def get_page_content(url, proxies):
    
    header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }
    
    # Set up a session
    session = requests.Session()
    #add the proxy to the session
    session.proxies = proxies
    
    #access the website page through the proxy
    page = session.get(url, headers=header)
    #check if the website was loaded succesfully
    assert page.status_code == 200
    
    #this return the html content from the page
    soup = BeautifulSoup(page.content, 'html.parser')
    
    return soup


def get_product_information(soup):
    #get the title of the product
    title = soup.find('span', attrs={'id': 'productTitle'}).get_text(strip=True)
    # get the price of the product
    price = soup.find('span', attrs={'class': 'a-offscreen'}).get_text(strip=True)
    #print(title)
    #print(price)

    feature_bullets = soup.find('div', id='feature-bullets')
    #this is an empty list where the description text will be saved
    description = []
    if feature_bullets:
        ul = feature_bullets.find('ul', class_='a-unordered-list')
        if ul:
            # Extract text from each 'li' tag within the 'ul'
            for li in ul.find_all('li', class_='a-spacing-mini'):
                bullet_text = li.get_text(strip=True)
                description.append(bullet_text)
                #combines all description into a single text
                text = ' '.join(description)
                

     #returns the title, price and description of the product
    return title, price,text


def get_similar_products(item):
    # Extract product title
    product_tag = item.find('img', class_='shopbylook-btf-image-elem')
    product_title = product_tag['alt'] if product_tag else 'No product_tag alt text found'

    # Extract price of similar product
    price_tag = item.find('span', class_='a-offscreen')
    price = price_tag.get_text(strip=True) if price_tag else 'No price found'

    # Extract price fraction
    fraction_tag = item.find('span', class_='a-price-fraction')
    price_fraction = fraction_tag.get_text(strip=True) if fraction_tag else 'No price fraction found'
    #combine price and price fraction into the single price
    #it will look like $200.20
    final_price = price + "."+ price_fraction

    # Display results
   # print(f"Image Alt Text: {product_title}")
    #print(f"Price: {price}")
  #  print(f"final_price: {final_price}")



    similar_product_data = product_title,final_price

    return similar_product_data


def get_review_details(review):
    
    # Extract the product name
    name = review.find("span", class_ = "a-profile-name").get_text(strip=True)
    #print(name)
        
    location_tag = review.find("span", class_='a-size-base a-color-secondary review-date')
    if location_tag:
        location = location_tag.get_text(strip=True)
        
        # Extract country name using regex
        country_match = re.search(r'Reviewed in ([a-zA-Z\s]+) on', location)
        country = country_match.group(1) if country_match else "Unknown"
        #print("Country:", country)
        #print("Reviewer Location:", location)
    
    # Extract Reviewer Rating
    rating_tag = review.find("span", class_='a-icon-alt')
    if rating_tag:
        rate = rating_tag.get_text(strip=True)
        #extract rating using regex
        rating_match = re.search(r'(\d+\.\d+|\d+)', rate)
        rating = rating_match.group(1) if rating_match else "Unknown"
        #print("Rating:", rating)
        
     # Extract the review text
    review_body = review.find('div', class_='review-text-content')
    if review_body:
        review_text = review_body.find('span').get_text(separator=' ').strip()
        #print("Review Text:", review_text)
        
        
    return name, country, rating, review_text



def extract_info_to_dataframe(url, proxies):
    
    # Get page content
    soup = get_page_content(url, proxies)
    
    # Extract product information
    title, price, description = get_product_information(soup)
    product_info = [
        {"Title": title,
            "Price": price,
            "Description": description}]

    # Extract similar products
    similar_products = []
    items_section = soup.find_all('div', class_='shopbylook-btf-item-box')
    if not items_section:
        print("No items found with the class 'shopbylook-btf-item-box'.")
    else:
        for item in items_section:
            product_title, final_price = get_similar_products(item)
            similar_products.append({
                "Similar Product Title": product_title,
                "Similar Product Price": final_price})

    # Extract reviews
    review_details = []
    
    #Extract reviews from users in countries outside USA
    foreign_reviews = soup.find_all('div', class_='a-section review aok-relative cr-desktop-review-page-0')
    for review in foreign_reviews:
        name, country, rating, review_text = get_review_details(review)
        review_details.append((name, country, rating, review_text))
    
    #Extract reviews from users in countries outside USA
    us_reviews = soup.find_all('div', attrs={'data-hook': 'review', 'class': 'a-section review aok-relative'})
    for review in us_reviews:
        name, country, rating, review_text = get_review_details(review)
        review_details.append((name, country, rating, review_text))

    # Prepare the product information for DataFrame
    # for product_title, final_price in similar_products:
    review_data = []
    for reviewer in review_details:
        name, country, rating, review_text = reviewer
        review_data.append({
            "Reviewer Name": name,
            "Location": country,
            "Rating": rating,
            "Review Text": review_text
        })

    merged_list = []
    
    merged_list.extend(product_info)
    merged_list.extend(similar_products)
    merged_list.extend(review_data)
            
    df = pd.DataFrame.from_dict(merged_list)
    df.to_csv('amz_research_sheet.csv', index=False)
    print("File saved succesfully")

    # Create a DataFrame from the collected data
    pass

if __name__ == "__main__":
    extract_info_to_dataframe(url, proxies)

    
    
    