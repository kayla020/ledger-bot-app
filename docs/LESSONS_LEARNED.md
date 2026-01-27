# Lessons Learned - Ledger Bot Exploration Day

**Date:** January 23, 2026
**Project:** Building an AI assistant for GL Publisher

---

## Technical Lessons

### 1. Socket Mode > Webhooks for Internal Bots

**What we learned:**
- Socket Mode eliminates need for public endpoints
- No ngrok needed (which is flagged as security risk internally)
- Simpler to run locally and deploy
- Better for corporate environments with strict security

**Takeaway:** For internal tools, always check if Socket Mode is available before setting up webhooks.

### 2. Company Infrastructure First

**The Journey:**
- Started trying to use Anthropic API directly → auth error
- Tried company gateway (llm.w10e.com) → wrong endpoint/auth
- Finally discovered LiteLLM staging endpoint → worked!

**What we learned:**
- Always check #platform or internal docs FIRST
- Company infrastructure is there for a reason (cost control, compliance)
- Using internal tools = less friction with security/procurement

**Takeaway:** Before reaching for external APIs, ask "Do we have an internal version?"

### 3. UX Beats Raw Performance

**The Problem:**
- LLM responses take 2-5 seconds
- Users perceive this as "slow" or "broken"

**The Solution:**
- Added ":hourglass_flowing_sand: Thinking..." indicator
- Updates to final answer when ready
- Suddenly feels much faster!

**Takeaway:** Perceived performance > actual performance. Give users immediate feedback.

### 4. Knowledge Curation vs Retrieval Tradeoff

**Two Approaches:**

