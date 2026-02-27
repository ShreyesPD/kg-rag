import logging
from typing import Dict, List, Any
from .neo4j_client import Neo4jClient
from .csv_parser import ClinicalTrialCSVParser

logger = logging.getLogger(__name__)

class ClinicalTrialGraphBuilder:
    """
    Builds Neo4j graph from parsed clinical trial data
    """
    
    def __init__(self, neo4j_client: Neo4jClient):
        self.client = neo4j_client
    
    def initialize_schema(self):
        """Create constraints and indexes for the graph schema"""
        logger.info("Initializing graph schema...")
        self.client.create_constraints()
        self.client.create_indexes()
        logger.info("Schema initialization complete")
    
    def create_clinical_trial_node(self, trial_data: Dict[str, Any]):
        """
        Create a ClinicalTrial node
        
        Args:
            trial_data: Dictionary containing trial information
        """
        query = """
        MERGE (ct:ClinicalTrial {nct_number: $nct_number})
        SET ct.title = $title,
            ct.url = $url,
            ct.acronym = $acronym,
            ct.status = $status,
            ct.brief_summary = $brief_summary,
            ct.has_results = $has_results,
            ct.sex = $sex,
            ct.age = $age,
            ct.phases = $phases,
            ct.enrollment = $enrollment,
            ct.funder_type = $funder_type,
            ct.study_type = $study_type,
            ct.study_design = $study_design,
            ct.start_date = $start_date,
            ct.primary_completion_date = $primary_completion_date,
            ct.completion_date = $completion_date,
            ct.first_posted = $first_posted,
            ct.last_update_posted = $last_update_posted
        RETURN ct
        """
        
        self.client.execute_write(query, trial_data)
    
    def create_condition_nodes(self, nct_number: str, conditions: List[str]):
        """
        Create Condition nodes and link to trial
        
        Args:
            nct_number: Clinical trial NCT number
            conditions: List of condition names
        """
        for condition in conditions:
            query = """
            MATCH (ct:ClinicalTrial {nct_number: $nct_number})
            MERGE (c:Condition {name: $condition})
            MERGE (ct)-[:STUDIES]->(c)
            """
            self.client.execute_write(query, {
                'nct_number': nct_number,
                'condition': condition
            })
    
    def create_intervention_nodes(self, nct_number: str, interventions: List[str]):
        """
        Create Intervention nodes and link to trial
        Also create TREATS relationships between interventions and conditions
        
        Args:
            nct_number: Clinical trial NCT number
            interventions: List of intervention strings (e.g., "DRUG: Zanidatamab")
        """
        for intervention_str in interventions:
            parts = intervention_str.split(':', 1)
            intervention_type = parts[0].strip() if len(parts) > 1 else 'UNKNOWN'
            intervention_name = parts[1].strip() if len(parts) > 1 else intervention_str.strip()
            
            query = """
            MATCH (ct:ClinicalTrial {nct_number: $nct_number})
            MERGE (i:Intervention {name: $intervention_name})
            SET i.type = $intervention_type
            MERGE (ct)-[:USES_INTERVENTION]->(i)
            """
            self.client.execute_write(query, {
                'nct_number': nct_number,
                'intervention_name': intervention_name,
                'intervention_type': intervention_type
            })
            
            self._create_intervention_condition_links(nct_number, intervention_name)
    
    def _create_intervention_condition_links(self, nct_number: str, intervention_name: str):
        """
        Create TREATS relationships between intervention and conditions studied in the trial
        
        Args:
            nct_number: Clinical trial NCT number
            intervention_name: Name of the intervention
        """
        query = """
        MATCH (ct:ClinicalTrial {nct_number: $nct_number})-[:STUDIES]->(c:Condition)
        MATCH (i:Intervention {name: $intervention_name})
        MERGE (i)-[:TREATS]->(c)
        """
        self.client.execute_write(query, {
            'nct_number': nct_number,
            'intervention_name': intervention_name
        })
    
    def create_sponsor_nodes(self, nct_number: str, sponsors: List[str], collaborators: List[str]):
        """
        Create Sponsor nodes and link to trial
        
        Args:
            nct_number: Clinical trial NCT number
            sponsors: List of sponsor names
            collaborators: List of collaborator names
        """
        for sponsor in sponsors:
            query = """
            MATCH (ct:ClinicalTrial {nct_number: $nct_number})
            MERGE (s:Sponsor {name: $sponsor})
            MERGE (ct)-[:SPONSORED_BY {role: 'primary'}]->(s)
            """
            self.client.execute_write(query, {
                'nct_number': nct_number,
                'sponsor': sponsor
            })
        
        for collaborator in collaborators:
            query = """
            MATCH (ct:ClinicalTrial {nct_number: $nct_number})
            MERGE (s:Sponsor {name: $collaborator})
            MERGE (ct)-[:SPONSORED_BY {role: 'collaborator'}]->(s)
            """
            self.client.execute_write(query, {
                'nct_number': nct_number,
                'sponsor': collaborator
            })
    
    def create_location_nodes(self, nct_number: str, locations: List[str]):
        """
        Create Location nodes and link to trial
        
        Args:
            nct_number: Clinical trial NCT number
            locations: List of location names
        """
        for location in locations:
            query = """
            MATCH (ct:ClinicalTrial {nct_number: $nct_number})
            MERGE (l:Location {name: $location})
            MERGE (ct)-[:CONDUCTED_AT]->(l)
            """
            self.client.execute_write(query, {
                'nct_number': nct_number,
                'location': location
            })
    
    def create_outcome_nodes(self, nct_number: str, outcomes: List[Dict[str, str]], outcome_type: str):
        """
        Create OutcomeMeasure nodes and link to trial
        
        Args:
            nct_number: Clinical trial NCT number
            outcomes: List of outcome dictionaries with description and timeframe
            outcome_type: Type of outcome (primary, secondary, other)
        """
        for outcome in outcomes:
            query = """
            MATCH (ct:ClinicalTrial {nct_number: $nct_number})
            CREATE (om:OutcomeMeasure {
                description: $description,
                timeframe: $timeframe,
                type: $outcome_type
            })
            MERGE (ct)-[:MEASURES]->(om)
            """
            self.client.execute_write(query, {
                'nct_number': nct_number,
                'description': outcome['description'],
                'timeframe': outcome['timeframe'],
                'outcome_type': outcome_type
            })
    
    def build_trial_graph(self, trial_data: Dict[str, Any]):
        """
        Build complete graph for a single clinical trial
        
        Args:
            trial_data: Parsed trial data from CSV parser
        """
        trial = trial_data['trial']
        entities = trial_data['entities']
        nct_number = trial['nct_number']
        
        logger.info(f"Building graph for trial {nct_number}")
        
        self.create_clinical_trial_node(trial)
        
        if entities['conditions']:
            self.create_condition_nodes(nct_number, entities['conditions'])
        
        if entities['interventions']:
            self.create_intervention_nodes(nct_number, entities['interventions'])
        
        if entities['sponsors'] or entities['collaborators']:
            self.create_sponsor_nodes(nct_number, entities['sponsors'], entities['collaborators'])
        
        if entities['locations']:
            self.create_location_nodes(nct_number, entities['locations'])
        
        if entities['primary_outcomes']:
            self.create_outcome_nodes(nct_number, entities['primary_outcomes'], 'primary')
        
        if entities['secondary_outcomes']:
            self.create_outcome_nodes(nct_number, entities['secondary_outcomes'], 'secondary')
        
        if entities['other_outcomes']:
            self.create_outcome_nodes(nct_number, entities['other_outcomes'], 'other')
        
        logger.info(f"Successfully built graph for trial {nct_number}")
    
    def build_from_csv(self, csv_path: str, clear_existing: bool = False):
        """
        Build complete graph from CSV file
        
        Args:
            csv_path: Path to clinical trials CSV file
            clear_existing: Whether to clear existing data first
        """
        if clear_existing:
            logger.warning("Clearing existing database...")
            self.client.clear_database()
        
        self.initialize_schema()
        
        parser = ClinicalTrialCSVParser(csv_path)
        trials = parser.parse_all_trials()
        
        logger.info(f"Building graph for {len(trials)} trials...")
        
        for idx, trial_data in enumerate(trials, 1):
            try:
                self.build_trial_graph(trial_data)
                if idx % 10 == 0:
                    logger.info(f"Progress: {idx}/{len(trials)} trials processed")
            except Exception as e:
                logger.error(f"Error building graph for trial {trial_data['trial']['nct_number']}: {str(e)}")
                continue
        
        logger.info("Graph building complete!")
        
        stats = self.client.get_database_stats()
        logger.info("Database statistics:")
        for stat in stats:
            logger.info(f"  {stat['label']}: {stat['count']} nodes")
