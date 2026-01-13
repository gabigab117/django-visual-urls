# Django Visual URLs

Visualize your Django URL patterns as an interactive graph.

## Installation

```bash
pip install django-visual-urls
```

Add to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'django_visual_urls',
]
```

## Usage

Generate a visual representation of your URLs:

```bash
python manage.py visualize
```

This creates an `url_map.html` file at your project root containing an interactive Mermaid.js graph.

### Options

**Include admin URLs** (excluded by default):

```bash
python manage.py visualize --include-admin
```

## How it Works

The command recursively analyzes your Django URL patterns and generates a graph showing:

- **URL nodes** (blue): URL paths
- **View nodes** (green): View functions or classes
- **Edges**: Relationships between URLs and views

The visualization handles:
- Simple URL patterns with `path()` or `re_path()`
- Nested patterns with `include()`
- Named URL patterns

## Example

Given this `urls.py`:

```python
from django.urls import path, include
from . import views

api_patterns = [
    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
]

urlpatterns = [
    path('', views.home, name='home'),
    path('api/', include(api_patterns)),
]
```

The generated graph will show the URL structure with `/api/users/` and `/api/users/<int:pk>/` as separate nodes connected to their respective views.

## Development

### Setup

```bash
git clone https://github.com/gabigab117/django-visual-urls.git
cd django-visual-urls
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running Tests

```bash
pytest
```

Tests verify:
- HTML file generation
- Mermaid syntax presence
- Recursive URL pattern handling
- Admin URL filtering

## Technical Details

The package works by:

1. Importing your project's root URLconf
2. Recursively traversing `URLPattern` and `URLResolver` objects
3. Building a Mermaid.js graph definition
4. Generating a standalone HTML file with the embedded graph

## Requirements

- Python 3.9+
- Django 3.2+

## License

MIT

## Links

- [Repository](https://github.com/gabigab117/django-visual-urls)
- [Mermaid.js Documentation](https://mermaid.js.org/)
