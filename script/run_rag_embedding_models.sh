#!/bin/bash

# Batch run script for RAG experiments with different embedding models
# Using the --param flag to specify custom parameter files

echo "Starting batch RAG experiments with E5, NV-Embed-v2 and Qwen3-Embedding-8B (seeds 42, 43, 44)"
echo "=============================================="

# Define the base pipeline file
PIPELINE="examples/rag_local_embed.yaml"

# Define parameter files for all three models
PARAMS=(
    # E5-base-v2
    "examples/parameter/local_embed/hippo_2wiki_e5_4omini_42.yaml"
    "examples/parameter/local_embed/hippo_2wiki_e5_4omini_43.yaml"
    "examples/parameter/local_embed/hippo_2wiki_e5_4omini_44.yaml"

    # NV-Embed-v2
    "examples/parameter/local_embed/hippo_2wiki_nv_embed_v2_4omini_42.yaml"
    "examples/parameter/local_embed/hippo_2wiki_nv_embed_v2_4omini_43.yaml"
    "examples/parameter/local_embed/hippo_2wiki_nv_embed_v2_4omini_44.yaml"

    # Qwen3-Embedding-8B
    "examples/parameter/local_embed/hippo_2wiki_qwen3_embedding_8b_4omini_42.yaml"
    "examples/parameter/local_embed/hippo_2wiki_qwen3_embedding_8b_4omini_43.yaml"
    "examples/parameter/local_embed/hippo_2wiki_qwen3_embedding_8b_4omini_44.yaml"
)

# Run experiments sequentially
for param_file in "${PARAMS[@]}"; do
    # Extract model and seed info from filename
    if [[ $param_file == *"e5"* ]]; then
        model="E5-base-v2"
    elif [[ $param_file == *"nv_embed_v2"* ]]; then
        model="NV-Embed-v2"
    elif [[ $param_file == *"qwen3_embedding_8b"* ]]; then
        model="Qwen3-Embedding-8B"
    else
        model="Unknown"
    fi

    seed=$(echo $param_file | grep -oE '[0-9]+\.yaml' | grep -oE '[0-9]+')

    echo ""
    echo "----------------------------------------"
    echo "Running $model experiment with seed $seed"
    echo "Parameter file: $param_file"
    echo "----------------------------------------"

    # Run ultrarag with custom parameter file
    ultrarag run $PIPELINE --param $param_file

    if [ $? -eq 0 ]; then
        echo "✓ $model seed $seed experiment completed successfully"
    else
        echo "✗ $model seed $seed experiment failed"
    fi
done

echo ""
echo "=============================================="
echo "All embedding model experiments completed!"
echo "Results saved in respective output directories"