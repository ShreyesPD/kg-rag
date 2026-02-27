import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class Neo4jClient:
    """
    Neo4j database client for managing connections and executing queries
    """
    
    def __init__(self, uri=None, user=None, password=None, database=None):
        load_dotenv()
        
        self.uri = uri or os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = user or os.getenv('NEO4J_USER', 'neo4j')
        self.password = password or os.getenv('NEO4J_PASSWORD')
        self.database = database or os.getenv('NEO4J_DATABASE', 'neo4j')
        
        if not self.password:
            raise ValueError("Neo4j password not found. Please set NEO4J_PASSWORD in .env file")
        
        self.driver = None
        self._connect()
    
    def _connect(self):
        """Establish connection to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            self.driver.verify_connectivity()
            logger.info(f"Successfully connected to Neo4j at {self.uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise
    
    def close(self):
        """Close the database connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def execute_query(self, query, parameters=None):
        """
        Execute a Cypher query and return results
        
        Args:
            query: Cypher query string
            parameters: Dictionary of query parameters
            
        Returns:
            List of records
        """
        with self.driver.session(database=self.database) as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    
    def execute_write(self, query, parameters=None):
        """
        Execute a write transaction
        
        Args:
            query: Cypher query string
            parameters: Dictionary of query parameters
            
        Returns:
            Query result summary
        """
        with self.driver.session(database=self.database) as session:
            result = session.run(query, parameters or {})
            summary = result.consume()
            return summary
    
    def create_constraints(self):
        """Create unique constraints for the clinical trials graph schema"""
        constraints = [
            "CREATE CONSTRAINT clinical_trial_nct IF NOT EXISTS FOR (ct:ClinicalTrial) REQUIRE ct.nct_number IS UNIQUE",
            "CREATE CONSTRAINT condition_name IF NOT EXISTS FOR (c:Condition) REQUIRE c.name IS UNIQUE",
            "CREATE CONSTRAINT intervention_name IF NOT EXISTS FOR (i:Intervention) REQUIRE i.name IS UNIQUE",
            "CREATE CONSTRAINT sponsor_name IF NOT EXISTS FOR (s:Sponsor) REQUIRE s.name IS UNIQUE",
            "CREATE CONSTRAINT location_name IF NOT EXISTS FOR (l:Location) REQUIRE l.name IS UNIQUE"
        ]
        
        for constraint in constraints:
            try:
                self.execute_write(constraint)
                logger.info(f"Created constraint: {constraint}")
            except Exception as e:
                logger.warning(f"Constraint may already exist: {str(e)}")
    
    def create_indexes(self):
        """Create indexes for better query performance"""
        indexes = [
            "CREATE INDEX clinical_trial_status IF NOT EXISTS FOR (ct:ClinicalTrial) ON (ct.status)",
            "CREATE INDEX clinical_trial_phase IF NOT EXISTS FOR (ct:ClinicalTrial) ON (ct.phases)",
            "CREATE INDEX condition_name_text IF NOT EXISTS FOR (c:Condition) ON (c.name)",
            "CREATE INDEX intervention_name_text IF NOT EXISTS FOR (i:Intervention) ON (i.name)"
        ]
        
        for index in indexes:
            try:
                self.execute_write(index)
                logger.info(f"Created index: {index}")
            except Exception as e:
                logger.warning(f"Index may already exist: {str(e)}")
    
    def clear_database(self):
        """Clear all nodes and relationships (use with caution!)"""
        query = "MATCH (n) DETACH DELETE n"
        self.execute_write(query)
        logger.warning("Database cleared!")
    
    def get_database_stats(self):
        """Get statistics about the database"""
        query = """
        MATCH (n)
        RETURN labels(n) AS label, count(*) AS count
        ORDER BY count DESC
        """
        return self.execute_query(query)
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
