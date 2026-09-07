# Supra Hospital AI Assistant - Setup & Run Guide

## 🚀 Quick Start (5 minutes)

### Step 1: Install Python Dependencies
```bash
cd supra-hospital-ai
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Set API Key
Get your Anthropic API key from https://console.anthropic.com

**Linux/Mac:**
```bash
export ANTHROPIC_API_KEY=sk-ant-...your-key-here...
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-...your-key-here..."
```

**Windows (CMD):**
```cmd
set ANTHROPIC_API_KEY=sk-ant-...your-key-here...
```

### Step 3: Start the Backend
```bash
python backend.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Open the App
1. Open your browser
2. Navigate to: `http://127.0.0.1:8000`
3. You should see the Supra Hospital AI Assistant interface

### Step 5: Test It
1. Click any test query (e.g., "What pain medication should I give a post-TKR patient?")
2. The system will submit it automatically and:
   - Search the knowledge base for relevant protocols
   - Fetch a context-aware response from Claude
   - Display protocols and alerts
   - Show confidence level

---

## 📋 Project Structure

```
supra-hospital-ai/
├── backend.py                 # FastAPI backend with Claude integration
├── frontend.html              # React-based web UI
├── knowledge-base.json        # Hospital protocols and patient alerts
├── requirements.txt           # Python dependencies
├── SETUP.md                   # This file
├── DESIGN_DOCUMENT.md         # 10-page architecture document
└── README.md                  # Quick reference
```

---

## 🏥 What's Inside

### Knowledge Base (knowledge-base.json)
Contains Supra Hospital's institutional knowledge:
- **8 Medical Protocols** (Post-TKR Pain, DVT Prophylaxis, Sepsis, etc.)
- **2 Patient Alerts** (Rajan with cardiac stent, Mrs. Padma with diabetes)
- **Hospital Formulary** (Preferred drug brands)
- **Medical Equipment Preferences** (Implants, etc.)
- **Emergency Codes**

### Backend (backend.py)
FastAPI server with:
- `/query` → Context-aware medical queries
- `/protocols` → Browse all hospital protocols
- `/alerts` → View patient safety alerts
- `/formulary` → Check drug preferences
- `/hospital-info` → Hospital details

**Key Features:**
- Searches knowledge base for relevant protocols
- Passes hospital context to Claude API
- Highlights patient alerts
- Prioritizes Supra-specific protocols over generic advice

### Frontend (frontend.html)
Single-file React app with:
- **Query Interface**: Input queries with role selection
- **Test Queries**: 5 pre-built test cases
- **Response Display**: Shows Claude's answer with relevant protocols
- **Alert Highlighting**: Critical patient information emphasized
- **Confidence Badges**: Shows how well the system matched the query

---

## 🧪 Test These Queries

The system is loaded with these test cases. Try them all:

1. **"What pain medication should I give a post-TKR patient?"**
   - ✅ Should mention Supra's Paracetamol 650mg QDS protocol
   - ✅ Should WARN about Supra's NSAID ban after TKR
   - ❌ ChatGPT would suggest NSAIDs (generic approach)

2. **"Patient Rajan has knee pain, what should I prescribe?"**
   - ✅ Should trigger CRITICAL alert about Rajan's cardiac stent
   - ✅ Should refuse all NSAIDs explicitly
   - ✅ Should suggest only safe alternatives
   - ❌ ChatGPT wouldn't know Rajan's history

3. **"When should I start DVT prophylaxis after surgery?"**
   - ✅ Should mention Supra's 12-hour post-op timing
   - ✅ Should mention Enoxaparin 40mg SC dosing
   - ✅ Should mention 14-day (TKR) vs 28-day (THR) durations
   - ❌ ChatGPT would give generic timings

4. **"What's our sepsis protocol?"**
   - ✅ Should mention Supra's tight 1-hour lactate window
   - ✅ Should mention Supra's specific fluid/vasopressor approach
   - ✅ Should note this is v3 (2026) - more aggressive than older versions
   - ❌ ChatGPT would cite generic sepsis bundles

5. **"Tell me about Mrs. Padma's medication management"**
   - ✅ Should highlight her diabetes + Ekadashi fasting pattern
   - ✅ Should mention insulin timing adjustment protocol
   - ✅ Should note her previous hypoglycemia episodes
   - ❌ ChatGPT wouldn't have any patient-specific knowledge

---

## 🔧 Troubleshooting

### "Connection refused" on port 8000
- Make sure backend is running: `python backend.py`
- Check if port 8000 is already in use: `lsof -i :8000` (Mac/Linux)

### "API key not configured"
- Did you set the `ANTHROPIC_API_KEY` environment variable?
- Check: `echo $ANTHROPIC_API_KEY` (Mac/Linux) or `echo %ANTHROPIC_API_KEY%` (Windows)

### "ModuleNotFoundError: No module named 'fastapi'"
- Run: `pip install -r requirements.txt`

### "CORS error in browser console"
- Backend's CORS middleware should handle this
- Try hard-refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)

### Frontend shows "No response" or blank
- Open browser developer console (F12)
- Check the Network tab - look for failed requests to localhost:8000
- Make sure backend is running and accessible

---

## 📊 Performance Notes

- **Query Response Time**: 3-8 seconds (mostly Claude API latency)
- **Knowledge Base Search**: <100ms
- **Concurrent Users**: Limited by Claude API rate limits (shared tier)

---

## 🔐 Security Notes

⚠️ **This is a prototype.** For production deployment:
1. **API Keys**: Use environment variables, never hardcode
2. **CORS**: Restrict to hospital network only
3. **Authentication**: Add role-based access control
4. **Data**: Encrypt sensitive patient information
5. **Audit Logging**: Log all queries and responses
6. **Compliance**: Ensure HIPAA/GDPR compliance
7. **Rate Limiting**: Implement per-user query limits

---

## 🚀 Next Steps for Production

1. **Database**: Move knowledge base to SQL Server/PostgreSQL
2. **Vector Search**: Add embeddings for faster protocol matching
3. **Role-Based Access**: Implement permission system
4. **Audit Trail**: Log all medical queries for compliance
5. **Integration**: Connect to hospital EHR system
6. **Mobile App**: Build native iOS/Android versions
7. **Offline Mode**: Cache frequently accessed protocols

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify environment setup
3. Check Claude API console for rate limits
4. Review backend logs for detailed errors

---

## 📄 Additional Resources

- **Design Document**: See `DESIGN_DOCUMENT.md` (10-page architecture)
- **API Reference**: See `backend.py` for endpoint documentation
- **Knowledge Base**: See `knowledge-base.json` for all protocols
