# Quick Start Guide

Get up and running with the Grok Agentic Research Framework in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Up API Key

1. Get your Grok API key from [console.x.ai](https://console.x.ai)
2. Use promo code `grok_eng_b4d86a51` for $20 free credits
3. Create a `.env` file:

```bash
cp .env.example .env
```

4. Edit `.env` and add your key:
```
GROK_API_KEY=your_api_key_here
```

## Step 3: Test Setup

```bash
python test_setup.py
```

This will verify:
- ✅ All dependencies are installed
- ✅ Configuration is correct
- ✅ Data generation works
- ✅ Retrieval system works
- ✅ API connection (if key is set)

## Step 4: Run Your First Query

### Interactive Mode
```bash
python main.py
```

Then enter a query like:
```
What are people saying about AI safety?
```

### Single Query Mode
```bash
python main.py --query "What are the main trends in tech discussions?"
```

## Example Queries to Try

1. **Trend Analysis**
   ```
   What are people saying about AI?
   ```

2. **Information Extraction**
   ```
   Find posts about Python from verified accounts
   ```

3. **Comparison**
   ```
   Compare sentiment about crypto vs traditional finance
   ```

4. **Temporal Analysis**
   ```
   How has sentiment changed over time?
   ```

## Understanding the Output

The agent will:
1. **Plan** - Break down your query into steps
2. **Execute** - Retrieve relevant data
3. **Analyze** - Deep analysis of results
4. **Refine** - Iteratively improve if needed
5. **Summarize** - Generate final answer

Results are saved to `output/research_result.json`

## Troubleshooting

### "GROK_API_KEY not found"
- Make sure `.env` file exists and contains `GROK_API_KEY=...`
- Or set environment variable: `export GROK_API_KEY=your_key`

### API Errors
- Check your API key is valid
- Verify you have credits in your account
- Check [xAI docs](https://docs.x.ai) for latest API endpoint

### No Results Found
- Mock data will auto-generate on first run
- Check `data/mock_x_data.json` exists
- Try broader search terms

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [MODEL_SELECTION.md](MODEL_SELECTION.md) for model configuration
- Customize `config.py` for your needs
- Add your own data to `data/` directory

## Need Help?

- Check the README for detailed documentation
- Review error messages - they include helpful tips
- Test individual components with `test_setup.py`

Happy researching! 🔍
