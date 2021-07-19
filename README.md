This is the repo for sequential query analysis in NLI

1. Download data & model (we use SmBop for text2sql. For the environment settings for the model, please refer to [*my forked version*](https://github.com/xingbow/SmBop)):
```
python download_model_data.py
```

2. set up frontend
```
cd frontend
- npm install
- npm run serve
```

3. set up backend
```
cd backend
- python run-data-backend.py
```



Environment:
- vue@2.6.11
- d3v5
- python 3.7 or above
