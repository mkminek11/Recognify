# 🧠 Recognify

<div align="center">

**A smart flashcard learning tool that extracts images from presentations and turns them into interactive study sets**

[Features](#-features) •
[Quick Start](#-quick-start) •
[Installation](#-installation) •
[Usage](#-usage)

</div>

---

## 🎯 What is Recognify?

Recognify is an intelligent study tool that revolutionizes how you learn with visual content. Upload PowerPoint presentations, and Recognify automatically extracts images and text labels to create interactive flashcard sets. Perfect for biology, anatomy, geography, art history, or any subject with visual components!

### ✨ Key Highlights

- 🖼️ **Automatic Image Extraction** - Upload presentations and get instant flashcard sets
- 🎮 **Interactive Learning** - Keyboard and mouse-controlled quiz interface  
- 🔄 **Smart Workflows** - Number-to-label mapping for rapid data entry
- 📱 **Modern UI** - Responsive design with Alpine.js reactivity
- 🔐 **User Management** - Secure authentication and personal collections
- 🌐 **URL Support** - Add images directly from web URLs (with proper headers for Wikimedia!)

---

## 🚀 Features

### 📚 **Content Creation**
- **Presentation Processing**: Extract images and labels from PowerPoint files automatically
- **Manual Upload**: Add individual images via file upload or URL
- **Smart Labeling**: Quick number-to-label mapping workflow
- **Draft System**: Work-in-progress management with auto-save

### 🎯 **Learning Interface**
- **Flashcard Mode**: Interactive image recognition quizzes
- **Adaptive Learning**: Skip familiar images to focus on challenging content
- **Performance Tracking**: Track correct/incorrect answers
- **Flexible Controls**: Keyboard shortcuts and mouse controls

---

## ⚡ Quick Start

**Try Recognify now:** [https://recognify.onrender.com](https://recognify.onrender.com)

No installation required! Just visit the link above and start creating your first flashcard set! 🎉

### For Local Development

```bash
# Clone the repository
git clone https://github.com/mkminek11/recognify.git
cd recognify

# Install dependencies
pip install -e .

# Set environment variables (create .env file)
SECRET_KEY=your-super-secret-key
HASHID_SALT=your-unique-salt

# Run the application
python main.py
```

Visit `http://127.0.0.1:5000` for local development.

---

## 🔧 Installation

### Access Online
**No installation needed!** Visit [https://recognify.onrender.com](https://recognify.onrender.com) to use Recognify immediately.

### Local Development Setup

For developers who want to run Recognify locally:

#### Prerequisites
- Python 3.12+
- Modern web browser with JavaScript enabled

#### Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/mkminek11/recognify.git
   cd recognify
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # source .venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   ```

4. **Configure environment**
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-super-secret-key
   HASHID_SALT=your-unique-salt
   FLASK_ENV=development
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

The database will be created automatically on first run.

---

## 📖 Usage

### Creating Your First Set

1. **Sign Up/Login** - Create an account or log in
2. **Create New Set** - Click "Create a new set" from the dashboard
3. **Add Content**: Choose your method:
   - 📄 **Upload Presentation**: Drag & drop PowerPoint files for automatic extraction
   - 🖼️ **Manual Images**: Upload individual image files
   - 🔗 **Image URLs**: Paste direct image links from the web

### Smart Labeling Workflow

The number-to-label mapping feature speeds up data entry:

```
1. Upload presentation → Images extracted with labels
2. Type numbers (1-9) → Auto-fills corresponding labels
3. Tab to next image → Seamless workflow
4. Submit set → Ready for learning!
```

### Learning Interface

**Keyboard Controls:**
- `Space` - Reveal/hide answer
- `→ (Right Arrow)` - Mark correct, next image  
- `← (Left Arrow)` - Mark incorrect, next image
- `💡 Lightbulb Button` - Skip this image permanently

**Mouse Controls:**
- `Left Click` - Reveal answer or mark incorrect
- `Right Click` - Mark correct
- `Middle Click` - Reveal/hide answer

### Tips for Best Results

- **Presentations**: Use slides with clear images and text labels for best extraction
- **Image Quality**: Higher resolution images work better for recognition
- **Consistent Labeling**: Use clear, concise labels for better learning
- **Regular Practice**: Use the skip feature to focus on challenging images

---

## 🛠️ Technical Details

### Built With
- **Backend**: Flask, SQLAlchemy, python-pptx
- **Frontend**: Alpine.js, Axios, vanilla JavaScript
- **Database**: SQLite (default)
- **Authentication**: Flask-Login with session management

For detailed API documentation, see [API.md](API.md).

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ for visual learners**

</div>
