"""P1: impact annotations require citations; uncited positive must fail."""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from probe import ROOT
from export_frontend import export, write_impact_report


class ImpactGateTests(unittest.TestCase):
    def test_current_export_has_verified_impact(self):
        snap = json.loads((ROOT / 'frontend/public/data/snapshot.json').read_text(encoding='utf-8'))
        report = write_impact_report(snap['graph']['nodes'])
        self.assertLess(report['unclear_ratio'], 1.0)
        self.assertGreaterEqual(report['counts'].get('positive', 0), 1)
        for n in snap['graph']['nodes']:
            if n.get('impact') in ('positive', 'negative'):
                self.assertTrue(n.get('impact_source_ids'), n['id'])

    def test_annotation_without_sources_rejected(self):
        path = ROOT / 'data/impact_annotations.json'
        snap_path = ROOT / 'frontend/public/data/snapshot.json'
        original = path.read_text(encoding='utf-8')
        # export_frontend writes artifacts only; still restore public if anything races.
        public_backup = snap_path.read_bytes() if snap_path.exists() else None
        try:
            data = json.loads(original)
            data['annotations'].append({
                'node_id': 'theme.ai_dc',
                'impact': 'positive',
                'rationale': 'fake',
                'source_ids': [],
            })
            path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'impact annotation missing source_ids'):
                export()
        finally:
            path.write_text(original, encoding='utf-8')
            if public_backup is not None:
                snap_path.write_bytes(public_backup)
            else:
                joinable = ROOT / 'artifacts/frontend/snapshot.p2.joinable.json'
                if joinable.exists():
                    snap_path.write_bytes(joinable.read_bytes())
                else:
                    export()


if __name__ == '__main__':
    unittest.main()
