#!/usr/bin/env python3
"""
I2I Dispute Resolution Tool

Manages dispute initialization, analysis, and resolution.
"""

import argparse
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


CLAIM_TEMPLATE = """# Claim: {claim_title}

**Agent**: {agent_name}
**Confidence**: {confidence}
**Date**: {date}
**Claim ID**: {claim_id}

## Position
{position}

## Detailed Argument
{argument}

## Evidence
### Evidence 1: {title}
- **Content**: {content}
- **Source**: {source}
- **Type**: {benchmark|documentation|empirical_data|expert_opinion|logical_proof|code_example|test_result}
- **Strength**: {strong|moderate|weak}
- **Relevance**: {relevance}

### Evidence 2: {title}
{evidence_fields}

## Reasoning
{reasoning}

## Proposed Resolution
{proposed_resolution}

## Open Questions
{open_questions}
"""


def init_dispute(
    topic: str,
    claim: str,
    confidence: str,
    agent_name: str,
    repo_path: Path = Path('.')
) -> str:
    """Initialize a new dispute."""

    dispute_id = str(uuid.uuid4())
    dispute_dir = repo_path / 'disputes' / topic

    # Create dispute directory
    dispute_dir.mkdir(parents=True, exist_ok=True)

    # Generate claim ID
    claim_id = f"claim-{agent_name}-{uuid.uuid4().hex[:8]}"

    # Create claim file
    claim_file = dispute_dir / f"{claim_id}.md"

    claim_content = CLAIM_TEMPLATE.format(
        claim_title=claim,
        agent_name=agent_name,
        confidence=confidence,
        date=datetime.now().strftime('%Y-%m-%d'),
        claim_id=claim_id,
        position=claim,
        argument="",
        evidence_fields="",
        reasoning="",
        proposed_resolution="",
        open_questions=""
    )

    with open(claim_file, 'w') as f:
        f.write(claim_content)

    # Create dispute metadata
    metadata = {
        'dispute_topic': topic,
        'dispute_id': dispute_id,
        'initiated_by': agent_name,
        'initiated_date': datetime.now().isoformat(),
        'status': 'open',
        'claims': [
            {
                'claim_id': claim_id,
                'agent': agent_name,
                'position': claim,
                'confidence': confidence,
                'evidence': [],
                'reasoning': '',
                'proposed_resolution': '',
                'submitted_date': datetime.now().isoformat()
            }
        ],
        'objections': [],
        'metadata': {
            'directory': str(dispute_dir)
        }
    }

    metadata_file = dispute_dir / 'metadata.json'
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"Dispute initialized: {topic}")
    print(f"Directory: {dispute_dir}")
    print(f"Claim ID: {claim_id}")

    return str(dispute_dir)


def add_counter_claim(
    dispute_dir: Path,
    claim: str,
    confidence: str,
    agent_name: str
) -> str:
    """Add a counter-claim to an existing dispute."""

    metadata_file = dispute_dir / 'metadata.json'

    with open(metadata_file, 'r') as f:
        metadata = json.load(f)

    # Generate claim ID
    claim_id = f"claim-{agent_name}-{uuid.uuid4().hex[:8]}"

    # Create claim file
    claim_file = dispute_dir / f"{claim_id}.md"

    claim_content = CLAIM_TEMPLATE.format(
        claim_title=claim,
        agent_name=agent_name,
        confidence=confidence,
        date=datetime.now().strftime('%Y-%m-%d'),
        claim_id=claim_id,
        position=claim,
        argument="",
        evidence_fields="",
        reasoning="",
        proposed_resolution="",
        open_questions=""
    )

    with open(claim_file, 'w') as f:
        f.write(claim_content)

    # Update metadata
    metadata['claims'].append({
        'claim_id': claim_id,
        'agent': agent_name,
        'position': claim,
        'confidence': confidence,
        'evidence': [],
        'reasoning': '',
        'proposed_resolution': '',
        'submitted_date': datetime.now().isoformat()
    })

    metadata['status'] = 'in_progress'

    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"Counter-claim added: {claim_id}")

    return claim_id


def analyze_dispute(dispute_dir: Path) -> Dict[str, Any]:
    """Analyze a dispute and provide evaluation."""

    metadata_file = dispute_dir / 'metadata.json'

    with open(metadata_file, 'r') as f:
        metadata = json.load(f)

    analysis = {
        'dispute_topic': metadata['dispute_topic'],
        'dispute_id': metadata['dispute_id'],
        'initiated_by': metadata['initiated_by'],
        'status': metadata['status'],
        'number_of_claims': len(metadata['claims']),
        'number_of_objections': len(metadata.get('objections', [])),
        'claims_summary': []
    }

    for claim in metadata['claims']:
        analysis['claims_summary'].append({
            'agent': claim['agent'],
            'position': claim['position'],
            'confidence': claim['confidence'],
            'evidence_count': len(claim.get('evidence', []))
        })

    return analysis


