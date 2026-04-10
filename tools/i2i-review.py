#!/usr/bin/env python3
"""
I2I Code Review Tool

Generates and parses structured code reviews.
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


# Review template
REVIEW_TEMPLATE = """# Code Review: {target_agent}

---
**Date**: {date}
**Repository**: {repository}
**Branch**: {branch}
**Commit**: {commit}
**Reviewer**: {reviewer}
**Review Scope**: {scope}
**Files Reviewed**: {files_reviewed}
**Lines of Code**: {lines_of_code}
---

## Executive Summary
{executive_summary}

## Strengths
{strengths}

## Suggested Improvements
{suggested_improvements}

## Blind Spots
{blind_spots}

## Synergy Opportunities
{synergy_opportunities}

## Detailed Observations
{detailed_observations}

## Testing & Verification
- **Tests reviewed?**: {tests_reviewed}
- **Test coverage**: {test_coverage}
- **Edge cases considered?**: {edge_cases}
- **Performance implications?**: {performance}
- **Security concerns?**: {security}

## What I Learned
{what_i_learned}

## Conclusion
{conclusion}

**Recommendation**: {recommendation}
**Rating**: {rating}
**Blocking Issues**: {blocking_issues}

## Next Steps
{next_steps}

---

**This review was committed with I2I protocol:**

```
[I2I:REVIEW] {target_agent} — {summary}

**Strengths**
{strengths_summary}

**Suggested Improvements**
{suggested_improvements_summary}

**Blind Spots**
{blind_spots_summary}

**Synergy Opportunities**
{synergy_summary}
```
"""


def create_review_template(
    target_agent: str,
    repository: str,
    branch: str,
    commit: str,
    reviewer: str,
    scope: str = "general",
    output_file: str = None
) -> str:
    """Generate a review template."""

    review_data = {
        'target_agent': target_agent,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'repository': repository,
        'branch': branch,
        'commit': commit,
        'reviewer': reviewer,
        'scope': scope,
        'files_reviewed': 0,
        'lines_of_code': 0,
        'executive_summary': '{2-3 sentence overview of the review}',
        'strengths': '### {Category 1}\n- {specific strength with example}\n- **Impact**: {why this matters}',
        'suggested_improvements': '### {Category} (Priority: high|medium|low)\n**Issue**: {what could be improved}\n**Suggestion**: {specific recommendation}',
        'blind_spots': '### {Category}\n**Concern**: {potential issue}\n**Confidence**: {high|medium|low}',
        'synergy_opportunities': '- **{collaboration idea}**: {description}',
        'detailed_observations': '{Additional specific feedback}',
        'tests_reviewed': '{yes|no|partial}',
        'test_coverage': '{percentage}',
        'edge_cases': '{list}',
        'performance': '{description}',
        'security': '{description}',
        'what_i_learned': '- {lesson 1}\n- {lesson 2}',
        'conclusion': '{Overall assessment}',
        'recommendation': '{merge|needs_work|reject}',
        'rating': '{excellent|good|acceptable|needs_improvement}',
        'blocking_issues': '{list any issues}',
        'next_steps': '1. {action 1}\n2. {action 2}',
        'summary': '{Brief summary}',
        'strengths_summary': '- {strength 1}',
        'suggested_improvements_summary': '- {improvement 1}',
        'blind_spots_summary': '- {potential issue}',
        'synergy_summary': '- {collaboration}'
    }

    review = REVIEW_TEMPLATE.format(**review_data)

    if output_file:
        with open(output_file, 'w') as f:
            f.write(review)
        print(f"Review template written to {output_file}")
    else:
        print(review)

    return review


def parse_review(review_file: Path) -> Dict[str, Any]:
    """Parse a review file into structured data."""
    with open(review_file, 'r') as f:
        content = f.read()

    # Simple parsing (in production, use proper Markdown parser)
    lines = content.split('\n')

    review_data = {
        'target_agent': '',
        'date': '',
        'repository': '',
        'branch': '',
        'commit': '',
        'reviewer': '',
        'strengths': [],
        'suggested_improvements': [],
        'blind_spots': [],
        'synergy_opportunities': []
    }

    # Extract metadata from frontmatter
    in_frontmatter = False
    for line in lines:
        if line.strip() == '---':
            in_frontmatter = not in_frontmatter
            continue

        if in_frontmatter:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_').replace('*', '')
                value = value.strip()
                review_data[key] = value

    return review_data


def validate_review(review_file: Path) -> List[str]:
    """Validate a review against I2I format."""
    errors = []

    with open(review_file, 'r') as f:
        content = f.read()

    # Check required sections
    required_sections = [
        '## Executive Summary',
        '## Strengths',
        '## Suggested Improvements',
        '## Blind Spots',
        '## Synergy Opportunities',
        '## Conclusion'
    ]

    for section in required_sections:
        if section not in content:
            errors.append(f"Missing section: {section}")

    # Check frontmatter
    if '---' not in content:
        errors.append("Missing frontmatter markers (---)")

    # Check I2I protocol mention
    if '[I2I:REVIEW]' not in content:
        errors.append("Missing I2I protocol message at end")

    return errors


def analyze_code(repo_path: Path, branch: str) -> Dict[str, Any]:
    """Analyze code for review (placeholder)."""
    # In production, this would:
    # - Checkout branch
    # - Run static analysis
    # - Check test coverage
    # - Scan for security issues

    return {
        'files_analyzed': 0,
        'lines_of_code': 0,
        'test_coverage': 0,
        'security_issues': [],
        'performance_issues': []
    }


def main():
    parser = argparse.ArgumentParser(
        description='I2I Code Review Tool'
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Template command
    tpl_parser = subparsers.add_parser('template', help='Generate review template')
    tpl_parser.add_argument('--target-agent', required=True, help='Agent being reviewed')
    tpl_parser.add_argument('--repo', required=True, help='Repository URL')
    tpl_parser.add_argument('--branch', default='main', help='Branch name')
    tpl_parser.add_argument('--commit', help='Commit hash')
    tpl_parser.add_argument('--reviewer', default='you', help='Reviewer name')
    tpl_parser.add_argument('--scope', default='general', help='Review scope')
    tpl_parser.add_argument('--output', help='Output file')

    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse review file')
    parse_parser.add_argument('--review-file', required=True, help='Review file to parse')

    # Validate command
    val_parser = subparsers.add_parser('validate', help='Validate review format')
    val_parser.add_argument('--review-file', required=True, help='Review file to validate')

    args = parser.parse_args()

    if args.command == 'template':
        create_review_template(
            target_agent=args.target_agent,
            repository=args.repo,
            branch=args.branch,
            commit=args.commit or 'HEAD',
            reviewer=args.reviewer,
            scope=args.scope,
            output_file=args.output
        )

    elif args.command == 'parse':
        review_data = parse_review(Path(args.review_file))
        print(json.dumps(review_data, indent=2))

    elif args.command == 'validate':
        errors = validate_review(Path(args.review_file))

        if errors:
            print(f"Validation failed with {len(errors)} errors:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("Review validation passed!")


if __name__ == '__main__':
    main()
