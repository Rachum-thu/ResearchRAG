# ResearchRAG

This project is built on the [UltraRAG 2.0](https://github.com/OpenBMB/UltraRAG) framework as the deployment foundation.

## Project Structure

```
ResearchRAG/
├── src/                 # Core framework code and utilities
├── servers/             # Individual server implementations (retriever, generator, etc.)
├── examples/            # Pipeline configuration files and usage examples
├── data/                # Dataset files and corpus data
├── prompt/              # Template files for prompt generation
├── output/              # Generated outputs and results
├── logs/                # Application logs and debugging info
├── script/              # Utility scripts and automation tools
└── README.md           # This file
```

### Key Directories:
- **`servers/`**: Each subdirectory contains a complete server implementation with its own configuration
- **`examples/`**: YAML files defining different pipeline workflows (RAG, evaluation, etc.)
- **`src/`**: The UltraRAG framework core, including server base classes and client logic
- **`data/`**: Input datasets, knowledge bases, and corpus files for processing
- **`prompt/`**: Jinja2 templates for dynamic prompt generation

## Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Rachum-thu/ResearchRAG.git
cd ResearchRAG
```

### 2. Create Conda Environment
```bash
# Create a new conda environment
conda create -n ResearchRAG python=3.11 -y

# Activate the environment
conda activate ResearchRAG
```

### 3. Install uv Package Manager
```bash
pip install uv
```

### 4. Install Project Dependencies
```bash
# Install the project in editable mode with all dependencies
uv pip install -e .
```

## Development

This project uses uv as the package manager for faster dependency resolution and installation.

### Key Dependencies Include:
- OpenAI API client
- FastAPI/Starlette framework
- Pydantic data validation
- NLTK natural language processing
- Pandas data processing
- Other AI/ML related libraries

### Usage

## Testing RAG Local Retriever

To test the basic RAG functionality with local retrieval:

```bash
# Run the RAG pipeline with local retriever
ultrarag run examples/RAG_local_retrieve.yaml

# View the results with web interface
python ./script/case_study.py --data output/memory_nq_RAG_local_retrieve_<timestamp>.json --host 127.0.0.1 --port 8080 --title "RAG Case Study Viewer"
```

This will:
1. Run a complete RAG pipeline using Qwen/Qwen3-Embedding-0.6B for embeddings and GPT-4.1-mini for generation
2. Process the sample Natural Questions dataset 
3. Generate results with evaluation metrics (accuracy, F1, ROUGE scores, etc.)
4. Launch a web interface to interactively explore the results, including retrieved documents and LLM responses