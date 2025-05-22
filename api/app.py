from flask import Flask,jsonify,request,abort

from dotenv import load_dotenv

from import_script import populate_db, get_all_recipes

load_dotenv()
from config import Config
from models import db
from models.association import recipe_category
from models.category import Category
from models.ingredient import Ingredient
from models.recipe import Recipe
from sqlalchemy.orm import joinedload




app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


@app.route('/')
def helloWorld():
    return "Welcome to my Snack App"

@app.route('/api/recipes', methods=['GET'])
# def get_recipes():
#     # return jsonify(recipes)
#     recipes = []
#     for recipe in db.session.query(Recipe).all():
#
#         recipes.append(recipe.as_dict())
#     return jsonify(recipes)
def get_recipes():
    recipes = []

    # Use joinedload to preload ingredients and categories
    all_recipes = db.session.query(Recipe).options(
        joinedload(Recipe.ingredients),
        joinedload(Recipe.categories)
    ).all()

    for recipe in all_recipes:
        recipe_data = recipe.as_dict()


        # Add ingredients manually
        recipe_data['ingredients'] = [
            {
                'name': ing.name,
                'unit': ing.unit,
                'quantity': str(ing.quantity)
            } for ing in recipe.ingredients
        ]

        # Add categories manually
        recipe_data['categories'] = [cat.name for cat in recipe.categories]

        recipes.append(recipe_data)

    return jsonify(recipes)


@app.route('/api/recipes/<int:recipe_id>', methods=['GET'] )
def get_recipe(recipe_id):
    recipe = db.session.query(Recipe).options(
        joinedload(Recipe.ingredients),
        joinedload(Recipe.categories)
    ).filter_by(id=recipe_id).first()

    if recipe is None:
        return jsonify({'error': 'recipe not found'})

    recipe_data = recipe.as_dict()

    recipe_data['ingredients'] = [
        {
            'name': ing.name,
            'unit': ing.unit,
            'quantity': str(ing.quantity)
        } for ing in recipe.ingredients
    ]

    recipe_data['categories'] = [cat.name for cat in recipe.categories]

    return jsonify(recipe_data)


@app.route('/api/recipes', methods=['POST'])
def create_recipe():
    data = request.get_json()

    new_recipe = Recipe(
        name=data['name'],
        pictures=data['pictures'],
        instructions=data['instructions'],
        duration=data['duration'],

    )
    db.session.add(new_recipe)
    db.session.flush()
    for ing in data['ingredients']:
        new_ingredient = Ingredient(
            name=ing['name'],
            unit=ing['unit'],
            quantity=ing['quantity'],
            recipe_id=new_recipe.id,

        )
        db.session.add(new_ingredient)

    for cat in data['categories']:
        category = db.session.query(Category).filter_by(name=cat).first()
        if category is None:
            return jsonify({'error': f'category {cat["name"]} not found'}), 400
        new_recipe.categories.append(category)

    db.session.commit()

    return jsonify(new_recipe), 201

@app.route('/api/recipes/<int:recipe_id>', methods=['PUT'])
def update_recipe(recipe_id):
    data = request.get_json()

    recipe = db.session.query(Recipe).filter_by(id=recipe_id).first()
    recipe = recipe.as_dict()
    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404

    recipe.name = data['name']
    recipe.instructions = data['instructions']
    recipe.duration = data['duration']

    pictures = data['pictures']
    if data['instructions']:
        Ingredient.query.filter_by(recipe_id=recipe_id).delete()

        for ing in data['ingredients']:
            new_ingredient = Ingredient(
                name=ing['name'],
                unit=ing['unit'],
                quantity=ing['quantity'],
                recipe_id=recipe.id
            )

            db.session.add(new_ingredient)

    if data['categories']:
        recipe.categories.clear()
        for cat_name in data['categories']:
            category = db.session.query(Category).filter_by(name=cat_name).first()
            if not category:
                return jsonify({'error': f'category not found'}), 400
            recipe.categories.append(category)

    db.session.commit()
    return jsonify(recipe),201

    # for recipe in recipes:
    #     if recipe['id'] == recipe_id:
    #         recipe['recipe name'] = name if (name:=request.json.get('recipe name')) else recipe['recipe name']
    #         recipe['duration'] = duration if (duration:=request.json.get('duration')) else recipe['duration']
    #         recipe['pictures'] = pictures if (pictures:=request.json.get('pictures')) else recipe['pictures']
    #         recipe['instructions'] = instructions if (instructions:=request.json.get('instructions')) else recipe['instructions']
    #         recipe['categories'] = categories if (categories:=request.json.get('categories')) else recipe['categories']
    #         recipe['ingredients'] = ingredients if (ingredients:=request.json.get('ingredients')) else recipe['ingredients']
    #         return jsonify(recipe)
    # return jsonify("There is no recipe with id {}".format(recipe_id)),404

@app.route('/api/recipes/<int:recipe_id>', methods=['DELETE'])
def delete_recipe(recipe_id):
    recipe = db.session.query(Recipe).filter_by(id=recipe_id).first()
    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404
    Ingredient.query.filter_by(recipe_id=recipe.id).delete()
    recipe.categories.clear()
    db.session.delete(recipe)
    db.session.commit()
    return jsonify({"message": f"Recipe ID {recipe_id} deleted successfully."}), 204


if __name__ == '__main__':
    # with app.app_context():
    #     db.drop_all()
    #     db.create_all()

    # Use the following line if you want to populate the database with sample data
    # populate_db(get_all_recipes(), app, db)

    app.run(host="0.0.0.0")