# Import necessary libraries
import csv
import random
import datetime
import math
import os
import sqlite3 # NEW: To interact with SQLite database
import pandas as pd # NEW: To use pandas for easier SQL loading

# --- Configuration Constants ---
NUMBER_OF_INFLUENCERS = 100
NUMBER_OF_POSTS = 500
START_DATE = datetime.date(2025, 1, 1)
END_DATE = datetime.date(2025, 7, 21)
SPONSORED_POST_PROBABILITY = 0.70
TOTAL_USERS = 100000
ORGANIC_CONVERSION_RATE = 0.002

# --- Payout Logic Constants (These define how payouts are generated in this script) ---
PAYOUT_SEGMENTATION_THRESHOLD = 500000
COMMISSION_RATE = 0.08
POST_PAYOUT_BASE_MULTIPLIER = 0.05
POST_PAYOUT_PROGRESSIVE_INCREMENT = 0.01
POST_PAYOUT_TIER_SIZE = 300000

# --- Brand & Product Data ---
BRANDS = {
    "MuscleBlaze": {"campaigns": ["MB_Performance_Q2", "MB_Summer_Shred"], "products": {"Whey Protein": 3800, "Creatine Monohydrate": 900, "Pre-Workout 300": 1500, "BCAA Pro": 1200}},
    "HKVitals": {"campaigns": ["HKV_Wellness_Launch", "HKV_Immunity_Boost"], "products": {"Multivitamin Tablets": 650, "Omega-3 Fish Oil": 950, "Biotin Gummies": 800, "Collagen Powder": 1800}},
    "Gritzo": {"campaigns": ["Gritzo_Kids_Health", "Gritzo_Active_Growth"], "products": {"SuperMilk for Kids": 900, "Mighty Munchies": 350, "Kids Protein Peanut Butter": 450}}
}

# --- Database Configuration (from constants.py) ---
from constants import DB_NAME # Import DB_NAME from constants.py

def create_influencers(count):
    """Creates a list of synthetic influencer dictionaries."""
    influencers = []
    first_names_female = ["Priya", "Ananya", "Saanvi", "Diya", "Isha", "Myra", "Kiara", "Zoya", "Aisha", "Zara"]
    first_names_male = ["Aarav", "Rohan", "Vikram", "Aditya", "Arjun", "Kabir", "Vivaan", "Reyansh", "Dev", "Aryan"]
    last_names = ["Sharma", "Singh", "Gupta", "Reddy", "Patel", "Desai", "Kumar", "Mehta", "Nair", "Joshi"]
    categories = ["Fitness", "Health & Wellness", "Nutrition", "Lifestyle", "Yoga", "Bodybuilding"]
    platforms = ["Instagram", "YouTube", "Twitter"]
    tiers = {"Micro": (10000, 99999, 0.40), "Mid-tier": (100000, 499999, 0.30), "Macro": (500000, 999999, 0.15), "Mega": (1000000, 7000000, 0.10), "Nano": (1000, 9999, 0.05)}
    
    for i in range(1, count + 1):
        gender = random.choices(["Female", "Male"], weights=[0.6, 0.4], k=1)[0]
        name = f"{random.choice(first_names_female if gender == 'Female' else first_names_male)} {random.choice(last_names)}"
        tier_choice = random.choices(list(tiers.keys()), weights=[v[2] for v in tiers.values()], k=1)[0]
        min_followers, max_followers, _ = tiers[tier_choice]
        follower_count = random.randint(min_followers, max_followers)
        payout_basis = 'Post' if follower_count >= PAYOUT_SEGMENTATION_THRESHOLD else 'Order'
        influencers.append({"influencer_id": f"inf_{i:03d}", "name": name, "category": random.choice(categories), "gender": gender, "follower_count": follower_count, "platform": random.choices(platforms, weights=[0.7, 0.25, 0.05], k=1)[0], "payout_basis": payout_basis})
    return influencers

def create_posts(influencers_data, count):
    """Creates a list of synthetic post dictionaries."""
    posts = []
    total_days = (END_DATE - START_DATE).days
    
    for i in range(1, count + 1):
        influencer = random.choice(influencers_data)
        post_date = START_DATE + datetime.timedelta(days=random.randint(0, total_days))
        is_sponsored = random.random() < SPONSORED_POST_PROBABILITY
        brand_name, campaign_name = (random.choice(list(BRANDS.keys())), None) if is_sponsored else (None, None)
        if brand_name: campaign_name = random.choice(BRANDS[brand_name]["campaigns"])
        
        reach = int(influencer['follower_count'] * random.uniform(0.4, 1.6))
        likes = int(reach * random.uniform(0.02, 0.10))
        comments = int(likes * random.uniform(0.005, 0.05))
        
        posts.append({"post_id": f"post_{i:03d}", "influencer_id": influencer['influencer_id'], "platform": influencer['platform'], "date": post_date.strftime('%Y-%m-%d'), "brand": brand_name, "campaign": campaign_name, "reach": reach, "likes": likes, "comments": comments})
    return posts

