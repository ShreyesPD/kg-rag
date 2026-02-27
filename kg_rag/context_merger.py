import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class ContextMerger:
    """
    Merges contexts from multiple sources (SPOKE and Neo4j)
    """
    
    def __init__(self, max_context_length: int = 4000):
        """
        Args:
            max_context_length: Maximum length of merged context
        """
        self.max_context_length = max_context_length
    
    def merge_contexts(self, 
                      spoke_context: Optional[str] = None, 
                      neo4j_context: Optional[str] = None,
                      prioritize: str = 'both') -> str:
        """
        Merge contexts from SPOKE and Neo4j
        
        Args:
            spoke_context: Context from SPOKE API
            neo4j_context: Context from Neo4j clinical trials
            prioritize: Which source to prioritize ('spoke', 'neo4j', 'both')
            
        Returns:
            Merged context string
        """
        contexts = []
        
        if prioritize == 'neo4j':
            if neo4j_context:
                contexts.append(("Clinical Trials Database", neo4j_context))
            if spoke_context:
                contexts.append(("SPOKE Biomedical Knowledge Graph", spoke_context))
        elif prioritize == 'spoke':
            if spoke_context:
                contexts.append(("SPOKE Biomedical Knowledge Graph", spoke_context))
            if neo4j_context:
                contexts.append(("Clinical Trials Database", neo4j_context))
        else:
            if spoke_context:
                contexts.append(("SPOKE Biomedical Knowledge Graph", spoke_context))
            if neo4j_context:
                contexts.append(("Clinical Trials Database", neo4j_context))
        
        if not contexts:
            return "No relevant context found."
        
        merged_parts = []
        total_length = 0
        
        for source_name, context in contexts:
            if total_length + len(context) > self.max_context_length:
                remaining_space = self.max_context_length - total_length
                if remaining_space > 100:
                    context = context[:remaining_space] + "..."
                else:
                    break
            
            merged_parts.append(f"[Source: {source_name}] {context}")
            total_length += len(context)
        
        merged_context = "\n\n".join(merged_parts)
        
        logger.info(f"Merged context from {len(contexts)} source(s), total length: {len(merged_context)}")
        
        return merged_context
    
    def deduplicate_information(self, context: str) -> str:
        """
        Remove duplicate sentences from context
        
        Args:
            context: Context string
            
        Returns:
            Deduplicated context
        """
        sentences = context.split('. ')
        seen = set()
        unique_sentences = []
        
        for sentence in sentences:
            sentence_normalized = sentence.lower().strip()
            if sentence_normalized and sentence_normalized not in seen:
                seen.add(sentence_normalized)
                unique_sentences.append(sentence)
        
        return '. '.join(unique_sentences)
