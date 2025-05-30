import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import json

# Generate synthetic data
def generate_quality_data(n_samples=10000):
    crops = ['TOMATO', 'LETTUCE', 'CUCUMBER', 'BASIL', 'SPINACH']
    growth_stages = ['GERMINATION', 'VEGETATIVE', 'FLOWERING', 'FRUITING']

    # Optimal conditions for each crop and stage
    crop_conditions = {
        'TOMATO': {
            'GERMINATION': {'temp': (22, 25), 'humidity': (80, 90), 'co2': (400, 600)},
            'VEGETATIVE': {'temp': (20, 26), 'humidity': (60, 80), 'co2': (800, 1200)},
            'FLOWERING': {'temp': (18, 24), 'humidity': (65, 75), 'co2': (1000, 1500)},
            'FRUITING': {'temp': (18, 25), 'humidity': (60, 70), 'co2': (800, 1200)}
        },
        'LETTUCE': {
            'GERMINATION': {'temp': (18, 21), 'humidity': (70, 80), 'co2': (400, 600)},
            'VEGETATIVE': {'temp': (17, 23), 'humidity': (50, 70), 'co2': (800, 1200)},
            'FLOWERING': {'temp': (16, 22), 'humidity': (50, 65), 'co2': (800, 1200)},
            'FRUITING': {'temp': (16, 22), 'humidity': (50, 65), 'co2': (800, 1200)}
        },
        'CUCUMBER': {
            'GERMINATION': {'temp': (23, 26), 'humidity': (80, 90), 'co2': (400, 600)},
            'VEGETATIVE': {'temp': (22, 28), 'humidity': (70, 90), 'co2': (1000, 1500)},
            'FLOWERING': {'temp': (20, 26), 'humidity': (70, 85), 'co2': (1000, 1500)},
            'FRUITING': {'temp': (20, 25), 'humidity': (70, 80), 'co2': (800, 1200)}
        },
        'BASIL': {
            'GERMINATION': {'temp': (20, 25), 'humidity': (80, 90), 'co2': (400, 600)},
            'VEGETATIVE': {'temp': (20, 25), 'humidity': (60, 70), 'co2': (800, 1200)},
            'FLOWERING': {'temp': (18, 24), 'humidity': (55, 65), 'co2': (800, 1200)},
            'FRUITING': {'temp': (18, 24), 'humidity': (55, 65), 'co2': (800, 1200)}
        },
        'SPINACH': {
            'GERMINATION': {'temp': (18, 22), 'humidity': (75, 85), 'co2': (400, 600)},
            'VEGETATIVE': {'temp': (16, 22), 'humidity': (50, 70), 'co2': (800, 1200)},
            'FLOWERING': {'temp': (15, 21), 'humidity': (50, 65), 'co2': (800, 1200)},
            'FRUITING': {'temp': (15, 21), 'humidity': (50, 65), 'co2': (800, 1200)}
        }
    }

    data = []

    for _ in range(n_samples):
        crop = np.random.choice(crops)
        growth_stage = np.random.choice(growth_stages)
        optimal = crop_conditions[crop][growth_stage]

        # Generate parameters with some random variation
        temp = np.random.normal((optimal['temp'][0] + optimal['temp'][1])/2, 2)
        humidity = np.random.normal((optimal['humidity'][0] + optimal['humidity'][1])/2, 5)
        co2 = np.random.normal((optimal['co2'][0] + optimal['co2'][1])/2, 100)

        # PPFD values adjusted for growth stages
        ppfd_ranges = {
            'GERMINATION': (100, 200),
            'VEGETATIVE': (400, 600),
            'FLOWERING': (600, 800),
            'FRUITING': (500, 700)
        }
        ppfd_range = ppfd_ranges[growth_stage]
        ppfd = np.random.normal((ppfd_range[0] + ppfd_range[1])/2, 50)

        # pH and EC ranges
        ph = np.random.normal(6.0, 0.2)  # Most crops prefer 5.8-6.2
        ec = np.random.normal(2.0, 0.2)  # Typical range 1.5-2.5

        # Additional parameters
        leaf_color = np.random.normal(0.8, 0.1)  # NDVI-like index (0-1)

        # Stem thickness varies by stage
        stem_thickness_ranges = {
            'GERMINATION': (1, 3),
            'VEGETATIVE': (4, 8),
            'FLOWERING': (6, 10),
            'FRUITING': (8, 12)
        }
        stem_range = stem_thickness_ranges[growth_stage]
        stem_thickness = np.random.normal((stem_range[0] + stem_range[1])/2, 1)

        # Plant height varies by stage
        height_ranges = {
            'GERMINATION': (2, 5),
            'VEGETATIVE': (10, 30),
            'FLOWERING': (20, 50),
            'FRUITING': (30, 60)
        }
        height_range = height_ranges[growth_stage]
        plant_height = np.random.normal((height_range[0] + height_range[1])/2, 5)

        days_since_planting = np.random.randint(20, 90)

        # Nutrient levels vary by stage
        nutrient_ranges = {
            'GERMINATION': (0.4, 0.6),
            'VEGETATIVE': (0.7, 0.9),
            'FLOWERING': (0.8, 1.0),
            'FRUITING': (0.7, 0.9)
        }
        nutrient_range = nutrient_ranges[growth_stage]
        n_level = np.random.normal((nutrient_range[0] + nutrient_range[1])/2, 0.1)
        p_level = np.random.normal((nutrient_range[0] + nutrient_range[1])/2, 0.1)
        k_level = np.random.normal((nutrient_range[0] + nutrient_range[1])/2, 0.1)

        # Water quality (TDS varies by stage)
        tds_ranges = {
            'GERMINATION': (400, 600),
            'VEGETATIVE': (500, 700),
            'FLOWERING': (600, 800),
            'FRUITING': (500, 700)
        }
        tds_range = tds_ranges[growth_stage]
        tds = np.random.normal((tds_range[0] + tds_range[1])/2, 50)

        # Calculate quality score based on growth stage and parameters
        def calculate_parameter_score(value, optimal_range):
            mid_point = (optimal_range[0] + optimal_range[1]) / 2
            range_width = optimal_range[1] - optimal_range[0]
            deviation = abs(value - mid_point)
            return max(0, min(10, 10 - (deviation / (range_width/2)) * 10))

        # Calculate stage-specific scores
        temp_score = calculate_parameter_score(temp, optimal['temp'])
        humidity_score = calculate_parameter_score(humidity, optimal['humidity'])
        co2_score = calculate_parameter_score(co2, optimal['co2'])
        ppfd_score = calculate_parameter_score(ppfd, ppfd_ranges[growth_stage])

        # Weight factors for different stages
        stage_weights = {
            'GERMINATION': {
                'temp': 1.5, 'humidity': 1.3, 'co2': 0.8, 'ppfd': 0.7,
                'nutrients': 0.6, 'water': 1.0
            },
            'VEGETATIVE': {
                'temp': 1.2, 'humidity': 1.1, 'co2': 1.2, 'ppfd': 1.3,
                'nutrients': 1.4, 'water': 1.1
            },
            'FLOWERING': {
                'temp': 1.1, 'humidity': 1.0, 'co2': 1.3, 'ppfd': 1.4,
                'nutrients': 1.2, 'water': 1.0
            },
            'FRUITING': {
                'temp': 1.0, 'humidity': 0.9, 'co2': 1.1, 'ppfd': 1.2,
                'nutrients': 1.1, 'water': 1.0
            }
        }

        weights = stage_weights[growth_stage]

        # Calculate weighted quality score
        quality_score = np.mean([
            temp_score * weights['temp'],
            humidity_score * weights['humidity'],
            co2_score * weights['co2'],
            ppfd_score * weights['ppfd'],
            (n_level * 10) * weights['nutrients'],
            (p_level * 10) * weights['nutrients'],
            (k_level * 10) * weights['nutrients'],
            min(10, max(0, (800 - abs(600 - tds))/80)) * weights['water']
        ])

        # Add some noise to the final score
        quality_score = min(10, max(0, quality_score + np.random.normal(0, 0.2)))

        data.append({
            'temperature': temp,
            'humidity': humidity,
            'co2_level': co2,
            'ppfd': ppfd,
            'ph': ph,
            'ec': ec,
            'leaf_color_index': leaf_color,
            'stem_thickness': stem_thickness,
            'plant_height': plant_height,
            'days_since_planting': days_since_planting,
            'nitrogen_level': n_level,
            'phosphorus_level': p_level,
            'potassium_level': k_level,
            'water_tds': tds,
            'crop': crop,
            'growth_stage': growth_stage,
            'quality_score': quality_score
        })

    return pd.DataFrame(data)

