# Recognify

**Recognify** is a web-based application designed to help users practice recognizing animals, plants, and other objects from images. The platform allows users to create interactive learning sets by importing images from presentations or uploading custom images, associating them with labels, and organizing them into topics for practice and study.

## 🎯 Purpose

Recognify enables users to:
- Import images from PowerPoint presentations
- Create custom labels for images (either from slide text or custom-written)
- Organize images into learning sets
- Practice object recognition through interactive gameplay
- Share learning sets with other users

## 🏗️ Project Structure

```
recognify/
├── 📁 app/                   # Main Flask application package
│   ├── 📄 __init__.py        # Package initialization
│   ├── 📄 db.py              # Database configuration
│   ├── 📄 lib.py             # Core Flask app setup and utilities
│   ├── 📄 models.py          # SQLAlchemy database models
│   └── 📁 routes/            # Application routes (blueprints)
│       ├── 📄 admin.py       # Admin panel routes
│       └── 📄 main.py        # Main application routes
│
├── 📁 instance/              # Flask instance folder
│   └── 📄 db.sqlite          # SQLite database file
│
├── 📁 static/                # Static assets (CSS, JS, images)
│   ├── 📁 css/               # Stylesheets
│   ├── 📁 js/                # JavaScript files
│   │   ├── 📁 alpine/        # Alpine.js library
│   │   └── 📁 htmx/          # HTMX library
│   └── 📁 uploads/           # User uploaded images
│
├── 📁 templates/             # Jinja2 HTML templates
│   └── 📄 base.html          # Base template
│
├── 📁 .venv/                 # Python virtual environment
├── 📄 .flaskenv              # Flask environment variables
├── 📄 .python-version        # Python version specification
├── 📄 main.py                # Application entry point
├── 📄 pyproject.toml         # Project configuration and dependencies
├── 📄 uv.lock                # Dependency lock file
└── 📄 TODO.md                # Project todo list
```

## 🛠️ Technology Stack

### Backend
- **Flask** - Python web framework
- **SQLAlchemy** - ORM for database operations
- **Flask-Login** - User authentication management
- **SQLite** - Lightweight database for development
- **python-pptx** - PowerPoint file processing
- **Hashids** - ID obfuscation for security

### Frontend
- **Jinja2** - Server-side templating
- **HTMX** - Dynamic HTML updates
- **Alpine.js** - Lightweight JavaScript framework
- **CSS** - Custom styling

### Development Tools
- **uv** - Python package manager
- **Python 3.12+** - Programming language

## 📊 Database Schema

### Models

#### User
- **id** (Primary Key)
- **username** (Unique)
- **password** (Hashed)
- **permission** (Access level)
- **created_at** (Timestamp)

#### Set
- **id** (Primary Key)
- **name** (Unique)
- **description**
- **is_public** (Boolean)
- **created_at** (Timestamp)
- **owner_id** (Foreign Key → User)

#### Image
- **id** (Primary Key)
- **filename** (Unique)
- **original_filename**
- **set_id** (Foreign Key → Set)
- **label_id** (Foreign Key → Label, Optional)

#### Label
- **id** (Primary Key)
- **name**
- **set_id** (Foreign Key → Set)

### Relationships
- **User** ↔ **Set**: One-to-Many (owner relationship)
- **Set** ↔ **Image**: One-to-Many
- **Set** ↔ **Label**: One-to-Many
- **Label** ↔ **Image**: One-to-Many (optional)

## 🚀 Getting Started

### Prerequisites
- Python 3.12 or higher
- uv package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mkminek11/recognify.git
   cd recognify
   ```

2. **Set up virtual environment and install dependencies**
   ```bash
   uv sync
   ```

3. **Activate virtual environment**
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## 🎮 Features

### Current Features
- ✅ User authentication and authorization
- ✅ PowerPoint presentation import
- ✅ Image extraction from slides
- ✅ Custom label creation and editing
- ✅ Set management (create, edit, delete)
- ✅ Interactive practice mode
- ✅ Image shuffling for varied practice sessions

### Planned Features
- 🔄 Direct image upload (without presentations)
- 🔄 Advanced scoring and progress tracking
- 🔄 Multi-user collaboration on sets
- 🔄 Mobile-responsive design
- 🔄 Export/import functionality for sets
- 🔄 Advanced search and filtering

## 👥 User Roles

### Standard User (Permission 0)
- Create and manage their own sets
- Practice with any public set
- Edit their own content

### Admin User (Permission 1+)
- Access admin panel
- Manage all users and sets
- Clear database content
- System-wide configuration

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True
```

### Database Configuration
The application uses SQLite by default. The database file is automatically created in the `instance/` directory.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 📞 Contact

**Project Owner:** mkminek11  
**Repository:** [https://github.com/mkminek11/recognify](https://github.com/mkminek11/recognify)

---

*Recognify - Making object recognition practice engaging and accessible for everyone.*