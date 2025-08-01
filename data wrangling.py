import spacy
import tqdm
import warnings

# Suppress spacy UserWarnings about W008
warnings.filterwarnings("ignore", category=UserWarning, message=".*W008.*")

"""
Pipeline that validates simulated data from the internet, processes it, 
and enriches it with categories via NLP.
Then it generates SQL INSERT statements.
"""

def database():
    """
    A simulated data source, e.g. preprocessed output from web scraping
    """

    new_products = [
        ("Apples", 1, "kg"),
        ("Bananas", 1, "kg"),
        ("Potatoes", 1, "kg"),
        ("Tomatoes", 1, "kg"),
        ("Butter", 25000, "g"),
        ("Eggs", 6, "pcs"),
        ("Hard cheese", 250, "g"),
        ("Natural yogurt", 200, "g"),
        ("Whole milk pasteurized", 1, "l"),
        ("Oat flakes", 1, "kg"),
        ("Honey", 500, "g"),
        ("Rye bread", 500, "g"),
        ("Long grain rice", 1, "kg"),
        ("Spaghetti", 500, "g"),
        ("White flour", 1, "kg"),
        ("Granulated sugar", 1, "kg"),
        ("Mayonnaise tube", 265, "g"),
        ("Sunflower oil", 1, "l"),
        ("Table salt", 1, "kg"),
        ("Bratwurst", 300, "g"),
        ("Smoked trout fillet", 150, "g"),
        ("Sliced chicken", 300, "g"),
        ("Butter biscuits Petit Beurre", 200, "g"),
        ("Lasagna bolognese", 500, "g"),
        ("Milk chocolate", 100, "g"),
        ("Pizza Margherita", 400, "g"),
        ("Paprika potato chips bag", 300, "g"),
        ("Coffee capsules lungo", 10, "pcs"),
        ("Carbonated mineral water", 1, "l"),
        ("Orange juice", 1, "l"),
        ("All-purpose cleaner liquid", 1, "l"),
        ("Dishwasher powder", 1, "kg"),
        ("Household paper", 2, "pcs"),
        ("Napkins", 15, "pcs"),
        ("Laundry detergent (color wash), liquid", 1, "l"),
        ("Toilet paper", 6, "pcs"),
        ("Deodorant spray", 150, "ml"),
        ("Shower shampoo", 300, "ml"),
        ("Liquid soap", 500, "ml"),
        ("Toothpaste", 125, "ml")
    ]
    return new_products


def mass_to_gram(value, unit):
    """
    Converts different mass units to grams.
    """

    unit = unit.lower()

    if unit in ['g', 'gram', 'grams']:
        new_value = value
        new_unit = 'g'

    elif unit in ['mg', 'milligram', 'milligrams']:
        new_value = value / 1000
        new_unit = 'g'

    elif unit in ['kg', 'kilogram', 'kilograms']:
        new_value = value * 1000
        new_unit = 'g'

    elif unit in ['t', 'tonne', 'ton', 'tons']:
        new_value = value * 1_000_000
        new_unit = 'g'

    elif unit in ['lb', 'lbs', 'pound', 'pounds']:
        new_value = value * 453.592
        new_unit = 'g'

    elif unit in ['oz', 'ounce', 'ounces']:
        new_value = value * 28.3495
        new_unit = 'g'

    elif unit in ['st', 'stone', 'stones']:
        new_value = value * 6350.29
        new_unit = 'g'

    else:
        new_value = None
        new_unit = None
        print(f"Error: Unknown unit '{unit}'.")

    return new_value, new_unit


def liquid_to_ml(value, unit):
    """
    Converts different liquid units to milliliters.
    """

    unit = unit.lower()

    if unit in ['ml', 'milliliter', 'millilitre']:
        new_value = value
        new_unit = 'ml'

    elif unit in ['cl', 'centiliter', 'centilitre']:
        new_value = value * 10
        new_unit = 'ml'

    elif unit in ['dl', 'deciliter', 'decilitre']:
        new_value = value * 100
        new_unit = 'ml'

    elif unit in ['l', 'liter', 'litre']:
        new_value = value * 1000
        new_unit = 'ml'

    elif unit in ['hl', 'hectoliter', 'hectolitre']:
        new_value = value * 100000
        new_unit = 'ml'

    elif unit in ['gal', 'gallon', 'gallons']:
        new_value = value * 3785.41
        new_unit = 'ml'

    elif unit in ['qt', 'quart', 'quarts']:
        new_value = value * 946.353
        new_unit = 'ml'

    elif unit in ['pt', 'pint', 'pints']:
        new_value = value * 473.176
        new_unit = 'ml'

    elif unit in ['cup', 'cups', 'tasse']:
        new_value = value * 240
        new_unit = 'ml'

    elif unit in ['floz', 'fluid ounce', 'fluid ounces']:
        new_value = value * 29.5735
        new_unit = 'ml'

    else:
        new_value = None
        new_unit = None
        print(f"Error: Unknown unit '{unit}'.")

    return new_value, new_unit


