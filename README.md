# Smart Traffic Light

Using reinforcement learning to optimize traffic light operations to maximize throughput.

## Setup Development Environment

```bash
# clone repo
git clone https://github.com/rankun203/traffic_light_ml

# install dependencies
poetry install

# run a static policy
poetry run python run_static.py

# run gym train environment
poetry run python gym_train.py

# Setup auto-reload
npx nodemon -w . -x "poetry run python run_static.py" -e "py toml"
```

> [!NOTE]
> You should have [Poetry](https://python-poetry.org/) and [Node.js](https://nodejs.org/) installed

