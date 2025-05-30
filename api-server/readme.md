# Plant Disease Detection API - README

## Overview

The Plant Disease Detection API provides the ability to detect diseases in plant images and predict crop yields. The API is structured around multiple endpoints that allow you to interact with different features such as disease detection, yield prediction, and equipment maintenance prediction.

## Version

**1.0.0**

**OAS 3.1** (OpenAPI Specification)

**Base URL:** `/openapi.json`

## Endpoints

### 1. **Predict Yield**

**Endpoint:** `/api/predict-yield/`
**Method:** POST
**Description:** This endpoint predicts the yield of a given crop based on various growing system parameters.

#### Request Body:

**Content Type:** `application/json`

```json
{
  "crop": "Tomato",
  "growing_system": "NFT",
  "greenhouse_area": 1,
  "germination": {
    "temperature": 18,
    "humidity": 40,
    "led_r": 100,
    "led_g": 100,
    "led_b": 100
  },
  "vegetative": {
    "temperature": 18,
    "humidity": 40,
    "led_r": 100,
    "led_g": 100,
    "led_b": 100
  },
  "flowering": {
    "temperature": 18,
    "humidity": 40,
    "led_r": 100,
    "led_g": 100,
    "led_b": 100
  },
  "fruiting": {
    "temperature": 18,
    "humidity": 40,
    "led_r": 100,
    "led_g": 100,
    "led_b": 100
  }
}
```

#### Response:

**Code:** 200
**Content Type:** `application/json`

```json
{
  "total_yield": 0,
  "yield_per_plant": 0,
  "total_plants": 0,
  "plants_per_m2": 0,
  "greenhouse_area": 0,
  "growing_system": "string",
  "crop": "string",
  "units": {
    "total_yield": "grams",
    "yield_per_plant": "grams/plant",
    "plants_per_m2": "plants/m²",
    "greenhouse_area": "m²"
  }
}
```

**Code:** 422
**Content Type:** `application/json`

```json
{
  "detail": [
    {
      "loc": ["string", 0],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

---

### 2. **Detect Disease**

**Endpoint:** `/api/detect/`
**Method:** POST
**Description:** This endpoint allows you to upload a plant image and detect any diseases present.

#### Request Body:

**Content Type:** `multipart/form-data`

* **file:** A plant image in binary format.

#### Response:

**Code:** 200
**Content Type:** `application/json`

```json
"string"
```

**Code:** 422
**Content Type:** `application/json`

```json
{
  "detail": [
    {
      "loc": ["string", 0],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

---

### 3. **Check File**

**Endpoint:** `/debug/check-file/{filename}`
**Method:** GET
**Description:** This endpoint checks if a specific file exists.

#### Parameters:

* **filename:** (string) The name of the file to check.

#### Response:

**Code:** 200
**Content Type:** `application/json`

```json
"string"
```

**Code:** 422
**Content Type:** `application/json`

```json
{
  "detail": [
    {
      "loc": ["string", 0],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

---

### 4. **Predict Maintenance**

**Endpoint:** `/api/predict-maintenance/`
**Method:** POST
**Description:** This endpoint predicts whether maintenance is needed for a given piece of equipment based on various parameters.

#### Request Body:

**Content Type:** `application/json`

```json
{
  "equipment_age": 0,
  "temperature": 0,
  "vibration_level": 100,
  "power_consumption": 0,
  "humidity_exposure": 100,
  "usage_hours": 0,
  "last_maintenance": 0
}
```

#### Response:

**Code:** 200
**Content Type:** `application/json`

```json
{
  "risk_level": "string",
  "maintenance_needed": true,
  "recommended_date": "string",
  "issues": [
    "string"
  ],
  "health_score": 0
}
```

**Code:** 422
**Content Type:** `application/json`

```json
{
  "detail": [
    {
      "loc": ["string", 0],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

---

## API Specifications

The API is defined according to **OAS 3.1**. You can explore the full API specification in **OpenAPI JSON format** at the following URL:

* **OpenAPI Specification:** `/openapi.json`

---

## Dependencies

This API uses the following dependencies:

* **FastAPI**: For building the API.
* **Uvicorn**: For serving the FastAPI app.
* **Werkzeug**: For security utilities.
* **Pydantic**: For data validation and typing.
* **OpenCV**: For image processing in disease detection.
* **NumPy**: For numerical computations.
* **Pandas**: For data manipulation.
* **InferenceSDK**: For machine learning inferences.

---

## Usage

To interact with the API, you can send requests using any HTTP client such as **Postman** or **cURL**. For example:

### Predict Yield Example (cURL):

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/predict-yield/' \
  -H 'Content-Type: application/json' \
  -d '{
        "crop": "Tomato",
        "growing_system": "NFT",
        "greenhouse_area": 1,
        "germination": {
          "temperature": 18,
          "humidity": 40,
          "led_r": 100,
          "led_g": 100,
          "led_b": 100
        },
        "vegetative": {
          "temperature": 18,
          "humidity": 40,
          "led_r": 100,
          "led_g": 100,
          "led_b": 100
        },
        "flowering": {
          "temperature": 18,
          "humidity": 40,
          "led_r": 100,
          "led_g": 100,
          "led_b": 100
        },
        "fruiting": {
          "temperature": 18,
          "humidity": 40,
          "led_r": 100,
          "led_g": 100,
          "led_b": 100
        }
      }'
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue or submit a pull request.