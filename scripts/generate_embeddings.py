#!/usr/bin/env python3
"""
Batch embedding generation script for Day 2 deliverable.
Processes the entire complaint dataset and generates embeddings.
"""
import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.services.embedding_service import get_embedding_service
from app.config import INPUT_CSV, OUTPUT_CSV, DATA_DIR
from app.utils.logger import get_logger

logger = get_logger(__name__)

def ensure_data_directory():
    """Ensure data directory exists"""
    os.makedirs(DATA_DIR, exist_ok=True)
    logger.info(f"Data directory: {DATA_DIR}")

def load_complaints_data(input_path: str) -> pd.DataFrame:
    """
    Load the multilingual complaints dataset.
    
    Args:
        input_path: Path to CSV file
        
    Returns:
        DataFrame with complaint data
    """
    try:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        df = pd.read_csv(input_path)
        logger.info(f"Loaded dataset: {len(df)} complaints")
        logger.info(f"Columns: {list(df.columns)}")
        
        # Ensure we have a 'text' column
        if 'text' not in df.columns:
            # Try to find text column with different names
            text_columns = [col for col in df.columns if 'text' in col.lower() or 'complaint' in col.lower()]
            if text_columns:
                df = df.rename(columns={text_columns[0]: 'text'})
                logger.info(f"Renamed column '{text_columns[0]}' to 'text'")
            else:
                raise ValueError("No text column found in dataset")
        
        # Sample preview
        logger.info("\nSample complaints:")
        for i, text in enumerate(df['text'].head(3)):
            logger.info(f"{i+1}. {text[:100]}...")
        
        return df
        
    except Exception as e:
        logger.error(f"Failed to load data: {str(e)}")
        raise

def generate_embeddings(df: pd.DataFrame, batch_size: int = 32) -> pd.DataFrame:
    """
    Generate embeddings for all complaints.
    
    Args:
        df: DataFrame with complaint texts
        batch_size: Batch size for processing
        
    Returns:
        DataFrame with added 'embedding' column
    """
    try:
        # Initialize service
        service = get_embedding_service()
        info = service.get_embedding_info()
        
        logger.info(f"\nStarting embedding generation...")
        logger.info(f"Model: {info['model']}")
        logger.info(f"Dimension: {info['dimension']}")
        logger.info(f"Batch size: {batch_size}")
        
        # Extract texts
        texts = df['text'].fillna('').astype(str).tolist()
        
        # Generate embeddings in batches with progress bar
        all_embeddings = []
        
        for i in tqdm(range(0, len(texts), batch_size), 
                     desc="Generating embeddings",
                     unit="batch"):
            batch_texts = texts[i:i+batch_size]
            
            # Process batch
            embeddings = service.generate_embeddings_batch(
                batch_texts,
                normalize_hinglish=True,
                batch_size=batch_size
            )
            
            all_embeddings.extend(embeddings)
        
        # Add embeddings to dataframe
        df['embedding'] = all_embeddings
        
        # Validate embeddings
        valid_count = sum(service.validate_embedding(emb) for emb in all_embeddings)
        logger.info(f"\nEmbedding generation complete!")
        logger.info(f"Total complaints: {len(df)}")
        logger.info(f"Valid embeddings: {valid_count}/{len(df)}")
        
        return df
        
    except Exception as e:
        logger.error(f"Embedding generation failed: {str(e)}")
        raise

def save_embeddings(df: pd.DataFrame, output_path: str):
    """
    Save embeddings to file.
    
    Args:
        df: DataFrame with embeddings
        output_path: Output file path
    """
    try:
        # For CSV, embeddings will be saved as string representations
        df.to_csv(output_path, index=False)
        
        logger.info(f"\nSaved embeddings to: {output_path}")
        logger.info(f"File size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")
        
        # Show sample of saved data
        sample_df = pd.read_csv(output_path)
        logger.info(f"\nSample saved data:")
        logger.info(f"Columns: {list(sample_df.columns)}")
        
        if 'embedding' in sample_df.columns:
            sample_embedding = eval(sample_df['embedding'].iloc[0]) if isinstance(sample_df['embedding'].iloc[0], str) else sample_df['embedding'].iloc[0]
            logger.info(f"First embedding (first 5 values): {sample_embedding[:5]}")
            logger.info(f"Embedding length: {len(sample_embedding)}")
        
    except Exception as e:
        logger.error(f"Failed to save embeddings: {str(e)}")
        raise

def main():
    """Main execution function"""
    try:
        logger.info("=" * 60)
        logger.info("DAY 2: BATCH EMBEDDING GENERATION")
        logger.info("=" * 60)
        
        # Step 1: Ensure directories
        ensure_data_directory()
        
        # Step 2: Load data
        df = load_complaints_data(INPUT_CSV)
        
        # Step 3: Generate embeddings
        df_with_embeddings = generate_embeddings(df, batch_size=32)
        
        # Step 4: Save results
        save_embeddings(df_with_embeddings, OUTPUT_CSV)
        
        # Step 5: Summary
        logger.info("\n" + "=" * 60)
        logger.info("DAY 2 COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"Input file: {INPUT_CSV}")
        logger.info(f"Output file: {OUTPUT_CSV}")
        logger.info(f"Total complaints processed: {len(df_with_embeddings)}")
        logger.info("\nNext steps:")
        logger.info("1. Check the output CSV file")
        logger.info("2. Start the AI service: python -m app.main")
        logger.info("3. Access API docs at http://localhost:8000/docs")
        
    except FileNotFoundError as e:
        logger.error(f"Data file error: {str(e)}")
        logger.info("\nPlease ensure your dataset is at:")
        logger.info(f"  {INPUT_CSV}")
        logger.info("\nExpected columns should include 'text' with complaint content")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()