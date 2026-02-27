"""
CLI script to ingest clinical trial CSV data into Neo4j
"""

import sys
import os
import argparse
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kg_rag.neo4j_integration import Neo4jClient, ClinicalTrialGraphBuilder
from kg_rag.config_loader import config_data

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Ingest clinical trial CSV data into Neo4j')
    parser.add_argument(
        '--csv-path',
        type=str,
        default=config_data.get('CLINICAL_TRIALS_CSV_PATH'),
        help='Path to clinical trials CSV file'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear existing data before ingestion'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show database statistics only (no ingestion)'
    )
    
    args = parser.parse_args()
    
    try:
        logger.info("Connecting to Neo4j...")
        client = Neo4jClient()
        
        if args.stats:
            logger.info("Database Statistics:")
            stats = client.get_database_stats()
            for stat in stats:
                print(f"  {stat['label']}: {stat['count']} nodes")
            client.close()
            return
        
        if not args.csv_path:
            logger.error("No CSV path specified. Use --csv-path or set CLINICAL_TRIALS_CSV_PATH in config.yaml")
            return
        
        if not os.path.exists(args.csv_path):
            logger.error(f"CSV file not found: {args.csv_path}")
            return
        
        logger.info(f"Building graph from CSV: {args.csv_path}")
        builder = ClinicalTrialGraphBuilder(client)
        builder.build_from_csv(args.csv_path, clear_existing=args.clear)
        
        logger.info("\nIngestion complete! Database statistics:")
        stats = client.get_database_stats()
        for stat in stats:
            print(f"  {stat['label']}: {stat['count']} nodes")
        
        client.close()
        logger.info("Done!")
        
    except Exception as e:
        logger.error(f"Error during ingestion: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
