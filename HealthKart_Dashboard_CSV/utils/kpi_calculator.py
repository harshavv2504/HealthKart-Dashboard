# utils/kpi_calculator.py
from constants import PROFIT_MARGIN_FACTOR

def calculate_kpis(filtered_orders_df, filtered_payment_log_df):
    """
    Calculates key performance indicators (KPIs) from filtered data.
    Returns a dictionary of KPIs.
    """
    total_revenue = filtered_orders_df['revenue_generated'].sum()
    total_payout = filtered_payment_log_df['payment_amount'].sum()
    net_profit = (total_revenue * PROFIT_MARGIN_FACTOR) - total_payout

    baseline_revenue = filtered_orders_df[
        filtered_orders_df['platform'].isna() | (filtered_orders_df['platform'] == '')
    ]['revenue_generated'].sum()

    influencer_driven_revenue = total_revenue - baseline_revenue

    incremental_roas = influencer_driven_revenue / total_payout if total_payout > 0 else 0
    roi = (net_profit / total_payout) * 100 if total_payout > 0 else 0

    # This already correctly drops NaNs before counting unique campaigns
    num_campaigns = filtered_orders_df['campaign'].dropna().nunique()
    total_orders = len(filtered_orders_df)

    influenced_orders_count = filtered_orders_df[
        filtered_orders_df['platform'].notna() & (filtered_orders_df['platform'] != '')
    ].shape[0]
    organic_orders_count = filtered_orders_df[
        filtered_orders_df['platform'].isna() | (filtered_orders_df['platform'] == '')
    ].shape[0]

    overall_net_profit_percentage = (net_profit / total_revenue) if total_revenue > 0 else 0

    return {
        "total_revenue": total_revenue,
        "total_payout": total_payout,
        "net_profit": net_profit,
        "baseline_revenue": baseline_revenue,
        "influencer_driven_revenue": influencer_driven_revenue,
        "incremental_roas": incremental_roas,
        "roi": roi,
        "num_campaigns": num_campaigns,
        "total_orders": total_orders,
        "influenced_orders_count": influenced_orders_count,
        "organic_orders_count": organic_orders_count,
        "overall_net_profit_percentage": overall_net_profit_percentage
    }