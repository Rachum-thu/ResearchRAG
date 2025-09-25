#!/bin/bash

# Batch run script for vanilla experiments with different seeds
# Using the new --param flag to specify custom parameter files

echo "Starting batch vanilla experiments with seeds 42, 43, 44"
echo "=============================================="

# Define the base pipeline file
PIPELINE="examples/vanilla.yaml"

# Define parameter files
PARAMS=(
    "examples/parameter/vanilla/vanilla_hippo_2wiki_4omini_42.yaml"
    "examples/parameter/vanilla/vanilla_hippo_2wiki_4omini_43.yaml"
    "examples/parameter/vanilla/vanilla_hippo_2wiki_4omini_44.yaml"
)

# Run experiments sequentially
for param_file in "${PARAMS[@]}"; do
    seed=$(echo $param_file | grep -oE '[0-9]+\.yaml' | grep -oE '[0-9]+')
    echo ""
    echo "----------------------------------------"
    echo "Running experiment with seed $seed"
    echo "Parameter file: $param_file"
    echo "----------------------------------------"

    # Run ultrarag with custom parameter file
    ultrarag run $PIPELINE --param $param_file

    if [ $? -eq 0 ]; then
        echo " Seed $seed experiment completed successfully"
    else
        echo " Seed $seed experiment failed"
    fi
done

echo ""
echo "=============================================="
echo "All vanilla experiments completed!"
echo "Results saved in respective output directories"