**A. Static Knowledge Base (What we built):**
- ✅ Curated, high-quality information
- ✅ Fast responses (small context)
- ✅ Easy to maintain
- ❌ Limited by size (can't include everything)
- ❌ Manual updates needed

**B. RAG/Dynamic Retrieval (Phase 2):**
- ✅ Can include entire repository
- ✅ Always up-to-date
- ✅ Handles specific queries better
- ❌ More complex infrastructure
- ❌ Potential for irrelevant results

**What we learned:**
- Start with static, add dynamic later
- Hybrid approach is best: core knowledge static + detailed queries dynamic

**Takeaway:** Don't over-engineer. Static knowledge base got us 80% of value in 20% of time.

### 5. Tool Calling is Powerful (But We Discovered It Late)

**Current Bot:**
- Has one big static knowledge base
- Claude generates answers from that context

**Refactored Bot (In Progress):**
- Has tools: `search_adrs()`, `find_impact_builders()`, etc.
- Claude decides when to use them
- Can fetch specific, detailed information on demand

**What we learned:**
- Tool calling lets you keep context small but knowledge large
- Claude is good at deciding when to use tools
- Enables richer, more accurate answers

**Takeaway:** Design for tool calling from the start. Don't just dump everything in context.

### 6. Shared Libraries Enable Scaling

**The Evolution:**
1. Built Slack bot with embedded knowledge
2. Planned MCP server as separate project
3. Realized: we'd duplicate all the code!
4. Refactored to shared library approach

**Benefits:**
- Write search/query logic once
- Multiple interfaces use same knowledge
- DRY principle maintained
- Easy to add new interfaces later

**Takeaway:** When building similar functionality for multiple interfaces, extract to shared library immediately.

---

## Workflow Lessons

### 7. Claude Code Enables Rapid Prototyping

**What happened:**
- Built working Slack bot in ~4 hours
- Fixed multiple authentication/config issues
- Wrote comprehensive documentation
- Created implementation plan for Phase 2

**How Claude helped:**
- Fast iteration on code
- Helped debug auth issues
- Generated documentation templates
- Wrote implementation plans

**Takeaway:** Claude Code is like having a senior engineer pair programming with you. Use it for exploration days.

### 8. TDD Is Worth It (But Flexible)

**Slack Bot:**
- Built exploratory-style (no tests)
- Fast to get working
- ⚠️ Now needs tests before production

**MCP Server:**
- Using TDD from day 1
- Slower initial progress
- ✅ More confidence in each piece

**What we learned:**
- Exploration: Move fast, add tests later
- Production: TDD from start
- Refactoring: Write tests before changing

**Takeaway:** Match testing approach to project phase. Exploration != Production.

### 9. Parallel Execution for Plans

**Traditional:**
- Write plan
- Implement step by step
- Slow, sequential

**With Claude:**
- Write detailed plan
- Spawn separate Claude session
- That session implements while you work on something else
- Parallel progress!

**Takeaway:** Use parallel Claude sessions for independent work streams.

### 10. Documentation While Building > Documentation After

**What worked:**
- Documented as we built
- Captured decisions in ADR format
- Wrote demo script before demo
- Everything fresh in mind

**What would have failed:**
- Trying to remember details later
- Reconstructing reasoning after the fact

**Takeaway:** Document continuously, not at the end. Future you will thank present you.

---

## Design Lessons

### 11. One Interface Isn't Enough

**Initial Idea:** Just build MCP server for personal use

**Better Idea:** Hybrid with Slack bot for teams

**Why:**
- Different audiences have different needs
- Teams want accessible (Slack)
- You want deep integration (MCP)
- Shared library makes both viable

**Takeaway:** Think about all potential users, not just yourself.

### 12. Start with Real Problems, Not Cool Tech

**Could have built:**
- Vector database with embeddings
- Complex RAG system
- Multi-agent orchestration

**Actually built:**
- Simple static knowledge base
- Slack bot that answers questions
- Solves real pain point NOW

**What we learned:**
- Cool tech is tempting
- Solving real problem is valuable
- Can always add sophistication later

**Takeaway:** Tech is means, not end. Start with user pain, add tech as needed.

### 13. Security Should Be Easy, Not Bolted On

**What we did right:**
- Used Socket Mode (no public endpoints)
- Environment variables for secrets from day 1
- `.gitignore` for sensitive files
- Company infrastructure (approved tools)

**What could have gone wrong:**
- Hardcoded API keys
- Ngrok flagged by security
- External API without approval
- Webhook endpoint vulnerabilities

**Takeaway:** Make secure path the easy path. Don't make developers choose between security and productivity.

---

## Communication Lessons

### 14. Show > Tell

**For the demo:**
- Not just talking about what it does
- Actually using it live
- Showing the code
- Walking through the architecture

**Why it matters:**
- People need to see it work
- Reduces skepticism
- Makes it concrete
- Easier to give feedback

**Takeaway:** Always demo, never just present slides.

### 15. Frame as Experiment, Not Product

**Good framing:**
- "I explored building this on exploration day"
- "Here's what I learned"
- "What feedback do you have?"

**Bad framing:**
- "This is the solution"
- "We should deploy this immediately"
- "It's perfect"

**Why:**
- Reduces defensiveness to feedback
- Opens dialogue
- Manages expectations
- Encourages iteration

**Takeaway:** Exploration days are about learning, not perfection.

---

## What I'd Do Differently Next Time

### Start Earlier on Infrastructure Research
**Issue:** Lost 1-2 hours figuring out LiteLLM setup
**Solution:** Check #platform channel and internal docs first

### Design for Tool Calling from Start
**Issue:** Had to refactor to add tool support
**Solution:** Plan tool interface early, even if not implementing yet

### Set Up Testing Framework Early
**Issue:** Now need to add tests retroactively
**Solution:** 5 minutes to set up pytest would have paid off

### Record Demo Video During Build
**Issue:** Recreating things for demo later
**Solution:** Screen record interesting moments as you go

### Ask for Feedback Earlier
**Issue:** Built in isolation all day
**Solution:** Quick check-ins with team throughout day

---

## Surprising Discoveries

### 1. Socket Mode Exists!
Didn't know this was an option. Game changer for internal tools.

### 2. Claude Can Write Implementation Plans
The detailed task-by-task plans with test code, commands, expected output - incredibly useful.

### 3. MCP Server Architecture
Didn't realize it was stdio-based, not HTTP. Simpler than expected.

### 4. How Well Static Knowledge Works
Thought we'd need RAG immediately. Static knowledge base handles 80% of questions.

### 5. Tool Calling Maturity
OpenAI's tool calling API (used by LiteLLM) is really good. Claude decides when to use tools intelligently.

---

## Metrics Worth Tracking

If we deploy this, measure:

### Usage
- Questions asked per day
- Unique users per week
- Repeat users (sign of value)

### Quality
- Thumbs up/down on answers
- Follow-up questions (sign of incomplete answer?)
- Questions that couldn't be answered

### Impact
- Time saved (vs asking in Slack)
- Reduction in support questions to team
- Onboarding time for new engineers

### Cost
- API calls per day
- Cost per question
- Cost per team

---

## Resources Created

### Code
- ✅ Working Slack bot
- 🏗️ Shared knowledge library (in progress)
- 🏗️ MCP server (in progress)
- ✅ Comprehensive knowledge base

### Documentation
- ✅ Exploration day summary
- ✅ Demo script
- ✅ This lessons learned doc
- ✅ Implementation plans
- ✅ Architecture diagrams

### Artifacts
- ✅ `.env` template
- ✅ `requirements.txt`
- ✅ Test fixtures
- ✅ Git repo with history

---

## Key Insights for Future Projects

1. **Start with user problem** - Tech follows, not leads
2. **Security by default** - Don't make it optional
3. **Document as you build** - Not after
4. **Iterate quickly** - Perfection is the enemy
5. **Share early** - Get feedback sooner
6. **Use company tools** - Don't reinvent
7. **Think about interfaces** - Who uses it matters
8. **Test matters** - But match rigor to phase
9. **UX matters** - Even for internal tools
10. **Have fun** - This should be exciting!

---

## Questions This Raises

### Technical
- How do we handle knowledge base updates over time?
- What's our caching strategy for Phase 2?
- How do we measure answer accuracy?

### Organizational
- Who "owns" this bot if it's successful?
- What's the support model?
- How do we handle feature requests?

### Strategic
- Should other teams build similar bots for their systems?
- Is this a pattern worth standardizing?
- What's the ROI calculation?

---

## Thank You

To everyone who:
- Answered questions in Slack
- Wrote the excellent GL Publisher docs
- Built the LiteLLM infrastructure
- Gave me exploration day time
- Will give feedback on this!

---

*Remember: Exploration days are about learning, not just building. The insights matter as much as the artifact.*

---

## Action Items

### This Week
- [ ] Complete MCP server implementation
- [ ] Add tests to Slack bot
- [ ] Demo to BOR Write team
- [ ] Collect feedback

### Next Sprint
- [ ] Address feedback from demo
- [ ] Plan Phase 2 features
- [ ] Write production deployment plan
- [ ] Set up metrics/monitoring

### Future
- [ ] Share learnings in tech blog?
- [ ] Present at engineering all-hands?
- [ ] Help other teams build similar tools?

---

**Most Important Lesson:** Building AI tools is like building any tool - start with real problems, ship quickly, iterate based on feedback. The AI part doesn't change good product development fundamentals.
