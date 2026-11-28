import markdown, pathlib, subprocess
here = pathlib.Path(__file__).parent
md = "\n\n".join((here/f"part{i}.md").read_text() for i in range(1,5))
(here/"Oroboro_Studies_Combined_Report.md").write_text(md)
body = markdown.markdown(md, extensions=["tables","md_in_html","attr_list","toc","sane_lists"])
css = (here/"style.css").read_text()
html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Leftovers, Gates and the Last Push: Oroboro combined report</title>
<meta name="author" content="Caitlyn Randels"><style>{css}</style></head><body>{body}</body></html>"""
(here/"Oroboro_Studies_Combined_Report.html").write_text(html)
subprocess.run(["google-chrome","--headless=new","--no-sandbox","--disable-gpu","--no-pdf-header-footer",
  "--print-to-pdf="+str(here/"Oroboro_Studies_Combined_Report.pdf"),
  "file://"+str(here/"Oroboro_Studies_Combined_Report.html")],check=True,capture_output=True)
print("built")
