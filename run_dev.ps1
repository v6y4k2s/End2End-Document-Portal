# Local development server: auto-reloads on source changes only
# (excludes env/ so installed packages don't trigger spurious restarts).
uvicorn api.main:app --host 127.0.0.1 --port 8080 --reload `
  --reload-dir api --reload-dir src --reload-dir utils `
  --reload-dir logger --reload-dir exception --reload-dir config `
  --reload-dir model --reload-dir prompt `
  --reload-dir static --reload-dir templates
