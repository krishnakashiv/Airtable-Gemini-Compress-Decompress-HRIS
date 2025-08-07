import sys
import argparse
import json
import logging
from services.compression_service import CompressionService
from services.decompression_service import DecompressionService
from models.screening_result import ScreeningResult

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main application entry point"""
    if len(sys.argv) < 3:
        logger.error("Usage: python main.py [compress|decompress] <applicant_id>")
        sys.exit(1)
    
    command = sys.argv[1]
    applicant_id = sys.argv[2]
    
    logger.info(f"Executing {command} command for applicant ID: {applicant_id}")
    
    if command == "compress":
        compress_applicant(applicant_id)
    elif command == "decompress":
        decompress_applicant(applicant_id)
    else:
        logger.error("Invalid command. Use 'compress' or 'decompress'")
        sys.exit(1)


def compress_applicant(applicant_id: str):
    """Compress applicant data and perform analysis"""
    try:
        compression_service = CompressionService()
        result = compression_service.compress_applicant(applicant_id)
        
        # Log results
        logger.info(f"Applicant ID: {result['applicant_id']}")
        logger.info(f"Shortlist Status: {result['shortlist_status']}")
        logger.info(f"LLM Score: {result['llm_score']}")
        logger.info(f"Screening Reason: {result['reason']}")
        
    except Exception as e:
        logger.error(f"Error compressing applicant: {e}")
        sys.exit(1)


def decompress_applicant(applicant_id: str):
    """Decompress applicant data and rebuild detailed records"""
    try:
        decompression_service = DecompressionService()
        result = decompression_service.decompress_applicant(applicant_id)
        
        # Log results
        logger.info(f"Successfully decompressed applicant ID: {result['applicant_id']}")
        logger.info(f"Personal ID: {result['personal_id']}")
        logger.info(f"Personal Info: {result['personal'].name}, {result['personal'].email}")
        logger.info(f"Work Experience entries: {len(result['experience'])}")
        logger.info(f"Salary Preferences updated")
        
    except Exception as e:
        logger.error(f"Error decompressing applicant: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
