from sqlalchemy import create_engine
import pandas as pd
import datetime as dt
import json

def append_to_database(new_df, db_path='sqlite:///news_data.db', table_name='news_data'):
    engine = create_engine(db_path, echo=False)
    new_df.to_sql(table_name, con=engine, if_exists='append', index=False)

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
    else:
        raise ValueError("Invalid date_range. Use 'today' or 'week'.")
    
    result_df = filtered_df[['timestamp', 'news_text']]
    result_json = result_df.to_json(orient='records')
    return json.loads(result_json)