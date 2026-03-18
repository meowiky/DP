

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
```

```bash
uvicorn robot_api.main:app --reload
```

`http://127.0.0.1:8000/docs`


```bash
curl -X POST http://127.0.0.1:8000/move/cartesian \
  -H "Content-Type: application/json" \
  -d '{
    "x": 300,
    "y": 0,
    "z": 400,
    "rx": 180,
    "ry": 0,
    "rz": 0,
    "vel": 10
  }'
```
