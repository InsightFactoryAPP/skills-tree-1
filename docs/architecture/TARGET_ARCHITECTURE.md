# Target Architecture

The target architecture is an incremental separation of the existing working system. No rewrite is authorized.

```text
                +-------------------+
                | Goal Resolution   |
                +---------+---------+
                          |
                          v
                +-------------------+
                | Candidate Service |
                +---------+---------+
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
      Taxonomy          Graph          Evidence
          |               |               |
          +---------------+---------------+
                          v
                +-------------------+
                | Scoring            |
                +---------+---------+
                          v
                +-------------------+
                | Calibration        |
                +---------+---------+
                          v
                +-------------------+
                | Constraints        |
                +---------+---------+
                          v
                +-------------------+
                | Recommendation     |
                +---------+---------+
                          |
             +------------+------------+
             |                         |
             v                         v
       Learning Path             Architecture
             |                    Inference
             |                         |
             +------------+------------+
                          v
                     Blueprint
```

## Separation strategy

1. Establish behavioral tests around existing production behavior.
2. Extract pure domain models and scoring contracts without changing semantics.
3. Extract repositories for taxonomy, graph, benchmark, and calibration data.
4. Move recommendation orchestration into an application service.
5. Make API, CLI, and MCP adapters consume the application service rather than each other.
6. Add versioned provenance to recommendation results.
7. Replace static architecture selection incrementally with capability/graph inference while retaining the current mapping as a fallback.

## Constraints

- Existing public CLI commands remain available.
- Existing API endpoints remain available unless a versioned contract requires otherwise.
- Existing MCP tools remain available.
- Generated graph data remains an artifact of its generator and is never edited manually to fix runtime behavior.
- Deterministic recommendation content is mandatory.
- New dependencies require a demonstrated need.
