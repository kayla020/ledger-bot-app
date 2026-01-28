# Ledger Bot - Demo Script

**Duration:** 15 minutes
**Audience:** BOR Write team / Engineering managers
**Goal:** Show what was built and get feedback

---

## Setup (Before Demo)

**Terminal 1:**
```bash
cd /Users/kayla.lu/ledger-bot-app
python app.py
# Should show: "⚡️ Ledger Bot is running in Socket Mode!"
```

**Terminal 2:**
```bash
cd /Users/kayla.lu/ledger-bot-app
# Open for showing code/files
```

**Slack:**
- Open DM with Ledger Bot
- Have #bor-write-eng channel ready

**Browser:**
- README at `/Users/kayla.lu/ledger-bot-app/docs/EXPLORATION_DAY_SUMMARY.md`
- Architecture diagram ready (draw on whiteboard or have slide)

---

## Part 1: The Problem (2 minutes)

**Say:**
> "Today I explored using Claude to solve a team problem: onboarding to GL Publisher is hard. Teams ask us the same questions over and over - 'How do I create ledger lines?' 'What's an Impact Builder?' 'Why did my activity fail?'"
>
> "I wanted to see if we could build an AI assistant that knows our system inside and out."

**Show:**
- Point to `oracle-gl-publisher` repo complexity (many modules, ADRs, schemas)
- Mention scattered documentation problem

---

## Part 2: What I Built - Slack Bot (5 minutes)

**Say:**
> "I built Ledger Bot - a Slack bot powered by Claude that has comprehensive knowledge of GL Publisher."

### Demo 1: Basic Question

**In Slack DM to bot:**
```
What is GL Publisher?
```

**Point out:**
- "Thinking..." indicator (instant feedback)
- Comprehensive answer covering architecture
- Mentions key modules

### Demo 2: Technical Question

**Ask:**
```
How do I create ledger lines for a new activity type?
```

**Point out:**
- Step-by-step instructions
- Mentions Avro schema, Impact Builder, Kafka
- References specific files/patterns

### Demo 3: Troubleshooting

**Ask:**
```
My activity is stuck in NEW status, what should I check?
```

**Point out:**
- Actionable troubleshooting steps
- Specific things to check (logs, schema, etc.)

### Demo 4: Deep Knowledge

**Ask:**
```
What's an idempotency key and why does it matter?
```

**Point out:**
- References ADR 0007
- Explains historical context
- Shows where it's used in the system

---

## Part 3: Show the Knowledge Base (2 minutes)

**Terminal 2:**
```bash
cat knowledge_base.txt | head -50
```

**Say:**
> "The bot has 188 lines of curated knowledge covering:"

**Scroll through:**
- Architecture overview
- Oracle GL schema tables (all 5)
- How to create Impact Builders
- Common integration patterns
- Real ADR content
- Troubleshooting guides

**Say:**
> "I manually curated this from the README, CLAUDE.md, schema reference, and key ADRs. Quality over quantity - it's only 6.5KB so responses are fast."

---

## Part 4: Architecture & Security (2 minutes)

**Whiteboard/Diagram:**

```
┌─────────────────┐
│  Slack Bot      │
│  (Socket Mode)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Company        │
│  LiteLLM        │
│  Gateway        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Claude         │
│  Sonnet 4.5     │
└─────────────────┘
```

**Say:**
> "Key architecture decisions:"
> - **Socket Mode** - No webhooks, no ngrok (security approved)
> - **Company LiteLLM** - Uses our infrastructure, not external API
> - **Claude Sonnet 4.5** - Most intelligent model
> - **Python + Slack Bolt** - Fast to build, easy to maintain

---

## Part 5: The Vision - Hybrid Architecture (3 minutes)

**Say:**
> "But this is just phase 1. I designed it to support TWO interfaces:"

**Show diagram:**
```
┌─────────────────────────────┐
│  Shared Knowledge Library   │
│  - search_adrs()            │
│  - find_impact_builders()   │
│  - get_schema_info()        │
└────────┬───────────┬────────┘
         │           │
    ┌────▼─┐    ┌───▼────┐
    │Slack │    │  MCP   │
    │ Bot  │    │ Server │
    └──────┘    └────────┘
    (Teams)     (Personal)
```

**Explain:**
- **Slack Bot:** Team onboarding, quick questions, accessible to everyone
- **MCP Server:** Deep Claude Desktop integration for coding
- **Shared Library:** Write tools once, both use them (DRY)

**Show:**
```bash
cat docs/plans/2026-01-23-hybrid-bot-mcp-architecture.md | head -100
```

**Say:**
> "I wrote a detailed implementation plan. Actually running right now in another session - Claude is building it task-by-task while we talk!"

---

## Part 6: Use Cases (2 minutes)

### For Other Teams (Slack Bot)

**Scenario 1: New Integration**
> Engineer from another team: "@ledgerbot We're adding crypto staking rewards to the ledger. What do we need to do?"
> Bot would guide them through: schema → Impact Builder → testing

**Scenario 2: Debugging**
> "@ledgerbot Activities are failing with 'invalid code combination'. What does that mean?"
> Bot explains code combinations, references GL_CODE_COMBINATIONS table, common issues

