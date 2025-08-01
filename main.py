import mysql.connector
from mysql.connector import Error
import datetime
import customtkinter as ctk

# --- Database Configuration ---
HOST = "localhost"
DATABASE = "manuel projekt v4"
USER = "BargainBot"
PASSWORD = "%BargainBot"


# -------------------------------

def connect_to_database():
    """
    Establishes a connection to the database and returns the
    connection object
    """

    try:
        connection = mysql.connector.connect(
            host=HOST,
            database=DATABASE,
            user=USER,
            password=PASSWORD
        )
        # print(f"connected.")
        return connection

    except Error:
        return None


def get_productname(product_id):
    """
    This function returns the product name for a given product ID.
    """
    connection = connect_to_database()
    cursor = connection.cursor()

    query = "SELECT productname FROM product WHERE product_id = %s"
    cursor.execute(query, (product_id,))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result[0]  # Product name


def get_all_product_ids():
    """
    This function returns all product IDs from the database.
    """
    connection = connect_to_database()
    cursor = connection.cursor()

    query = "SELECT product_id FROM product"
    cursor.execute(query)
    results = cursor.fetchall()

    cursor.close()
    connection.close()

    all_product_ids = [item[0] for item in results]  # List of product IDs
    return all_product_ids


def get_user_prename(user_id):
    """
    This function returns the user's first name for a given user ID.
    """
    connection = connect_to_database()
    cursor = connection.cursor()

    query = "SELECT user.prename FROM user WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result[0]  # User's first name


def frequency_based_analysis(look_back_weeks=None):  # Baseline
    """
    This function performs a frequency analysis to determine the most
    frequently purchased products.
    """

    shoppinglist_id_per_user, user_id = get_shoppinglist_per_user()
    all_products_with_timestamp_per_user = get_all_products_with_timestamp_per_user(shoppinglist_id_per_user)
    # print(get_all_products_with_timestamp_per_user)
    product_quantities = {}
    current_time = datetime.datetime.now()  # Current time as reference point

    user_prename = get_user_prename(user_id)

    for product_id, amount, shoppinglist_id, timestamp in all_products_with_timestamp_per_user:

        # If a look_back_weeks is defined, data is filtered
        if look_back_weeks is not None:
            time_difference = current_time - timestamp

            if time_difference.days > (look_back_weeks * 7):
                continue  # Skip data outside the look-back window

        if product_id in product_quantities:
            product_quantities[product_id] += amount

        else:
            product_quantities[product_id] = amount

    # Sort products by their total amount in descending order
    sorted_products_list = sorted(product_quantities.items(), key=lambda item: item[1], reverse=True)  # descending

    # Convert sorted list of tuples back to a dictionary
    sorted_products_dict = dict(sorted_products_list)  # {product_id: total_amount, ...}
    # print(sorted_products_dict)

    print(79 * "-")
    print(f"Top products of {user_prename} in the last {look_back_weeks} weeks:")
    print("Quantity ¦ Product name")

    for product_id, amount in sorted_products_dict.items():
        product_name = get_productname(product_id)
        print(f"{amount} ¦ {product_name}")
        # sorted_products_dict[product_name] = sorted_products_dict.pop(id)
    return sorted_products_dict


def get_all_products_with_timestamp_per_user(shoppinglist_id_per_user):
    """
    This function extracts for a shoppinglist_id all products with quantity and timestamp
    """
    connection = connect_to_database()
    cursor = connection.cursor()

    query = """ 
            SELECT product_shoppinglist.productproduct_id, product_shoppinglist.amount, 
            product_shoppinglist.Shoppinglistshoppinglist_id, shoppinglist.timestamp FROM product_shoppinglist JOIN 
            product ON product_shoppinglist.productproduct_id = product.product_id JOIN 
            shoppinglist ON shoppinglist.shoppinglist_id = product_shoppinglist.shoppinglistshoppinglist_id  
            WHERE product_shoppinglist.shoppinglistshoppinglist_id = %s;
        """

    products_with_timestamp_per_user = []

    for id in shoppinglist_id_per_user:
        cursor.execute(query, (id,))
        results = cursor.fetchall()

        for r in results:
            products_with_timestamp_per_user.append(r)

    # print(products_with_timestamp_per_user)

    cursor.close()
    connection.close()
    return products_with_timestamp_per_user


