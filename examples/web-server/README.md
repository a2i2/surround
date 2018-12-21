# Web service runner example

## Setup
Install `flask` (check version from project [readme](../../README.md)).
## Run
Simple run
```bash
python main.py
```

## Test
GET `/metadata` to check required input and output
```bash
curl http://localhost:5000/metadata
```
POST `/predict` to run pipeline via http
```bash
curl -d '{"name": "Test"}' -H "Content-Type: application/json" -X POST http://localhost:5000/predict
```
