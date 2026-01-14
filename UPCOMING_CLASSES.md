# 📅 Upcoming Classes - Google ADK Course

This document details the planned classes to complete the Google Agent Development Kit (ADK) course.

---

## 🎯 Current Course Status

### ✅ Completed Classes (1-9)

1. ✅ Introduction to ADK
2. ✅ Advanced LLM Management
3. ✅ Mastering Tools
4. ✅ MCP Integration
5. ✅ Advanced Workflows
6. ✅ Callbacks in ADK
7. ✅ Sessions and Memory
8. ✅ Artifacts - Binary Data and File Management
9. ✅ Context Management - Caching and Compression

---

## 📋 Planned Classes (10-17)

### **CLASS 10: Grounding and RAG (Retrieval-Augmented Generation)** 🔥
**Priority:** HIGH | **Estimated Duration:** 2-3 hours

#### Learning Objectives
- Connect agents with internal enterprise data
- Implement semantic search and retrieval
- Generate grounded responses from documents
- Optimize relevance and accuracy

#### Detailed Content

**1. Introduction to Grounding**
- What is grounding and why is it critical?
- Difference between RAG and fine-tuning
- Enterprise use cases

**2. Google Search Grounding**
- Real-time searches
- Automatic citations and sources
- Limitations and best practices

**3. Vertex AI Search Tool**
- Configure datastores in Vertex AI
- Index enterprise documents
- Multi-format search (PDF, HTML, TXT)

**4. Vertex AI RAG Engine**
- Create RAG corpus
- Configure embeddings
- Tune similarity thresholds
- Optimize retrieval quality

**5. Advanced Techniques**
- Hybrid search (keyword + semantic)
- Result re-ranking
- Chunking strategies
- Metadata filtering

**6. Practical Use Cases**
- **Enterprise chatbot**: Product/service KB
- **Legal assistant**: Laws and precedents database
- **Technical support**: Technical documentation
- **Onboarding**: Employee manuals

---

### **CLASS 11: Streaming and Gemini Live API** 🎙️
**Priority:** HIGH | **Estimated Duration:** 2-3 hours

#### Learning Objectives
- Implement bidirectional streaming
- Create natural conversational interfaces
- Handle real-time audio and video
- Build empathetic voice assistants

#### Detailed Content

**1. Introduction to Streaming**
- Difference between turn-by-turn and streaming
- Advantages of bidi-streaming
- Ideal use cases

**2. Basic Streaming Configuration**
- Text streaming setup
- Event handling

**3. Gemini Live API - Audio Streaming**
- Configure audio input/output
- PCM format (24kHz, 16-bit mono)
- Voice Activity Detection (VAD)
- Natural interruptions

**4. Audio Transcription**
- Real-time transcriptions
- Partial vs complete transcriptions
- Caption generation

**5. Proactive Audio & Affective Dialog**
- Model detects emotions in voice
- Adaptive empathetic responses
- Proactive suggestions

**6. Video Streaming**
- Video frame streaming
- Real-time visual analysis
- Multimodal (audio + video + text)

**7. Use Cases**
- **Customer service bot**: Empathetic voice support
- **Virtual tutor**: Interactive education
- **Medical assistant**: Voice consultations
- **Live transcription**: Meetings and events

---

### **CLASS 12: Agent Testing and Evaluation** 🧪
**Priority:** MEDIUM-HIGH | **Estimated Duration:** 2 hours

#### Learning Objectives
- Implement unit tests for agents
- Evaluate response quality
- Automate workflow testing
- Establish CI/CD for agents

#### Detailed Content

**1. Unit Testing of Tools**
**2. Integration Testing of Agents**
**3. Mocking External Services**
**4. Test Conversations**
**5. Evaluation Metrics**
- Response relevance
- Tool calling accuracy
- Latency benchmarks
- Token usage tracking
- Cost per interaction

**6. A/B Testing**
**7. Regression Testing**
**8. LLM-as-Judge**

---

### **CLASS 13: Deployment and Production** 🚀
**Priority:** HIGH | **Estimated Duration:** 2-3 hours

#### Learning Objectives
- Deploy agents to Agent Engine
- Configure authentication and authorization
- Implement production monitoring
- Optimize costs and performance

#### Detailed Content

**1. Agent Engine (Vertex AI)**
- Deployment process
- Configuration management

**2. REST API Endpoints**
- List deployed agents
- Query endpoints
- API management

**3. Authentication**
- Service accounts
- API keys
- OAuth integration

**4. Environment Variables & Secrets**
- Secret Manager integration
- Secure configuration

**5. Monitoring & Logging**
- Cloud Logging setup
- Performance metrics
- Error tracking

**6. Rate Limiting & Quotas**
**7. Cost Optimization**
**8. Versioning & Rollback**
**9. Load Balancing & Scaling**

---

### **CLASS 14: Security and Guardrails** 🔒
**Priority:** HIGH | **Estimated Duration:** 2 hours