def get_shoppinglist_per_user(user_id=None):
    """
    This function returns all shoppinglist_ids of a user
    """
    if user_id is None:
        user_id = int(input("User ID: "))

    connection = connect_to_database()
    cursor = connection.cursor()
    query = """
            SELECT shoppinglist.shoppinglist_id, shoppinglist.timestamp
            FROM shoppinglist
            WHERE useruser_id = %s;
            """
    cursor.execute(query, (user_id,))
    results = cursor.fetchall()
    # print(results)

    cursor.close()
    connection.close()

    shoppinglist_id_per_user = [item[0] for item in results]
    # print(f"shoppinglist_id_per_user: {shoppinglist_id_per_user}")
    return shoppinglist_id_per_user, user_id  # example: [1, 2, 3, 4] shoppinglist ids of the user


def get_shoppinglist(shoppinglist_id):
    connection = connect_to_database()
    cursor = connection.cursor()

    query = """
            SELECT product.productname, product_shoppinglist.amount
            FROM product_shoppinglist JOIN product ON product_shoppinglist.Productproduct_id = product.product_id 
            WHERE product_shoppinglist.Shoppinglistshoppinglist_id = %s;
            """

    cursor.execute(query, (shoppinglist_id,))
    results = cursor.fetchall()

    shoppinglist = [(amount, product_name) for product_name, amount in results]
    # print(f"shoppinglist{shoppinglist}")

    cursor.close()
    connection.close()
    return shoppinglist


def get_price(shoppinglist):
    connection = connect_to_database()
    cursor = connection.cursor()

    shoppinglist_shop_price = []

    for amount, product_name in shoppinglist:
        query = """
        SELECT s.name, sp.price
        FROM product p
        JOIN store_product sp ON p.product_id = sp.productproduct_id
        JOIN store s ON sp.storestore_id = s.store_id
        WHERE p.productname = %s;
        """
        cursor.execute(query, (product_name,))
        results = cursor.fetchall()

        for store_name, price in results: shoppinglist_shop_price.append((amount, product_name, store_name, price))

    # print(f"shoppinglist_shop_price{shoppinglist_shop_price}")

    cursor.close()
    connection.close()

    return shoppinglist_shop_price


def get_cheapest_1_store(shoppinglist_shop_price):
    store_totals = {}

    for amount, product_name, store_name, unit_price in shoppinglist_shop_price:
        total_price = amount * unit_price

        if store_name not in store_totals:
            store_totals[store_name] = 0.0

        store_totals[store_name] += total_price

    #for store, total in store_totals.items():
        #print(f"{store}: {total:.2f} CHF")
    product_with_assigned_store = []  # [(amount, product_name, store_name, price), ...]

    cheapest_store = min(store_totals, key=store_totals.get)
    # print(f"Cheapest store: {cheapest_store} with {store_totals[cheapest_store]:.2f} CHF")

    for amount, product_name, store_name, unit_price in shoppinglist_shop_price:

        if store_name == cheapest_store:
            enhanced_tuple = (amount, product_name, store_name, unit_price)
            product_with_assigned_store.append(enhanced_tuple)

    # print(f"Product with assigned store: {product_with_assigned_store}")
    return store_totals, cheapest_store, product_with_assigned_store  # [(1, 'Apples', 'Aldi', 1.58),..]


