# Orchestrator Toolkit - Quick Commands
# Usage: make plan TITLE="your title here"
#        make spec PLAN=P-XXXX TITLE="your spec title"
#        make exec SPEC=S-XXXX
#        make new TEXT="any otk command"

.PHONY: help plan spec exec new

# Default target: show help
help:
	@echo "Orchestrator Toolkit - Quick Commands"
	@echo ""
	@echo "Usage:"
	@echo "  make plan TITLE=\"your plan title\"        - Create a new plan"
	@echo "  make spec PLAN=P-XXXX TITLE=\"spec title\" - Create a spec for a plan"
	@echo "  make exec SPEC=S-XXXX                    - Execute a spec"
	@echo "  make new TEXT=\"any otk command\"          - Run any otk-new command"
	@echo ""
	@echo "Examples:"
	@echo "  make plan TITLE=\"Implement user authentication\""
	@echo "  make spec PLAN=P-0001 TITLE=\"Database schema design\""
	@echo "  make exec SPEC=S-0001"
	@echo "  make new TEXT=\"task 'Fix login bug'\""

plan:
	@if [ -z "$(TITLE)" ]; then \
		echo "Error: TITLE is required"; \
		echo "Usage: make plan TITLE=\"your plan title\""; \
		exit 1; \
	fi
	@otk-new "plan $(TITLE)"

spec:
	@if [ -z "$(PLAN)" ] || [ -z "$(TITLE)" ]; then \
		echo "Error: PLAN and TITLE are required"; \
		echo "Usage: make spec PLAN=P-XXXX TITLE=\"your spec title\""; \
		exit 1; \
	fi
	@otk-new "spec for $(PLAN) $(TITLE)"

exec:
	@if [ -z "$(SPEC)" ]; then \
		echo "Error: SPEC is required"; \
		echo "Usage: make exec SPEC=S-XXXX"; \
		exit 1; \
	fi
	@otk-new "execute $(SPEC)"

new:
	@if [ -z "$(TEXT)" ]; then \
		echo "Error: TEXT is required"; \
		echo "Usage: make new TEXT=\"your otk command\""; \
		exit 1; \
	fi
	@otk-new "$(TEXT)"