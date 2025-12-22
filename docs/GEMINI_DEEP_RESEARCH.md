# Project Brain-Radio: Autonomous Agentic Music Architecture

1. Executive Research Report: The State of Autonomous Coding Agents & Music Information Retrieval
1.1 The Paradigm Shift: From Deterministic Software to Agentic Workflows
The software engineering landscape is currently navigating a pivotal transition from deterministic, human-authored logic to probabilistic, agent-driven architectures. As of late 2024 and early 2025, the capabilities of Large Language Models (LLMs) such as OpenAI’s GPT-4o, o1-preview, and Anthropic’s Claude 3.5 Sonnet have crystallized into distinct levels of autonomy. The research indicates a progression from Level 1 "Copilots" (intelligent information retrieval) to Level 4 "Multi-Agent Constellations" where loosely coupled agents collaborate on complex tasks.1
For the construction of Brain-Radio, we function primarily within Level 3: Cross-System Agentic Workflow Orchestration. This level is characterized by complex workflow execution where a supervisory agent manages specialized sub-agents. This architectural choice is driven by the limitations of single-model systems; while models like OpenAI's o1 demonstrate advanced reasoning capabilities 2, they still struggle with maintaining global context over extended engineering tasks. Therefore, a "Supervisor-Worker" topology—orchestrated via frameworks like LangGraph—has emerged as the standard for robust application development.3
The specific mandate to utilize "autonomous coding agents" (historically rooted in the Codex lineage) to build this system necessitates a dual-layer approach to agency:
The Builder Layer: Autonomous agents (like Devin, OpenDevin, or custom LangGraph workflows) that utilize Test Driven Development (TDD) to generate the system code.4
The Runtime Layer: The internal agents of "Brain-Radio" that perceive user intent, analyze audio, and curate playlists during operation.6
This report serves as the comprehensive architectural blueprint for Brain-Radio, integrating deep research into a cohesive narrative that spans infrastructure choices, product requirements, and rigorous quality assurance protocols.
1.2 The Crisis in Music Information Retrieval (MIR)
A critical driver for the "Brain-Radio" architecture is the abrupt degradation of public music APIs. For over a decade, the Spotify Web API served as the de facto "brain" for music applications, providing rich metadata including audio features (valence, energy, danceability) and algorithmic recommendations. However, starting in November 2024 and continuing through 2025, Spotify deprecated these key endpoints for new applications.7
The deprecation of the Get Recommendations and Get Audio Features endpoints 8 fundamentally breaks the traditional "thin client" architecture where an app simply visualizes data computed by Spotify's servers. Furthermore, the preview_url endpoint, essential for sampling tracks, has become unreliable, returning null values or 404 errors across vast segments of the catalog due to licensing shifts.9
Strategic Implication: Brain-Radio cannot rely on external "black-box" intelligence. It must possess a "Local Brain"—a self-contained Audio Intelligence Pipeline capable of extracting semantic and acoustic features directly from raw audio data. This requirement shifts the architectural burden from API integration to Edge AI processing, necessitating robust containerization to handle dependencies like ffmpeg, Essentia (C++), and PyTorch models.11
1.3 Architectural Decision: Infrastructure Orchestration
The user query requires a definitive selection between Docker, Docker Compose, and Kubernetes (K8s) for the Brain-Radio infrastructure. This decision is pivotal, influencing development velocity, operational complexity, and system resilience.
1.3.1 Comparative Analysis: The Orchestration Trilemma
The following analysis synthesizes research on container lifecycles 13, agent deployment patterns 6, and resource overhead.16
Feature
Docker (Standalone)
Docker Compose
Kubernetes (K8s)
Primary Use Case
Single container apps, scripts
Multi-container local dev & small prod
Enterprise-scale distributed systems
Complexity
Low
Low-Medium
High (Control Plane, Etcd, Ingress)
Networking
Manual linking
Automatic bridge networks via YAML
Complex CNI (Flannel/Calico), Service Mesh
State Management
Host volumes
Named volumes, easy backup
Persistent Volume Claims (PVC), Storage Classes
Agent Support
Basic
Excellent (GPU support, Watch mode)
Advanced (auto-scaling agents)
Dev Cycle Time
Fast
Fast (Hot reload supported)
Slow (Build -> Push -> Deploy loop)
Resource Overhead
Minimal
Minimal (~20MB for daemon)
Heavy (~2GB+ for control plane)

