from pathlib import Path

def get_project_root(marker_name="dscim-testing"):
    path = Path().resolve()
    while path.name != marker_name and path.parent != path:
        path = path.parent
    return path
