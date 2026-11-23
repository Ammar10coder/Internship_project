"""Read only the public latest-tenders table. Preserve the last successful snapshot."""
import json
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
from lxml import html
from .scoring import classify

URL = "https://eprocure.gov.in/eprocure/app"
CACHE = Path(__file__).resolve().parents[1] / "data" / "portal.json"


def parse(page):
    soup = html.fromstring(page)
    results = {}
    for header in soup.xpath("//tr"):
        names = [" ".join(c.text_content().split()).lower() for c in header.xpath("./td|./th")]
        if "tender title" not in names or "closing date" not in names:
            continue
        table = header.xpath("ancestor::table[1]")[0]
        for row in table.xpath(".//tr"):
            cells = row.xpath("./td|./th")
            if len(cells) != len(names):
                continue
            title_cell = cells[names.index("tender title")]
            links = title_cell.xpath(".//a[@href]")
            if not links:
                continue
            title = " ".join(title_cell.text_content().split())
            fields = dict(zip(names, [" ".join(c.text_content().split()) for c in cells]))
            ref = next((v for k,v in fields.items() if "reference" in k), "")
            source = urljoin(URL, links[0].get("href"))
            if urlsplit(source).hostname not in ("eprocure.gov.in","www.eprocure.gov.in") or urlsplit(source).scheme != "https":
                source = URL
            date = fields["closing date"]
            for fmt in ("%d-%b-%Y %I:%M %p","%d-%b-%Y %H:%M","%d-%b-%Y"):
                try:
                    date = datetime.strptime(date, fmt).date().isoformat()
                    break
                except ValueError:
                    continue
            key = sha256((ref+"|"+title).encode()).hexdigest()[:18]
            result = classify(title)
            results[key] = dict(id="cppp-"+key, title=title, ref=ref, deadline=date, url=source,
                source="CPPP", category=result.category, score=result.score, decision=result.decision,
                explanation=result.explanation, priority=result.priority)
    if not results:
        raise ValueError("Portal returned no readable latest-tender rows.")
    return list(results.values())


def cached():
    return json.loads(CACHE.read_text()) if CACHE.exists() else {"rows": [], "updated": None}


def refresh():
    with urlopen(Request(URL, headers={"User-Agent":"TenderAI classroom project/1.0"}), timeout=12) as response:
        rows = parse(response.read(3_000_000))
    snapshot = {"rows":rows, "updated":datetime.now(timezone.utc).isoformat()}
    CACHE.parent.mkdir(exist_ok=True)
    with NamedTemporaryFile("w",dir=CACHE.parent,delete=False) as f:
        json.dump(snapshot,f)
    Path(f.name).replace(CACHE)
    return snapshot
