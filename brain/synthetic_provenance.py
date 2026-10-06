"""Server-only synthetic scope; never serialized to clients or supplied by a model.

Approval IDs come from trusted fixture/native configuration. They authorize the
data category, not employee access. Engine still checks current native access at
every model stage. Full source must retain its original synthetic marker.
"""
from .retrieval import resolve_window


class SyntheticProvenance:
    def __init__(self, approved_ids, resource_lookup):
        self.approved_ids = frozenset(approved_ids)
        self.resource_lookup = resource_lookup

    def permits(self, evidence, marker_check):
        if evidence.resource_id not in self.approved_ids:
            return False
        resource = self.resource_lookup(evidence.resource_id)
        if (not resource or resource.get('active') is not True
                or type(evidence.version) is not int or type(resource['version']) is not int
                or resource['id'] != evidence.resource_id
                or resource['version'] != evidence.version
                or resource['source'] != evidence.source
                or not marker_check(resource['text'], resource['source'])):
            return False
        try:
            locator, text = resolve_window(resource, evidence.evidence_id)
        except (KeyError, ValueError):
            return False
        return (text == evidence.text and locator == evidence.locator
                and resource['title'] == evidence.title
                and resource['source_url'] == evidence.source_url
                and resource['source_updated_at'] == evidence.source_updated_at)
