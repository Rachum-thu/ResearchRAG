#!/usr/bin/env python3
"""
Convert HippoRAG 2wikimultihopqa dataset to UltraRAG format
"""

import json
import os
from pathlib import Path


def convert_questions(input_file, output_file):
    """Convert question data to UltraRAG format"""
    print(f"Converting questions from {input_file} to {output_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    converted_data = []
    for idx, item in enumerate(data):
        converted_item = {
            "id": idx,
            "question": item["question"],
            "golden_answers": [item["answer"]] if "answer" in item else [],
            "meta_data": {
                "relevant_doc_ids": item.get("supporting_facts_index", [])
            }
        }
        converted_data.append(converted_item)
    
    # Write as JSONL format
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in converted_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"Converted {len(converted_data)} questions")
    return len(converted_data)


def convert_corpus(input_file, output_file):
    """Convert corpus data to UltraRAG format"""
    print(f"Converting corpus from {input_file} to {output_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    converted_data = []
    for item in data:
        # Use the index field as the document ID
        doc_id = str(item["index"])
        
        # Combine title and text as contents
        title = item.get("title", "")
        text = item.get("text", "")
        
        if title and text:
            contents = f"{title}: {text}"
        else:
            contents = text or title
        
        converted_item = {
            "id": doc_id,
            "contents": contents
        }
        converted_data.append(converted_item)
    
    # Write as JSONL format
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in converted_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"Converted {len(converted_data)} documents")
    return len(converted_data)


def main():
    # Set file paths
    base_dir = Path(__file__).parent
    
    # Input files
    questions_input = base_dir / "2wikimultihopqa_with_index.json"
    corpus_input = base_dir / "2wikimultihopqa_corpus_with_index.json"
    
    # Output files (save to /data directory)
    data_dir = base_dir.parent.parent  # Go up to /data directory
    questions_output = data_dir / "2wikimultihopqa_questions.jsonl"
    corpus_output = data_dir / "2wikimultihopqa_corpus.jsonl"
    
    # Convert files
    if questions_input.exists():
        num_questions = convert_questions(questions_input, questions_output)
    else:
        print(f"Warning: {questions_input} not found")
    
    if corpus_input.exists():
        num_docs = convert_corpus(corpus_input, corpus_output)
    else:
        print(f"Warning: {corpus_input} not found")
    
    print("\nConversion complete!")
    print(f"Question data: {questions_output}")
    print(f"Corpus data: {corpus_output}")


if __name__ == "__main__":
    main()