# Train the model with the generated data
def train_quality_model():
    # Generate data
    df = generate_quality_data(10000)
    print("Data generated successfully:", df.shape)
    
    # Create one-hot encoding for categorical variables
    X = df.drop(['quality_score'], axis=1)
    
    # Convert crop and growth_stage to uppercase to ensure consistency
    X['crop'] = X['crop'].str.upper()
    X['growth_stage'] = X['growth_stage'].str.upper()
    
    # Create dummy variables
    X = pd.get_dummies(X, columns=['crop', 'growth_stage'])
    y = df['quality_score']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Print model performance
    train_score = model.score(X_train_scaled, y_train)
    test_score = model.score(X_test_scaled, y_test)
    print(f"Train R² score: {train_score:.3f}")
    print(f"Test R² score: {test_score:.3f}")
    
    # Save model, scaler and feature names
    joblib.dump(model, 'crop_quality_model.pkl')
    joblib.dump(scaler, 'quality_scaler.pkl')
    joblib.dump(X.columns.tolist(), 'feature_names.pkl')
    
    print(f"Model and scaler saved. Feature columns: {X.columns}")
    
    return model, scaler, X.columns.tolist()

# Function to define quality categories
def get_quality_category(score):
    if score < 3:
        return "Poor"
    elif score < 5:
        return "Fair" 
    elif score < 7:
        return "Good"
    elif score < 9:
        return "Very Good"
    else:
        return "Excellent"