def get_cheapest_2_store(shoppinglist_shop_price):
    """
    From a product perspective, there would be many possibilities and the computational effort would be enormous.
    From a store perspective, the effort is much lower. We look for all possible store pairs and add for each
    of these pairs the product at the store that is cheapest of the two. Then we get lists that
    show how expensive it would be if you chose store x and store y for shopping. From this, we select
    the cheapest option. This idea could be extended to more stores as the count is nCr n,
    so with 6 stores in the database, it would be at most 20 lists.
    """

    product_details = {}  # {'Product name': {'Store name': (Price, Original tuple)}}
    all_shops = set()  # To collect all store names

    for item in shoppinglist_shop_price:
        _, product_name, shop_name, price = item  # without ID
        all_shops.add(shop_name)  # Add store to the set

        if product_name not in product_details:
            product_details[product_name] = {}

        # Store the price and the entire original tuple
        product_details[product_name][shop_name] = (price, item)

    shops_list = list(all_shops)

    min_overall_price = 1000000

    # All possible store pairs
    num_shops = len(shops_list)

    for i in range(num_shops):

        for j in range(i + 1, num_shops):  # no duplicate pairs (Shop A, Shop B) same as (Shop B, Shop A)

            shop1 = shops_list[i]
            shop2 = shops_list[j]

            current_pair_total_price = 0.0
            # Product assignments for the current pair
            current_pair_product_choices = []

            # Price for this store pair
            # For each product, choose the cheaper price within the two stores of this pair
            for product_name, shops_offering_product in product_details.items():
                price_in_shop1 = shops_offering_product.get(shop1)
                price_in_shop2 = shops_offering_product.get(shop2)

                # Choose the cheaper store for this product within the current pair
                if price_in_shop1 and price_in_shop2:

                    if price_in_shop1[0] <= price_in_shop2[0]:
                        current_pair_total_price += price_in_shop1[0]
                        current_pair_product_choices.append(price_in_shop1[1])  # Adds the original tuple

                    else:
                        current_pair_total_price += price_in_shop2[0]
                        current_pair_product_choices.append(price_in_shop2[1])

            # Find best store pair
            # If the current total price is less than the previous best, update the values
            if current_pair_total_price < min_overall_price:
                min_overall_price = current_pair_total_price
                product_with_assigned_store = current_pair_product_choices

        return product_with_assigned_store


def get_shopping_list_gui(product_list):
    """
    Opens a GUI window with customTkinter for entering the shopping list
    """

    shoppinglist = []

    # Main window
    app = ctk.CTk()
    app.title("Create your shopping list here")
    app.geometry("400x800")

    # Title
    title_label = ctk.CTkLabel(master=app, text="Select products and enter quantity", font=("Verdana", 14))
    title_label.pack(padx=20, pady=(20, 10))

    # Window for products
    scrollable_frame = ctk.CTkScrollableFrame(master=app, label_text="Available Products")
    scrollable_frame.pack(padx=20, pady=10, fill="both", expand=True)

    checkbox_vars = {}
    entry_widgets = {}

    # Products
    for product in product_list:
        row_frame = ctk.CTkFrame(master=scrollable_frame)
        row_frame.pack(fill="x", padx=10, pady=5)

        # Checkbox
        checkbox_vars[product] = ctk.StringVar(value="off")
        checkbox = ctk.CTkCheckBox(
            master=row_frame,
            text=product,
            variable=checkbox_vars[product],
            onvalue="on",
            offvalue="off"
        )
        checkbox.pack(side="left", padx=5)

        # Quantity entry
        entry = ctk.CTkEntry(master=row_frame, width=50, placeholder_text="0")
        entry.pack(side="right", padx=5)
        entry_widgets[product] = entry  # Store the entry widget for later access

    # Confirm button
    def on_confirm_click():
        """
        This function is executed when the button is clicked.
        """

        # Collect inputs
        for product, var in checkbox_vars.items():
            if var.get() == "on":
                # Assign quantity
                quantity_entry = entry_widgets[product]
                quantity_str = quantity_entry.get()
                # Convert quantity to number
                quantity = int(quantity_str) if quantity_str else 1

                if quantity > 0:
                    shoppinglist.append((quantity, product))

        # Close the window
        app.destroy()

    confirm_button = ctk.CTkButton(master=app, text="Confirm and save ✅", command=on_confirm_click)
    confirm_button.pack(padx=20, pady=20)

    # Start the GUI and wait
    app.mainloop()

    return shoppinglist


