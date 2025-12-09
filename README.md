# 📢 Social Media Agent

A Python-based AI-powered social media content generator that creates posts, images, and video scripts for Instagram and other platforms.

## ✨ Features

- 🤖 **AI-Generated Posts**: Creates 3 unique social media posts using GPT-4
- 🎨 **AI Image Generation**: Generates branded images using FLUX AI model
- 🖼️ **Custom Image Support**: Upload your own designs
- 🎬 **Video Reel Scripts**: Creates TikTok/Instagram Reel scripts with scenes
- 📤 **Auto-Publishing**: Sends content to Instagram via Zapier webhook
- 💾 **Result Storage**: Saves all outputs to JSON files
- 🖥️ **Streamlit Dashboard**: User-friendly web interface

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd social-media-agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.template .env
```

Edit `.env` and add your API keys:

```env
OPENAI_API_KEY=sk-proj-...
ZAPIER_WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/...
REPLICATE_API_TOKEN=r8_...
```

### 4. Run the Application

**Option A: Streamlit Dashboard (Recommended)**
```bash
streamlit run dashboard.py
```

**Option B: Command Line**
```bash
python run.py
```

## 🔑 API Keys Setup

### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy and paste into `.env`

### Replicate API Token
1. Visit [Replicate Account](https://replicate.com/account/api-tokens)
2. Create a new token
3. Copy and paste into `.env`

### Zapier Webhook URL
1. Create a Zapier account at [zapier.com](https://zapier.com)
2. Create a new Zap with a "Webhooks by Zapier" trigger
3. Choose "Catch Hook"
4. Copy the webhook URL
5. Connect it to Instagram or other social media actions

## 📁 Project Structure

```
social-media-agent/
│
├── config.py              # Configuration loader (loads from .env)
├── main.py                # Main pipeline orchestrator
├── tools.py               # Core functions (posts, images, scripts)
├── dashboard.py           # Streamlit web interface
├── run.py                 # Command-line runner
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (YOU CREATE THIS)
├── .gitignore            # Git ignore file
├── README.md             # This file
│
└── images/               # Generated/uploaded images (auto-created)
```

## 🎯 Usage Examples

### Dashboard Usage

1. Run: `streamlit run dashboard.py`
2. Enter a topic (e.g., "AI in Education UAE")
3. Choose options:
   - ☑️ Generate AI Images
   - ☑️ Use Custom Image (upload your own)
   - ☑️ Post to Instagram
4. Click "🚀 Run Campaign"
5. View results in the dashboard

### Command Line Usage

Edit `run.py` settings:

```python
TOPIC = "Sustainable Energy in UAE"
GENERATE_IMAGE = True
USE_CUSTOM_IMAGE = False
PUSH_TO_ZAPIER = True
```

Then run:
```bash
python run.py
```

## 📋 Configuration Options

| Parameter | Type | Description |
|-----------|------|-------------|
| `topic` | str | Main theme for content generation |
| `generate_image` | bool | Generate AI images using FLUX |
| `use_custom_image` | bool | Use uploaded custom image |
| `custom_image_path` | str | Path to custom image file |
| `push_to_zap` | bool | Send to Instagram via Zapier |

## 🎨 Image Generation

The agent uses **FLUX Schnell** by Black Forest Labs to generate:
- Ultra-realistic commercial photographs
- UAE-themed locations (Dubai/Abu Dhabi)
- Golden hour lighting
- 16:9 aspect ratio
- Automatic brand text overlay ("Experts Group FZE")

## 📤 Output Format

Results are saved as JSON files with timestamp:

```json
{
  "topic": "AI in Education UAE",
  "posts": [...],
  "image_prompts": [...],
  "reel_script": {...},
  "images": {"image_urls": [...]},
  "zapier_status": {...}
}
```

## 🛡️ Security Notes

- **NEVER commit `.env` or `config.py` to Git**
- The `.gitignore` file protects these automatically
- Regenerate API keys if accidentally exposed
- Keep your Zapier webhook URL private

## 🐛 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt --upgrade
```

### "API key not found" errors
- Check `.env` file exists
- Verify API keys are correct
- Ensure no extra spaces in `.env`

### Font errors on Linux/Mac
The app automatically detects your system font. If issues occur:
- **Linux**: Install DejaVu fonts
- **Mac**: Default Helvetica should work

### Zapier not receiving data
- Test webhook URL in browser
- Check Zapier dashboard for errors
- Verify webhook is turned ON

## 📦 Dependencies

- `openai` - GPT-4 text generation
- `replicate` - FLUX image generation
- `streamlit` - Web dashboard
- `Pillow` - Image processing
- `requests` - HTTP requests
- `python-dotenv` - Environment variables

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - feel free to use for personal or commercial projects.

## 🆘 Support

For issues or questions:
- Open a GitHub issue
- Check existing issues for solutions
- Review the troubleshooting section

## 🎉 Acknowledgments

- OpenAI for GPT-4
- Black Forest Labs for FLUX
- Replicate for API hosting
- Zapier for automation

---

**Made with ❤️ for automated social media management**