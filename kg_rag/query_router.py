import logging
from typing import Tuple, List
import re

logger = logging.getLogger(__name__)

class QueryRouter:
    """
    Routes queries to appropriate database(s) based on question content
    """
    
    def __init__(self, default_mode: str = 'both'):
        """
        Args:
            default_mode: Default routing mode ('spoke', 'neo4j', 'both')
        """
        self.default_mode = default_mode
        
        self.neo4j_keywords = [
            'trial', 'trials', 'clinical trial', 'study', 'studies',
            'nct', 'phase', 'intervention', 'sponsor', 'enrollment',
            'recruiting', 'completed', 'outcome', 'measure'
        ]
        
        self.spoke_keywords = [
            'gene', 'protein', 'pathway', 'mechanism', 'biological',
            'molecular', 'genetic', 'mutation', 'expression'
        ]
    
    def route_query(self, question: str, user_preference: str = None) -> str:
        """
        Determine which database(s) to query
        
        Args:
            question: User's question
            user_preference: User's explicit database preference ('spoke', 'neo4j', 'both', None)
            
        Returns:
            Database mode: 'spoke', 'neo4j', or 'both'
        """
        if user_preference and user_preference in ['spoke', 'neo4j', 'both']:
            logger.info(f"Using user preference: {user_preference}")
            return user_preference
        
        question_lower = question.lower()
        
        neo4j_score = sum(1 for kw in self.neo4j_keywords if kw in question_lower)
        spoke_score = sum(1 for kw in self.spoke_keywords if kw in question_lower)
        
        if self._contains_nct_number(question):
            logger.info("Detected NCT number - routing to Neo4j")
            return 'neo4j'
        
        if neo4j_score > spoke_score and neo4j_score > 0:
            logger.info(f"Neo4j keywords detected (score: {neo4j_score}) - routing to Neo4j")
            return 'neo4j'
        elif spoke_score > neo4j_score and spoke_score > 0:
            logger.info(f"SPOKE keywords detected (score: {spoke_score}) - routing to SPOKE")
            return 'spoke'
        else:
            logger.info(f"Using default mode: {self.default_mode}")
            return self.default_mode
    
    def _contains_nct_number(self, text: str) -> bool:
        """Check if text contains an NCT number pattern"""
        nct_pattern = r'\bNCT\d{8}\b'
        return bool(re.search(nct_pattern, text, re.IGNORECASE))
    
    def extract_entities(self, question: str) -> dict:
        """
        Extract potential entities from the question
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with extracted entities
        """
        entities = {
            'nct_numbers': [],
            'conditions': [],
            'interventions': [],
            'keywords': []
        }
        
        nct_pattern = r'\bNCT\d{8}\b'
        entities['nct_numbers'] = re.findall(nct_pattern, question, re.IGNORECASE)
        
        words = question.split()
        entities['keywords'] = [w.strip('.,?!') for w in words if len(w) > 3]
        
        return entities