def create_shoppinglist_per_store(product_with_assigned_store):
    """
    Groups products by store and returns a dictionary.
    """

    grouped_data = {}
    # print(f"product_with_assigned_store: {product_with_assigned_store}")
    for amount, product_name, store_name, unit_price in product_with_assigned_store:

        if store_name not in grouped_data:
            grouped_data[store_name] = []

        grouped_data[store_name].append((amount, product_name, unit_price))

    total_price = 0.0

    for store, products in grouped_data.items():

        total_price_per_shop = sum(amount * unit_price for amount, product_name, unit_price in products)
        print(f"\n  {store} \n")

        for product_info in products:
            amount, product_name, unit_price = product_info
            print(f"  {amount}x {product_name} at {unit_price:.2f} CHF")

        print(50 * "-" + f"\nTotal price at {store}: {total_price_per_shop:.2f} CHF\n" + 50 * "=")
        total_price += total_price_per_shop

    print(f"\nTotal costs at all stores: {total_price:.2f} CHF\n" + 50 * "=")

    return grouped_data


def main():
    """
    Main function to run the script.
    """

    print("------------------------- Welcome to BargainBot! -------------------------")
    print("This program helps you find the cheapest stores for your products.\n")

    all_product_ids = get_all_product_ids()
    available_products = [get_productname(product_id) for product_id in all_product_ids]

    while True:
        print("\n------------Main Menu------------")
        search_or_enter_shoppinglist = input(
            "\n1 : Create new shopping list \n2 : Load existing shopping list \nX : Exit program "
            "\n Input:  ").strip().upper()

        if search_or_enter_shoppinglist == "2":
            shoppinglist_id = int(input("\nEnter the ID of the shopping list you want to load: "))
            shoppinglist = get_shoppinglist(shoppinglist_id)
            # print(f"Loaded shopping list: {shoppinglist}")

        elif search_or_enter_shoppinglist == "1":
            print("\nYou can now create your shopping list in the GUI.")
            shoppinglist = get_shopping_list_gui(available_products)

        elif search_or_enter_shoppinglist == "X":
            print("\nProgram will exit.")
            print("\n" + 79 * "-")
            break

        else:
            print("\nInvalid input. Please choose an option from the main menu:")
            continue

        while True:
            number_of_stores = int(input("\nNumber of stores you want to shop in (1 or 2): "))

            if number_of_stores not in [1, 2]:
                print("\nInvalid input. Please enter 1 or 2.")
                continue

            else:
                break

        print("\n" + 79 * "-")
        print("\nBargainBot recommends you shop in the following stores:")

        # print(f"shoppinglist = {shoppinglist}")

        shoppinglist_shop_price = get_price(shoppinglist)

        if number_of_stores == 1:
            store_totals, cheapest_store, product_with_assigned_store = get_cheapest_1_store(
                shoppinglist_shop_price)  # Simple sum calculation

        elif number_of_stores > 1:
            product_with_assigned_store = get_cheapest_2_store(
                shoppinglist_shop_price)  # Pairwise calculation per product, then selection of overall best pairs

        shoppinglist_per_store = create_shoppinglist_per_store(product_with_assigned_store)

        print("\n" + 79 * "-")


if __name__ == "__main__":
    # shoppinglist_id = int(input("Shopping-List ID: "))

    # shoppinglist = get_shoppinglist(shoppinglist_id)
    # shoppinglist_shop_price = get_price(shoppinglist)
    # get_cheapest_store(shoppinglist_shop_price)
    # shoppinglist_id_per_user = get_shoppinglist_per_user()
    # products_with_timestamp_per_user = get_all_products_with_timestamp_per_user(shoppinglist_id_per_user)
    # weeks=[1, 2, 3, 4, 10, 20, 30, 40, 50] # Look-back weeks
    # for week in weeks:
    #    sorted_products_dict = frequency_based_analysis(week)
    main()
