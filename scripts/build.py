import html
import json
import os
import re
import shutil
import unicodedata
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


def slugify(txt, separator="-"):
    txt = unicodedata.normalize("NFKD", txt)
    txt = txt.lower()
    txt = re.sub(r"[^\w\s-]", "", txt)
    txt = re.sub(r"[-_\s]+", separator, txt).strip(separator)
    return txt


def text(value):
    value = html.escape(value)
    value = re.sub(r"([0-9]+|[IVX]+)([eè]re?s?|[eè]mes?)", r"\1<sup>\2</sup>", value)
    value = value.replace("\n", "<br>")
    return value


@pass_context
def format_path(ctx, path, prefix="", here=False):
    if not here and ctx["path"] != ".":
        path = ctx["path"] + "/" + path
    value = path.rpartition("/")[-1]
    if prefix:
        ret = prefix
    else:
        ret = "Calendrier de l'Avent"
    try:
        value = int(value)
        ret += f" {value}"
        if ctx["names"] and path in ctx["names"]:
            ret += f" ({ctx['names'][path]})"
    except ValueError:
        if path != ".":
            ret += f" {ctx['names'][path]}"
    return ret


@pass_context
def static(ctx, value: str):
    return (PosixPath("static") / value).relative_to(PosixPath(ctx["output_url"]).parent, walk_up=True)


folders = []
for base_folder in ("cate", "personal"):
    folders.extend(str(folder) for folder in Path(base_folder).iterdir())
folders.sort()

names = {
    "cate/2019": "les saints",
    "cate": "du caté",
    "personal": "personnel (avec citations)",
}

env = Environment(loader=FileSystemLoader([".", "templates"]))
env.filters.update(
    {
        "format_day": format_day,
        "format_day_html": format_day_html,
        "format_path": format_path,
        "slugify": slugify,
        "static": static,
        "text": text,
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
        elif params["day"] != 25:
            raise ValueError(f"No data found for {output_url}")

    output = template.render(params)
    if data_folder:
        file_urls = re.findall(r'<(?:img|link|script|audio)[^>]+(?:href|src)="\.\./([^."][^"]*)"', output)
        file_urls.extend(file.name for file in data_folder.glob("*.lrc"))
        for file_url in file_urls:
            dest = output_file.parent.parent / file_url
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(data_folder / file_url, dest)

    output_file.write_text(output, encoding="utf-8")


def make_tree(paths: list[str]):
    ret = ({}, ())

    def add_folder(path: list[str]):
        folder = ret
        for item in path:
            folder = folder[0].setdefault(item, ({}, ()))

    for path in paths:
        path = path.split("/")
        add_folder(path)

    return ret


def get_directory_listings(folder, current_dir=".") -> dict[str, tuple[list[str], list[str]]]:
    current_dir = current_dir.removeprefix("./")
    if not folder[0] and not folder[1]:
        return {}
    ret = {}
    for subdir, contents in folder[0].items():
        ret.update(get_directory_listings(contents, current_dir + "/" + subdir))
    ret[current_dir] = ([*folder[0]], folder[1])
    return ret


def main():
    STATIC_FOLDER = OUTPUT_FOLDER / "static"
    print("Removing old files")
    try:
        shutil.rmtree(OUTPUT_FOLDER)
    except FileNotFoundError:
        pass
    OUTPUT_FOLDER.mkdir(parents=True)

    print("Copying static files")
    shutil.copytree(Path(__file__).parent.parent / "static", STATIC_FOLDER)

    list_template = env.get_template("list.html")

    print("Generating directory listings")
    for path, listing in get_directory_listings(make_tree(folders)).items():
        output = list_template.render(output_url=path + "/index.html", path=path, listing=listing, names=names)
        (OUTPUT_FOLDER / path).mkdir(parents=True, exist_ok=True)
        (OUTPUT_FOLDER / path / "index.html").write_text(output, encoding="utf-8")

    print("Generating Advent calendar pages")
    for folder in folders:
        print("*", folder)
        template_folder = (
            "personal/generic"
            if folder
            in ("personal/2019", "personal/2020", "personal/2021", "personal/2022", "personal/2023", "personal/2024")
            else folder
        )
        days = range(1, 25 + 1)
        render(
            env.get_template(f"{template_folder}/home.html"), f"{folder}/index.html", {"days": days, "folder": folder}
        )

        day_template = env.get_template(f"{template_folder}/day.html")
        for day in days:
            if day == 25:
                template = env.get_template(f"{folder}/{day}.html")
            else:
                template = day_template
            render(template, f"{folder}/{day}/index.html", {"day": day, "folder": folder}, Path(folder))

    for file in OUTPUT_FOLDER.glob("**/*"):
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
                minify_doctype=False,
                minify_css=True,
                minify_js=True,
            ).removeprefix(prefix)
        except:  # noqa
            pass
        else:
            file.write_text(data, "utf-8")


if __name__ == "__main__":
    main()