1.3.2 The Verdict: Docker Compose
Docker Compose is the optimal architecture for Brain-Radio.
Reasoning:
Agent-Specific Enhancements: Docker has recently evolved Compose to specifically support AI agent workflows. Features like docker compose watch allow for hot-reloading of Python code inside containers, which is critical for the rapid TDD cycles required by the prompt.6
Complexity vs. Value: Kubernetes introduces a massive "complexity tax." Running K8s (even lightweight versions like K3s) requires managing a control plane, etcd database, and complex networking ingress.13 For a "personal" or SME-scale agent system processing music, this overhead yields diminishing returns. The system does not require the "self-healing" of 1000 pods; it requires tight integration between the Vector DB (Qdrant) and the Analysis Service.
GPU Passthrough: Deep learning models (like LAION-CLAP) require GPU acceleration. Configuring nvidia-container-runtime in Docker Compose is significantly more straightforward than managing GPU nodes and taints/tolerations in a K8s cluster.17
Data Persistence: The "Brain" requires persistent storage for the Vector Database (Qdrant) and Agent Memory (Postgres). Docker Compose handles named volumes effortlessly for this scale, whereas K8s requires configuring StorageClasses and PVCs, which is often overkill for single-node deployments.16
Decision: We will architect Brain-Radio using Docker Compose, utilizing the services definition to orchestrate the API, Vector DB, and Database layers, interconnected via a private bridge network.
2. AGENTS.md: The Cognitive Architecture
2.1 Agentic Topology: The Supervisor Pattern
To satisfy the requirement of "autonomous coding agents building Brain-Radio" and the internal logic of the system itself, we define a recursive architecture. The system logic is encapsulated in AGENTS.md, which defines the runtime behavior of the Brain-Radio bots.
We utilize LangGraph as the orchestration framework. Research indicates that linear chains (LangChain) are insufficient for complex tasks requiring loops, retries, and state persistence.18 LangGraph allows us to define a cyclic graph where the state (conversation history, errors, plan) is passed between nodes.
The Supervisor (Orchestrator)
The central node that routes tasks. It maintains the AgentState and decides whether to route to the Planner, Analyst, or DJ agents. It utilizes the PostgresSaver checkpointing mechanism to maintain long-term memory of user preferences (e.g., "User hates Country music") across sessions.19
2.2 Agent Definitions & System Prompts
2.2.1 The Planner Agent (The "Architect")
Role: Decomposes abstract natural language queries into concrete technical steps.
Input: "I want a playlist that feels like a rainy cyberpunk city."
Output: Structured Plan: ``
System Prompt:"You are the Planner. You do not write code or query databases directly. Your goal is to translate user vibes into acoustic parameters. You know that 'high energy' maps to energy > 0.8 and bpm > 130. You know that 'sad' maps to valence < 0.4 and mode = 0 (Minor). Output a list of execution steps."
2.2.2 The Analyst Agent (The "Ear")
Role: Interfaces with the local Audio Analysis Pipeline. It wraps the complexity of Essentia and CLAP.
Tools: analyze_audio_file(path), get_audio_embedding(path).
Behavior: When a new track is added, this agent spins up. It is robust to failures (e.g., corrupt MP3s) and ensures the Vector DB is populated. It handles the "physics" of the sound.20
2.2.3 The DJ Agent (The "Curator")
Role: Executes the search and formats the output.
Tools: qdrant_search(vector, filter), create_playlist_file(tracks).
System Prompt:"You are the DJ. You execute the Planner's strategy. You query Qdrant using Hybrid Search (combining dense vector similarity with metadata filters). You prioritize seamless transitions between tracks (harmonic mixing). If a search yields no results, you relax the constraints and retry (Self-Correction)."
2.3 Tools & Capabilities
The agents are empowered by a specific set of Python tools, strictly typed with Pydantic for validation.21
Tool: analyze_audio
Library: essentia.standard
Reasoning: Research confirms Essentia (C++) is faster and more feature-rich for batch processing than Librosa (Python-native), specifically for rhythm and key extraction.22
Outputs: BPM, Key, Scale, Loudness, Danceability (inferred).
Tool: generate_embedding
Model: laion/clap-htsat-unfused
Reasoning: LAION-CLAP enables Zero-Shot classification. It maps audio and text to the same latent space. This allows the user to search for "sound of a vacuum cleaner" or "happy rock" without those tags explicitly existing in the metadata.23
Tool: vector_search
Database: Qdrant
Method: Cosine Similarity with Payload Filtering.
2.4 State Management Schema
The AgentState is the shared memory structure passed between nodes in the LangGraph.

