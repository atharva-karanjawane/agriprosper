from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import shutil
import uuid
import pickle
from pydantic import BaseModel, Field
from typing import List, Dict, Literal
from datetime import datetime, timedelta
import json
import cv2
import numpy as np
import pandas as pd
import joblib 
from enum import Enum
from crop_quality import predict_quality

# Lazy loading of models
model = None
feature_names = None
quality_model = None
scaler = None

def load_yield_model():
    global model, feature_names
    if model is None:
        with open('crop_yield_model.pkl', 'rb') as f:
            model, feature_names = pickle.load(f)
    return model, feature_names

def load_quality_models():
    global quality_model, scaler
    if quality_model is None:
        quality_model = joblib.load('crop_quality_model.pkl')
    if scaler is None:
        scaler = joblib.load('quality_scaler.pkl')
    return quality_model, scaler

class StageData(BaseModel):
    temperature: float = Field(..., ge=18, le=30, description="Temperature in Celsius")
    humidity: float = Field(..., ge=40, le=80, description="Humidity percentage")
    led_r: float = Field(..., ge=0, le=100, description="Red LED intensity (0-100)")
    led_g: float = Field(..., ge=0, le=100, description="Green LED intensity (0-100)")
    led_b: float = Field(..., ge=0, le=100, description="Blue LED intensity (0-100)")

class PredictionRequest(BaseModel):
    crop: Literal['Tomato', 'Lettuce', 'Basil', 'Spinach', 'Cucumber']
    growing_system: Literal['NFT', 'DWC', 'Vertical', 'Traditional']
    greenhouse_area: float = Field(..., gt=0, le=10000, description="Greenhouse area in square meters")
    germination: StageData
    vegetative: StageData
    flowering: StageData
    fruiting: StageData

class PredictionResponse(BaseModel):
    total_yield: float
    yield_per_plant: float
    total_plants: int
    plants_per_m2: float
    greenhouse_area: float
    growing_system: str
    crop: str
    units: dict = {
        "total_yield": "grams",
        "yield_per_plant": "grams/plant",
        "plants_per_m2": "plants/m²",
        "greenhouse_area": "m²"
    }

