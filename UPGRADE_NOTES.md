# 📋 Dependency Upgrade Guide for SarkariSarthi 2.0

## 🔄 Upgrade Summary

This document outlines all dependency upgrades made to modernize SarkariSarthi and ensure compatibility with the latest versions.

---

## 📊 Upgrade Details

### Core Web Scraping & Parsing
| Package | Old Version | New Version | Change | Reason |
|---------|-------------|-------------|--------|--------|
| requests | 2.31.0 | 2.32.3 | +0.1.3 | Security & bug fixes |
| beautifulsoup4 | 4.12.2 | 4.13.1 | +0.0.9 | Performance improvements |
| lxml | 4.9.3 | 4.10.0 | +0.0.7 | Security patches |
| selenium | 4.15.2 | 4.26.1 | +11.9 | **Critical security updates** |

### Date & Time Utilities
| Package | Old Version | New Version | Change | Reason |
|---------|-------------|-------------|--------|--------|
| python-dateutil | 2.8.2 | 2.8.2 | - | Already latest |
| pytz | 2023.3 | 2023.3 | - | Already latest |
| schedule | 1.2.0 | 1.2.1 | +0.0.1 | Minor bug fixes |

### CLI / UX Utilities
| Package | Old Version | New Version | Change | Reason |
|---------|-------------|-------------|--------|--------|
| tqdm | 4.66.1 | 4.66.1 | - | Already latest |
| colorlog | 6.8.0 | 6.8.2 | +0.0.2 | Bug fixes |
| pyyaml | 6.0.1 | 6.0.1 | - | Already latest |

### PDF Parsing
| Package | Old Version | New Version | Change | Reason |
|---------|-------------|-------------|--------|--------|
| PyMuPDF | 1.23.8 | 1.23.8 | - | Already latest |
| pdfplumber | 0.10.3 | 0.10.3 | - | Already latest |

### 🤖 AI & NLP (Language Understanding) - **CRITICAL**
| Package | Old Version | New Version | Change | Reason |
|---------|-------------|-------------|--------|--------|
| transformers | 4.35.2 | 4.41.2 | +6.0 | **Major: New models, performance** |
| torch | 2.1.1 | 2.5.1 | +4.0 | **Major: GPU/CPU optimization** |
| spacy | 3.7.2 | 3.8.1 | +0.1.0 | NLP improvements |
| openai | 1.3.5 | 1.52.0 | +50.0 | **BREAKING CHANGES - See below** |

### Data Handling
| Package | Old Version | New Version | Change | Reason |
|---------|-------------|-------------|--------|--------|
| pandas | 2.1.3 | 2.2.3 | +0.1.0 | Performance & features |
| numpy | 1.25.2 | 1.26.4 | +0.1.2 | Stability improvements |

### Telegram Bot Integration
| Package | Old Version | New Version | Change | Reason |
|---------|-------------|-------------|--------|--------|
| python-telegram-bot | 20.7 | 21.3 | +0.6 | API improvements |

### File, Env & System Utilities
| Package | Old Version | New Version | Change | Reason |
|---------|-------------|-------------|--------|--------|
| pathlib2 | 2.3.7.post1 | 2.3.7.post1 | - | Already latest |
| python-dotenv | 1.0.0 | 1.0.0 | - | Already latest |

### Testing & Coverage
| Package | Old Version | New Version | Change | Reason |
|---------|-------------|-------------|--------|--------|
| pytest | 7.4.3 | 7.4.4 | +0.0.1 | Bug fixes |
| pytest-cov | 4.1.0 | 4.1.0 | - | Already latest |

### Backend (API, Frontend Integration)
| Package | Old Version | New Version | Change | Reason |
|---------|-------------|-------------|--------|--------|
| flask | 3.0.0 | 3.0.3 | +0.0.3 | Security patches |
| flask-cors | 4.0.0 | 4.0.1 | +0.0.1 | Minor updates |

---

## 🚨 CRITICAL BREAKING CHANGES

### 1. **OpenAI 1.3.5 → 1.52.0** (MAJOR UPGRADE)

**Breaking Changes:**
- API client initialization has changed
- Async client usage pattern modified
- Response objects restructured
- Error handling changed

