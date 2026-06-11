"""Jinja2 template configuration with autoescaping (XSS protection)."""
from fastapi.templating import Jinja2Templates

# Jinja2 autoescaping is enabled by default for .html templates, which
# escapes interpolated values and mitigates reflected/stored XSS.
templates = Jinja2Templates(directory="app/templates")
templates.env.globals["app_name"] = "AI Interview Assistant"
