import sqlite3
import os

# --- Database Configuration (from constants.py) ---
from constants import DB_NAME 

# --- Payout Logic Constants (Needed for SQL calculations) ---
# These constants are embedded directly into the SQL queries.
# They must match the constants defined in your generate_data.py script.
COMMISSION_RATE = 0.08
PAYOUT_SEGMENTATION_THRESHOLD = 500000
POST_PAYOUT_BASE_MULTIPLIER = 0.05
POST_PAYOUT_PROGRESSIVE_INCREMENT = 0.01
POST_PAYOUT_TIER_SIZE = 300000

# --- Cost of Goods Constant (Used in SQL Calculations) ---
# This constant is used for calculating Gross Profit in the influencer_performance view.
COST_OF_GOODS_PERCENTAGE = 0.55 # 55% of revenue generated

def execute_sql_query(query, db_name=DB_NAME):
    """
    Connects to the SQLite database and executes a given SQL query.
    Commits the transaction and prints a success message or an error.
    """
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit() # Save changes to the database
        print(f"Successfully executed SQL query.")
    except sqlite3.Error as e:
        print(f"SQL Error: {e}\nQuery:\n{query}")
        raise # Re-raise the exception to stop execution if there's a critical SQL error

def main():
    """
    Orchestrates the creation of cleaned and transformed data marts (views) in SQLite.
    
    This script relies on raw data tables (raw_influencers, raw_posts, raw_tracking_data)
    being already populated in 'data.db' by running generate_data.py.
    It does NOT modify the raw data generation (generate_data.py).
    """
    print("--- Creating SQL Data Marts in SQLite ---")

    # --- Mart 1: payments_log View ---
    # Purpose: To create a complete, itemized log of all payment events.
    # This view fully reconstructs the payment logic from original cleaning_functions/payments_log.py
    # by joining raw tables and calculating payouts within SQL.
    # It includes post_id and invoice_date, which are critical for dashboard filtering.
    # It uses UNION ALL to combine 'Post'-based and 'Order'-based payments.

    # Split DROP VIEW and CREATE VIEW into separate statements for sqlite3.ProgrammingError
    drop_payments_log_sql = "DROP VIEW IF EXISTS payments_log;"
    payments_log_create_sql = f"""
    CREATE VIEW payments_log AS
    
    -- Part 1: Calculate Payments for 'Post'-based Influencers
    -- This section processes posts made by influencers whose payout_basis is 'Post'.
    -- Each post from such an influencer generates a payment.
    SELECT
        -- Generate a unique payment_log_id for each post-based payment entry.
        -- Using a combination of 'plog_post_' and the post_id for uniqueness.
        'plog_post_' || P.post_id AS payment_log_id,
        P.influencer_id,
        I.payout_basis AS payment_basis, -- This will be 'Post'
        P.post_id,
        P.platform AS source, -- The platform where the post was made is considered the source.
        P.date AS invoice_date, -- The date of the post is the invoice date.
        -- Calculate payment_amount for Post-based influencers:
        -- ROUND(follower_count * (BASE_MULTIPLIER + (tiers_above_base * PROGRESSIVE_INCREMENT)), 2)
        -- Note: SQLite's math functions are basic. CAST(... AS REAL) for float division.
        -- MAX(0, ...) is used to ensure 'tiers_above_base' is not negative.
        ROUND(
            I.follower_count * (
                {POST_PAYOUT_BASE_MULTIPLIER} +
                -- Calculate 'tiers_above_base': (follower_count - THRESHOLD) / TIER_SIZE
                MAX(0, CAST((I.follower_count - {PAYOUT_SEGMENTATION_THRESHOLD}) AS REAL) / {POST_PAYOUT_TIER_SIZE}) * {POST_PAYOUT_PROGRESSIVE_INCREMENT}
            ), 2
        ) AS payment_amount
    FROM
        raw_posts AS P -- Start with the raw_posts table
    JOIN
        raw_influencers AS I ON P.influencer_id = I.influencer_id -- Join to get influencer details (like payout_basis, follower_count)
    WHERE
        I.payout_basis = 'Post' -- Filter only for influencers whose payout basis is 'Post'
        -- This SQL reflects the rule: payments are generated for ALL posts by 'Post'-based influencers,
        -- regardless of whether the post has a 'brand' associated with it.
    
    UNION ALL -- Combine the results of 'Post'-based payments with 'Order'-based payments
    
    -- Part 2: Calculate Payments for 'Order'-based Influencers
    -- This section processes tracking data for 'Influenced' orders by 'Order'-based influencers.
    -- Each such order generates a payment.
    SELECT
        -- Generate a unique payment_log_id for each order-based payment entry.
        -- We combine 'plog_order_', user_id, product (cleaned), and date for uniqueness.
        -- REPLACE(T.product, ' ', '_') is used to make product names URL-safe for ID.
        'plog_order_' || T.user_id || '_' || REPLACE(T.product, ' ', '_') || '_' || T.date AS payment_log_id,
        T.influencer_id,
        I.payout_basis AS payment_basis, -- This will be 'Order'
        -- Extract 'post_id' from the 'source' column (e.g., 'trk_inf_001_post_002' -> 'post_002').
        -- SUBSTR and INSTR are SQLite string functions.
        CASE
            WHEN T.source LIKE 'trk_%' THEN SUBSTR(T.source, INSTR(T.source, 'post_'))
            ELSE NULL
        END AS post_id,
        T.source, -- Original source from tracking_data (e.g., tracking link or 'organic').
        T.date AS invoice_date, -- The order date is the invoice date.
        -- Calculate payment_amount for Order-based influencers: ROUND(revenue * COMMISSION_RATE, 2)
        ROUND(T.revenue * {COMMISSION_RATE}, 2) AS payment_amount
    FROM
        raw_tracking_data AS T -- Start with the raw_tracking_data table (orders)
    JOIN
        raw_influencers AS I ON T.influencer_id = I.influencer_id -- Join to get influencer details (like payout_basis)
    WHERE
        T.attribution_type = 'Influenced' AND I.payout_basis = 'Order'; -- Filter for 'Influenced' orders and 'Order'-based influencers
    """

    print("\n[Mart 1/3] Creating payments_log view...")
    execute_sql_query(drop_payments_log_sql) # Execute DROP VIEW first
    execute_sql_query(payments_log_create_sql) # Then execute CREATE VIEW
    print("[Mart 1/3] payments_log view created.")


    # --- Mart 2: enriched_orders View ---
    # Purpose: Replicates the merging and enrichment logic from cleaning_functions/orders_tracking.py.
    # Combines raw tracking data (orders) with post details and influencer metadata.
    # Split DROP VIEW and CREATE VIEW into separate statements
    drop_enriched_orders_sql = "DROP VIEW IF EXISTS enriched_orders;"
    enriched_orders_create_sql = f"""
    CREATE VIEW enriched_orders AS
    SELECT
        T1.campaign,
        T1.influencer_id,
        T1.product,
        T1.date AS order_date, -- Renamed from 'date' in raw_tracking_data
        T1.orders,
        COALESCE(T1.revenue, 0) AS revenue_generated, -- Renamed from 'revenue' in raw_tracking_data
        CAST(COALESCE(T1.revenue, 0) * {COST_OF_GOODS_PERCENTAGE} AS INTEGER) AS cost_of_goods, -- Calculated: revenue * 0.55
        (COALESCE(T1.revenue, 0) - CAST(COALESCE(T1.revenue, 0) * {COST_OF_GOODS_PERCENTAGE} AS INTEGER)) AS gross_profit, -- Calculated: revenue - cogs
        T1.attribution_type,
        -- Extract post_id from source if it's an influenced order (matches Python logic)
        CASE
            WHEN T1.source LIKE 'trk_%' THEN SUBSTR(T1.source, INSTR(T1.source, 'post_'))
            ELSE NULL
        END AS post_id,
        P.platform AS platform, -- CORRECTED: Pulled from raw_posts (P)
        P.date AS post_date, -- Post date from raw_posts (original 'date_y' in Python merge)
        P.reach,
        P.likes,
        P.comments,
        T1.brand AS brand, -- EXPLICIT ALIAS for brand
        I.name AS name, -- EXPLICIT ALIAS for name
        I.category,
        I.gender,
        I.follower_count,
        I.payout_basis AS "Payout Type" -- Payout basis from raw_influencers, renamed
    FROM
        raw_tracking_data AS T1 -- Start with raw_tracking_data (orders)
    LEFT JOIN
        raw_posts AS P ON T1.influencer_id = P.influencer_id AND
                           (CASE WHEN T1.source LIKE 'trk_%' THEN SUBSTR(T1.source, INSTR(T1.source, 'post_')) ELSE NULL END) = P.post_id
    LEFT JOIN
        raw_influencers AS I ON T1.influencer_id = I.influencer_id
    ORDER BY
        order_date ASC;
    """
    print("\n[Mart 2/3] Creating enriched_orders view...")
    execute_sql_query(drop_enriched_orders_sql) # Execute DROP VIEW first
    execute_sql_query(enriched_orders_create_sql) # Then execute CREATE VIEW
    print("[Mart 2/3] enriched_orders view created.")


    # --- Mart 3: influencer_performance View ---
    # Purpose: Aggregates data to influencer-level KPIs.
    # This view replicates the logic from cleaning_functions/influencer_performance.py.
    # It uses the newly created payments_log view for payout sums.
    # Split DROP VIEW and CREATE VIEW into separate statements
    drop_influencer_performance_sql = "DROP VIEW IF EXISTS influencer_performance;"
    influencer_performance_create_sql = f"""
    CREATE VIEW influencer_performance AS
    SELECT
        I.influencer_id,
        I.name AS Influencer,
        I.payout_basis AS "Payout Type",
        -- Posts, Reach, Likes, Comments (aggregated from raw_posts, all posts)
        COALESCE(P_agg.posts_count, 0) AS Posts,
        COALESCE(P_agg.reach, 0) AS Reach,
        COALESCE(P_agg.likes, 0) AS Likes,
        COALESCE(P_agg.comments, 0) AS Comments,
        -- Engagement Rate: ((Likes + Comments) / Reach) * 100
        COALESCE(ROUND((P_agg.likes + P_agg.comments) * 100.0 / P_agg.reach, 2), 0) AS "Engagement Rate",
        -- Orders, Revenue (aggregated from raw_tracking_data, only 'Influenced')
        COALESCE(T_agg.orders_count, 0) AS Orders,
        COALESCE(T_agg.revenue_sum, 0) AS Revenue,
        -- Payout (aggregated from payments_log view)
        COALESCE(PL_agg.total_payout_sum, 0) AS Payout,
        -- Gross Profit, Net Profit, ROAS, ROI
        -- Gross Profit: Revenue * (1 - COST_OF_GOODS_PERCENTAGE)
        COALESCE(T_agg.revenue_sum * (1 - {COST_OF_GOODS_PERCENTAGE}), 0) AS "Gross Profit",
        -- Net Profit: Gross Profit - Payout
        (COALESCE(T_agg.revenue_sum, 0) * (1 - {COST_OF_GOODS_PERCENTAGE})) - COALESCE(PL_agg.total_payout_sum, 0) AS "Net Profit",
        -- ROAS: Revenue / Payout (handle division by zero)
        CASE
            WHEN COALESCE(PL_agg.total_payout_sum, 0) = 0 THEN 0
            ELSE ROUND(COALESCE(T_agg.revenue_sum, 0) * 1.0 / COALESCE(PL_agg.total_payout_sum, 0), 0)
        END AS ROAS,
        -- ROI: (Net Profit / Payout) * 100 (handle division by zero)
        CASE
            WHEN COALESCE(PL_agg.total_payout_sum, 0) = 0 THEN 0
            ELSE ROUND(((COALESCE(T_agg.revenue_sum, 0) * (1 - {COST_OF_GOODS_PERCENTAGE})) - COALESCE(PL_agg.total_payout_sum, 0)) * 100.0 / COALESCE(PL_agg.total_payout_sum, 0), 0)
        END AS ROI
    FROM
        raw_influencers AS I
    LEFT JOIN (
        -- Subquery to aggregate post metrics per influencer
        SELECT influencer_id, COUNT(post_id) AS posts_count, SUM(reach) AS reach, SUM(likes) AS likes, SUM(comments) AS comments
        FROM raw_posts
        GROUP BY influencer_id
    ) AS P_agg ON I.influencer_id = P_agg.influencer_id
    LEFT JOIN (
        -- Subquery to aggregate tracking data (orders, revenue) per influencer for 'Influenced' attribution
        SELECT influencer_id, SUM(orders) AS orders_count, SUM(revenue) AS revenue_sum
        FROM raw_tracking_data
        WHERE attribution_type = 'Influenced'
        GROUP BY influencer_id
    ) AS T_agg ON I.influencer_id = T_agg.influencer_id
    LEFT JOIN (
        -- Subquery to aggregate total payout per influencer from the payments_log view
        SELECT influencer_id, SUM(payment_amount) AS total_payout_sum
        FROM payments_log -- Use the newly created payments_log view
        GROUP BY influencer_id
    ) AS PL_agg ON I.influencer_id = PL_agg.influencer_id
    GROUP BY
        I.influencer_id, I.name, I.payout_basis;
    """
    print("\n[Mart 3/3] Creating influencer_performance view...")
    execute_sql_query(drop_influencer_performance_sql) # Execute DROP VIEW first
    execute_sql_query(influencer_performance_create_sql) # Then execute CREATE VIEW
    print("[Mart 3/3] influencer_performance view created.")

    print("\n--- SQL Data Marts Created Successfully ---")


if __name__ == "__main__":
    # This script assumes generate_data.py has already been run to populate raw tables.
    # It checks for the existence of the database file before proceeding.
    if not os.path.exists(DB_NAME):
        print(f"Error: Database file '{DB_NAME}' not found. Please run generate_data.py first to populate raw data.")
    else:
        main()
