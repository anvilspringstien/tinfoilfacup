from pathlib import Path
import base64, hashlib, re

page = Path('beta/clubfinder-beta.html')
source = page.read_bytes()
pattern = rb'data:image/png;base64,([A-Za-z0-9+/=]+)'
images = list(re.finditer(pattern, source))
assert len(images) == 9, 'Unexpected number of BETA inline Stats images'
names = ['header-logo', 'rounds-completed', 'matches-played',
         'clubs-encountered', 'goals-seen', 'grounds-visited',
         'pigeon-miles-flown', 'report-logo', 'cup']
folder = Path('beta/assets/stats-report')
folder.mkdir(parents=True, exist_ok=True)
for index, (name, match) in enumerate(zip(names, images)):
    data = base64.b64decode(match.group(1), validate=True)
    assert data.startswith(b'\x89PNG\r\n\x1a\n')
    filename = f'{name}-{hashlib.sha256(data).hexdigest()[:12]}.png'
    url = f'assets/stats-report/{filename}'.encode()
    if index < 7:
        (folder / filename).write_bytes(data)
    source = source.replace(match.group(0), url, 1)
assert b'__LOGO__' in source and b'__CUP__' in source
source, n = re.subn(
    rb'doc\.replace\("__LOGO__","assets/stats-report/report-logo-[a-f0-9]+\.png"\)\.replace\("__CUP__","assets/stats-report/cup-[a-f0-9]+\.png"\)',
    b'doc', source)
assert n == 1 and b'__LOGO__' not in source and b'__CUP__' not in source
assert b'data:image/png;base64,' not in source
page.write_bytes(source)

test = Path('updater/beta_campaign_identity_regression.js')
text = test.read_text()
anchor = "const html=fs.readFileSync(path.join(ROOT,'beta','clubfinder-beta.html'),'utf8');\n"
validation = '''const reportImages=[...html.matchAll(/assets\\/stats-report\\/[a-z0-9-]+[.]png/g)].map(m=>m[0]);
if(reportImages.length!==7||new Set(reportImages).size!==7)throw new Error('BETA Stats: report assets missing from renderer');
for(const url of reportImages){
  const bytes=fs.readFileSync(path.join(ROOT,'beta',url));
  if(!bytes.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10])))
    throw new Error('BETA Stats: missing or invalid report image '+url);
}
'''
assert text.count(anchor) == 1
text = text.replace(anchor, anchor + validation)
anchor = '  const instantPage=getCertificateHtml();\n'
render_check = '''  function checkStatsImages(page){
    const urls=[...page.matchAll(new RegExp('<img[^>]+src="(assets/stats-report/[a-z0-9-]+[.]png)"','g'))].map(m=>m[1]);
    if(urls.length!==7||new Set(urls).size!==7||page.includes('data:image/png;base64,'))
      throw new Error('BETA Stats: expected seven distinct external report images; got '+JSON.stringify(urls));
    return urls;
  }
  const statsImages=checkStatsImages(instantPage);
'''
assert text.count(anchor) == 1
text = text.replace(anchor, anchor + render_check)
anchor = '  const statsPage=getCertificateHtml();\n'
refresh_check = '''  if(JSON.stringify(checkStatsImages(statsPage))!==JSON.stringify(statsImages))
    throw new Error('BETA Stats refresh: report image paths changed');
'''
assert text.count(anchor) == 1
text = text.replace(anchor, anchor + refresh_check)
test.write_text(text)
