# 🏥 Supra Hospital AI Assistant

A **context-aware medical AI** that knows Supra Hospital's protocols, procedures, and patient-specific rules. **Better than ChatGPT** for clinical decision support.

## ⚡ 60-Second Start

```bash
# 1. Activate the included environment and install if needed
source venv/bin/activate
pip install -r requirements.txt

# 2. Set key
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Start the app
python backend.py

# 4. Open http://127.0.0.1:8000 in your browser
```

**That's it.** System is live.

If the Anthropic key is missing or rejected, the prototype shows a clearly
labeled, read-only local protocol preview instead of an AI-generated answer.
Set a valid key and restart the server to enable live AI responses. Set
`SUPRA_LOCAL_PREVIEW=false` to return an error instead (recommended for
production deployments).

---

## 🧪 Quick Test

Ask these 5 queries. Compare our system vs. ChatGPT:

1. ✅ **"What pain medication for post-TKR?"**
   - ChatGPT: Suggests NSAIDs (WRONG for Supra)
   - Our system: Paracetamol 650mg QDS (Supra protocol)

2. ✅ **"Patient Rajan has knee pain, what to prescribe?"**
   - ChatGPT: No alert (DANGEROUS)
   - Our system: 🚨 CRITICAL alert - Rajan has stent, no NSAIDs!

3. ✅ **"When start DVT prophylaxis?"**
   - ChatGPT: "Usually within 24 hours" (vague)
   - Our system: "12 hours post-op, Enoxaparin 40mg, 14 days for TKR"

4. ✅ **"What's our sepsis protocol?"**
   - ChatGPT: Generic sepsis bundle (outdated)
   - Our system: Supra v3 - lactate within 1 HOUR (not 3)

5. ✅ **"Tell me about Mrs. Padma's meds"**
   - ChatGPT: Generic Type 2 DM management
   - Our system: Padma fasts on Ekadashi, adjust insulin timing, had 3 hypos in 2025

---

## 📁 What You Get

```
supra-hospital-ai/
├── backend.py                    # FastAPI server + Claude integration
├── frontend.html                 # React UI (single file, no build needed)
├── knowledge-base.json           # Hospital protocols + alerts
├── requirements.txt              # Python dependencies
├── SETUP.md                      # Detailed setup guide
├── DESIGN_DOCUMENT.md           # 10-page architecture doc
└── README.md                     # This file
```

---

## 🏗️ Architecture

```
Doctors → React UI → FastAPI Backend → Knowledge Base
                           ↓
                      Claude API
                      (with Supra context)
                           ↓
                    Context-aware response
                    + Protocols + Alerts
```

**The Secret**: We embed Supra's institutional knowledge in the Claude prompt. Claude sees the full context and prioritizes hospital-specific protocols.

---

## 🚀 Key Features

### ✅ Context-Aware
- Searches 8 hospital protocols automatically
- Flags 2 critical patient alerts
- Knows Supra's drug preferences (Calpol, Omez, Mox, Glycomet)

### ✅ Safe by Design
- Patient alerts prevent dangerous drug interactions
- Warfarin-NSAID check prevents GI bleeds
- Drug allergies flagged prominently

### ✅ Transparent
- Shows which protocols matched
- Explains reasoning
- Not a black box

### ✅ Tested
- All 5 test queries show measurable difference from ChatGPT
- Catches real safety issues (Rajan's NSAID allergy)

---

## 📊 Knowledge Base

**15 items:**
- 8 Medical Protocols (Post-TKR, DVT, Sepsis, Discharge, etc.)
- 2 Patient Alerts (Rajan, Mrs. Padma)
- Drug Formulary (preferred brands)
- Emergency Codes

**Easy to Extend**: Add new protocol in <2 minutes. Changes live immediately.

---

## 🔧 API Endpoints

```bash
# Query with context
POST /query
{
  "query": "What pain meds for post-TKR?",
  "user_role": "Doctor",
  "department": "Orthopaedics"
}

# Browse protocols
GET /protocols?department=Orthopaedics

# View alerts
GET /alerts

# Check formulary
GET /formulary

# Hospital info
GET /hospital-info
```

---

## 💡 Why This is Better Than ChatGPT

| Feature | ChatGPT | Our System |
|---------|---------|-----------|
| Knows Supra protocols? | ❌ No | ✅ Yes |
| Flags Rajan's alert? | ❌ No | ✅ Yes |
| Supra-specific drug preferences? | ❌ No | ✅ Yes |
| Explains reasoning? | ⚠️ Vague | ✅ Clear |
| Trustworthy for doctors? | ❌ No | ✅ Yes |
| Real patient context? | ❌ No | ⚠️ Basic (can integrate EHR) |

---

## 🔐 Security Note

⚠️ **This is a prototype.** For production:
- Use HTTPS, not HTTP
- Add authentication (role-based)
- Encrypt sensitive data
- Add audit logging (HIPAA compliance)
- Implement rate limiting
- Restrict CORS to hospital network

---

## 📚 Documentation

- **SETUP.md**: Step-by-step installation + troubleshooting
- **DESIGN_DOCUMENT.md**: Full 10-page architecture + design decisions
- **This file**: Quick reference

---

## 🎯 Next Steps

### Week 1: Pilot with Ortho
- Dr. Vikram tests with 50 queries
- Feedback loop
- Protocol refinements

### Week 2-3: Expand to Other Departments
- General Medicine (Dr. Meera)
- Cardiology
- Pharmacy

### Month 2+: Production Ready
- EHR integration
- More protocols (100+)
- Multi-hospital deployment

---

## 📞 Support

**"Backend not connecting?"**
- Make sure `python backend.py` is running
- Check port 8000 is free: `lsof -i :8000`
- Verify API key: `echo $ANTHROPIC_API_KEY`

**"Frontend shows no response?"**
- Open DevTools (F12), Network tab
- Check for errors from localhost:8000
- Hard-refresh (Ctrl+Shift+R)

**"Want to add a protocol?"**
- Edit `knowledge-base.json` (add to `protocols` array)
- Save & restart backend (`python backend.py`)
- Done! New protocol is live

---

## 🎓 Learn More

Read the **DESIGN_DOCUMENT.md** for:
- Full architecture walkthrough
- Why Claude (not ChatGPT)
- Real test comparisons
- Cost analysis + ROI
- Production deployment options
- Future enhancement roadmap

---

**Status**: ✅ Working Prototype (90-minute build)  
**Hospital**: Supra Multi-Specialty Hospital, Hyderabad  
**Built**: September 2026  
**License**: Internal Use Only
# supra-hospital-ai