def create_tracking_data(posts_data):
    """Creates sales tracking data, including both influenced and organic sales."""
    tracking = []
    user_id_counter = 1
    total_days = (END_DATE - START_DATE).days
    
    # --- Influenced Sales ---
    for post in posts_data:
        if post["brand"]:
            brand_info = BRANDS[post["brand"]]
            num_orders = int(post["likes"] * random.uniform(0.005, 0.02))
            for _ in range(num_orders):
                product, revenue = random.choice(list(brand_info["products"].items()))
                order_date = datetime.datetime.strptime(post["date"], '%Y-%m-%d').date() + datetime.timedelta(days=random.randint(1, 7))
                tracking.append({
                    "source": f"trk_{post['influencer_id']}_{post['post_id']}", 
                    "campaign": post["campaign"], 
                    "influencer_id": post["influencer_id"], 
                    "user_id": f"user_{user_id_counter:05d}", 
                    "product": product, 
                    "date": order_date.strftime('%Y-%m-%d'), 
                    "orders": 1, 
                    "revenue": revenue, 
                    "attribution_type": "Influenced", 
                    "brand": post["brand"]
                })
                user_id_counter += 1

    # --- Organic Sales ---
    num_organic_orders = int(TOTAL_USERS * ORGANIC_CONVERSION_RATE * total_days)
    for _ in range(num_organic_orders):
        brand_name = random.choice(list(BRANDS.keys()))
        product, revenue = random.choice(list(BRANDS[brand_name]["products"].items()))
        order_date = START_DATE + datetime.timedelta(days=random.randint(0, total_days))
        
        organic_record = {
            "source": "organic",
            "campaign": None,
            "influencer_id": None,
            "user_id": f"user_{user_id_counter:05d}",
            "product": product,
            "date": order_date.strftime('%Y-%m-%d'),
            "orders": 1,
            "revenue": revenue,
            "attribution_type": "Organic",
            "brand": brand_name
        }
        tracking.append(organic_record)
        user_id_counter += 1
        
    return tracking

def create_payouts(influencers_data, posts_data, tracking_data):
    """
    Creates the raw payouts data (payouts.csv).
    IMPORTANT: This function does NOT include 'post_id' or 'invoice_date' in the generated data
    because generate_data.py is treated as raw, unmodifiable client data.
    These columns will be reconstructed in SQL later.
    """
    payouts = []
    
    # Map influencer_id to payout_basis and follower_count for quick lookup
    influencer_details_map = {
        inf['influencer_id']: {'payout_basis': inf.get('payout_basis'), 'follower_count': inf.get('follower_count')}
        for inf in influencers_data
    }

    # Identify influencers who made at least one post (branded or not)
    # This aligns with the rule that all posts count for 'Post'-based payments.
    active_influencers_from_posts = {p["influencer_id"] for p in posts_data}
    
    payout_id_counter = 1 # Counter for unique payout IDs

    # Iterate through each influencer to determine their payouts
    for influencer in influencers_data:
        inf_id = influencer["influencer_id"]
        
        # Only process influencers who have made at least one post
        if inf_id not in active_influencers_from_posts:
            continue
            
        basis = influencer_details_map[inf_id]['payout_basis']
        
        if basis == 'Order':
            # For Order-based influencers, create a payout entry for EACH relevant tracking record (Influenced order)
            relevant_tracking_records = [
                rec for rec in tracking_data
                if rec.get('influencer_id') == inf_id and rec.get('attribution_type') == 'Influenced'
            ]
            for record in relevant_tracking_records:
                payouts.append({
                    "payout_id": f"p_out_{payout_id_counter:03d}",
                    "influencer_id": inf_id,
                    "basis": "Order",
                    "rate": COMMISSION_RATE, # Rate is the commission rate (0.08)
                    "orders": record['orders'], # Number of orders for this specific record
                    "total_payout": round(record['revenue'] * COMMISSION_RATE, 2), # Calculate total payout for this record
                    # post_id and invoice_date are NOT included here as per client data constraint
                })
                payout_id_counter += 1
        
        elif basis == 'Post':
            followers = influencer_details_map[inf_id]['follower_count']
            
            # For Post-based influencers, iterate through ALL their posts (branded or not)
            all_influencer_posts = [p for p in posts_data if p["influencer_id"] == inf_id]
            
            if not all_influencer_posts: # Skip if no posts found (should be covered by active_influencers check)
                continue

            for post in all_influencer_posts:
                # Calculate the progressive pay multiplier based on follower tiers
                tiers_above_base = max(0, math.floor((followers - PAYOUT_SEGMENTATION_THRESHOLD) / POST_PAYOUT_TIER_SIZE))
                multiplier = POST_PAYOUT_BASE_MULTIPLIER + (tiers_above_base * POST_PAYOUT_PROGRESSIVE_INCREMENT)
                rate = round(followers * multiplier, 2) # Rate per post based on followers

                payouts.append({
                    "payout_id": f"p_out_{payout_id_counter:03d}",
                    "influencer_id": inf_id,
                    "basis": "Post",
                    "rate": rate, # Rate per post
                    "orders": 0, # Orders is 0 for Post-based payouts
                    "total_payout": rate, # Total payout for this specific post
                    # post_id and invoice_date are NOT included here as per client data constraint
                })
                payout_id_counter += 1
    
    return payouts

