#!/usr/bin/env python3

import requests
import json
import html

get_prodid_url = "https://www.ica.se/api/search/v2/quicksearch?query="
product = "Kykling och curry"
response = requests.get(f"{get_prodid_url}{product}")
product_response = response.json()
for x in range(min(3, len(product_response['RecipeResult']['Documents']))):
    product_documents = product_response['RecipeResult']['Documents'][x]
    recipe_id = product_documents['_id']
    recipe_title = product_documents['Title'].strip()
    recipe_cook_time = product_documents['CookingTimeValue']
    recipe_rating = product_documents['Rating']['AverageRating']
    #recipe_image = product_documents['Images']
    #print(recipe_image[0]['AbsoluteUrl'])
    print(f"{x+1}. {recipe_title} med ID {recipe_id} tar {recipe_cook_time} minuter att laga och har betyget {recipe_rating} stjärnor")

recipe_input = int(input("Välj recept: "))-1
product_documents = product_response['RecipeResult']['Documents'][recipe_input]
recipe_id = product_documents['_id']

url = f"https://handla.api.ica.se//api/recipes/recipe/{recipe_id}"
response = requests.get(url)
json_data = response.json()
recipe_title = json_data['Title']
avalible_portions = json_data['ExtraPortions']
cooking_steps = json_data['CookingStepsWithTimers']
cooking_time = json_data['CookingTime']
recipe_ingredients = json_data['IngredientGroups']
# How to render åäö: html.unescape
#for k in recipe_ingredients[0]['Ingredients']:
    #print(k['Text'])


#print(json.dumps(json_data['IngredientGroups'], indent=4, sort_keys=True))
#print(cooking_steps)

# AVALIBLE PORTIONS
#for x in avalible_portions:
    #print(x['Portions'])


