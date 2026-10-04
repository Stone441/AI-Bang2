"""Trusted local multi-source operator mapping; no source accounts are inferred."""
import importlib
import json
from pathlib import Path

MODULES = {'confluence': 'scripts.confluence_probe', 'jira': 'scripts.jira_query',
           'slack': 'scripts.slack_query', 'drive': 'scripts.drive_query'}


def load_reader(path, prompt_actor=None):
    path = Path(path)
    config = json.loads(path.read_text())
    if (set(config) != {'approved_synthetic_only', 'identity_mapping_reviewed', 'sources'}
            or config['approved_synthetic_only'] is not True
            or config['identity_mapping_reviewed'] is not True
            or not isinstance(config['sources'], dict)
            or not 2 <= len(config['sources']) <= 4
            or set(config['sources']) - set(MODULES)):
        raise ValueError('Reviewed synthetic multi-source mapping required')
    readers, mappings, modules = {}, {}, {}
    # Validate the whole bundle before requesting any secret or calling any API.
    for source, reference in sorted(config['sources'].items()):
        if not isinstance(reference, str) or not reference:
            raise ValueError('Local source configuration path required')
        target = path.parent / reference
        source_config = json.loads(target.read_text())
        if prompt_actor is None or prompt_actor not in source_config['delegations']:
            raise ValueError('One mapped operator required on every source')
        mappings[source] = source_config['delegations'][prompt_actor]['account_id']
        modules[source] = importlib.import_module(MODULES[source])
        readers[source] = modules[source].load_reader(target)
    if len({r.tenant for r in readers.values()}) != 1:
        raise ValueError('One tenant required across sources')
    for source, reader in sorted(readers.items()):
        if prompt_actor not in reader.delegations:
            print(f'{source.title()}: enter the credential for the reviewed operator mapping.', flush=True)
            hidden = (modules[source].hidden_delegation if source in ('confluence', 'jira')
                      else modules[source].hidden_token)
            reader.delegations[prompt_actor] = hidden(mappings[source])
    return readers
