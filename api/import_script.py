import csv
import json
import re

def getAllRecipes():
    ingredient_regex = re.compile(r'^(?P<quantity>\d+)(?P<unit>[a-zA-Z]*) (?P<name>.+)$')
    with open('../recipes.csv', "r") as csvfile, open("../recipes.json", "w") as jsonfile:
        all_recipes = []
        dict_reader = csv.DictReader(csvfile)
        for row in dict_reader:
            row["Categories"] = row["Categories"].split(",")
            row["Ingredients"] = row["Ingredients"].split(",")
            ingredints = []
            for ingr in row["Ingredients"]:
                ingredient_matches = ingredient_regex.match(ingr)
                try:
                    float_quantity = float(ingredient_matches["quantity"])
                except ValueError:
                    float_quantity = None
                    error_message = ValueError
                    print(error_message)

                ingredints.append({
                    "quantity": float_quantity,
                    "unit": ingredient_matches["unit"],
                    "name": ingredient_matches["name"],
                })

            row["Ingredients"] = ingredints
            all_recipes.append(row)
            json.dump(all_recipes, jsonfile)
            return all_recipes


if __name__ == '__main__':
    recipes = getAllRecipes()