# Reference values for parameters by crop and growth stage
def get_optimal_conditions():
    return {
        'TOMATO': {
            'GERMINATION': {'temp': (22, 25), 'humidity': (80, 90), 'co2': (400, 600), 'ph': (5.8, 6.2), 'ec': (1.5, 2.5), 'ppfd': (100, 200)},
            'VEGETATIVE': {'temp': (20, 26), 'humidity': (60, 80), 'co2': (800, 1200), 'ph': (5.8, 6.2), 'ec': (2.0, 3.0), 'ppfd': (400, 600)},
            'FLOWERING': {'temp': (18, 24), 'humidity': (65, 75), 'co2': (1000, 1500), 'ph': (5.8, 6.2), 'ec': (2.2, 3.5), 'ppfd': (600, 800)},
            'FRUITING': {'temp': (18, 25), 'humidity': (60, 70), 'co2': (800, 1200), 'ph': (5.8, 6.2), 'ec': (2.2, 3.5), 'ppfd': (500, 700)}
        },
        'LETTUCE': {
            'GERMINATION': {'temp': (18, 21), 'humidity': (70, 80), 'co2': (400, 600), 'ph': (5.5, 6.0), 'ec': (1.0, 1.5), 'ppfd': (100, 200)},
            'VEGETATIVE': {'temp': (17, 23), 'humidity': (50, 70), 'co2': (800, 1200), 'ph': (5.5, 6.0), 'ec': (1.0, 1.8), 'ppfd': (400, 600)},
            'FLOWERING': {'temp': (16, 22), 'humidity': (50, 65), 'co2': (800, 1200), 'ph': (5.5, 6.0), 'ec': (1.0, 1.8), 'ppfd': (600, 800)},
            'FRUITING': {'temp': (16, 22), 'humidity': (50, 65), 'co2': (800, 1200), 'ph': (5.5, 6.0), 'ec': (1.0, 1.8), 'ppfd': (500, 700)}
        },
        'CUCUMBER': {
            'GERMINATION': {'temp': (23, 26), 'humidity': (80, 90), 'co2': (400, 600), 'ph': (5.5, 6.5), 'ec': (1.8, 2.5), 'ppfd': (100, 200)},
            'VEGETATIVE': {'temp': (22, 28), 'humidity': (70, 90), 'co2': (1000, 1500), 'ph': (5.5, 6.5), 'ec': (2.0, 3.0), 'ppfd': (400, 600)},
            'FLOWERING': {'temp': (20, 26), 'humidity': (70, 85), 'co2': (1000, 1500), 'ph': (5.5, 6.5), 'ec': (2.2, 3.5), 'ppfd': (600, 800)},
            'FRUITING': {'temp': (20, 25), 'humidity': (70, 80), 'co2': (800, 1200), 'ph': (5.5, 6.5), 'ec': (2.2, 3.5), 'ppfd': (500, 700)}
        },
        'BASIL': {
            'GERMINATION': {'temp': (20, 25), 'humidity': (80, 90), 'co2': (400, 600), 'ph': (5.5, 6.5), 'ec': (1.0, 1.5), 'ppfd': (100, 200)},
            'VEGETATIVE': {'temp': (20, 25), 'humidity': (60, 70), 'co2': (800, 1200), 'ph': (5.5, 6.5), 'ec': (1.0, 1.8), 'ppfd': (400, 600)},
            'FLOWERING': {'temp': (18, 24), 'humidity': (55, 65), 'co2': (800, 1200), 'ph': (5.5, 6.5), 'ec': (1.0, 1.8), 'ppfd': (600, 800)},
            'FRUITING': {'temp': (18, 24), 'humidity': (55, 65), 'co2': (800, 1200), 'ph': (5.5, 6.5), 'ec': (1.0, 1.8), 'ppfd': (500, 700)}
        },
        'SPINACH': {
            'GERMINATION': {'temp': (18, 22), 'humidity': (75, 85), 'co2': (400, 600), 'ph': (6.0, 7.0), 'ec': (1.0, 1.5), 'ppfd': (100, 200)},
            'VEGETATIVE': {'temp': (16, 22), 'humidity': (50, 70), 'co2': (800, 1200), 'ph': (6.0, 7.0), 'ec': (1.0, 1.8), 'ppfd': (400, 600)},
            'FLOWERING': {'temp': (15, 21), 'humidity': (50, 65), 'co2': (800, 1200), 'ph': (6.0, 7.0), 'ec': (1.0, 1.8), 'ppfd': (600, 800)},
            'FRUITING': {'temp': (15, 21), 'humidity': (50, 65), 'co2': (800, 1200), 'ph': (6.0, 7.0), 'ec': (1.0, 1.8), 'ppfd': (500, 700)}
        }
    }

