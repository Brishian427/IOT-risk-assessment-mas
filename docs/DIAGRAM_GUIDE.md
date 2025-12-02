# How to Add Diagrams to README

## Overview

GitHub supports **Mermaid diagrams** natively in Markdown files. Mermaid is a diagramming and charting tool that uses text-based syntax to create diagrams.

## Supported Diagram Types

GitHub supports these Mermaid diagram types:
- Flowcharts (graph, flowchart)
- Sequence diagrams
- Class diagrams
- State diagrams
- Entity Relationship diagrams
- User Journey diagrams
- Gantt charts
- Pie charts
- Git graphs
- And more...

## Syntax

Wrap your Mermaid code in a code block with `mermaid` language identifier:

````markdown
```mermaid
graph TD
    A[Start] --> B[Process]
    B --> C[End]
```
````

## Examples in This Project

### 1. System Workflow Diagram (Flowchart)

Shows the complete workflow with decision points:

```mermaid
graph TD
    Start([Risk Input]) --> GenEnsemble[Generator Ensemble]
    GenEnsemble --> Aggregator[Aggregator]
    Aggregator --> ChallengerA[Challenger A]
    Aggregator --> ChallengerB[Challenger B]
    Aggregator --> ChallengerC[Challenger C]
    ChallengerA --> Verifier[Verifier]
    ChallengerB --> Verifier
    ChallengerC --> Verifier
    Verifier --> End([Final Assessment])
```

### 2. Sequence Diagram

Shows the interaction between components over time:

```mermaid
sequenceDiagram
    participant User
    participant GenEnsemble
    participant Aggregator
    participant Verifier
    
    User->>GenEnsemble: Risk Input
    GenEnsemble->>Aggregator: 9 Assessments
    Aggregator->>Verifier: Synthesized Draft
    Verifier->>User: Final Assessment
```

## Styling

You can style nodes in flowcharts:

```mermaid
graph TD
    A[Node A] --> B[Node B]
    style A fill:#e1f5ff
    style B fill:#fff4e1
```

## Common Patterns

### Decision Points

```mermaid
graph TD
    A[Start] --> B{Decision?}
    B -->|Yes| C[Path A]
    B -->|No| D[Path B]
```

### Parallel Execution

```mermaid
graph TD
    A[Start] --> B[Task 1]
    A --> C[Task 2]
    A --> D[Task 3]
    B --> E[End]
    C --> E
    D --> E
```

### Loops

```mermaid
graph TD
    A[Start] --> B[Process]
    B --> C{Check}
    C -->|Retry| B
    C -->|Done| D[End]
```

## Tips

1. **Keep it Simple**: Complex diagrams can be hard to read
2. **Use Labels**: Clear labels make diagrams understandable
3. **Consistent Styling**: Use consistent colors for similar components
4. **Test Locally**: Use [Mermaid Live Editor](https://mermaid.live/) to preview
5. **Version Control**: Mermaid diagrams are text-based, so they work great with Git

## Tools

- **Mermaid Live Editor**: https://mermaid.live/ (preview and edit)
- **Mermaid Documentation**: https://mermaid.js.org/
- **GitHub Support**: https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams

## Alternative: Images

If you need more complex diagrams, you can also:

1. Create diagrams using tools like:
   - Draw.io / diagrams.net
   - PlantUML
   - Excalidraw
   - Lucidchart

2. Export as PNG/SVG

3. Add to repository in `docs/images/`

4. Reference in README:
   ```markdown
   ![Architecture Diagram](docs/images/architecture.png)
   ```

## Best Practices

1. **Place diagrams near relevant text**: Don't put all diagrams at the top
2. **Add captions**: Use text above/below to explain the diagram
3. **Keep updated**: Update diagrams when architecture changes
4. **Accessibility**: Ensure diagrams are readable in both light and dark modes

