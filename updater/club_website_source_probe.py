#!/usr/bin/env python3
"""Read-only discovery of public directory table/export availability.
Does not scrape protected APIs, bypass access controls, or approve URLs.
"""
import argparse
import csv
import html.parser
import json
import pathlib
import urllib.request

URL = "https://www.thenon-leaguenetwork.co.uk/clubs-directory"

class Tables(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows=[]; self.row=None; self.cell=None; self.links=[]; self.href=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="tr":self.row=[]
        if tag in ("td","th") and self.row is not None:self.cell=[]
        if tag=="a":self.href=a.get("href")
    def handle_data(self,data):
        if self.cell is not None:self.cell.append(data)
    def handle_endtag(self,tag):
        if tag in ("td","th") and self.cell is not None and self.row is not None:
            self.row.append("".join(self.cell).strip());self.cell=None
        if tag=="tr" and self.row is not None:
            if self.row:self.rows.append(self.row)
            self.row=None
        if tag=="a":self.href=None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    out=pathlib.Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    request=urllib.request.Request(URL,headers={"User-Agent":"TinFoilFACup-WebsiteAudit/1.0 (research; no bulk crawling)"})
    with urllib.request.urlopen(request,timeout=25) as response:
        content=response.read(10_000_000)
        mime=response.headers.get("Content-Type","")
    doc=content.decode("utf-8","replace")
    parser=Tables();parser.feed(doc)
    result={"source":URL,"content_type":mime,"download_bytes":len(content),"html_table_rows":len(parser.rows),
            "has_club_name":("Club Name" in doc),"has_website_header":("Website" in doc),
            "note":"Only visible HTML tables parsed; Wix may render the directory client-side. No JS execution or hidden API scraping."}
    if parser.rows:
        header=next((r for r in parser.rows if "Club Name" in r and "Website" in r),None)
        if header:
            idx=parser.rows.index(header);rows=[r for r in parser.rows[idx+1:] if len(r)==len(header)]
            mapping=dict(zip(header,range(len(header))))
            with open(str(out)+".csv","w",newline="",encoding="utf-8") as f:
                w=csv.writer(f);w.writerow(["Club Name","Website","Postcode"])
                for r in rows:w.writerow([r[mapping["Club Name"]],r[mapping["Website"]],r[mapping["Postcode"]] if "Postcode" in mapping else ""])
            result["exported_records"]=len(rows)
        else:result["exported_records"]=0
    else:result["exported_records"]=0
    pathlib.Path(str(out)+".json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
    if not result["exported_records"]:
        print("No directly parseable public HTML table. Obtain permitted CSV export from directory operator; do not claim coverage.")

if __name__=="__main__":main()
