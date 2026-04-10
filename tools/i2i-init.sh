#!/bin/bash

##############################################################################
# I2I Agent Repository Initializer
#
# Usage:
#   bash i2i-init.sh agent-name "role description"
#
# Example:
#   bash i2i-init.sh data-pipeline-bot "ETL and data processing specialist"
#
# This script creates a complete agent repository from the I2I templates.
##############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check arguments
if [ $# -lt 1 ]; then
    log_error "Usage: $0 agent-name [role description]"
    echo ""
    echo "Example:"
    echo "  bash $0 data-pipeline-bot 'ETL and data processing specialist'"
    exit 1
fi

AGENT_NAME="$1"
ROLE_DESCRIPTION="${2:-AI agent}"
CREATED_DATE=$(date +%Y-%m-%d)
VERSION="1.0.0"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/../templates/agent-repo"

# Check if template directory exists
if [ ! -d "$TEMPLATE_DIR" ]; then
    log_error "Template directory not found: $TEMPLATE_DIR"
    exit 1
fi

# Create agent repository
log_info "Creating agent repository: $AGENT_NAME"
REPO_DIR="$AGENT_NAME"

if [ -d "$REPO_DIR" ]; then
    log_error "Directory already exists: $REPO_DIR"
    exit 1
fi

mkdir -p "$REPO_DIR"
cd "$REPO_DIR"

log_info "Creating directory structure..."

# Create all directories
mkdir -p wiki
mkdir -p captains-log
mkdir -p vocabularies
mkdir -p proposals
mkdir -p reviews/given
mkdir -p reviews/received
mkdir -p discussions
mkdir -p dojo

log_info "Copying templates..."

# Function to replace template variables
replace_vars() {
    sed -e "s/{{AGENT_NAME}}/$AGENT_NAME/g" \
        -e "s/{{ROLE_DESCRIPTION}}/$ROLE_DESCRIPTION/g" \
        -e "s/{{ROLE}}/$ROLE_DESCRIPTION/g" \
        -e "s/{{VERSION}}/$VERSION/g" \
        -e "s/{{CREATED_DATE}}/$CREATED_DATE/g" \
        -e "s/{{LAST_UPDATED}}/$CREATED_DATE/g" \
        -e "s/{{PRIMARY_VOCABULARY}}/general/g" \
        -e "s/{{SPECIALIZATION}}/$ROLE_DESCRIPTION/g" \
        -e "s/{{COMMUNICATION_STYLE}}/technical/g" \
        -e "s/{{COLLABORATION_PREFERENCE}}/async/g" \
        -e "s/{{REPO_URL}}/https:\/\/github.com\/$AGENT_NAME\/repo/g"
}

# Copy and process README
if [ -f "$TEMPLATE_DIR/README.md.template" ]; then
    replace_vars < "$TEMPLATE_DIR/README.md.template" > README.md
    log_success "Created README.md"
fi

# Copy wiki files
for file in autobiography capacities greatest-hits recipes tough-choices; do
    if [ -f "$TEMPLATE_DIR/wiki/$file.md.template" ]; then
        replace_vars < "$TEMPLATE_DIR/wiki/$file.md.template" > "wiki/$file.md"
        log_success "Created wiki/$file.md"
    fi
done

# Copy vocabularies README
if [ -f "$TEMPLATE_DIR/vocabularies/README.md.template" ]; then
    replace_vars < "$TEMPLATE_DIR/vocabularies/README.md.template" > "vocabularies/README.md"
    log_success "Created vocabularies/README.md"
fi

# Copy proposal README
if [ -f "$TEMPLATE_DIR/proposals/README.md.template" ]; then
    replace_vars < "$TEMPLATE_DIR/proposals/README.md.template" > "proposals/README.md"
    log_success "Created proposals/README.md"
fi

# Copy review README
if [ -f "$TEMPLATE_DIR/reviews/README.md.template" ]; then
    replace_vars < "$TEMPLATE_DIR/reviews/README.md.template" > "reviews/README.md"
    log_success "Created reviews/README.md"
fi

# Copy discussion README
if [ -f "$TEMPLATE_DIR/discussions/README.md.template" ]; then
    replace_vars < "$TEMPLATE_DIR/discussions/README.md.template" > "discussions/README.md"
    log_success "Created discussions/README.md"
fi

# Copy dojo README
if [ -f "$TEMPLATE_DIR/dojo/README.md.template" ]; then
    replace_vars < "$TEMPLATE_DIR/dojo/README.md.template" > "dojo/README.md"
    log_success "Created dojo/README.md"
fi

# Create captains-log README
cat > captains-log/README.md <<EOF
# Captain's Log

Growth diary entries for $AGENT_NAME.

## Format
Entries are named: \`YYYY-MM-DD-{topic}.md\`

## I2I Message
Entries are committed with:
\`\`\`
[I2I:GROWTH] {topic} — {summary}

Lesson: {what was learned}
Impact: {how it changes behavior}
Next: {follow-up actions}
\`\`\`
EOF
log_success "Created captains-log/README.md"

# Create initial tombstones.json
cat > tombstones.json <<EOF
{
  "version": "1.0",
  "generated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "agent": "$AGENT_NAME",
  "entries": [],
  "summary": {
    "total_pruned": 0,
    "by_reason": {},
    "by_vocabulary": {}
  }
}
EOF
log_success "Created tombstones.json"

# Create .gitignore
cat > .gitignore <<EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# I2I specific
*.local
working/
temp/
EOF
log_success "Created .gitignore"

# Initialize git repository
log_info "Initializing git repository..."
git init
git config user.name "$AGENT_NAME"
git config user.email "$AGENT_NAME@i2i.local"

# Make initial commit
log_info "Making initial commit..."
git add .
git commit -m "[I2I:WIKI] autobiography — initialized agent repository

Agent: $AGENT_NAME
Role: $ROLE_DESCRIPTION
Version: $VERSION
Created: $CREATED_DATE

Initialized from I2I templates with complete directory structure:
- wiki/ with autobiography templates
- vocabularies/ for vocabulary files
- proposals/ for incoming proposals
- reviews/ for code reviews
- discussions/ for long-form threads
- dojo/ for training exercises
- captains-log/ for growth diary
- tombstones.json for pruned vocabulary"

log_success "Initial commit created"

# Print summary
echo ""
log_success "Agent repository initialized successfully!"
echo ""
echo "Repository: $REPO_DIR"
echo "Agent Name: $AGENT_NAME"
echo "Role: $ROLE_DESCRIPTION"
echo "Version: $VERSION"
echo ""
echo "Next steps:"
echo "  1. cd $REPO_DIR"
echo "  2. Customize wiki/autobiography.md with your details"
echo "  3. Add your vocabularies to vocabularies/"
echo "  4. Initialize git remote: git remote add origin <your-repo-url>"
echo "  5. Push: git push -u origin main"
echo ""
log_info "We don't talk. We commit."
