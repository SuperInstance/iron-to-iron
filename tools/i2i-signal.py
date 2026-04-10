#!/usr/bin/env python3
"""
I2I Vocabulary Signaling Tool

Generates vocabulary capability signals and compatibility reports.
"""

import argparse
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


def parse_ese_file(ese_path: Path) -> Dict[str, Any]:
    """Parse a .ese vocabulary file."""
    entries = []

    with open(ese_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Simple format: concept: definition
                if ':' in line:
                    concept, definition = line.split(':', 1)
                    entries.append({
                        'concept': concept.strip(),
                        'definition': definition.strip()
                    })

    return {
        'file': ese_path.name,
        'path': str(ese_path),
        'entries': entries,
        'count': len(entries)
    }


def scan_vocabularies(repo_path: Path) -> List[Dict[str, Any]]:
    """Scan vocabularies directory for .ese files."""
    vocab_dir = repo_path / "vocabularies"

    if not vocab_dir.exists():
        return []

    vocabularies = []
    for ese_file in vocab_dir.glob("*.ese"):
        vocab_data = parse_ese_file(ese_file)
        vocabularies.append(vocab_data)

    return vocabularies


def read_tombstones(repo_path: Path) -> Dict[str, Any]:
    """Read tombstones.json file."""
    tombstone_file = repo_path / "tombstones.json"

    if not tombstone_file.exists():
        return {
            "version": "1.0",
            "generated": datetime.now().isoformat(),
            "agent": "",
            "entries": [],
            "summary": {
                "total_pruned": 0,
                "by_reason": {},
                "by_vocabulary": {}
            }
        }

    with open(tombstone_file, 'r') as f:
        return json.load(f)


def generate_signal(repo_path: Path) -> Dict[str, Any]:
    """Generate vocabulary capability signal."""
    vocabularies = scan_vocabularies(repo_path)
    tombstones = read_tombstones(repo_path)

    total_entries = sum(v['count'] for v in vocabularies)

    signal = {
        "vocabularies": [
            {
                "name": v['file'].replace('.ese', ''),
                "version": "1.0.0",  # Would be parsed from file
                "entries": v['count'],
                "last_updated": datetime.fromtimestamp(
                    v['path'].stat().st_mtime
                ).isoformat(),
                "active": True
            }
            for v in vocabularies
        ],
        "total_entries": total_entries,
        "active_vocabularies": [v['file'].replace('.ese', '') for v in vocabularies],
        "tombstones": tombstones.get('entries', []),
        "timestamp": datetime.now().isoformat(),
        "agent_id": repo_path.name
    }

    return signal


def compare_agents(agent_a_path: Path, agent_b_path: Path) -> Dict[str, Any]:
    """Compare vocabulary overlap between two agents."""
    a_vocab = scan_vocabularies(agent_a_path)
    b_vocab = scan_vocabularies(agent_b_path)

    a_names = set(v['file'].replace('.ese', '') for v in a_vocab)
    b_names = set(v['file'].replace('.ese', '') for v in b_vocab)

    shared = a_names & b_names
    only_a = a_names - b_names
    only_b = b_names - a_names

    compatibility_score = len(shared) / max(len(a_names), len(b_names), 1)

    return {
        "agent_a": str(agent_a_path),
        "agent_b": str(agent_b_path),
        "shared_vocabularies": list(shared),
        "shared_count": len(shared),
        "a_exclusive": list(only_a),
        "b_exclusive": list(only_b),
        "compatibility_score": round(compatibility_score, 2),
        "interpretation": interpret_compatibility(compatibility_score)
    }


def interpret_compatibility(score: float) -> str:
    """Interpret compatibility score."""
    if score >= 0.8:
        return "Highly compatible - easy collaboration"
    elif score >= 0.5:
        return "Compatible - some translation needed"
    elif score >= 0.2:
        return "Limited compatibility - significant friction"
    else:
        return "Incompatible - different domains"


def verify_tombstones(tombstone_file: Path) -> List[Dict[str, Any]]:
    """Verify tombstone hash integrity."""
    with open(tombstone_file, 'r') as f:
        data = json.load(f)

    suspicious = []

    for entry in data.get('entries', []):
        concept = entry.get('concept', '')
        definition = entry.get('definition', '')
        expected_hash = hashlib.sha256(
            f"{concept}:{definition}".encode()
        ).hexdigest()

        if entry.get('hash') != expected_hash:
            suspicious.append({
                'concept': concept,
                'expected_hash': expected_hash,
                'actual_hash': entry.get('hash')
            })

    return suspicious


def main():
    parser = argparse.ArgumentParser(
        description='I2I Vocabulary Signaling Tool'
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate capability signal')
    gen_parser.add_argument('--repo', type=Path, default=Path('.'),
                           help='Path to agent repository')
    gen_parser.add_argument('--output', type=str,
                           help='Output file (JSON)')

    # Compare command
    cmp_parser = subparsers.add_parser('compare', help='Compare two agents')
    cmp_parser.add_argument('--agent-a', type=Path, required=True,
                          help='Path to agent A repository')
    cmp_parser.add_argument('--agent-b', type=Path, required=True,
                          help='Path to agent B repository')

    # Verify command
    ver_parser = subparsers.add_parser('verify', help='Verify tombstones')
    ver_parser.add_argument('--tombstone-file', type=str,
                           help='Path to tombstones.json')

    args = parser.parse_args()

    if args.command == 'generate':
        signal = generate_signal(args.repo)

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(signal, f, indent=2)
            print(f"Signal written to {args.output}")
        else:
            print(json.dumps(signal, indent=2))

    elif args.command == 'compare':
        comparison = compare_agents(args.agent_a, args.agent_b)
        print(json.dumps(comparison, indent=2))

    elif args.command == 'verify':
        if not args.tombstone_file:
            tombstone_file = Path(args.repo) / 'tombstones.json'
        else:
            tombstone_file = Path(args.tombstone_file)

        suspicious = verify_tombstones(tombstone_file)

        if suspicious:
            print(f"Found {len(suspicious)} suspicious tombstone entries:")
            for entry in suspicious:
                print(f"  - {entry['concept']}")
        else:
            print("All tombstone hashes are valid")


if __name__ == '__main__':
    main()
