import pandas as pd
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class ClinicalTrialCSVParser:
    """
    Parser for clinical trial CSV data
    Extracts entities and relationships from CSV format
    """
    
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.df = None
        self._load_csv()
    
    def _load_csv(self):
        """Load CSV file into pandas DataFrame"""
        try:
            self.df = pd.read_csv(self.csv_path)
            logger.info(f"Loaded {len(self.df)} clinical trials from {self.csv_path}")
        except Exception as e:
            logger.error(f"Failed to load CSV: {str(e)}")
            raise
    
    def _parse_multi_value_field(self, value: str, delimiter: str = '|') -> List[str]:
        """
        Parse fields that contain multiple values separated by delimiter
        
        Args:
            value: String value potentially containing multiple items
            delimiter: Separator character (default: |)
            
        Returns:
            List of individual values
        """
        if pd.isna(value) or value == '':
            return []
        
        values = [v.strip() for v in str(value).split(delimiter)]
        return [v for v in values if v]
    
    def _parse_outcome_measures(self, value: str) -> List[Dict[str, str]]:
        """
        Parse outcome measures which have format: "Description, Timeframe"
        
        Args:
            value: Outcome measure string
            
        Returns:
            List of dictionaries with description and timeframe
        """
        if pd.isna(value) or value == '':
            return []
        
        outcomes = []
        measures = self._parse_multi_value_field(value, delimiter='|')
        
        for measure in measures:
            parts = measure.split(',')
            if len(parts) >= 2:
                outcomes.append({
                    'description': parts[0].strip(),
                    'timeframe': ','.join(parts[1:]).strip()
                })
            else:
                outcomes.append({
                    'description': measure.strip(),
                    'timeframe': 'Not specified'
                })
        
        return outcomes
    
    def parse_trial(self, row: pd.Series) -> Dict[str, Any]:
        """
        Parse a single clinical trial row into structured data
        
        Args:
            row: Pandas Series representing one trial
            
        Returns:
            Dictionary with trial data and related entities
        """
        trial_data = {
            'nct_number': row.get('NCT Number', ''),
            'title': row.get('Study Title', ''),
            'url': row.get('Study URL', ''),
            'acronym': row.get('Acronym', ''),
            'status': row.get('Study Status', ''),
            'brief_summary': row.get('Brief Summary', ''),
            'has_results': row.get('Study Results', '') == 'YES',
            'sex': row.get('Sex', ''),
            'age': row.get('Age', ''),
            'phases': row.get('Phases', ''),
            'enrollment': row.get('Enrollment', ''),
            'funder_type': row.get('Funder Type', ''),
            'study_type': row.get('Study Type', ''),
            'study_design': row.get('Study Design', ''),
            'start_date': row.get('Start Date', ''),
            'primary_completion_date': row.get('Primary Completion Date', ''),
            'completion_date': row.get('Completion Date', ''),
            'first_posted': row.get('First Posted', ''),
            'last_update_posted': row.get('Last Update Posted', '')
        }
        
        entities = {
            'conditions': self._parse_multi_value_field(row.get('Conditions', '')),
            'interventions': self._parse_multi_value_field(row.get('Interventions', '')),
            'sponsors': self._parse_multi_value_field(row.get('Sponsor', '')),
            'collaborators': self._parse_multi_value_field(row.get('Collaborators', '')),
            'locations': self._parse_multi_value_field(row.get('Locations', '')),
            'primary_outcomes': self._parse_outcome_measures(row.get('Primary Outcome Measures', '')),
            'secondary_outcomes': self._parse_outcome_measures(row.get('Secondary Outcome Measures', '')),
            'other_outcomes': self._parse_outcome_measures(row.get('Other Outcome Measures', ''))
        }
        
        return {
            'trial': trial_data,
            'entities': entities
        }
    
    def parse_all_trials(self) -> List[Dict[str, Any]]:
        """
        Parse all trials in the CSV
        
        Returns:
            List of parsed trial dictionaries
        """
        trials = []
        for idx, row in self.df.iterrows():
            try:
                parsed = self.parse_trial(row)
                trials.append(parsed)
            except Exception as e:
                logger.error(f"Error parsing trial at row {idx}: {str(e)}")
                continue
        
        logger.info(f"Successfully parsed {len(trials)} trials")
        return trials
    
    def get_unique_entities(self) -> Dict[str, set]:
        """
        Extract all unique entities across all trials
        
        Returns:
            Dictionary with sets of unique conditions, interventions, etc.
        """
        unique = {
            'conditions': set(),
            'interventions': set(),
            'sponsors': set(),
            'locations': set()
        }
        
        trials = self.parse_all_trials()
        for trial in trials:
            entities = trial['entities']
            unique['conditions'].update(entities['conditions'])
            unique['interventions'].update(entities['interventions'])
            unique['sponsors'].update(entities['sponsors'] + entities['collaborators'])
            unique['locations'].update(entities['locations'])
        
        return unique
