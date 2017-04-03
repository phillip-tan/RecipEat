import requests
import json
from pprint import pprint

app_id = '1032528d' #WILL eventually EXTRACT OUT
app_key = '86f7d4445c3089d85c8cc6a398de3827' # WILL EVENTUALY EXTRACT OUT 
recipes_url = 'http://api.yummly.com/v1/api/recipes?'

def build_recipe_list_request(ingredients): #allowedIngredient is list of ingredients from Machine Learning
    api_url = 'http://api.yummly.com/v1/api/recipes?' + \
    	'_app_id=' + app_id + '&' + '_app_key=' + app_key + \
    	'&requirePictures=True' + '&allowedCuisine[]=cuisine^cuisine-french'

    for ingredient in ingredients:
        api_url += '&allowedIngredient[]=' + str(ingredient)

    return api_url


def get_yummly_json(api_url): #should return JSONP not JSON
    yummly_response = requests.get(api_url)
    json_objects = yummly_response.json()
    return json_objects


def build_recipe_steps_request(recipe_id):
	api_url = "http://api.yummly.com/v1/api/recipe/" + recipe_id + \
		"?_app_id=1032528d&_app_key=86f7d4445c3089d85c8cc6a398de3827"
	return api_url


#ENTRY POINT
#input: List of ingredients:
def get_recipes(ingredients):
	recipe_ids = get_yummly_json(build_recipe_list_request(ingredients))
	# print recipe_ids
	if 'matches' not in recipe_ids:
		return None

	list_of_recipes = recipe_ids['matches']
	recipe_information = [] #tuples of (name, url_to_src_recipe, image_url)
	for each in list_of_recipes:
		recipe_val = get_yummly_json(build_recipe_steps_request(each['id']))
		name = recipe_val['name'].encode('utf-8')
		url_to_src = recipe_val['source']['sourceRecipeUrl'].encode('utf-8')
		img_url = recipe_val['images'][0]['hostedLargeUrl'].encode('utf-8')
		recipe_information.append((name, url_to_src, img_url))
	return recipe_information


# yummly_json = get_yummly_json(build_recipe_list_request(ingredients))
# print yummly_json
# print('API Call: ' + build_recipe_list_request(ingredients))
# print('-----------------------------------------------------------------------')


