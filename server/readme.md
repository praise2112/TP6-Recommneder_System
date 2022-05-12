# Recommender System - Movie Lens Dataset
<hr/>


Dataset from [kaggle](https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset) 

## Install requirements
```shell
pip install -r requirments.txt
```

## Usage

<hr/>

### `server.py` - Flask API

### Arguments
- `--port`  Server port

### Example
```shell
python server.py --port 80
```
<br/>

<hr/>


### API Inference 

- Collaborative
    - `<api_url>/collaborative/<title>`

    - `<api_url>/collaborative/<user>?user=true`


- Content Based

  - `<api_url>/contentbased/<title>`
  

### Example
`http://127.0.0.1:80/collaborative/title/Ghost Rider`

