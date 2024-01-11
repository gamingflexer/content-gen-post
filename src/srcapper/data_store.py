from sqlalchemy import create_engine
import pandas as pd
import datetime as dt
import json

def append_to_database(new_df, db_path='sqlite:///news_data.db', table_name='news_data', force = False):
    engine = create_engine(db_path, echo=False)
    with engine.connect() as connection:
        existing_df = pd.read_sql_table(table_name, con=connection)
    existing_df['timestamp'] = pd.to_datetime(existing_df['timestamp'])
    today_date = dt.date.today()
    
    if force:
        new_df.to_sql(table_name, con=engine, if_exists='append', index=False)
        print(f"Appended {len(new_df)} records to database.")
        return
    
    existing_records_today = existing_df[existing_df['timestamp'].dt.date == today_date]
    print(f"Found {len(existing_records_today)} records for today.")
    if existing_records_today.empty:
        new_df.to_sql(table_name, con=engine, if_exists='append', index=False)
        print(f"Appended {len(new_df)} records to database.")
    elif len(existing_records_today) < 5:
        new_df.to_sql(table_name, con=engine, if_exists='append', index=False)
        print(f"Appended {len(new_df)} records to database, because there were only {len(existing_records_today)} records for today.")
    else:
        print(f"Found {len(existing_records_today)} records for today. Skipping append.")


def retrieve_records(db_path='sqlite:///news_data.db', table_name='news_data', date_range='today'):
    engine = create_engine(db_path, echo=False)

    with engine.connect() as connection:
        df = pd.read_sql_table(table_name, con=connection)

    df['timestamp'] = pd.to_datetime(df['timestamp'])

    if date_range == 'today':
        today_date = dt.date.today()
        filtered_df = df[df['timestamp'].dt.date == today_date]
    elif date_range == 'week':
        week_start = dt.date.today() - dt.timedelta(days=dt.date.today().weekday())
        filtered_df = df[df['timestamp'].dt.date >= week_start]
        
        # Sample 5 random records from each day in the week
        sampled_records = []
        for day in range(7):
            day_date = week_start + dt.timedelta(days=day)
            day_df = filtered_df[filtered_df['timestamp'].dt.date == day_date]
            
            if not day_df.empty:
                sampled_day_records = day_df.sample(n=min(5, len(day_df)), random_state=42)
                sampled_records.append(sampled_day_records)

        # Combine the sampled records into a single DataFrame
        filtered_df = pd.concat(sampled_records)
    else:
        raise ValueError("Invalid date_range. Use 'today' or 'week'.")
    
    result_df = filtered_df[['timestamp', 'news_text']]
    result_json = result_df.to_json(orient='records')
    output = json.loads(result_json)
    print(f"Retrieved {len(output)} records from database.")
    return output