def save_to_csv(data, filename, fieldnames, directory="."):
    """Saves a list of dictionaries to a CSV file in a specified directory."""
    filepath = os.path.join(directory, filename)
    os.makedirs(directory, exist_ok=True)
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(data)
        print(f"Successfully generated {filepath}")
    except IOError as e:
        print(f"Error writing to {filepath}: {e}")

def load_data_into_sqlite(data_list, table_name, db_name=DB_NAME):
    """
    Loads a list of dictionaries into a SQLite table using Pandas.
    It drops the table if it exists and handles date format conversion.
    """
    print(f"Loading data into SQLite table: {table_name}...")
    try:
        with sqlite3.connect(db_name) as conn:
            df = pd.DataFrame(data_list)
            # Ensure date columns are strings before loading to SQLite if they are datetime objects
            # SQLite stores dates as TEXT by default, so string format is best for direct loading.
            for col in ['date', 'order_date', 'post_date', 'invoice_date']:
                if col in df.columns and pd.api.types.is_datetime64_any_dtype(df[col]):
                    df[col] = df[col].dt.strftime('%Y-%m-%d')
            
            # Use if_exists='replace' to ensure a clean table on each run
            df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"Successfully loaded data into {table_name} table.")
    except Exception as e:
        print(f"Error loading data into SQLite table {table_name}: {e}")
        raise # Re-raise the exception to stop the script if loading fails

def main():
    """
    The main function to orchestrate the entire raw data generation process.
    It generates data in memory, saves it to CSVs, and loads it into SQLite tables.
    """
    print("--- Starting Raw Data Generation and SQLite Loading ---")
    
    # Ensure the 'data' directory exists for CSV backups
    if not os.path.exists('data'):
        os.makedirs('data')

    # Generate all raw data in memory as lists of dictionaries.
    print("Generating synthetic data...")
    influencers = create_influencers(NUMBER_OF_INFLUENCERS)
    posts = create_posts(influencers, NUMBER_OF_POSTS)
    tracking = create_tracking_data(posts)
    payouts = create_payouts(influencers, posts, tracking) # This now includes post_id and invoice_date

    # Save each generated dataset to its respective CSV file in the 'data' directory.
    # This serves as a raw data backup.
    print("Saving raw data to CSVs...")
    save_to_csv(influencers, "influencers.csv", ["influencer_id", "name", "category", "gender", "follower_count", "platform", "payout_basis"], directory='data')
    save_to_csv(posts, "posts.csv", ["post_id", "influencer_id", "platform", "date", "brand", "campaign", "reach", "likes", "comments"], directory='data')
    save_to_csv(tracking, "tracking_data.csv", ["source", "campaign", "influencer_id", "user_id", "product", "date", "orders", "revenue", "attribution_type", "brand"], directory='data')
    # IMPORTANT: payouts.csv fieldnames do NOT include post_id or invoice_date, as per client data constraint.
    save_to_csv(payouts, "payouts.csv", ["payout_id", "influencer_id", "basis", "rate", "orders", "total_payout"], directory='data')

    # Load the generated data into SQLite tables.
    print("Loading raw data into SQLite tables...")
    load_data_into_sqlite(influencers, "raw_influencers")
    load_data_into_sqlite(posts, "raw_posts")
    load_data_into_sqlite(tracking, "raw_tracking_data")
    load_data_into_sqlite(payouts, "raw_payouts") # This table will NOT have post_id or invoice_date

    print("\n--- Raw data generation and SQLite loading complete. ---")

# This standard Python construct ensures that the main() function is called
# only when the script is executed directly from the command line.
if __name__ == "__main__":
    main()