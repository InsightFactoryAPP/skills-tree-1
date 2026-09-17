"""Pytest bootstrap for shared runtime compatibility adapters."""

# Import the runtime taxonomy adapter before test modules instantiate the
# legacy GoalTaxonomyParser. The adapter installs the Level-4 taxonomy mapping
# compatibility needed by the current canonical GOAL_TAXONOMY.md format.
import tools.taxonomy_runtime  # noqa: F401