def validate_products(new_products):
    """
    This function organizes the validation of products.
    """

    validated_products = []

    for tupel in new_products:
        unit = tupel[2]
        if unit.lower() in ['g', 'gram', 'grams',
                            'mg', 'milligram', 'milligrams',
                            'kg', 'kilogram', 'kilograms',
                            't', 'tonne', 'ton', 'tons',
                            'lb', 'lbs', 'pound', 'pounds',
                            'oz', 'ounce', 'ounces',
                            'st', 'stone', 'stones']:

            value, unit = mass_to_gram(tupel[1], tupel[2])
            validated_products.append((tupel[0], value, unit))

        elif unit.lower() in ['ml', 'milliliter', 'millilitre',
                              'cl', 'centiliter', 'centilitre',
                              'dl', 'deciliter', 'decilitre',
                              'l', 'liter', 'litre',
                              'hl', 'hectoliter', 'hectolitre',
                              'gal', 'gallon', 'gallons',
                              'qt', 'quart', 'quarts',
                              'pt', 'pint', 'pints',
                              'cup', 'cups', 'tasse',
                              'floz', 'fluid ounce', 'fluid ounces']:

            value, unit = liquid_to_ml(tupel[1], tupel[2])
            validated_products.append((tupel[0], value, unit))

        elif unit.lower() in ['stück', 'stückchen', 'stücklein', 'stk', 'st', 'pcs', 'piece', 'pieces']:
            value, unit = tupel[1], 'pcs'
            validated_products.append((tupel[0], value, unit))

    return validated_products


