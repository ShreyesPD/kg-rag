import yaml
import os

with open('config.yaml', 'r') as f:
    config_data = yaml.safe_load(f)
        
with open('system_prompts.yaml', 'r') as f:
    system_prompts = yaml.safe_load(f)
    
if 'GPT_CONFIG_FILE' in config_data:
    # Handle both Unix ($HOME) and Windows (%USERPROFILE%) home directory variables
    home_dir = os.environ.get('HOME') or os.environ.get('USERPROFILE')
    if home_dir and '$HOME' in config_data['GPT_CONFIG_FILE']:
        config_data['GPT_CONFIG_FILE'] = config_data['GPT_CONFIG_FILE'].replace('$HOME', home_dir)

    
__all__ = [
    'config_data',
    'system_prompts'
]