def resolve_dispute(
    dispute_dir: Path,
    resolution: str,
    rationale: str,
    winner: str = None,
    dissenter: str = None,
    resolution_type: str = "consensus"
) -> str:
    """Resolve a dispute with agreed resolution."""

    metadata_file = dispute_dir / 'metadata.json'

    with open(metadata_file, 'r') as f:
        metadata = json.load(f)

    # Create resolution
    resolution_data = {
        'resolution_type': resolution_type,
        'winner': winner,
        'resolution': resolution,
        'rationale': rationale,
        'dissenters': [dissenter] if dissenter else [],
        'resolved_date': datetime.now().isoformat()
    }

    metadata['resolution'] = resolution_data
    metadata['status'] = 'resolved'

    # Create resolution file
    resolution_file = dispute_dir / 'resolution.md'
    resolution_content = f"""# Resolution: {metadata['dispute_topic']}

**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Resolution Type**: {resolution_type}
**Winner**: {winner or 'N/A'}
**Dissenter**: {dissenter or 'None'}

## Disputed
{metadata['dispute_topic']}

## Resolution
{resolution}

## Rationale
{rationale}

## Participants
{', '.join(set(claim['agent'] for claim in metadata['claims']))}
"""

    with open(resolution_file, 'w') as f:
        f.write(resolution_content)

    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"Dispute resolved: {metadata['dispute_topic']}")
    print(f"Resolution: {resolution}")
    print(f"Resolution file: {resolution_file}")

    return str(resolution_file)


def main():
    parser = argparse.ArgumentParser(
        description='I2I Dispute Resolution Tool'
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize a dispute')
    init_parser.add_argument('--topic', required=True, help='Dispute topic')
    init_parser.add_argument('--claim', required=True, help='Your position')
    init_parser.add_argument('--confidence', choices=['high', 'medium', 'low'],
                           default='medium', help='Confidence level')
    init_parser.add_argument('--agent', default='you', help='Your agent name')
    init_parser.add_argument('--repo', type=Path, default=Path('.'),
                           help='Repository path')

    # Counter-claim command
    counter_parser = subparsers.add_parser('counter-claim', help='Add counter-claim')
    counter_parser.add_argument('--dispute-dir', type=Path, required=True,
                              help='Dispute directory')
    counter_parser.add_argument('--claim', required=True, help='Your position')
    counter_parser.add_argument('--confidence', choices=['high', 'medium', 'low'],
                              default='medium', help='Confidence level')
    counter_parser.add_argument('--agent', default='you', help='Your agent name')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze dispute')
    analyze_parser.add_argument('--dispute-dir', type=Path, required=True,
                              help='Dispute directory')

    # Resolve command
    resolve_parser = subparsers.add_parser('resolve', help='Resolve dispute')
    resolve_parser.add_argument('--dispute-dir', type=Path, required=True,
                              help='Dispute directory')
    resolve_parser.add_argument('--resolution', required=True,
                              help='Agreed resolution')
    resolve_parser.add_argument('--rationale', required=True,
                              help='Why this resolution')
    resolve_parser.add_argument('--winner', help='Who won (optional)')
    resolve_parser.add_argument('--dissenter', help='Who dissented (optional)')
    resolve_parser.add_argument('--resolution-type',
                              choices=['consensus', 'compromise', 'arbitration', 'claim_victory'],
                              default='consensus', help='Resolution type')

    args = parser.parse_args()

    if args.command == 'init':
        init_dispute(
            topic=args.topic,
            claim=args.claim,
            confidence=args.confidence,
            agent_name=args.agent,
            repo_path=args.repo
        )

    elif args.command == 'counter-claim':
        add_counter_claim(
            dispute_dir=args.dispute_dir,
            claim=args.claim,
            confidence=args.confidence,
            agent_name=args.agent
        )

    elif args.command == 'analyze':
        analysis = analyze_dispute(args.dispute_dir)
        print(json.dumps(analysis, indent=2))

    elif args.command == 'resolve':
        resolve_dispute(
            dispute_dir=args.dispute_dir,
            resolution=args.resolution,
            rationale=args.rationale,
            winner=args.winner,
            dissenter=args.dissenter,
            resolution_type=args.resolution_type
        )


if __name__ == '__main__':
    main()
