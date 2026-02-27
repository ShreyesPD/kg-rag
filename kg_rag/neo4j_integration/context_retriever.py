import logging
from typing import List, Dict, Any, Optional
from .neo4j_client import Neo4jClient

logger = logging.getLogger(__name__)

class Neo4jContextRetriever:
    """
    Retrieves context from Neo4j clinical trials graph for RAG
    """
    
    def __init__(self, neo4j_client: Neo4jClient):
        self.client = neo4j_client
    
    def search_by_condition(self, condition: str, limit: int = 5) -> str:
        """
        Search for clinical trials by condition
        
        Args:
            condition: Condition/disease name
            limit: Maximum number of trials to return
            
        Returns:
            Formatted context string
        """
        query = """
        MATCH (ct:ClinicalTrial)-[:STUDIES]->(c:Condition)
        WHERE toLower(c.name) CONTAINS toLower($condition)
        OPTIONAL MATCH (ct)-[:USES_INTERVENTION]->(i:Intervention)
        OPTIONAL MATCH (ct)-[:SPONSORED_BY]->(s:Sponsor)
        RETURN ct.nct_number AS nct,
               ct.title AS title,
               ct.status AS status,
               ct.phases AS phases,
               ct.brief_summary AS summary,
               collect(DISTINCT c.name) AS conditions,
               collect(DISTINCT i.name) AS interventions,
               collect(DISTINCT s.name) AS sponsors
        LIMIT $limit
        """
        
        results = self.client.execute_query(query, {'condition': condition, 'limit': limit})
        return self._format_trial_results(results, f"trials studying {condition}")
    
    def search_by_intervention(self, intervention: str, limit: int = 5) -> str:
        """
        Search for clinical trials by intervention/drug
        
        Args:
            intervention: Intervention/drug name
            limit: Maximum number of trials to return
            
        Returns:
            Formatted context string
        """
        query = """
        MATCH (ct:ClinicalTrial)-[:USES_INTERVENTION]->(i:Intervention)
        WHERE toLower(i.name) CONTAINS toLower($intervention)
        OPTIONAL MATCH (ct)-[:STUDIES]->(c:Condition)
        OPTIONAL MATCH (i)-[:TREATS]->(tc:Condition)
        OPTIONAL MATCH (ct)-[:SPONSORED_BY]->(s:Sponsor)
        RETURN ct.nct_number AS nct,
               ct.title AS title,
               ct.status AS status,
               ct.phases AS phases,
               ct.brief_summary AS summary,
               i.name AS intervention_name,
               i.type AS intervention_type,
               collect(DISTINCT c.name) AS conditions,
               collect(DISTINCT tc.name) AS treats_conditions,
               collect(DISTINCT s.name) AS sponsors
        LIMIT $limit
        """
        
        results = self.client.execute_query(query, {'intervention': intervention, 'limit': limit})
        return self._format_intervention_results(results, intervention)
    
    def search_by_nct_number(self, nct_number: str) -> str:
        """
        Get detailed information about a specific clinical trial
        
        Args:
            nct_number: NCT number of the trial
            
        Returns:
            Formatted context string
        """
        query = """
        MATCH (ct:ClinicalTrial {nct_number: $nct_number})
        OPTIONAL MATCH (ct)-[:STUDIES]->(c:Condition)
        OPTIONAL MATCH (ct)-[:USES_INTERVENTION]->(i:Intervention)
        OPTIONAL MATCH (ct)-[:SPONSORED_BY]->(s:Sponsor)
        OPTIONAL MATCH (ct)-[:MEASURES]->(om:OutcomeMeasure)
        OPTIONAL MATCH (ct)-[:CONDUCTED_AT]->(l:Location)
        RETURN ct,
               collect(DISTINCT c.name) AS conditions,
               collect(DISTINCT {name: i.name, type: i.type}) AS interventions,
               collect(DISTINCT s.name) AS sponsors,
               collect(DISTINCT {description: om.description, type: om.type, timeframe: om.timeframe}) AS outcomes,
               collect(DISTINCT l.name) AS locations
        """
        
        results = self.client.execute_query(query, {'nct_number': nct_number})
        return self._format_detailed_trial(results)
    
    def search_by_keywords(self, keywords: List[str], limit: int = 5) -> str:
        """
        Search trials by multiple keywords
        
        Args:
            keywords: List of keywords to search
            limit: Maximum number of trials to return
            
        Returns:
            Formatted context string
        """
        keyword_pattern = '|'.join([f'(?i).*{kw}.*' for kw in keywords])
        
        query = """
        MATCH (ct:ClinicalTrial)
        WHERE ct.title =~ $pattern OR ct.brief_summary =~ $pattern
        OPTIONAL MATCH (ct)-[:STUDIES]->(c:Condition)
        OPTIONAL MATCH (ct)-[:USES_INTERVENTION]->(i:Intervention)
        RETURN ct.nct_number AS nct,
               ct.title AS title,
               ct.status AS status,
               ct.brief_summary AS summary,
               collect(DISTINCT c.name) AS conditions,
               collect(DISTINCT i.name) AS interventions
        LIMIT $limit
        """
        
        results = self.client.execute_query(query, {'pattern': keyword_pattern, 'limit': limit})
        return self._format_trial_results(results, f"trials matching keywords: {', '.join(keywords)}")
    
    def get_intervention_condition_relationships(self, intervention: str) -> str:
        """
        Get all conditions that an intervention treats
        
        Args:
            intervention: Intervention/drug name
            
        Returns:
            Formatted context string
        """
        query = """
        MATCH (i:Intervention)-[:TREATS]->(c:Condition)
        WHERE toLower(i.name) CONTAINS toLower($intervention)
        RETURN i.name AS intervention,
               i.type AS intervention_type,
               collect(DISTINCT c.name) AS treats_conditions
        """
        
        results = self.client.execute_query(query, {'intervention': intervention})
        
        if not results:
            return f"No treatment relationships found for intervention: {intervention}"
        
        context_parts = []
        for result in results:
            intervention_name = result['intervention']
            intervention_type = result.get('intervention_type', 'Unknown')
            conditions = result['treats_conditions']
            
            if conditions:
                context_parts.append(
                    f"{intervention_name} (type: {intervention_type}) is used to treat: {', '.join(conditions)}."
                )
        
        return ' '.join(context_parts)
    
    def _format_trial_results(self, results: List[Dict], context_label: str) -> str:
        """Format trial results into context string"""
        if not results:
            return f"No {context_label} found in the clinical trials database."
        
        context_parts = [f"Found {len(results)} {context_label}:"]
        
        for result in results:
            nct = result.get('nct', 'Unknown')
            title = result.get('title', 'No title')
            status = result.get('status', 'Unknown status')
            phases = result.get('phases', 'Unknown phase')
            conditions = result.get('conditions', [])
            interventions = result.get('interventions', [])
            
            trial_context = f"Clinical Trial {nct}: {title}. Status: {status}, Phase: {phases}."
            
            if conditions:
                trial_context += f" Studies conditions: {', '.join(conditions)}."
            
            if interventions:
                trial_context += f" Uses interventions: {', '.join(interventions)}."
            
            if result.get('summary'):
                trial_context += f" Summary: {result['summary'][:200]}..."
            
            context_parts.append(trial_context)
        
        return ' '.join(context_parts)
    
    def _format_intervention_results(self, results: List[Dict], intervention: str) -> str:
        """Format intervention-specific results"""
        if not results:
            return f"No clinical trials found using intervention: {intervention}"
        
        context_parts = [f"Found {len(results)} trials using {intervention}:"]
        
        for result in results:
            nct = result.get('nct', 'Unknown')
            title = result.get('title', 'No title')
            intervention_name = result.get('intervention_name', intervention)
            intervention_type = result.get('intervention_type', 'Unknown')
            conditions = result.get('conditions', [])
            treats_conditions = result.get('treats_conditions', [])
            
            trial_context = f"Trial {nct}: {title}. Uses {intervention_name} (type: {intervention_type})."
            
            if conditions:
                trial_context += f" Studies: {', '.join(conditions)}."
            
            if treats_conditions:
                trial_context += f" This intervention treats: {', '.join(treats_conditions)}."
            
            context_parts.append(trial_context)
        
        return ' '.join(context_parts)
    
    def _format_detailed_trial(self, results: List[Dict]) -> str:
        """Format detailed trial information"""
        if not results or not results[0].get('ct'):
            return "Clinical trial not found."
        
        result = results[0]
        ct = result['ct']
        
        context = f"Clinical Trial {ct['nct_number']}: {ct['title']}. "
        context += f"Status: {ct['status']}, Phase: {ct.get('phases', 'Unknown')}. "
        
        if ct.get('brief_summary'):
            context += f"Summary: {ct['brief_summary']} "
        
        if result.get('conditions'):
            context += f"Studies conditions: {', '.join(result['conditions'])}. "
        
        if result.get('interventions'):
            interventions = [f"{i['name']} ({i['type']})" for i in result['interventions']]
            context += f"Interventions: {', '.join(interventions)}. "
        
        if result.get('sponsors'):
            context += f"Sponsored by: {', '.join(result['sponsors'])}. "
        
        if result.get('outcomes'):
            primary_outcomes = [o['description'] for o in result['outcomes'] if o['type'] == 'primary']
            if primary_outcomes:
                context += f"Primary outcomes: {', '.join(primary_outcomes)}. "
        
        return context
