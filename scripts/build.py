import json
import os
import re
import shutil
from pathlib import Path, PosixPath

import minify_html
from jinja2 import Environment, FileSystemLoader, Template, pass_context
from markupsafe import Markup

OUTPUT_FOLDER = Path(__file__).parent.parent / ("public" if "GITLAB_CI" in os.environ else "output")


def format_day_html(value):
    value = int(value)
    return Markup(str(value) + ("<sup>er</sup>" if value == 1 else ""))


def format_day(value):
    value = int(value)
    return str(value) + ("er" if value == 1 else "")


@pass_context
def static(ctx, value: str):
    return (PosixPath("static") / value).relative_to(PosixPath(ctx["output_url"]).parent, walk_up=True)


folders = [
    "personal/2023",
    "personal/2024",
]

env = Environment(loader=FileSystemLoader("templates"))
env.filters.update(
    {
        "format_day": format_day,
        "format_day_html": format_day_html,
        "static": static,
    }
)


def render(template: Template, output_url: str, params=None, data_folder: Path | None = None):
    output_file = OUTPUT_FOLDER / output_url
    output_file.parent.mkdir(parents=True, exist_ok=True)

    params = {"output_url": output_url, **(params or {})}
    if "day" in params and data_folder:
        day = params["day"]
        json_file = data_folder / f"{day}.json"
        image_file = data_folder / f"{day}.jpg"
        if json_file.exists():
            params.update(json.loads(json_file.read_text("utf-8")))
        elif image_file.exists():
            params["image_url"] = f"../{day}.jpg"

    output = template.render(params)
    for image_url in re.findall(r'<img src="\.\./([^"]+)"', output):
        shutil.copy(data_folder / image_url, output_file.parent.parent / image_url)

    output_file.write_text(output, encoding="utf-8")


def main():
    STATIC_FOLDER = OUTPUT_FOLDER / "static"
    try:
        shutil.rmtree(OUTPUT_FOLDER)
    except FileNotFoundError:
        pass
    OUTPUT_FOLDER.mkdir(parents=True)

    shutil.copytree(Path(__file__).parent.parent / "static", STATIC_FOLDER)

    for folder in folders:
        template_folder = "personal/2023" if folder == "personal/2024" else folder
        days = range(1, 25 + 1)
        render(env.get_template(f"{template_folder}/home.html"), f"{folder}/index.html", {"days": days})

        template = env.get_template(f"{template_folder}/day.html")
        for day in days:
            render(template, f"{folder}/{day}/index.html", {"day": day}, Path(folder))

    for file in STATIC_FOLDER.glob("**/*"):
        prefix = {
            ".html": "",
            ".css": "<style>",
            ".js": "<script>",
        }.get(file.suffix)
        if prefix is None:
            continue
        data = file.read_text("utf-8")
        print("Minifying", file)
        try:
            data = minify_html.minify(
                prefix + data,
                do_not_minify_doctype=True,
                minify_css=True,
                minify_js=True,
            ).removeprefix(prefix)
        except:  # noqa
            pass
        else:
            file.write_text(data, "utf-8")


if __name__ == "__main__":
    main()
