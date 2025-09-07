# Netflix-Clone
This is created by https://app.emergent.sh/ which is an AI tool


| Feature / Aspect | **Prompt Engineering** | **Context Engineering** |
|-----------------|----------------------|------------------------|
| **Goal** | Guide AI to perform a task (e.g., review Python code) | Provide AI with full technical context so it acts like a knowledgeable collaborator |
| **Scope** | Single task or isolated code snippet | Project-wide scope including codebase, modules, memory, tools, and documentation |
| **Instructions / Rules** | Role assignment, a few examples, constraints | Detailed project rules, coding standards, chain-of-thought instructions, risk prioritization |
| **Context Provided** | Minimal: code snippet, high-level project description | Extensive: project architecture, prior reviews, module dependencies, company guidelines, long-term memory |
| **References** | Optional: a few links or examples | Integrated: full documentation folders, previous fixes, external references, coding standards |
| **Output Expectation** | Task-focused: vulnerabilities and improvement suggestions | Context-aware: detailed analysis, step-by-step fixes, cross-module impact, references, reasoning steps |
| **Use Case** | General purpose code review, QA checks, task automation | Building LLM-based software tools or AI agents that need deep domain knowledge and project awareness |
| **Complexity** | Moderate | High, but enables highly reliable, production-ready outputs |
| **Analogy** | Asking a smart intern “review this code” | Managing a smart intern with full project files, past experience, and structured guidelines |

### When to Use Each Approach

| **Use Prompt Engineering When...**                          | **Use Context Engineering When...**                           |
|-------------------------------------------------------------|---------------------------------------------------------------|
| Building general-purpose AI interactions                    | Building AI-powered applications for production                |
| Creating one-off AI solutions                               | Creating AI agents that need to maintain state                 |
| Experimenting with AI capabilities                          | Integrating AI into existing software systems                  |
| Working on personal productivity tools                      | Building tools that require dynamic knowledge access           |
| The context is relatively simple and static                 | Working on complex, multi-step AI workflows                    |


