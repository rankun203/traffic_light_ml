# Smart Traffic Light

Using reinforcement learning to optimize traffic light operations to maximize throughput.

## Setup Development Environment

```bash
# clone repo
git clone https://github.com/rankun203/traffic_light_ml

# install dependencies
poetry install

# run app
poetry run python main.py

# Setup auto-reload
npx nodemon -w . -x "poetry run python main.py" -e "py toml"
```

> [!NOTE]
> You should have [Poetry](https://python-poetry.org/) and [Node.js](https://nodejs.org/) installed

