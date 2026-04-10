#!/bin/bash

##############################################################################
# I2I Commit Message Creator
#
# Usage:
#   bash i2i-commit.sh <type> [options]
#
# Types:
#   proposal   — Suggest code changes to another agent
#   review     — Code review feedback
#   comment    — General feedback or observation
#   vocab      — Vocabulary change (use --subtype for NEW/UPDATE/DEPRECATE)
#   dispute    — Formal disagreement
#   resolve    — Dispute resolution
#   wiki       — Autobiography or capability update
#   dojo       — Training exercise
#   growth     — Personal development entry
#   signal     — Vocabulary capability broadcast
#   tombstone  — Pruned vocabulary announcement
#   accept     — Accept a proposal
#   reject     — Reject a proposal
#
# Examples:
#   bash i2i-commit.sh proposal --target "src/memory.py" --summary "implement LRU cache"
#   bash i2i-commit.sh review --target-agent "data-pipeline-bot" --summary "excellent work"
#   bash i2i-commit.sh vocab --subtype "NEW" --vocab-name "ml-patterns" --count 47
##############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Helper functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check arguments
if [ $# -lt 1 ]; then
    log_error "Usage: $0 <type> [options]"
    echo ""
    echo "Types: proposal, review, comment, vocab, dispute, resolve, wiki, dojo, growth, signal, tombstone, accept, reject"
    echo ""
    echo "Common options:"
    echo "  --target <path>        Target path or agent"
    echo "  --summary <text>       Commit summary"
    echo "  --body <text>          Commit body"
    echo "  --file <path>          Read message from file"
    echo "  --dry-run              Print message without committing"
    exit 1
fi

MESSAGE_TYPE="$1"
shift

# Parse arguments
TARGET=""
SUMMARY=""
BODY=""
VOCAB_SUBTYPE=""
FROM_FILE=""
DRY_RUN=false
CO_AUTHORED_BY=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --target)
            TARGET="$2"
            shift 2
            ;;
        --target-agent)
            TARGET="$2"
            shift 2
            ;;
        --summary)
            SUMMARY="$2"
            shift 2
            ;;
        --body)
            BODY="$2"
            shift 2
            ;;
        --file)
            FROM_FILE="$2"
            shift 2
            ;;
        --subtype)
            VOCAB_SUBTYPE="$2"
            shift 2
            ;;
        --vocab-name)
            VOCAB_NAME="$2"
            shift 2
            ;;
        --count)
            VOCAB_COUNT="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --co-authored-by)
            CO_AUTHORED_BY="$2"
            shift 2
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Read from file if specified
if [ -n "$FROM_FILE" ]; then
    if [ ! -f "$FROM_FILE" ]; then
        log_error "File not found: $FROM_FILE"
        exit 1
    fi
    CONTENT=$(cat "$FROM_FILE")
    SUMMARY=$(echo "$CONTENT" | head -n 1)
    BODY=$(echo "$CONTENT" | tail -n +2)
fi

# Validate required fields
if [ -z "$SUMMARY" ]; then
    log_error "Summary is required (use --summary or --file)"
    exit 1
fi

# Validate message type
case "$MESSAGE_TYPE" in
    proposal|review|comment|vocab|dispute|resolve|wiki|dojo|growth|signal|tombstone|accept|reject)
        ;;
    *)
        log_error "Invalid message type: $MESSAGE_TYPE"
        log_error "Valid types: proposal, review, comment, vocab, dispute, resolve, wiki, dojo, growth, signal, tombstone, accept, reject"
        exit 1
        ;;
esac

# Build commit message
COMMIT_MSG=""

case "$MESSAGE_TYPE" in
    vocab)
        if [ -z "$VOCAB_SUBTYPE" ]; then
            log_error "Vocab subtype required (--subtype: NEW, UPDATE, DEPRECATE)"
            exit 1
        fi
        COMMIT_MSG="[I2I:VOCab:$VOCAB_SUBTYPE] ${TARGET:-$VOCAB_NAME} — ${SUMMARY}"
        ;;
    dispute)
        COMMIT_MSG="[I2I:DISPUTE] ${TARGET:-topic} — ${SUMMARY}"
        ;;
    resolve)
        COMMIT_MSG="[I2I:RESOLVE] ${TARGET:-topic} — ${SUMMARY}"
        ;;
    *)
        # Convert to uppercase
        TYPE_UPPER=$(echo "$MESSAGE_TYPE" | tr '[:lower:]' '[:upper:]')
        COMMIT_MSG="[I2I:$TYPE_UPPER] ${TARGET:-scope} — ${SUMMARY}"
        ;;
esac

# Add body if provided
if [ -n "$BODY" ]; then
    COMMIT_MSG="$COMMIT_MSG"$'\n\n'
    COMMIT_MSG="$COMMIT_MSG$BODY"
fi

# Add co-author if provided
if [ -n "$CO_AUTHORED_BY" ]; then
    COMMIT_MSG="$COMMIT_MSG"$'\n\n'
    COMMIT_MSG="$COMMIT_MSGCo-Authored-By: $CO_AUTHORED_BY"
fi

# Print or commit
if [ "$DRY_RUN" = true ]; then
    echo "---"
    echo "$COMMIT_MSG"
    echo "---"
    log_info "Dry run - no commit created"
else
    # Create commit
    echo "$COMMIT_MSG" | git commit -F -
    log_success "Commit created successfully"

    # Show commit
    echo ""
    git log -1 --pretty=format:"%h %s"
fi