Python


from typing import TypedDict, Annotated, List, Union
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    # Chat history
    messages: Annotated, operator.add]
    # The current abstract plan
    plan: List[str]
    # Acoustic constraints derived from plan
    constraints: dict[str, Union[float, str]]
    # The list of candidate tracks found
    candidate_tracks: List[dict]
    # Retry counter for error handling
    retries: int


3. PRD.md: Product Requirements Document
3.1 Product Overview
Brain-Radio is a local-first, autonomous music curation system. It bypasses the limitations of commercial streaming APIs by using local AI agents to analyze, index, and curate music libraries based on natural language "vibe" requests.
3.2 User Personas
Persona A: The Data Audiophile
Profile: Has a large local library (FLAC/MP3). Distrusts streaming algorithms. Wants granular control (e.g., "Play songs in the key of A Minor, sorted by increasing BPM").
Needs: Precision, metadata accuracy, harmonic mixing.
Persona B: The Vibe Surfer
Profile: Doesn't know music theory. Wants music to match a feeling or scene (e.g., "Background music for reading sci-fi novels").
Needs: Semantic understanding, zero-shot retrieval.
3.3 Functional Requirements
3.3.1 Audio Ingestion & Analysis ("The Brain")
FR-01: System MUST ingest audio files from a mounted Docker volume.
FR-02: System MUST extract low-level features (BPM, Key, Loudness, Onsets) using Essentia.25
FR-03: System MUST generate a 512-dimension vector embedding for each track using LAION-CLAP.12
FR-04: System MUST store metadata and vectors in Qdrant.
3.3.2 Natural Language Querying ("The Interface")
FR-05: System MUST accept natural language queries via a REST API (FastAPI).
FR-06: The PlannerAgent MUST interpret queries and extract filtering logic (e.g., "fast" -> bpm > 120).
FR-07: The DJAgent MUST perform Hybrid Search:
Semantic: Matching the query text embedding to audio embeddings.
Keyword: Matching genre/artist metadata.
3.3.3 Playlist Generation ("The Output")
FR-08: System MUST output a playlist file (.m3u or .json).
FR-09: System SHOULD attempt "Harmonic Mixing" (ordering tracks by compatible keys) if requested.
3.4 Non-Functional Requirements (NFRs)
NFR-01 (Performance): Analysis of a 3-minute track must complete in < 2 seconds on standard hardware (AVX2 supported CPU).26
NFR-02 (Accuracy): BPM detection must be within +/- 2 BPM of ground truth for 90% of tracks (benchmarked against standard datasets like GTZAN).
NFR-03 (Availability): The system must function fully offline after the initial Docker pull. No dependency on Spotify/OpenAI APIs for the analysis phase (LLM may be local via Ollama or remote).
NFR-04 (Code Quality): The codebase must maintain 95% Test Coverage enforced by CI pipelines.27
3.5 UI/UX Specifications
Interface: CLI (Command Line Interface) and Swagger UI (via FastAPI).
Feedback Loop: The system must explain why it picked a song (e.g., "Selected 'Midnight City' because it matches the 'neon' vector and is in B Minor").
4. ACCEPTANCE_CRITERIA.md: The TDD Strategy
4.1 The Challenge of TDD in Agentic AI
Achieving 95% Code Coverage in an AI system is non-trivial because the "logic" often resides within the stochastic model, not the Python code. To satisfy the prompt's strict requirement, we employ a Determinism Isolation Strategy.4
We define three layers of testing, mapping to the Testing Pyramid:
4.2 Layer 1: Tool Unit Tests (Deterministic)
Scope: The Python functions called by the agent.
Coverage Target: 100%
AC-T1 (Audio Analysis):
Input: A synthetic sine wave audio file generated during the test setup.
Action: Call analyze_audio_features().
Assertion: Result must contain keys bpm, key, loudness. bpm must be strictly equal to the generated sine wave tempo.
AC-T2 (Vector DB):
Input: A mock Qdrant client (using unittest.mock).
Action: Call search_db().
Assertion: Verify client.search() was called with correct vector and filter arguments.
4.3 Layer 2: Agent Graph Tests (State Transitions)
Scope: The LangGraph control flow.
Coverage Target: 100%
AC-G1 (Planning Flow):
Context: Mock the LLM to return a "Tool Call" response.
Action: Invoke the Supervisor node.
Assertion: The graph state must transition from Supervisor to Tools.
AC-G2 (Error Handling):
Context: Mock the Tool node to raise a ValueError.
Action: Run the graph step.
Assertion: The graph must transition to a Retry or ErrorReporter node, and state["error_count"] must increment.
4.4 Layer 3: Acceptance Tests (End-to-End)
Scope: The full system.
Coverage Target: Integration paths.
AC-E1 (The "Sad Song" Test):
Given a library of 5 songs (2 happy, 3 sad), validated by human labeling.
When the user queries "Play me something depressing".
Then the output playlist must contain only the 3 sad songs.
Implementation: Use DeepEval or similar framework to grade the semantic relevance of the output.29
4.5 Testing Infrastructure & Libraries
To support this TDD workflow, the dev dependencies in pyproject.toml are critical:
pytest: Core runner.
pytest-cov: Coverage reporting (configured to fail under 95%).
vcrpy: To record and replay network interactions (if calling external LLMs during dev).
mutmut: Mutation testing to ensure tests are actually testing logic, not just running lines.30
5. Implementation Guide & Specifications
This section translates the research into concrete configuration and code specifications.
5.1 Infrastructure: compose.yaml
The following configuration implements the Docker Compose architecture decided in Section 1.3.

