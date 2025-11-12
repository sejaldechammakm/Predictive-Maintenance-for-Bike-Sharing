♦️Features

Database Integration: Data is stored and fetched from a PostgreSQL database.

Data Preprocessing: Handles missing values, cleans features, and creates additional engineered features such as:

vibration_per_km = average vibration per km since last maintenance

rain_ratio = ratio of rainy rides to days since last serviced

Machine Learning Model: Trains a predictive model using XG Boost to classify whether a bike needs maintenance (needs_maintenance = 1) or not (0).

