# Web service runner example

## Setup
Install required packages
| Package Name  | Version |
| ------------- | ------- |
| Flask         | 1.0.2   |
| gunicorn      | 19.9.0  |

## Run
Simple run
```bash
docker-compose up
```

## Test
GET `/metadata` to check required input and output
```bash
curl http://localhost:8000/metadata
```
POST `/predict` to run pipeline via http
```bash
curl -d '{"name": "Test"}' -H "Content-Type: application/json" -X POST http://localhost:8000/predict
```