YAML


# docker-compose.yml
services:
  # The Brain-Radio API & Agent Runtime
  brain-radio-api:
    build:
      context:.
      dockerfile: Dockerfile
    image: brain-radio:latest
    container_name: brain_radio_core
    ports:
      - "8000:8000"
    environment:
      - POSTGRES_URI=postgresql://user:pass@postgres:5432/brainradio
      - QDRANT_HOST=qdrant
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      -./data/music:/app/music_library:ro # Read-only music mount
      -./logs:/app/logs
    depends_on:
      qdrant:
        condition: service_healthy
      postgres:
        condition: service_healthy
    networks:
      - brain-net
    develop:
      watch:
        - action: sync
          path:./src
          target: /app/src
        - action: rebuild
          path:./pyproject.toml

  # Vector Database (The Memory)
  qdrant:
    image: qdrant/qdrant:latest
    container_name: brain_radio_qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_storage:/qdrant/storage
    healthcheck:
      test:
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - brain-net

  # Agent State Persistence
  postgres:
    image: postgres:16-alpine
    container_name: brain_radio_db
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: brainradio
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test:
      interval: 5s
      retries: 5
    networks:
      - brain-net

volumes:
  qdrant_storage:
  postgres_data:

networks:
  brain-net:
    driver: bridge


Key Architectural Insight: The develop.watch section is a crucial addition based on the research into Docker's latest "GenAI" features.6 It allows the developer to modify agent logic (Python files) on the host and have them instantly sync to the container without a rebuild, enabling the rapid TDD cycle requested.
5.2 Dependency Management: Dockerfile
The Dockerfile must handle the complex intersection of Python (LangChain), C++ (Essentia), and System libraries.

Dockerfile


# Dockerfile
FROM python:3.11-slim as builder

# Install system dependencies for audio processing
# ffmpeg is required by Essentia/Librosa for decoding
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY pyproject.toml.
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Copy application code
COPY src/./src/

# Runtime stage
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]


5.3 CI/CD Configuration: Enforcing 95% Coverage
To strictly satisfy the "95%+ code coverage" requirement, we must configure the testing runner (pytest) to treat low coverage as a failure. This acts as a gatekeeper for the Autonomous Coding Agent: if the agent generates code without corresponding tests, the build fails.
pyproject.toml Configuration:

Ini, TOML


[tool.pytest.ini_options]
addopts = "--cov=src --cov-report=term-missing --cov-fail-under=95"
testpaths = ["tests"]