class DiseaseDetector:
    def __init__(self):
        # Lazily initialize the client only when needed
        self._client = None
        
        self.output_dir = os.path.join(os.getcwd(), 'output')
        os.makedirs(self.output_dir, exist_ok=True)

    @property
    def client(self):
        # Lazy initialization of the client
        if self._client is None:
            from inference_sdk import InferenceHTTPClient
            self._client = InferenceHTTPClient(
                api_url="https://detect.roboflow.com",
                api_key="HwwpNHzzMg7ajSNvM4NS"
            )
        return self._client

    def draw_boxes(self, image_path, predictions, output_path):
        image = cv2.imread(image_path)
        for prediction in predictions:
            x = prediction['x']
            y = prediction['y']
            width = prediction['width']
            height = prediction['height']
        
            x1 = int(x - width/2)
            y1 = int(y - height/2)
            x2 = int(x + width/2)
            y2 = int(y + height/2)
            
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            label = f"{prediction['class']} ({prediction['confidence']:.2f})"
            cv2.putText(image, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        cv2.imwrite(output_path, image)
        return output_path

    def detect_diseases(self, image_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        result = self.client.infer(
            image_path,
            model_id="plant-diseases-c2yf6-mvmnh/1"
        )

        # Create relative paths for files
        base_filename = f"{timestamp}_disease_detection"
        annotated_image_name = f"{base_filename}_annotated.jpg"
        results_json_name = f"{base_filename}_results.json"

        annotated_image_path = os.path.join(self.output_dir, annotated_image_name)
        results_path = os.path.join(self.output_dir, results_json_name)

        with open(results_path, 'w') as f:
            json.dump(result, f, indent=4)

        self.draw_boxes(image_path, result['predictions'], annotated_image_path)

        # Return paths relative to the static directory
        return {
            'success': True,
            'predictions': result['predictions'],
            'annotated_image_path': f"/static/{annotated_image_name}",
            'results_file_path': f"/static/{results_json_name}"
        }

class MaintenanceData(BaseModel):
    equipment_age: float = Field(..., ge=0, description="Age of equipment in years")
    temperature: float = Field(..., description="Operating temperature")
    vibration_level: float = Field(..., ge=0, le=100, description="Vibration level (0-100)")
    power_consumption: float = Field(..., ge=0, description="Power consumption in kW")
    humidity_exposure: float = Field(..., ge=0, le=100, description="Humidity exposure level")
    usage_hours: float = Field(..., ge=0, description="Hours of operation")
    last_maintenance: float = Field(..., ge=0, description="Days since last maintenance")

class MaintenancePrediction(BaseModel):
    risk_level: str
    maintenance_needed: bool
    recommended_date: str
    issues: List[str]
    health_score: float

class QualityPredictionInput(BaseModel):
    crop: str = Field(..., description="Crop type (e.g., TOMATO, LETTUCE, CUCUMBER, BASIL, SPINACH)")
    growth_stage: str = Field(..., description="Growth stage (e.g., GERMINATION, VEGETATIVE, FLOWERING, FRUITING)")
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., description="Relative humidity percentage")
    co2_level: float = Field(..., description="CO2 level in ppm")
    ppfd: float = Field(..., description="Photosynthetic Photon Flux Density in μmol/m²/s")
    ph: float = Field(..., description="pH level of nutrient solution")
    ec: float = Field(..., description="Electrical Conductivity in mS/cm")
    leaf_color_index: float = Field(..., description="Leaf color index (0-1)")
    stem_thickness: float = Field(..., description="Stem thickness in mm")
    plant_height: float = Field(..., description="Plant height in cm")
    days_since_planting: int = Field(..., description="Days since planting")
    nitrogen_level: float = Field(..., description="Nitrogen level (0-1)")
    phosphorus_level: float = Field(..., description="Phosphorus level (0-1)")
    potassium_level: float = Field(..., description="Potassium level (0-1)")
    water_tds: float = Field(..., description="Water Total Dissolved Solids in ppm")

class QualityPredictionOutput(BaseModel):
    quality_score: float = Field(..., description="Quality score (0-10)")
    quality_category: str = Field(..., description="Quality category (Poor, Fair, Good, Very Good, Excellent)")
    recommendations: List[str] = Field(..., description="List of recommendations to improve quality")


app = FastAPI(
    title="Agri Prosper AI Server",
    description="API for detecting diseases in plant images and predicting crop yields",
    version="1.0.0",
    docs_url="/",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  
)

detector = DiseaseDetector()

# Register directories after creating them if they don't exist
UPLOAD_DIR = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="output"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.post("/api/predict-yield/", response_model=PredictionResponse)
async def predict_yield(request: PredictionRequest):
    # Load model only when needed
    model, feature_names = load_yield_model()
    
    plant_density = {
        'NFT': {
            'Tomato': 2, 'Lettuce': 16, 'Basil': 20,
            'Spinach': 25, 'Cucumber': 2.5
        },
        'DWC': {
            'Tomato': 1.5, 'Lettuce': 20, 'Basil': 25,
            'Spinach': 30, 'Cucumber': 2
        },
        'Vertical': {
            'Tomato': 4, 'Lettuce': 40, 'Basil': 50,
            'Spinach': 60, 'Cucumber': 4
        },
        'Traditional': {
            'Tomato': 1.5, 'Lettuce': 12, 'Basil': 16,
            'Spinach': 20, 'Cucumber': 1.8
        }
    }

    plants_per_m2 = plant_density[request.growing_system][request.crop]
    total_plants = int(request.greenhouse_area * plants_per_m2)

    features = {
        'greenhouse_area': request.greenhouse_area,
        'plants_per_m2': plants_per_m2,
        'total_plants': total_plants,
        'germination_temp': request.germination.temperature,
        'germination_humidity': request.germination.humidity,
        'germination_led_r': request.germination.led_r,
        'germination_led_g': request.germination.led_g,
        'germination_led_b': request.germination.led_b,
        'vegetative_temp': request.vegetative.temperature,
        'vegetative_humidity': request.vegetative.humidity,
        'vegetative_led_r': request.vegetative.led_r,
        'vegetative_led_g': request.vegetative.led_g,
        'vegetative_led_b': request.vegetative.led_b,
        'flowering_temp': request.flowering.temperature,
        'flowering_humidity': request.flowering.humidity,
        'flowering_led_r': request.flowering.led_r,
        'flowering_led_g': request.flowering.led_g,
        'flowering_led_b': request.flowering.led_b,
        'fruiting_temp': request.fruiting.temperature,
        'fruiting_humidity': request.fruiting.humidity,
        'fruiting_led_r': request.fruiting.led_r,
        'fruiting_led_g': request.fruiting.led_g,
        'fruiting_led_b': request.fruiting.led_b,
    }

    
    crops = ['Tomato', 'Lettuce', 'Basil', 'Spinach', 'Cucumber']
    for crop_name in crops:
        features[f'crop_{crop_name}'] = 1 if request.crop == crop_name else 0

    
    systems = ['NFT', 'DWC', 'Traditional', 'Vertical']
    for system in systems:
        features[f'growing_system_{system}'] = 1 if request.growing_system == system else 0

    input_df = pd.DataFrame([features])[feature_names]
    total_yield_prediction = model.predict(input_df)[0]
    yield_per_plant = total_yield_prediction / total_plants

    return PredictionResponse(
        total_yield=round(total_yield_prediction, 2),
        yield_per_plant=round(yield_per_plant, 2),
        total_plants=total_plants,
        plants_per_m2=plants_per_m2,
        greenhouse_area=request.greenhouse_area,
        growing_system=request.growing_system,
        crop=request.crop
    )

@app.post("/api/detect/", response_class=JSONResponse)
async def detect_disease_api(file: UploadFile = File(...)):
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = detector.detect_diseases(file_path)

    return {
        "success": True,
        "predictions": result['predictions'],
        "files": {
            "annotated_image": result['annotated_image_path'],
            "results_json": result['results_file_path']
        }
    }
    
@app.get("/debug/check-file/{filename}")
async def check_file(filename: str):
    output_path = os.path.join("output", filename)
    if os.path.exists(output_path):
        return {
            "exists": True,
            "size": os.path.getsize(output_path),
            "path": output_path
        }
    return {"exists": False}

@app.post("/api/predict-maintenance/", response_model=MaintenancePrediction)
async def predict_maintenance(data: MaintenanceData):
    # Simple rule-based system for demo
    # In production, you'd use a trained model
    health_score = 100.0
    issues = []

    # Age impact
    if data.equipment_age > 5:
        health_score -= 15
        issues.append("Equipment age above recommended")

    # Temperature impact
    if data.temperature > 35:
        health_score -= 10
        issues.append("High operating temperature")

    # Vibration impact
    if data.vibration_level > 70:
        health_score -= 20
        issues.append("High vibration levels")

    # Power consumption impact
    if data.power_consumption > 10:
        health_score -= 10
        issues.append("High power consumption")

    # Maintenance impact
    if data.last_maintenance > 90:
        health_score -= 15
        issues.append("Maintenance overdue")

    # Calculate risk level
    risk_level = "Low" if health_score >= 80 else "Medium" if health_score >= 60 else "High"

    # Determine if maintenance is needed
    maintenance_needed = health_score < 70

    # Calculate recommended maintenance date
    days_until_maintenance = max(0, int((70 - health_score) / 2))
    recommended_date = (datetime.now() + timedelta(days=days_until_maintenance)).strftime("%Y-%m-%d")

    return MaintenancePrediction(
        risk_level=risk_level,
        maintenance_needed=maintenance_needed,
        recommended_date=recommended_date,
        issues=issues,
        health_score=round(health_score, 2)
    )

@app.post("/api/predict-quality", response_model=QualityPredictionOutput)
async def predict_crop_quality(input_data: QualityPredictionInput):
    """
    Predict crop quality based on provided parameters.
    
    Returns quality score, category, and recommendations for improvement.
    """
    try:
        # Load quality models only when needed
        load_quality_models()
        
        # Convert Pydantic model to dict
        input_dict = input_data.dict()
        
        # Make prediction using the imported function
        result = predict_quality(input_dict)
        # Check if there was an error
        if "error" in result and result["quality_category"] == "Error":
            raise HTTPException(status_code=400, detail=result["error"])
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("output", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    
    print("AI Predictions API Server")
    print("Access the Swagger UI at http://localhost:8000/")
    
    # Use less memory-intensive reload options
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=[os.path.join(os.getcwd(), 'api-server')])
