# Hands-on Demo

## Env
```
# Clone github repo
git clone https://github.com/camel-ai/owl.git

# Change directory into project directory
cd owl

# Create a conda environment
conda create -n owl python=3.10

# Activate the conda environment
conda activate owl

# Option 1: Install as a package (recommended)
pip install -e .

# Option 2: Install from requirements.txt
pip install -r requirements.txt --use-pep517


sudo snap install ollama

ollama pull qwen2.5:72b

ollama run qwen2.5:72b
```

## Run

```python
python demo.py
```

