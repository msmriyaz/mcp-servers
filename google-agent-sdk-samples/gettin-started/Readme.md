source: https://google.github.io/adk-docs/
pip install google-adk
Documentation references:
https://google.github.io/adk-docs/get-started/tutorial/#4-interact-with-the-agent
ADK Streaming Quickstart - https://google.github.io/adk-docs/get-started/quickstart-streaming/
Build Your First Intelligent Agent Team: A Progressive Weather Bot with ADK - https://google.github.io/adk-docs/get-started/quickstart/
Local testing - https://google.github.io/adk-docs/get-started/local-testing/#working-directory
Sample agents - https://github.com/google/adk-samples
About SDK - https://google.github.io/adk-docs/get-started/about/#key-capabilities
Agents - https://google.github.io/adk-docs/agents/
How agents use tools - https://google.github.io/adk-docs/tools/#how-agents-use-tools
MCP tools - https://google.github.io/adk-docs/tools/mcp-tools/
Deployment - https://google.github.io/adk-docs/deploy/
Multi Agent - https://cloud.google.com/blog/products/ai-machine-learning/build-and-manage-multi-system-agents-with-vertex-ai

Killing if a port is in use by previous run:
netstat -ano | findstr :8000
if returned: 73972
taskkill /PID 73972 /F