# Generate recommendations based on conditions
def generate_recommendations(data, quality_score):
    crop = data['crop'].upper()
    growth_stage = data['growth_stage'].upper()
    
    optimal_conditions = get_optimal_conditions()
    
    # Make sure the crop exists in our reference data
    if crop not in optimal_conditions:
        return [f"Unknown crop: {crop}. Please check the crop name."]
    
    # Make sure the growth stage exists
    if growth_stage not in optimal_conditions[crop]:
        return [f"Unknown growth stage: {growth_stage}. Please check the growth stage."]
    
    # Get optimal conditions for this crop and stage
    optimal = optimal_conditions[crop][growth_stage]
    
    recommendations = []
    
    # Temperature
    if data['temperature'] < optimal['temp'][0]:
        recommendations.append(f"Increase temperature from {data['temperature']:.1f}°C to {optimal['temp'][0]}-{optimal['temp'][1]}°C range.")
    elif data['temperature'] > optimal['temp'][1]:
        recommendations.append(f"Decrease temperature from {data['temperature']:.1f}°C to {optimal['temp'][0]}-{optimal['temp'][1]}°C range.")
    
    # Humidity
    if data['humidity'] < optimal['humidity'][0]:
        recommendations.append(f"Increase humidity from {data['humidity']:.1f}% to {optimal['humidity'][0]}-{optimal['humidity'][1]}% range.")
    elif data['humidity'] > optimal['humidity'][1]:
        recommendations.append(f"Decrease humidity from {data['humidity']:.1f}% to {optimal['humidity'][0]}-{optimal['humidity'][1]}% range.")
    
    # CO2
    if data['co2_level'] < optimal['co2'][0]:
        recommendations.append(f"Increase CO2 level from {data['co2_level']:.0f}ppm to {optimal['co2'][0]}-{optimal['co2'][1]}ppm range.")
    elif data['co2_level'] > optimal['co2'][1]:
        recommendations.append(f"Decrease CO2 level from {data['co2_level']:.0f}ppm to {optimal['co2'][0]}-{optimal['co2'][1]}ppm range.")
    
    # PPFD
    if data['ppfd'] < optimal['ppfd'][0]:
        recommendations.append(f"Increase light intensity (PPFD) from {data['ppfd']:.0f}μmol/m²/s to {optimal['ppfd'][0]}-{optimal['ppfd'][1]}μmol/m²/s range.")
    elif data['ppfd'] > optimal['ppfd'][1]:
        recommendations.append(f"Decrease light intensity (PPFD) from {data['ppfd']:.0f}μmol/m²/s to {optimal['ppfd'][0]}-{optimal['ppfd'][1]}μmol/m²/s range.")
    
    # pH
    if data['ph'] < optimal['ph'][0]:
        recommendations.append(f"Increase nutrient solution pH from {data['ph']:.1f} to {optimal['ph'][0]}-{optimal['ph'][1]} range.")
    elif data['ph'] > optimal['ph'][1]:
        recommendations.append(f"Decrease nutrient solution pH from {data['ph']:.1f} to {optimal['ph'][0]}-{optimal['ph'][1]} range.")
    
    # EC
    if data['ec'] < optimal['ec'][0]:
        recommendations.append(f"Increase nutrient solution EC from {data['ec']:.1f}mS/cm to {optimal['ec'][0]}-{optimal['ec'][1]}mS/cm range.")
    elif data['ec'] > optimal['ec'][1]:
        recommendations.append(f"Decrease nutrient solution EC from {data['ec']:.1f}mS/cm to {optimal['ec'][0]}-{optimal['ec'][1]}mS/cm range.")
    
    # If quality is very low, provide general encouragement
    if quality_score < 3:
        recommendations.append("Multiple parameters are far from optimal. Consider reviewing and adjusting your growing environment according to recommendations above.")
    
    return recommendations

