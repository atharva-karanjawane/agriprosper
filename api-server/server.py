from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware  # Add CORS middleware
import uvicorn
import os
import shutil
import uuid
import pickle
from pydantic import BaseModel, Field
from typing import List, Dict, Literal
from datetime import datetime
import json
from inference_sdk import InferenceHTTPClient
import cv2
import numpy as np
import pandas as pd

with open('crop_yield_model.pkl', 'rb') as f:
    model, feature_names = pickle.load(f)

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
        self.client = InferenceHTTPClient(
            api_url="https://detect.roboflow.com",
            api_key="HwwpNHzzMg7ajSNvM4NS"
        )
        
        self.output_dir = os.path.join(os.getcwd(), 'output')
        os.makedirs(self.output_dir, exist_ok=True)

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
        
        base_filename = f"{timestamp}_disease_detection"
        annotated_image_path = os.path.join(self.output_dir, f"{base_filename}_annotated.jpg")
        results_path = os.path.join(self.output_dir, f"{base_filename}_results.json")
    
        with open(results_path, 'w') as f:
            json.dump(result, f, indent=4)
            
        self.draw_boxes(image_path, result['predictions'], annotated_image_path)
        
        return {
            'success': True,
            'predictions': result['predictions'],
            'annotated_image_path': annotated_image_path,
            'results_file_path': results_path
        }


app = FastAPI(
    title="Plant Disease Detection API",
    description="API for detecting diseases in plant images and predicting crop yields",
    version="1.0.0",
    docs_url="/",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

detector = DiseaseDetector()


UPLOAD_DIR = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/predict-yield/", response_model=PredictionResponse)
async def predict_yield(request: PredictionRequest):
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
    """
    Upload a plant image to detect diseases
    """
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

if __name__ == "__main__":
    print("Plant Disease Detection API Server")
    print("Access the Swagger UI at http://localhost:8000/")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)