[tool.coverage.run]
omit = [
    "src/main.py",  # Exclude entrypoint boilerplate
    "src/config.py" # Exclude simple config definitions
]


GitHub Actions Workflow (.github/workflows/tdd-check.yaml):

YAML


name: TDD Enforcement
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install Dependencies
        run: |
          pip install poetry
          poetry install
      - name: Run Tests with Strict Coverage
        run: poetry run pytest


5.4 Technical Deep Dive: The Local Audio "Brain"
The core differentiation of Brain-Radio is its independence from Spotify's deprecated API. We utilize a dual-model approach.
5.4.1 Essentia (Rhythm & Key)
We utilize essentia.standard.RhythmExtractor2013. Research 11 highlights its superiority over standard beat trackers due to its multi-feature voting scheme.
Implementation Note: We must handle the MonoLoader carefully. It downmixes stereo files to mono. We set the sample rate to 44.1kHz to match the model's training data.
5.4.2 LAION-CLAP (Semantics)
The CLAP model (Contrastive Language-Audio Pretraining) works by projecting audio and text into a shared 512-dimensional space.
Mechanism: When the user types "Rainy Jazz", we encode that text into vector $V_t$. We then search Qdrant for Audio Vectors $V_a$ such that CosineSimilarity($V_t$, $V_a$) is maximized.
Constraint: The model is large (~1GB). We load it once at startup in the AnalystAgent and keep it in memory (Singletion pattern) to avoid latency on per-track analysis.31
5.5 Future Outlook & Agent Evolution
The architecture defined here is "Level 3" (Orchestration). As we move toward "Level 4" (Collaborative Swarms) in late 2025, the architecture of Brain-Radio supports scaling:
Swarm Mode: The Planner and DJ agents could eventually run on separate physical machines (e.g., cloud GPU for planning, local NUC for analysis), communicating via the existing Postgres state backend.
Self-Improvement: Using the feedback loop (did the user skip the song?), the agent can fine-tune the prompt embeddings stored in Qdrant, effectively "learning" the user's taste without explicit thumbs-up/down actions.
This report confirms that by leveraging Docker Compose for infrastructure, LangGraph for cognitive orchestration, and a strict TDD methodology, it is possible to build a robust, autonomous music system that is resilient to the volatile API landscape of the modern web.
Works cited
State of the Art of Agentic AI Transformation | Bain & Company, accessed December 21, 2025, https://www.bain.com/insights/state-of-the-art-of-agentic-ai-transformation-technology-report-2025/
State of AI Agents in 2025: A Technical Analysis | by Carl Rannaberg | Medium, accessed December 21, 2025, https://carlrannaberg.medium.com/state-of-ai-agents-in-2025-5f11444a5c78
Andrew Ng: State of AI Agents | LangChain Interrupt - YouTube, accessed December 21, 2025, https://www.youtube.com/watch?v=4pYzYmSdSH4
Test-Driven Development with AI - Builder.io, accessed December 21, 2025, https://www.builder.io/blog/test-driven-development-ai
Has anyone tried testing different coding approaches (spec-driven, TDD, etc.) *systematically* with AI coding agents?, accessed December 21, 2025, https://www.reddit.com/r/ClaudeAI/comments/1oghhop/has_anyone_tried_testing_different_coding/
Docker Brings Compose to the Agent Era: Building AI Agents is Now Easy, accessed December 21, 2025, https://www.docker.com/blog/build-ai-agents-with-docker-compose/
Introducing some changes to our Web API - Spotify for Developers, accessed December 21, 2025, https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api
Solved: Spotify API /recommendations Endpoint Always Retur, accessed December 21, 2025, https://community.spotify.com/t5/Spotify-for-Developers/Spotify-API-recommendations-Endpoint-Always-Returns-404-Even/td-p/6917868
Preview URLs Deprecated? - The Spotify Community, accessed December 21, 2025, https://community.spotify.com/t5/Spotify-for-Developers/Preview-URLs-Deprecated/td-p/6791368
spotify preview_url not working anymore ? : r/spotifyapi - Reddit, accessed December 21, 2025, https://www.reddit.com/r/spotifyapi/comments/1opcut9/spotify_preview_url_not_working_anymore/
What is the difference between the way Essentia and Librosa generate MFCCs?, accessed December 21, 2025, https://dev.to/enutrof/what-is-the-difference-between-the-way-essentia-and-librosa-generate-mfccs-13n3
laion/larger_clap_general - Hugging Face, accessed December 21, 2025, https://huggingface.co/laion/larger_clap_general
Docker Compose vs Kubernetes: A Detailed Comparison - DataCamp, accessed December 21, 2025, https://www.datacamp.com/blog/docker-compose-vs-kubernetes
Container Lifecycle Management: Docker Compose vs Kubernetes | by Platform Engineers, accessed December 21, 2025, https://medium.com/@platform.engineers/container-lifecycle-management-docker-compose-vs-kubernetes-2815ae2e28e3
Deploying Multi-Task, Multi-Agent Platforms on Azure Container Apps: A Complete Guide, accessed December 21, 2025, https://medium.com/@alaminibrahim433/deploying-multi-task-multi-agent-platforms-on-azure-container-apps-a-complete-guide-d38811a53f5f
Docker vs Kubernetes, what's better in a Homelab? : r/selfhosted - Reddit, accessed December 21, 2025, https://www.reddit.com/r/selfhosted/comments/1208dz5/docker_vs_kubernetes_whats_better_in_a_homelab/
Build, Deploy, and Scale AI Agent systems using Docker MCP Gateway and Python, accessed December 21, 2025, https://www.ajeetraina.com/build-deploy-and-scale-ai-agent-systems-using-docker-mcp-gateway-and-python/
Set Up LangGraph in Minutes with Docker Compose (Docker Tutorial) - YouTube, accessed December 21, 2025, https://www.youtube.com/watch?v=28OkHz_IfJs
Memory - Docs by LangChain, accessed December 21, 2025, https://docs.langchain.com/oss/python/langgraph/add-memory
Beat detection and BPM tempo estimation — Essentia 2.1-beta6-dev documentation, accessed December 21, 2025, https://essentia.upf.edu/tutorial_rhythm_beatdetection.html
Pydantic AI: A Beginner's Guide With Practical Examples - DataCamp, accessed December 21, 2025, https://www.datacamp.com/tutorial/pydantic-ai-guide
Is the essentia library implemented in C++ slower than the librosa library implemented in Python? - Stack Overflow, accessed December 21, 2025, https://stackoverflow.com/questions/76121336/is-the-essentia-library-implemented-in-c-slower-than-the-librosa-library-imple
CLAP - Hugging Face, accessed December 21, 2025, https://huggingface.co/docs/transformers/model_doc/clap
CLAP: Learning Audio Concepts From Natural Language Supervision - Microsoft Research, accessed December 21, 2025, https://www.microsoft.com/en-us/research/publication/clap-learning-audio-concepts-from-natural-language-supervision/
essentia-tutorial/tutorial_extractors_musicextractor.ipynb at master - GitHub, accessed December 21, 2025, https://github.com/MTG/essentia-tutorial/blob/master/tutorial_extractors_musicextractor.ipynb
How fast big LLMs can work on consumer CPU and RAM instead of GPU? - Reddit, accessed December 21, 2025, https://www.reddit.com/r/LocalLLaMA/comments/1edryd2/how_fast_big_llms_can_work_on_consumer_cpu_and/
How much code coverage is enough? Best practices for coverage - Graphite, accessed December 21, 2025, https://graphite.com/guides/code-coverage-best-practices
Test - Docs by LangChain, accessed December 21, 2025, https://docs.langchain.com/oss/python/langchain/test
eval-view/guides/pytest-for-ai-agents-langgraph-ci.md at main - GitHub, accessed December 21, 2025, https://github.com/hidai25/eval-view/blob/main/guides/pytest-for-ai-agents-langgraph-ci.md
Code Coverage Best Practices - Google Testing Blog, accessed December 21, 2025, https://testing.googleblog.com/2020/08/code-coverage-best-practices.html
The GPU Paradox: Why Your GPU Might Be Slower Than Your CPU for LLM Inference | by Mubashir Rahim | Medium, accessed December 21, 2025, https://medium.com/@mubashirrahim3431/the-gpu-paradox-why-your-gpu-might-be-slower-than-your-cpu-for-llm-inference-0eb08f4711b5