#### Learning Objectives
- Implement input/output filtering
- Prevent prompt injection
- Detect PII (Personal Identifiable Information)
- Establish security policies

#### Detailed Content

**1. Input Guardrails**
- Keyword blocking
- Pattern matching
- Threat detection

**2. Output Filtering**
- Sensitive information removal
- Content moderation

**3. PII Detection**
- Pattern recognition
- Automatic redaction

**4. Tool-Level Authorization**
- Role-based access control
- Permission management

**5. Prompt Injection Prevention**
**6. Rate Limiting per User**
**7. Audit Logging**
**8. Content Moderation**

---

### **CLASS 15: Advanced Multi-Agent Architectures** 🏗️
**Priority:** MEDIUM-HIGH | **Estimated Duration:** 2-3 hours

#### Learning Objectives
- Implement Hierarchical Planner/Executor patterns
- Use AgentTool for delegation
- Coordinate specialized agents
- Handle escalation patterns

#### Detailed Content

**1. Hierarchical Planner/Executor**
- Planning agents
- Execution pipelines
- Coordination strategies

**2. AgentTool Pattern**
- Agents as tools
- Dynamic delegation
- Result aggregation

**3. Dynamic Agent Selection**
**4. Shared State Management**
**5. Escalation Patterns**
**6. Advanced Use Cases**
- Research assistant
- Content creation pipeline
- Data science assistant
- Customer service hierarchy

---

### **CLASS 16: Advanced Observability with Phoenix (Arize)** 📊
**Priority:** MEDIUM | **Estimated Duration:** 1.5 hours

#### Learning Objectives
- Integrate Phoenix/Arize with ADK
- Visualize agent traces
- Monitor performance
- Debug complex workflows

#### Detailed Content

**1. Phoenix Setup**
**2. Automatic Tracing**
**3. Custom Spans**
**4. Dashboard Visualization**
**5. Alerting**

---

### **CLASS 17: End-to-End Enterprise Use Cases** 💼
**Priority:** MEDIUM | **Estimated Duration:** 3-4 hours

#### Learning Objectives
- Integrate all course concepts
- Build production-ready applications
- Implement complete best practices

#### Use Cases to Develop

**1. E-commerce Customer Service Agent**
- Product search (RAG)
- Order management (Tools)
- Cart management (State)
- Multi-language support
- Audio support (Streaming)
- Human escalation

**2. Data Science Assistant**
- BigQuery integration
- Data analysis
- Visualization generation
- Report generation
- Model training

**3. Content Creation Pipeline**
- Research phase
- Planning
- Writing
- Editing
- Publishing

**4. Healthcare Assistant**
- Patient history
- Symptom analysis
- Appointment scheduling
- HIPAA compliance

**5. Legal Research Assistant**
- Case law search
- Document analysis
- Precedent finding
- Brief generation

---

## 📊 Visual Roadmap

```
Fundamentals (1-7) → Optimization (8-9) → Integration (10-11)
                                              ↓
                                    Testing & Deploy (12-13)
                                              ↓
                                    Advanced (14-16) → Enterprise (17)
```

## 🎯 Development Priorities

### Immediate (Next 2 weeks)
1. ✅ Class 10: Grounding and RAG
2. ✅ Class 11: Streaming and Gemini Live API

### Short Term (Next month)
3. Class 13: Deployment and Production
4. Class 14: Security and Guardrails
5. Class 12: Testing and Evaluation

### Medium Term (Next 2 months)
6. Class 15: Advanced Multi-Agent
7. Class 16: Observability
8. Class 17: Enterprise Use Cases

---

## 💡 Implementation Notes

### Each class should include:
- ✅ Complete and executable Jupyter notebook
- ✅ Working practical examples
- ✅ Video tutorial (20-40 minutes)
- ✅ Practical exercises
- ✅ Example code in repository
- ✅ References to official documentation
- ✅ Spanish and English versions

### Structure of each notebook:
1. Introduction and objectives
2. Theoretical concepts
3. Initial setup
4. Step-by-step examples
5. Practical use cases
6. Best practices
7. Anti-patterns to avoid
8. Practical exercise
9. Summary and references
10. Next class

---

## 🚀 Complete Course Goal

Upon completing all 17 classes, students will be able to:

✅ Build AI agents from scratch
✅ Implement complex multi-agent systems
✅ Integrate with external services (MCP, RAG, APIs)
✅ Optimize costs with caching and compression
✅ Deploy to production in Agent Engine
✅ Implement security and compliance
✅ Monitor and maintain agents in production
✅ Build enterprise-grade applications

---

## 📈 Success Metrics

- 🎯 90%+ exercise completion rate
- 💡 3+ personal projects developed
- 🏆 Course certification or badge
- 💼 Ability to implement production agents

---

**Last updated:** January 2026
**Maintained by:** @alarcon7a