def spacy_evaluation(productname, nlp):
    """
    This function uses spacy to determine the product category.
    """

    product_data = [
        ("Oranges", 1),
        ("Carrots", 1),
        ("Cucumbers", 1),
        ("Lettuce", 1),
        ("Onions", 1),
        ("Garlic", 1),
        ("Lemons", 1),
        ("Pears", 1),
        ("Grapes", 1),
        ("Broccoli", 1),
        ("Apples", 1),
        ("Bananas", 1),
        ("Potatoes", 1),
        ("Tomatoes", 1),
        ("Quark", 2),
        ("Yogurt", 2),
        ("Cream", 2),
        ("Milk", 2),
        ("Cream cheese", 2),
        ("Mozzarella", 2),
        ("Cottage cheese", 2),
        ("Feta", 2),
        ("Pudding", 2),
        ("Whipped cream", 2),
        ("Butter", 2),
        ("Eggs", 2),
        ("Hard cheese", 2),
        ("Natural yogurt", 2),
        ("Whole milk", 2),
        ("Toast bread", 3),
        ("Jam", 3),
        ("Peanut butter", 3),
        ("Muesli", 3),
        ("Cornflakes", 3),
        ("Rusks", 3),
        ("Crispbread", 3),
        ("Coffee", 3),
        ("Tea bags", 3),
        ("Nutella", 3),
        ("Oat flakes", 3),
        ("Honey", 3),
        ("Rye bread", 3),
        ("Penne", 4),
        ("Fusilli", 4),
        ("Basmati rice", 4),
        ("Polenta", 4),
        ("Spelt flour", 4),
        ("Durum wheat semolina", 4),
        ("Couscous", 4),
        ("Pasta", 4),
        ("Rice cakes", 4),
        ("Pizza flour", 4),
        ("Long grain rice", 4),
        ("Spaghetti", 4),
        ("White flour", 4),
        ("Raw sugar", 5),
        ("Powdered sugar", 5),
        ("Sea salt", 5),
        ("Pepper", 5),
        ("Vinegar", 5),
        ("Olive oil", 5),
        ("Sunflower oil", 5),
        ("Baking powder", 5),
        ("Vanilla sugar", 5),
        ("Ketchup", 5),
        ("Granulated sugar", 5),
        ("Mayonnaise", 5),
        ("Sunflower oil", 5),
        ("Table salt", 5),
        ("Ground beef", 6),
        ("Chicken breast", 6),
        ("Salmon fillet", 6),
        ("Tuna", 6),
        ("Salami", 6),
        ("Ham", 6),
        ("Bacon", 6),
        ("Shrimps", 6),
        ("Sausages", 6),
        ("Small sausages", 6),
        ("Fish sticks", 6),
        ("Bratwurst", 6),
        ("Trout fillet", 6),
        ("Sliced chicken", 6),
        ("Frozen pizza", 7),
        ("Soup", 7),
        ("Gummy bears", 7),
        ("Cookies", 7),
        ("Chocolate bars", 7),
        ("Nuts", 7),
        ("Popcorn", 7),
        ("Muesli bars", 7),
        ("Ready salad", 7),
        ("Butter cookies", 7),
        ("Lasagna bolognese", 7),
        ("Milk chocolate", 7),
        ("Pizza", 7),
        ("Potato chips", 7),
        ("Apple juice", 8),
        ("Cola", 8),
        ("Iced tea", 8),
        ("Beer", 8),
        ("Wine", 8),
        ("Espresso beans", 8),
        ("Tea", 8),
        ("Vegetable juice", 8),
        ("Energy drink", 8),
        ("Smoothie", 8),
        ("Coffee capsules", 8),
        ("Mineral water", 8),
        ("Orange juice", 8),
        ("Dish soap", 9),
        ("Laundry detergent", 9),
        ("Toilet paper", 9),
        ("Trash bags", 9),
        ("Aluminum foil", 9),
        ("Cling film", 9),
        ("Kitchen roll", 9),
        ("Batteries", 9),
        ("Light bulbs", 9),
        ("Cleaning wipes", 9),
        ("All-purpose cleaner", 9),
        ("Dishwasher detergent", 9),
        ("Household paper", 9),
        ("Napkins", 9),
        ("Laundry detergent", 9),
        ("Toilet paper", 9),
        ("Shampoo", 10),
        ("Shower gel", 10),
        ("Hand soap", 10),
        ("Moisturizer", 10),
        ("Toothbrushes", 10),
        ("Mouthwash", 10),
        ("Shaving foam", 10),
        ("Body lotion", 10),
        ("Hairspray", 10),
        ("Tampons", 10),
        ("Deodorant spray", 10),
        ("Shower shampoo", 10),
        ("Liquid soap", 10),
        ("Toothpaste", 10)
    ]

    doc = nlp(productname)

    max_similarity = -1
    predicted_category = None

    for product_entry, category_number in product_data:
        similarity = doc.similarity(nlp(product_entry))

        if similarity > max_similarity:
            max_similarity = similarity
            predicted_category = category_number

    # print(f"Product '{productname}' was assigned to category {predicted_category}.")
    return predicted_category


def get_categoryname(validated_products, nlp):
    """
    This function organizes the spacy application
    """

    validated_products_with_category_id = []
    for tupel in tqdm.tqdm(validated_products):
        productname = tupel[0]
        productcategoryproductcategory_id = spacy_evaluation(productname, nlp)
        validated_products_with_category_id.append((tupel[0], tupel[1], tupel[2], productcategoryproductcategory_id))

    # print(f"Validated products with category ID: {validated_products_with_category_id}")
    return validated_products_with_category_id


def product_insert_statement(validated_products_with_category_id):
    """
    This function takes a list of products and returns the SQL insert statements.
    """

    insert_statements = []

    for product in validated_products_with_category_id:
        productname, quantity, unit, productcategoryproductcategory_id = product
        statement = (f"INSERT INTO products (productcategoryproductcategory_id, productname, quantity, unit) VALUES "
                     f"('{productcategoryproductcategory_id}','{productname}', {quantity}, '{unit}');")
        insert_statements.append(statement)
        print(statement)

    return insert_statements


def main():
    """
    This function organizes the pipeline
    """

    new_products = database()
    print("--------Data validation")
    validated_products = validate_products(new_products)
    print("Converted to lowercase, units to 'g', 'ml', and 'pcs', and calculated quantity")
    nlp = spacy.load("de_core_news_md")
    print("--------Product categorization")
    productcategoryproductcategory_id = get_categoryname(validated_products, nlp)
    print("--------Generating insert statements")
    product_insert_statement(productcategoryproductcategory_id)
    print("--------Done!")
    # These INSERT statements can then be inserted into a database (preferably via the connection, see main.py)


main()