**Code Migration Required:**

#### Old Code (1.3.5):
```python
from openai import OpenAI

client = OpenAI(api_key="your-key")
response = client.Completion.create(
    model="gpt-3.5-turbo",
    prompt="Your prompt"
)
```

#### New Code (1.52.0):
```python
from openai import OpenAI

client = OpenAI(api_key="your-key")
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Your prompt"}]
)
```

**Action Required:** Update `fetch_jobs.py` to use the new OpenAI API format.

---

### 2. **PyTorch 2.1.1 → 2.5.1** (MAJOR UPGRADE)

**Changes:**
- New performance optimizations for transformers
- Updated CUDA compatibility
- Better memory management

**No Breaking Changes** - but models may load differently

**Action:** Reinstall and test model loading

---

### 3. **Transformers 4.35.2 → 4.41.2** (MAJOR UPGRADE)

**Changes:**
- New model implementations
- Improved tokenizer efficiency
- API consistency improvements

**Action:** Test all NLP models (summarization, NER, classification)

---

## 🧪 Testing Checklist

Before merging to main, test the following:

- [ ] **Install dependencies**: `pip install -r requirements.txt`
- [ ] **Web Scraping**: Run `python fetch_jobs.py` and verify job fetching works
- [ ] **AI Processing**: Test summarization on sample job descriptions
- [ ] **NER/Classification**: Verify category detection and skill extraction
- [ ] **Telegram Bot**: Send test message via telegram integration
- [ ] **Flask API**: Start Flask backend and verify endpoints work
- [ ] **Unit Tests**: Run `pytest tests/ -v`
- [ ] **Coverage**: Run `pytest tests/ --cov=. --cov-report=html`

---

## 🔄 How to Test Locally

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install upgraded requirements
pip install -r requirements.txt

# 3. Test individual components
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
python -c "import openai; print(f'OpenAI: {openai.__version__}')"

# 4. Run full test suite
pytest tests/ -v --tb=short

# 5. Test job scraper
python fetch_jobs.py --dry-run

# 6. Test telegram integration
python telegram_notifier.py --test
```

---

## ⚠️ Potential Issues & Solutions

### Issue 1: GPU Memory Issues with PyTorch 2.5.1
**Solution:** Set environment variable before running:
```bash
export CUDA_VISIBLE_DEVICES=0
python fetch_jobs.py
```

### Issue 2: OpenAI API Rate Limiting
**Solution:** Add retry logic:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def call_openai_api():
    # Your OpenAI call here
    pass
```

### Issue 3: Selenium WebDriver Compatibility
**Solution:** Update ChromeDriver to match installed Selenium version (4.26.1)
```bash
# Download from: https://googlechromelabs.github.io/chrome-for-testing/
```

---

## 🚀 Deployment Steps

1. **Create Pull Request**: From `deps/upgrade-dependencies` to `main`
2. **Run CI/CD Tests**: Wait for GitHub Actions to complete
3. **Code Review**: Review all changes
4. **Merge**: Merge to main branch
5. **Deploy**: GitHub Actions will auto-deploy to GitHub Pages
6. **Monitor**: Check logs for any errors

---

## 📝 Files Modified

- ✅ `requirements.txt` - Updated all dependencies

---

## 🔙 Rollback Instructions

If issues arise, rollback is simple:

```bash
# Revert to previous commit
git revert 4eef17d85447f5a02724314ad073d21575b3b58d

# Or switch back to main
git checkout main
```

---

## 📞 Support & Questions

If you encounter any issues during the upgrade:

1. Check the **Testing Checklist** above
2. Review **Potential Issues** section
3. Check GitHub Actions logs for deployment errors
4. Open an issue with error details

---

## ✅ Sign-off Checklist

- [ ] All tests pass locally
- [ ] No breaking changes in core functionality
- [ ] Telegram notifications working
- [ ] AI/NLP models loading correctly
- [ ] Web scraping functioning properly
- [ ] Ready to merge to main

---

**Last Updated:** May 13, 2026
**Upgrade Branch:** `deps/upgrade-dependencies`
**Status:** ✅ Ready for Testing
