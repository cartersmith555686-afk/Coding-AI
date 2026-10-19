"""Standalone CSS snippets."""
from tplkit import kit

CATEGORY = "CSS"
TEMPLATES, add = kit(CATEGORY)
RUNNABLE = set()
PHRASES = []
USE = "Put this in your stylesheet (style.css) or inside <style> tags."


def css(id, title, kw, code, phrases):
    add(id, title, kw, css=(code, None, USE))
    PHRASES.extend((p, id, "css") for p in phrases)


css("css_center", "Center anything (flexbox)", {"center": 5, "centre": 5, "centered": 5, "centering": 5, "middle": 3, "vertically": 3, "horizontally": 2},
    '.center {\n  display: flex;\n  justify-content: center;\n  align-items: center;\n  min-height: 100vh;\n}\n',
    ["css to center a div vertically and horizontally", "center something in the middle of the page css"])
css("css_button", "Styled button with hover", {"button": 5, "hover": 4, "buttons": 5, "btn": 4, "rounded": 2},
    '.button {\n  background: #5865f2;\n  color: #fff;\n  border: none;\n  border-radius: 8px;\n  padding: 12px 24px;\n  font-size: 1rem;\n  cursor: pointer;\n  transition: transform 0.15s, background 0.15s;\n}\n\n.button:hover {\n  background: #4752c4;\n  transform: translateY(-2px);\n}\n\n.button:active {\n  transform: translateY(0);\n}\n',
    ["css for a button with hover effect", "make a rounded button in css"])
css("css_card", "Card with shadow", {"card": 6, "cards": 6, "shadow": 4, "box": 1, "panel": 3},
    '.card {\n  background: #fff;\n  border-radius: 12px;\n  padding: 24px;\n  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);\n  max-width: 360px;\n}\n\n.card h2 {\n  margin-top: 0;\n}\n',
    ["css card with a shadow", "write css for a card"])
css("css_grid", "Responsive grid layout", {"grid": 6, "responsive": 4, "columns": 3, "layout": 3, "gallery": 3},
    '.grid {\n  display: grid;\n  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));\n  gap: 16px;\n  padding: 16px;\n}\n',
    ["css responsive grid layout", "css grid with columns that wrap"])
css("css_navbar", "Navigation bar", {"css": 3, "navbar": 6, "topbar": 5},
    '.navbar {\n  display: flex;\n  align-items: center;\n  justify-content: space-between;\n  padding: 0 24px;\n  height: 60px;\n  background: #1e1f22;\n  position: sticky;\n  top: 0;\n}\n\n.navbar a {\n  color: #fff;\n  text-decoration: none;\n  margin-left: 20px;\n}\n\n.navbar a:hover {\n  text-decoration: underline;\n}\n',
    ["css navbar", "css navbar styles"])
css("css_dark_mode", "Dark mode with CSS variables", {"dark": 6, "darkmode": 8, "theme": 4, "variables": 3, "night": 2, "light": 2},
    ':root {\n  --bg: #ffffff;\n  --text: #1a1a1a;\n}\n\n@media (prefers-color-scheme: dark) {\n  :root {\n    --bg: #121212;\n    --text: #eaeaea;\n  }\n}\n\nbody {\n  background: var(--bg);\n  color: var(--text);\n}\n',
    ["css dark mode", "dark theme with css variables"])
css("css_animation", "Animations (fade in, spin, pulse)", {"animation": 7, "animate": 5, "keyframes": 8, "fade": 5, "pulse": 5, "spin": 3, "transition": 2},
    '@keyframes fade-in {\n  from { opacity: 0; transform: translateY(10px); }\n  to { opacity: 1; transform: translateY(0); }\n}\n\n@keyframes spin {\n  to { transform: rotate(360deg); }\n}\n\n@keyframes pulse {\n  0%, 100% { transform: scale(1); }\n  50% { transform: scale(1.08); }\n}\n\n.fade-in { animation: fade-in 0.5s ease both; }\n.spinner { animation: spin 1s linear infinite; }\n.pulse { animation: pulse 1.5s ease-in-out infinite; }\n',
    ["css fade in animation", "css keyframes spin and pulse"])
css("css_glass", "Glassmorphism / gradient background", {"glass": 6, "glassmorphism": 8, "blur": 5, "gradient": 5, "frosted": 5, "background": 2},
    'body {\n  min-height: 100vh;\n  background: linear-gradient(135deg, #667eea, #764ba2);\n}\n\n.glass {\n  background: rgba(255, 255, 255, 0.15);\n  backdrop-filter: blur(12px);\n  border: 1px solid rgba(255, 255, 255, 0.3);\n  border-radius: 16px;\n  padding: 24px;\n  color: #fff;\n}\n',
    ["css glassmorphism card", "css gradient background with blur"])
css("css_reset", "CSS reset and base styles", {"reset": 7, "normalize": 6, "base": 2, "boxsizing": 6, "defaults": 2, "font": 2},
    '*, *::before, *::after {\n  box-sizing: border-box;\n}\n\nbody {\n  margin: 0;\n  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;\n  line-height: 1.5;\n}\n\nimg {\n  max-width: 100%;\n  display: block;\n}\n',
    ["css reset", "base css box-sizing and font defaults"])
css("css_toggle", "Toggle switch (checkbox)", {"toggle": 7, "switch": 6, "checkbox": 4, "slider": 2},
    '.switch {\n  position: relative;\n  display: inline-block;\n  width: 50px;\n  height: 28px;\n}\n\n.switch input {\n  opacity: 0;\n  width: 0;\n  height: 0;\n}\n\n.slider {\n  position: absolute;\n  inset: 0;\n  background: #888;\n  border-radius: 28px;\n  cursor: pointer;\n  transition: background 0.2s;\n}\n\n.slider::before {\n  content: "";\n  position: absolute;\n  height: 22px;\n  width: 22px;\n  left: 3px;\n  top: 3px;\n  background: #fff;\n  border-radius: 50%;\n  transition: transform 0.2s;\n}\n\ninput:checked + .slider {\n  background: #5865f2;\n}\n\ninput:checked + .slider::before {\n  transform: translateX(22px);\n}\n',
    ["css toggle switch", "css checkbox switch"])