# Function to predict quality from JSON input
def predict_quality(json_input):
    try:
        # Load the model, scaler, and feature names
        try:
            model = joblib.load('crop_quality_model.pkl')
            scaler = joblib.load('quality_scaler.pkl')
            feature_names = joblib.load('feature_names.pkl')
        except FileNotFoundError:
            print("Model files not found. Training a new model...")
            model, scaler, feature_names = train_quality_model()
        
        # Parse input JSON
        if isinstance(json_input, str):
            data = json.loads(json_input)
        else:
            data = json_input
        
        # Convert input to DataFrame
        input_df = pd.DataFrame([data])
        
        # Standardize crop and growth_stage to uppercase
        input_df['crop'] = input_df['crop'].str.upper()
        input_df['growth_stage'] = input_df['growth_stage'].str.upper()
        
        # Create dummy variables
        input_encoded = pd.get_dummies(input_df, columns=['crop', 'growth_stage'])
        
        # Make sure all necessary columns exist
        for feature in feature_names:
            if feature not in input_encoded.columns:
                input_encoded[feature] = 0
        
        # Keep only the features used by the model
        input_encoded = input_encoded[feature_names]
        
        # Scale the input
        input_scaled = scaler.transform(input_encoded)
        
        # Make prediction
        quality_score = float(model.predict(input_scaled)[0])
        
        # Ensure score is in range [0, 10]
        quality_score = max(0, min(10, quality_score))
        
        # Get quality category
        quality_category = get_quality_category(quality_score)
        
        # Generate recommendations
        recommendations = generate_recommendations(data, quality_score)
        
        # Prepare result
        result = {
            "quality_score": round(quality_score, 2),
            "quality_category": quality_category,
            "recommendations": recommendations
        }
        
        return result
    
    except Exception as e:
        error_msg = f"Error predicting quality: {str(e)}"
        print(error_msg)
        return {"error": error_msg}

# Function to handle API requests
def process_crop_quality_request(request_data):
    try:
        # Validate required fields
        required_fields = ['crop', 'growth_stage', 'temperature', 'humidity', 'co2_level', 'ppfd', 'ph', 'ec']
        for field in required_fields:
            if field not in request_data:
                return {"error": f"Missing required field: {field}"}
        
        # Predict quality
        result = predict_quality(request_data)
        return result
    
    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        print(error_msg)
        return {"error": error_msg}

# Main function for CLI usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Predict crop quality based on growing conditions')
    parser.add_argument('--train', action='store_true', help='Train a new model with synthetic data')
    parser.add_argument('--predict', type=str, help='JSON input for prediction')
    parser.add_argument('--file', type=str, help='Path to JSON file for prediction')
    
    args = parser.parse_args()
    
    if args.train:
        train_quality_model()
    
    if args.predict:
        try:
            data = json.loads(args.predict)
            result = predict_quality(data)
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"Error: {str(e)}")
    
    if args.file:
        try:
            with open(args.file, 'r') as f:
                data = json.load(f)
            result = predict_quality(data)
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"Error: {str(e)}")
    
    # If no arguments provided, train a model as default
    if not (args.train or args.predict or args.file):
        print("No arguments provided. Training a new model...")
        train_quality_model()