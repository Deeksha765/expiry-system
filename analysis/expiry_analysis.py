# analysis/expiry_analysis.py
# ─────────────────────────────────────────────────────────────
# Expiry analysis using Pandas
# ─────────────────────────────────────────────────────────────

import pandas as pd
from datetime import date

def analyze_products(products: list) -> dict:
    """
    Takes a list of product dicts from the DB.
    Returns analysis results including expiry classification
    and chart-ready data.
    """

    if not products:
        return {
            'total': 0, 'safe': 0, 'near_expiry': 0, 'expired': 0,
            'products': [],
            'chart_data': {
                'status_labels':   ['Safe', 'Near-Expiry', 'Expired'],
                'status_counts':   [0, 0, 0],
                'category_labels': [],
                'category_counts': []
            }
        }

    # ── Build DataFrame ─────────────────────────────────────
    df = pd.DataFrame(products)

    # Convert exp_date to datetime
    df['exp_date'] = pd.to_datetime(df['exp_date'])
    today          = pd.Timestamp(date.today())

    # ── Calculate days remaining ────────────────────────────
    df['days_remaining'] = (df['exp_date'] - today).dt.days

    # ── Classify status ─────────────────────────────────────
    def classify(days):
        if days < 0:
            return 'Expired'
        elif days <= 30:
            return 'Near-Expiry'
        else:
            return 'Safe'

    df['status'] = df['days_remaining'].apply(classify)

    # ── Aggregate counts ────────────────────────────────────
    status_counts   = df['status'].value_counts()
    category_counts = df.groupby('category')['status'].count()

    # ── Prepare product list for templates ─────────────────
    product_list = []
    for _, row in df.iterrows():
        product_list.append({
            'id':             int(row['id']),
            'barcode':        row['barcode'],
            'name':           row['name'],
            'category':       row['category'],
            'manufacturer':   row.get('manufacturer', ''),
            'exp_date':       row['exp_date'].strftime('%Y-%m-%d'),
            'days_remaining': int(row['days_remaining']),
            'status':         row['status'],
            'quantity':       int(row['quantity'])
        })

    return {
        'total':      len(df),
        'safe':       int(status_counts.get('Safe', 0)),
        'near_expiry':int(status_counts.get('Near-Expiry', 0)),
        'expired':    int(status_counts.get('Expired', 0)),
        'products':   product_list,
        'chart_data': {
            'status_labels':   ['Safe', 'Near-Expiry', 'Expired'],
            'status_counts':   [
                int(status_counts.get('Safe', 0)),
                int(status_counts.get('Near-Expiry', 0)),
                int(status_counts.get('Expired', 0))
            ],
            'category_labels': list(category_counts.index),
            'category_counts': [int(x) for x in category_counts.values]
        }
    }