**Scenario 3: Learning**
> New team member: "@ledgerbot Can you explain how reversals work?"
> Bot references ADR 0010, explains the pattern, shows where it's implemented

### For Your Team (MCP Server - Coming)

**Scenario: While Coding**
> You're implementing a new feature in your IDE
> Claude: "I see you're working with GL impacts. Let me search the ADRs..."
> Claude automatically finds relevant patterns, suggests code based on existing Impact Builders

---

## Part 7: Next Steps & Discussion (3 minutes)

### Phase 1 (This Week)
- ✅ Slack bot working (done today!)
- 🏗️ MCP server (implementing now)
- ⏭️ Testing both interfaces
- ⏭️ Add tests for Slack bot

### Phase 2 (Next Sprint)
- GraphQL API integration (query live activity status)
- Database access (check actual ledger state)
- Kafka monitoring (see what's in topics)
- Performance optimization (caching, indexing)

### Questions for Team

1. **Who should use it first?**
   - Beta with BOR Write only?
   - Open to specific teams asking lots of questions?
   - Announce company-wide?

2. **What knowledge gaps do you see?**
   - What questions should it answer that it can't yet?
   - What docs should be added?

3. **How should we measure success?**
   - Number of questions answered?
   - Time saved vs asking in Slack?
   - Quality of answers (feedback mechanism)?

4. **Cost management?**
   - Each question ~$0.01-0.05
   - Do we need rate limits?
   - Who pays for it?

5. **Maintenance?**
   - Who keeps knowledge base updated?
   - How often to refresh with new ADRs/changes?

---

## Closing

**Say:**
> "This was all built in one exploration day with Claude Code's help. The bot works now, the MCP server is building itself, and we have a solid architecture for expanding it."
>
> "Main value prop: Faster onboarding, less interruption of BOR Write team, better developer experience for teams integrating with our system."
>
> "I'd love your feedback - try the bot, tell me what works, what doesn't, what's missing."

**Show closing slide/summary:**
- ✅ Working Slack bot
- 🏗️ MCP server in progress
- 📋 Clear implementation plan
- 🎯 Phase 2 roadmap
- ❓ Need your input!

---

## Backup: If Things Go Wrong

### Bot Not Responding
**Fallback:** Show recordings or screenshots prepared in advance

### Question Bot Can't Answer Well
**Say:** "Great example of a gap in the knowledge base - this is exactly the kind of feedback we need!"

### Technical Issues
**Fallback:** Walk through the code instead
```bash
# Show app.py structure
# Show knowledge_base.txt
# Show implementation plan
```

---

## Post-Demo Actions

1. **Share in Slack:**
   - Post demo video/summary to #bor-write-eng
   - Invite people to try the bot
   - Link to documentation

2. **Collect Feedback:**
   - Create feedback form or Slack thread
   - What questions should it answer?
   - What would make it more useful?

3. **Iterate:**
   - Add common missing knowledge
   - Fix any issues found
   - Plan Phase 2 based on feedback

4. **Document:**
   - Update README with usage stats
   - Keep exploration day summary as reference
   - Share learnings in tech blog?

---

## Key Messages to Emphasize

1. **Built in One Day:** Shows rapid prototyping power of Claude Code
2. **Security First:** No ngrok, uses company infrastructure
3. **Scalable Design:** Shared library enables multiple interfaces
4. **Real Value:** Solves actual team pain (onboarding, repeated questions)
5. **Extensible:** Easy to add more knowledge, tools, capabilities

---

## Demo Checklist

**Before:**
- [ ] Bot running and responding
- [ ] Terminal windows set up
- [ ] Slack DM open
- [ ] Files ready to show
- [ ] Diagram ready

**During:**
- [ ] Start on time
- [ ] Show > Tell (demos, not just slides)
- [ ] Leave time for questions
- [ ] Take notes on feedback

**After:**
- [ ] Share summary doc
- [ ] Collect feedback
- [ ] Plan next iteration
- [ ] Thank the team!

---

*Good luck with the demo! Remember: It's an exploration day project - emphasize the learning and potential, not perfection.*

---

## Addendum: How to Try the MCP Server

### During Demo

**Say:**
> "The MCP server is a personal tool - each of you installs it on your own machine. It integrates with Claude Desktop."

**Show:**
- Installation guide at `mcp-server/TEAM_INSTALL_GUIDE.md`
- Mention it takes ~10 minutes

**Offer:**
> "I can do installation office hours this week if anyone wants help getting it set up."

### After Demo

**In Slack post:**
```
Thanks for attending the Ledger Bot demo!

Quick links:
📚 Full summary: [link to EXPLORATION_DAY_SUMMARY.md]
💬 Try Slack bot: DM @ledgerbot
💻 Install MCP server: [link to TEAM_INSTALL_GUIDE.md]
❓ Questions: Reply here or DM me

The Slack bot is ready to use now. MCP server requires ~10 min setup.
```

### Installation Support

**Set up:**
- Office hours (e.g., Thu 2-3pm)
- Or 1:1 pairing sessions
- Document common issues in FAQ

**Track:**
- Who installed it
- What issues they hit
- What questions come up
→ Use to improve install guide

