/**
 * TFFAC Mission Control -- authenticated read-only dashboard pilot.
 * Based on working Google login v3 and the standalone dashboard Mk I.
 * Optional Gmail read-only access; no persistent token storage or email write routes.
 * v7: club identity extraction correction (retains v6 count audit and v5 MIME fix).
 * Combined original-Mission-Control integration candidate. Do not deploy without staged approval.
 */
const DASHBOARD_HTML = [
  "<!doctype html>\n",
  "<html lang=\"en-GB\">\n",
  "<head>\n",
  "  <meta charset=\"utf-8\">\n",
  "  <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n",
  "  <meta name=\"theme-color\" content=\"#132923\">\n",
  "  <meta name=\"robots\" content=\"noindex,nofollow,noarchive\">\n",
  "  <meta name=\"description\" content=\"Local, read-only source monitoring and review workspace for Tin Foil FA Cup administrators. Not the public site.\">\n",
  "  <title>TFFAC Mission Control \u2014 Private HQ</title>\n",
  "  <style>\n",
  ":root{--ink:#18302c;--deep:#132923;--deep2:#1d3931;--cream:#f7f4eb;--paper:#fffdfa;--paper2:#f1f2ec;--line:#dfdfd4;--faint:#718078;--gold:#dfaa57;--amber:#ab752f;--red:#b35044;--green:#317960;--blue:#4c7485;--radius:15px;--shadow:0 11px 30px #20372b0b;--font:Inter,'Segoe UI',system-ui,-apple-system,BlinkMacSystemFont,sans-serif}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--cream);color:var(--ink);font:14px/1.5 var(--font)}button,input,select,textarea{font:inherit}button{cursor:pointer}a{color:#226d62;text-decoration:none}a:hover{text-decoration:underline}button:disabled{opacity:.48;cursor:not-allowed}button:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible,a:focus-visible{outline:3px solid #e6ad55;outline-offset:2px}.app{display:grid;grid-template-columns:248px minmax(0,1fr);min-height:100vh}.sidebar{background:var(--deep);color:#e9ede5;min-height:100vh;padding:28px 18px;display:flex;flex-direction:column;gap:26px;position:sticky;top:0;height:100vh;overflow:auto}.brand{padding:0 10px}.brandmark{display:flex;align-items:center;gap:12px}.crest{width:48px;height:51px;flex:0 0 auto;border:2px solid var(--gold);color:var(--gold);border-radius:10px 10px 16px 16px;display:grid;place-content:center;text-align:center;font-weight:950;font-family:Georgia,serif;line-height:1.02;letter-spacing:1px;font-size:14px;box-shadow:inset 0 0 0 3px #132923,inset 0 0 0 4px #8b754f}.brand strong{display:block;color:#fff9e9;letter-spacing:.08em;font-size:13px;line-height:1.3}.brand small{color:#b6c2b9;letter-spacing:.12em;font-size:10px}.internal{border:1px solid #7b7254;color:#e4bf80;border-radius:7px;padding:6px 9px;font-size:10px;font-weight:800;letter-spacing:.14em;display:inline-block;margin:22px 0 0 4px}.nav-group small{color:#9cab9f;text-transform:uppercase;font-size:10px;letter-spacing:.18em;font-weight:800;display:block;margin:0 0 10px 12px}.nav{display:flex;align-items:center;gap:12px;border:0;background:none;width:100%;color:#bed0c3;text-align:left;padding:12px;border-radius:10px;margin:3px 0;font-weight:600}.nav svg{width:19px;height:19px}.nav:hover{background:#ffffff13;color:white}.nav.active{background:#f1e9d716;color:#fff5e3;box-shadow:inset 3px 0 0 var(--gold)}.nav .count{margin-left:auto;font-size:11px;color:#c8d0c4;background:#ffffff16;border-radius:6px;padding:0 5px}.sidebar-footer{margin-top:auto;border-top:1px solid #ffffff20;padding:19px 11px 0;color:#b4c4b9;font-size:11px}.sidebar-footer b{display:block;color:#e5ebe1;margin-bottom:6px}.sidebar-footer .dot{margin-right:6px}.main{min-width:0}.topbar{height:76px;display:flex;justify-content:space-between;align-items:center;padding:0 38px;border-bottom:1px solid var(--line);background:#faf9f3bb;gap:20px}.breadcrumb{font-size:12px;color:#79827b;white-space:nowrap}.breadcrumb strong{font-size:12px;color:var(--ink)}.top-actions{display:flex;gap:12px;align-items:center;flex-wrap:wrap}.sync-note{font-size:11px;color:#61736b}.sync-note .dot{margin-right:5px}.content{padding:34px 38px 50px;max-width:1590px;margin:auto}.eyebrow{color:var(--amber);font-size:11px;letter-spacing:.14em;text-transform:uppercase;font-weight:900}.page-title{font:700 clamp(27px,3vw,39px)/1.15 Georgia,'Times New Roman',serif;letter-spacing:-.025em;margin:7px 0 10px;color:#1c3731}.subtitle{color:#6e7a72;font-size:13px;margin:0;max-width:800px}.page-head{display:flex;align-items:flex-end;justify-content:space-between;gap:18px;margin-bottom:30px}.page-head>div:last-child{flex-shrink:0}.btn{display:inline-flex;gap:7px;align-items:center;justify-content:center;border-radius:9px;border:1px solid #ced5cb;background:white;color:#24483f;font-weight:750;padding:10px 14px;min-height:38px;font-size:12px;box-shadow:none;text-decoration:none;transition:background .15s,border-color .15s}.btn:hover{background:#f1f5ed;text-decoration:none;border-color:#aabbb0}.btn.primary{background:#1e4e41;color:white;border-color:#1e4e41}.btn.primary:hover{background:#296351}.btn.dark{background:#142e27;color:white;border-color:#142e27}.btn.danger{color:#9c3a31;border-color:#e9ccc8}.btn.gold{background:#e9ba72;border-color:#e9ba72;color:#302819}.btn.small{min-height:31px;padding:6px 10px;font-size:11px}.btn.tiny{min-height:27px;padding:5px 8px;font-size:11px}.btn.ghost{background:transparent}.btn svg{width:15px;height:15px}.btn-row{display:flex;align-items:center;gap:9px;flex-wrap:wrap}.grid4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:17px}.grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:17px}.metric{background:var(--paper);border:1px solid var(--line);border-radius:var(--radius);padding:20px 22px;box-shadow:var(--shadow);min-width:0}.metric-top{display:flex;justify-content:space-between;align-items:center;gap:5px;color:#788178;text-transform:uppercase;letter-spacing:.09em;font-size:10px;font-weight:850}.metric-top .iconwrap{border-radius:10px;background:#f0f3ec;padding:8px;display:flex;color:#537569}.metric-top svg{width:16px;height:16px}.metric-val{font:700 35px/1.2 Georgia,serif;margin:13px 0 7px;white-space:nowrap;letter-spacing:-.04em}.metric-foot{font-size:11px;color:#738078;min-height:17px}.metric-foot strong{color:#486457}.metric.warn .iconwrap{color:#b6843c;background:#f9efd9}.metric.alert .iconwrap{color:var(--red);background:#fbefed}.metric.good .iconwrap{color:#35795f;background:#e8f3ec}.section-header{display:flex;align-items:center;justify-content:space-between;gap:15px;margin:33px 0 15px}.section-header h2{font:700 21px Georgia,serif;margin:0;color:#1c382f}.section-header p{margin:4px 0 0;color:#7a857d;font-size:12px}.surface{border:1px solid var(--line);background:var(--paper);border-radius:var(--radius);box-shadow:var(--shadow);overflow:hidden}.surface.pad{padding:22px}.surface .surface-head{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--line);padding:17px 21px;gap:12px}.surface h3{font-size:14px;margin:0;font-weight:850}.surface .surface-sub{color:#7a877d;font-size:11px}.progress{height:7px;border-radius:30px;background:#e6ebe4;overflow:hidden}.progress>span{display:block;height:100%;background:#347b64;border-radius:30px;transition:width .3s}.inline-progress{margin-top:18px}.tiny-note{font-size:11px;color:#77847a}.status{display:inline-flex;align-items:center;gap:6px;font-size:11px;font-weight:750;border-radius:50px;padding:4px 9px;line-height:1.25;white-space:nowrap;background:#eff1ec;color:#66736b}.status:before,.dot{content:'';display:inline-block;width:7px;height:7px;border-radius:50%;background:currentColor;flex:0 0 auto}.status.green{background:#e9f3ec;color:#32745d}.status.red{background:#f8eae6;color:#aa5245}.status.amber{background:#fbf1df;color:#a57534}.status.blue{background:#e7f1f5;color:#4b7181}.status.gray{background:#eff1ed;color:#68756e}.status.dark{background:#e2eae5;color:#224c3e}.tag{display:inline-block;border-radius:5px;padding:2px 7px;background:#f0f2ed;color:#5c6f65;font-size:10px;font-weight:750}.tag.hold{background:#faeddf;color:#9d6931}.watch-strip{display:grid;grid-template-columns:1.3fr 1fr;gap:17px}.watch-main{background:#1d3a32;color:#e9f2e9;padding:26px 28px;border-radius:var(--radius);position:relative;overflow:hidden;display:flex;justify-content:space-between;gap:15px}.watch-main:after{content:'\u2736';position:absolute;right:30px;top:-35px;color:#d6c39c10;font-size:190px;line-height:1}.watch-main h3{font:700 21px Georgia,serif;margin:6px 0 8px;color:#ffefd0}.watch-main p{margin:0;max-width:440px;color:#cadbd0;font-size:12px}.watch-main .watch-action{align-self:end;z-index:1;background:#e9ba72;border:0;border-radius:8px;padding:9px 15px;font-size:11px;font-weight:850;white-space:nowrap}.watch-main .eyebrow{color:#e9bf84}.watch-secondary{padding:20px 21px}.stat-row{display:flex;justify-content:space-between;align-items:center;gap:15px;padding:13px 0;border-top:1px solid var(--line)}.stat-row:first-child{border-top:0;padding-top:0}.stat-row:last-child{padding-bottom:0}.stat-row b{font-size:12px}.stat-row small{font-size:11px;color:#7d897e;display:block}.listlink{color:#246c5a;font-weight:700;font-size:11px}.quick-list{padding:4px 20px}.quick-row{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:13px 0;border-bottom:1px solid #edece4;cursor:pointer}.quick-row:last-child{border:0}.quick-row:hover strong{color:#24735b}.quick-row strong{display:block;font-size:12px}.quick-row small{display:block;color:#7d897d;font-size:11px;max-width:500px}.quick-row .status{flex-shrink:0}.table-wrap{overflow:auto;max-width:100%}table{border-collapse:collapse;width:100%;text-align:left}thead th{background:#f7f7f1;color:#7b887e;text-transform:uppercase;font-size:10px;letter-spacing:.08em;font-weight:850;white-space:nowrap;padding:13px 18px;border-bottom:1px solid var(--line)}tbody td{padding:14px 18px;border-bottom:1px solid #edeee7;font-size:12px;vertical-align:middle}tbody tr:hover{background:#fbfcf8}tbody tr:last-child td{border-bottom:0}.row-title{font-weight:850;color:#243f35;font-size:12px}.row-desc{font-size:11px;color:#829086;margin-top:3px}.td-actions{text-align:right;white-space:nowrap}.td-actions button{white-space:nowrap}.filters{display:flex;gap:10px;flex-wrap:wrap;padding:18px 20px;border-bottom:1px solid var(--line);align-items:center}.field{display:flex;flex-direction:column;gap:6px;min-width:0}.field label{font-size:11px;font-weight:800;color:#485e53}.field input,.field select,.field textarea,.input,.select{background:white;border:1px solid #d7dcd1;color:#253d33;border-radius:9px;padding:10px 11px;outline:0;width:100%;min-height:38px}.field textarea{min-height:90px;resize:vertical}.field input:focus,.field select:focus,.field textarea:focus,.input:focus{border-color:#6e9a82;box-shadow:0 0 0 3px #5a9b7931}.searchbox{position:relative;min-width:245px;flex:1}.searchbox input{padding-left:37px}.searchbox svg{width:16px;height:16px;position:absolute;left:13px;top:11px;color:#89988a}.filters select{width:auto;min-width:148px;font-size:12px}.pagination{display:flex;justify-content:space-between;align-items:center;padding:15px 20px;gap:12px;border-top:1px solid var(--line);font-size:11px;color:#7a867c}.pagination .btn{font-size:11px}.info-banner{display:flex;align-items:flex-start;gap:12px;background:#f2f1e9;border:1px solid #e7e2d3;border-radius:11px;padding:13px 16px;font-size:12px;color:#596c5e}.info-banner svg{flex-shrink:0;width:17px;height:17px;color:#937345;margin-top:1px}.info-banner strong{color:#314f40}.info-banner.error{background:#fff2ed;border-color:#f0cfc5;color:#93483d}.info-banner.error svg{color:#bd6251}.info-banner.success{background:#ecf5ed;border-color:#cce4d1;color:#34775e}.split{display:grid;grid-template-columns:minmax(0,1fr) 330px;gap:17px}.detail-panel{background:var(--paper);border:1px solid var(--line);border-radius:var(--radius);padding:20px 21px;align-self:start;position:sticky;top:16px}.detail-panel h3{font:700 22px Georgia,serif;margin:0 0 7px}.detail-panel h4{margin:20px 0 9px;font-size:12px}.detail-panel .kv{display:flex;justify-content:space-between;gap:10px;border-bottom:1px solid var(--line);padding:9px 0;font-size:11px}.detail-panel .kv span:first-child{color:#7f8b80}.detail-panel .kv b{overflow-wrap:anywhere;text-align:right}.evidence-list{display:flex;flex-direction:column;gap:8px}.evidence-list a{font-size:11px;overflow-wrap:anywhere}.note{font-size:11px;color:#819083}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:13px}.form-grid .full{grid-column:1 / -1}.form-controls{padding-top:17px;border-top:1px solid var(--line);margin-top:18px}.checks{display:grid;grid-template-columns:1fr 1fr;gap:8px 18px;margin:13px 0}.check{display:flex;align-items:flex-start;gap:8px;font-size:11px;cursor:pointer}.check input{width:15px;height:15px;accent-color:#33745f;margin-top:2px}.check span{line-height:1.4}.hold-list{display:flex;flex-direction:column;gap:7px;margin:12px 0}.hold-item{display:flex;gap:8px;align-items:flex-start;font-size:11px;color:#9b583a}.hold-item svg{width:14px;height:14px;margin-top:1px;flex-shrink:0}.tabbar{display:flex;gap:4px;border-bottom:1px solid var(--line);padding:0 20px;overflow:auto}.tab{border:0;border-bottom:2px solid transparent;background:transparent;color:#7b897d;padding:15px 10px 12px;font-size:12px;font-weight:750;white-space:nowrap}.tab.active{color:#2a6a55;border-color:#2f7b61}.activity{display:flex;flex-direction:column;gap:1px}.activity-item{display:flex;gap:12px;padding:12px 0;border-bottom:1px solid #eeeee6}.activity-item:last-child{border:0}.activity-icon{width:31px;height:31px;flex:0 0 auto;border-radius:9px;background:#f0f2ed;display:grid;place-content:center;color:#5f7c68}.activity-icon svg{width:15px;height:15px}.activity-item b{font-size:12px;display:block}.activity-item p{margin:3px 0;color:#79867d;font-size:11px}.activity-item time{color:#a1a99f;font-size:10px}.empty{padding:45px 22px;text-align:center;color:#879387}.empty svg{height:25px;width:25px;margin-bottom:8px}.empty b{display:block;color:#486155;margin-bottom:5px}.calendar-grid{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:5px}.slot{border-radius:6px;min-height:34px;border:1px solid #e5e8df;background:#e9eee8;color:#658077;display:flex;justify-content:center;align-items:center;flex-direction:column;font-size:10px;gap:2px;font-weight:800}.slot.ok{background:#d9eddf;color:#347358;border-color:#cde4d1}.slot.missing{background:#f7ded9;color:#aa5146;border-color:#edc7c0}.slot.delayed{background:#faedcf;color:#9f7839;border-color:#efdbac}.slot.pending{background:#edf0eb;color:#7c8b80}.slot.unknown{background:#f1f2ee;color:#869087}.slot span{font-size:9px;font-weight:550}.timeline{border-left:2px solid #dfe9dd;margin-left:6px;padding-left:20px;display:flex;flex-direction:column;gap:20px}.timeline-item{position:relative}.timeline-item:before{content:'';position:absolute;width:10px;height:10px;left:-26px;top:6px;border-radius:50%;background:#e7b96c;border:2px solid #fff}.timeline-item b{font-size:12px}.timeline-item p{font-size:11px;color:#768377;margin:4px 0}.timeline-item time{font-size:10px;color:#9aa39a}.drawer-backdrop{position:fixed;inset:0;background:#0c211c89;z-index:15;display:flex;justify-content:flex-end;animation:fade .15s}.drawer{background:#fcfbf5;width:min(590px,100%);height:100%;overflow:auto;padding:27px 29px;box-shadow:-12px 0 30px #0002}.drawer-header{display:flex;justify-content:space-between;align-items:flex-start;gap:15px;margin-bottom:24px}.drawer h2{font:700 27px Georgia,serif;margin:6px 0}.drawer h3{font-size:14px;margin:19px 0 10px}.icon-btn{border:1px solid #d8ddd2;background:white;border-radius:9px;width:34px;height:34px;display:grid;place-items:center;color:#64786b}.icon-btn svg{height:18px;width:18px}.drawer section{border-top:1px solid var(--line);padding:16px 0}.drawer section:first-of-type{border-top:0}.kv-list{display:grid;grid-template-columns:125px 1fr;gap:10px 16px;font-size:12px}.kv-list>div:nth-child(odd){color:#7d8a80}.kv-list>div:nth-child(even){font-weight:700;overflow-wrap:anywhere}.modal-backdrop{position:fixed;inset:0;z-index:25;background:#0c211c9e;display:flex;align-items:center;justify-content:center;padding:18px}.modal{width:min(660px,100%);max-height:92vh;overflow:auto;border-radius:16px;background:#fffcf5;padding:24px;box-shadow:0 16px 60px #07180f40}.modal-head{display:flex;align-items:center;justify-content:space-between;gap:15px;margin-bottom:15px}.modal h2{font:700 25px Georgia,serif;margin:4px 0}.toast-area{position:fixed;bottom:22px;right:22px;z-index:40;display:flex;flex-direction:column;gap:8px;max-width:min(420px,90vw)}.toast{background:#1d3d32;color:#fff9ec;padding:12px 15px;border-radius:9px;box-shadow:0 8px 25px #081d1740;font-size:12px;line-height:1.45}.toast.warn{background:#8b5940}.row-actions{display:flex;gap:8px;flex-wrap:wrap}.muted{color:#78887d}.text-sm{font-size:12px}.text-xs{font-size:11px}.bold{font-weight:800}.two-col{display:grid;grid-template-columns:1fr 1fr;gap:17px}.gap16{height:16px}.gap24{height:24px}.divider{height:1px;background:var(--line);margin:18px 0}.mono{font-family:Consolas,'Courier New',monospace;font-size:11px}.source-footer{font-size:11px;color:#859084;margin-top:28px}.source-footer a{margin-left:4px}.hide{display:none!important}.nowrap{white-space:nowrap}.wrap{overflow-wrap:anywhere}.right{text-align:right}.state-card{border:1px solid var(--line);border-radius:11px;background:#fff;padding:15px}.state-card h4{margin:0 0 8px;font-size:12px}.mini-stat{border-top:1px solid var(--line);padding:9px 0;display:flex;justify-content:space-between;font-size:11px}.mini-stat:first-child{border:0}.mini-stat span{color:#738178}.mini-stat strong{text-align:right}.document-link{display:inline-flex;gap:5px;align-items:center;font-size:11px;word-break:break-all}.document-link svg{height:13px;width:13px;flex-shrink:0}.legend{display:flex;align-items:center;flex-wrap:wrap;gap:11px;font-size:10px;color:#748077}.legend-item{display:flex;align-items:center;gap:5px}.legend-item i{width:8px;height:8px;border-radius:50%;display:inline-block}.screen-only{display:initial}@keyframes fade{from{opacity:0}to{opacity:1}}@media(max-width:1220px){.grid4{grid-template-columns:repeat(2,1fr)}.watch-strip{grid-template-columns:1fr}.split{grid-template-columns:minmax(0,1fr) 280px}.content{padding:28px}.topbar{padding:0 28px}}@media(max-width:970px){.app{grid-template-columns:80px minmax(0,1fr)}.sidebar{padding:22px 10px;align-items:center}.brandmark{justify-content:center}.brandmark div:nth-child(2),.sidebar .nav-group small,.nav span,.nav .count,.internal,.sidebar-footer{display:none}.nav{justify-content:center;padding:13px;width:54px}.sidebar .nav-group{width:100%}.split{grid-template-columns:1fr}.detail-panel{position:static}.two-col{grid-template-columns:1fr}}@media(max-width:700px){.app{display:block}.sidebar{height:auto;min-height:0;position:sticky;top:0;z-index:9;flex-direction:row;padding:9px 10px;overflow-x:auto;gap:10px}.brand{padding:0;align-self:center}.crest{width:34px;height:37px;font-size:10px}.nav-group{display:flex;gap:4px;width:auto!important}.nav{margin:0;width:41px;height:41px;padding:10px}.nav svg{width:18px;height:18px}.topbar{padding:0 17px;height:62px}.top-actions{gap:6px}.top-actions .sync-note{display:none}.content{padding:25px 15px 40px}.page-head{flex-wrap:wrap;margin-bottom:20px}.page-title{font-size:30px}.grid4,.grid3,.watch-strip,.two-col{grid-template-columns:1fr}.form-grid{grid-template-columns:1fr}.form-grid .full{grid-column:auto}.filters{padding:12px}.filters select{min-width:120px;flex:1}.searchbox{min-width:100%}.watch-main{flex-direction:column}.watch-main .watch-action{align-self:start}.calendar-grid{grid-template-columns:repeat(6,1fr)}.metric-val{font-size:32px}.drawer{padding:18px 16px}.modal{padding:17px}.section-header{align-items:start}.section-header .btn{white-space:nowrap}}@media print{.sidebar,.topbar,.btn,.filters,.pagination{display:none!important}.app{display:block}.content{padding:0}.surface,.metric{box-shadow:none}body{background:white}.screen-only{display:none!important}}\n",
  "@media(max-width:700px){.sidebar .nav-group{flex:0 0 auto;width:auto!important;gap:4px}.sidebar .nav{flex:0 0 41px;min-width:41px}.sidebar .brand{flex:0 0 auto}.topbar .top-actions [data-nav=\"approvals\"]{display:none}}\n",
  "@media(max-width:970px){.sidebar .nav .nav-icon{display:flex!important;align-items:center;justify-content:center}}\n",
  "/* Mission Control: calm signal hierarchy, paperwork beside the instruments. */\n",
  ".mission-head{display:flex;justify-content:space-between;align-items:end;gap:20px;margin:0 0 24px}\n",
  ".mission-head h1{font:700 clamp(32px,3.5vw,48px)/1.04 Georgia,serif;margin:8px 0 7px;letter-spacing:-.035em;color:#19372e}.mission-head p{margin:0;color:#637a6c;font:italic 17px Georgia,serif}\n",
  ".mission-star{font:normal 22px system-ui;color:#d2a359;margin-left:12px;vertical-align:middle}.mission-head-actions{display:flex;gap:9px;flex-wrap:wrap}\n",
  ".mission-master{border-radius:15px;display:flex;align-items:center;gap:17px;padding:20px 22px;margin-bottom:14px;background:#203c33;color:#fff;box-shadow:0 10px 26px #122c2314}.mission-master.unknown{background:#344b46}.mission-master.warning{background:#58462d}.mission-master.danger{background:#633d37}.mission-master .master-light{width:17px;height:17px;background:#cbd4ca;border-radius:50%;box-shadow:0 0 0 5px #ffffff1b;flex:none}.mission-master.warning .master-light{background:#edc276}.mission-master.danger .master-light{background:#ee9080}.mission-master div:nth-child(2){flex:1}.mission-master span{display:block;font-size:10px;letter-spacing:.14em;font-weight:900;color:#e1e7dd}.mission-master strong{display:block;margin:4px 0;font:700 23px Georgia,serif}.mission-master small{color:#e5e9e0;display:block;font-size:11px;max-width:770px}.mission-master .btn{border-color:#ffffff55;background:#ffffff15;color:#fff}\n",
  ".mission-sec{margin-top:26px}.signal-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.signal-card{background:#fffdfa;border:1px solid var(--line);border-top:4px solid #a7afa6;border-radius:12px;padding:16px 18px;text-align:left;min-height:159px;display:flex;flex-direction:column;box-shadow:var(--shadow);transition:transform .15s,border-color .15s}.signal-card:hover{transform:translateY(-2px);border-color:#a9b6a9}.signal-card.good{border-top-color:#3e9371}.signal-card.warning{border-top-color:#d6a151}.signal-card.danger{border-top-color:#b95448}.signal-card.unknown{border-top-color:#899a92}.signal-head{display:flex;align-items:center;justify-content:space-between;gap:5px;margin-bottom:18px}.signal-head>span:first-child{font-weight:850;letter-spacing:.1em;color:#708078;font-size:10px}.signal-card>strong{font:700 19px Georgia,serif;color:#213d33;margin-bottom:4px}.signal-card>small{font-size:11px;color:#77877b}.signal-more{margin-top:auto;padding-top:12px;font-size:10px;color:#49725f;display:flex;gap:5px;align-items:center;font-weight:750}.signal-more svg{width:13px;height:13px}.mission-tag{display:inline-flex;align-items:center;gap:7px;font-size:9px;letter-spacing:.065em;font-weight:900;color:#69766f;white-space:nowrap}.mission-lamp{width:8px;height:8px;display:block;border-radius:50%;background:#879a92;box-shadow:0 0 0 3px #eaf0ea}.mission-tag.good{color:#32735b}.mission-tag.good .mission-lamp{background:#378d68;box-shadow:0 0 0 3px #e0f1e5}.mission-tag.warning{color:#9a712d}.mission-tag.warning .mission-lamp{background:#d69e40;box-shadow:0 0 0 3px #fbefd9}.mission-tag.danger{color:#a44b40}.mission-tag.danger .mission-lamp{background:#c45043;box-shadow:0 0 0 3px #f9e8e5}\n",
  ".mission-columns{display:grid;grid-template-columns:1.17fr 1fr;gap:16px;margin-top:18px}.mission-bottom{grid-template-columns:1.08fr 1fr}.mission-panel-head{display:flex;justify-content:space-between;align-items:start;gap:12px;margin-bottom:16px}.mission-panel-head h2{font:700 22px Georgia,serif;margin:0 0 4px}.mission-panel-head p{font-size:11px;color:#758478;margin:0}.mission-panel-head>svg{width:20px;height:20px;color:#9eae9f;flex-shrink:0}.priority-list{border-top:1px solid var(--line)}.priority-row{display:flex;align-items:center;gap:11px;text-align:left;background:none;border:0;border-bottom:1px solid var(--line);width:100%;padding:12px 2px}.priority-row:hover{background:#f6f6f0}.priority-row>span:nth-child(2){flex:1}.priority-row b{display:block;font-size:12px;color:#334e40}.priority-row small{display:block;color:#7b897c;font-size:11px}.priority-row svg{width:14px;height:14px;color:#8b998d}.priority-dot{width:10px;height:10px;border-radius:50%;background:#9aac9f;flex:none}.priority-dot.warning{background:#d49b42}.priority-dot.danger{background:#b95548}.priority-dot.good{background:#478e6a}.mission-quicklinks{display:flex;gap:17px;flex-wrap:wrap;padding-top:14px}.mission-quicklinks a{font-size:11px;font-weight:800;display:inline-flex;align-items:center;gap:5px}.mission-quicklinks svg{width:12px;height:12px}.daily-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:11px}.daily-head strong{font:700 22px Georgia,serif}.daily-head small{display:block;font-size:11px;color:#829084;margin-top:4px}.daily-count{font-weight:850;color:#476b57;font-size:13px}.daily-list{padding:7px 0 11px}.daily-task{display:flex;gap:10px;padding:12px 2px;border-bottom:1px solid var(--line);cursor:pointer}.daily-task input{accent-color:#347a60;width:17px;height:17px;margin:2px 0 0}.daily-task b{font-size:12px;color:#354d40;display:block}.daily-task small{display:block;color:#7e8c7f;font-size:11px}.daily-task:has(input:checked) b{text-decoration:line-through;color:#819184}.mission-feature{display:grid;gap:9px;margin:15px 0 22px}.mission-feature strong{display:block;font:700 17px Georgia,serif}.mission-feature small{display:block;font-size:11px;color:#829083}.ideas-teaser{background:#fdfaf0}.idea-quote{font:italic 22px/1.3 Georgia,serif;color:#375e4b;margin:25px 0 9px}.idea-sub{font-size:11px;color:#819082;margin-bottom:22px}.mission-safety{margin-top:20px;border-top:1px solid var(--line);padding-top:17px;font-size:11px;color:#748575;display:flex;align-items:start;gap:7px;flex-wrap:wrap}.mission-safety svg{width:16px;height:16px;flex:none}\n",
  ".comparison-desk{margin-top:18px}.compare-grid{display:grid;grid-template-columns:1.05fr 1fr;gap:17px;margin-top:17px}.compare-grid .field{margin-bottom:12px}.compare-grid .field label{display:block;font-size:11px;font-weight:750;margin-bottom:5px}.compare-grid textarea{min-height:204px}.compare-source{font-size:11px;color:#768779}.compare-source svg{vertical-align:middle;width:13px;height:13px}.compare-status{background:#f3f5f0;border:1px solid #e5e9e0;border-radius:11px;padding:18px}.compare-status.good{background:#eef6ef;border-color:#c9e5cd}.compare-status.warning{background:#fbf5e9;border-color:#eedfbe}.compare-status.danger{background:#fcf0ed;border-color:#edcbc3}.compare-result-head{display:flex;flex-direction:column;align-items:start;gap:10px}.compare-result-head strong{font:700 19px/1.25 Georgia,serif;color:#2e4d3e}.compare-evidence-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:17px 0}.compare-evidence-grid small{font-size:10px;color:#809082;display:block}.compare-evidence-grid b{font-family:Consolas,monospace;font-size:13px;color:#314d3e;overflow-wrap:anywhere}.compare-history{margin-top:14px;border-top:1px solid var(--line);padding-top:13px}.compare-history strong{font-size:11px;display:block;margin-bottom:6px}.compare-history>small{font-size:10px;color:#89988e}.compare-history-row{display:flex;justify-content:space-between;border-bottom:1px solid var(--line);padding:8px 0;gap:8px;font-size:11px}.compare-history-row small{color:#859385}\n",
  ".ideas-hero{background:#1a3a30;color:#f7f1db;border-radius:15px;padding:30px 33px;position:relative;overflow:hidden}.ideas-hero:after{content:'\u2733';position:absolute;right:20px;top:-90px;font-size:320px;color:#ffffff0b}.ideas-hero .eyebrow{color:#edbf73}.ideas-hero h2{font:700 clamp(23px,2.7vw,37px)/1.18 Georgia,serif;max-width:770px;margin:15px 0}.ideas-hero p{font-size:13px;color:#cbdbcc;max-width:580px}.idea-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:15px}.idea-card{padding:21px;border-radius:12px;border:1px solid var(--line);background:#fffdfa;display:flex;flex-direction:column;min-height:240px}.idea-kicker{font-size:10px;letter-spacing:.12em;color:#b18338;font-weight:900}.idea-card h3{font:700 23px Georgia,serif;margin:13px 0 9px}.idea-card p{font-size:12px;color:#728477;white-space:pre-wrap;overflow-wrap:anywhere;flex:1}.idea-card-foot{display:flex;justify-content:space-between;align-items:center;gap:8px;border-top:1px solid var(--line);padding-top:12px}.idea-card-foot small{color:#89978a;font-size:10px}.ideas-empty{grid-column:1/-1;padding:52px 24px;background:#fffdfa;border:1px dashed #d5d8c6;text-align:center;border-radius:14px}.ideas-empty>svg{width:24px;height:24px;color:#a6a476}.ideas-empty h3{font:700 25px Georgia,serif;margin:12px 0}.ideas-empty p{font-size:12px;color:#758277}\n",
  "@media(max-width:1250px){.signal-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.mission-columns{grid-template-columns:1fr}}\n",
  "@media(max-width:700px){.mission-head{align-items:start;flex-direction:column}.mission-master{align-items:start;flex-wrap:wrap}.mission-master>.btn{margin-left:34px}.signal-grid,.compare-grid,.idea-grid{grid-template-columns:1fr}.signal-card{min-height:142px}.signal-head{margin-bottom:12px}.mission-panel-head h2{font-size:20px}.ideas-hero{padding:24px 19px}.compare-evidence-grid{gap:11px}.mission-quicklinks{gap:11px}}\n",
  "@media(max-width:700px){.mission-master{display:grid;grid-template-columns:20px minmax(0,1fr);align-items:start}.mission-master .master-light{grid-column:1;grid-row:1}.mission-master div:nth-child(2){grid-column:2;grid-row:1;min-width:0}.mission-master>.btn{grid-column:2;grid-row:2;margin:0;justify-self:start}.mission-master strong{font-size:22px}.mission-master span{letter-spacing:.09em}.mission-head-actions{width:100%}}\n",
  ".health-ribbon{display:flex;align-items:center;justify-content:space-between;gap:18px;background:#f7f8f2;border:1px solid var(--line);border-radius:10px;padding:14px 18px;margin-top:14px}.health-ribbon b{display:block;font-size:12px;color:#325043}.health-ribbon span:not(.mission-tag):not(.mission-lamp){font-size:11px;color:#77897b;display:block;margin-top:3px}.health-ribbon>div:last-child{display:flex;align-items:center;gap:13px;flex-wrap:wrap}.health-ribbon a{white-space:nowrap}\n",
  "@media(max-width:700px){.health-ribbon{align-items:start;flex-direction:column;gap:8px}}\n",
  "\n",
  "\n",
  "/* Links Desk: safe same-origin navigation plus ordinary external anchors; no API connectors. */\n",
  ".links-intro{display:flex;align-items:flex-start;gap:12px;background:#f5f6ee;border:1px solid var(--line);border-radius:12px;padding:16px 19px;margin:0 0 26px}.links-intro>svg{width:20px;height:20px;color:var(--green);flex:0 0 auto}.links-intro strong{display:block;font-size:13px}.links-intro p{color:#738076;font-size:12px;margin:4px 0 0}\n",
  ".links-category{margin:28px 0 13px}.links-category h2{font:700 21px Georgia,serif;color:#1c382f;margin:0 0 5px}.links-category p{font-size:12px;color:#75827a;margin:0}\n",
  ".links-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:13px}\n",
  ".links-card{display:flex;align-items:flex-start;gap:11px;min-height:97px;padding:17px 16px;border-radius:12px;border:1px solid var(--line);background:var(--paper);text-decoration:none;box-shadow:var(--shadow);color:var(--ink);transition:border-color .12s,background .12s;min-width:0}\n",
  ".links-card:hover{background:#f5f8f1;border-color:#9fb6a8;text-decoration:none}.links-card:focus-visible{outline:3px solid var(--gold);outline-offset:2px}\n",
  ".links-card-icon{height:32px;width:32px;display:flex;align-items:center;justify-content:center;border-radius:10px;background:#edf1e9;color:#467664;flex:0 0 auto}.links-card-icon svg{width:17px;height:17px}\n",
  ".links-card-body{flex:1;min-width:0}.links-card-body strong{font-size:13px;display:block;line-height:1.3}.links-card-body small{display:block;color:#748277;line-height:1.45;font-size:11px;margin-top:5px}.links-card .link-out{color:#869b8b;width:14px;height:14px;flex:0 0 auto;margin-top:3px}\n",
  ".links-footnote{margin-top:27px;padding-top:16px;border-top:1px solid var(--line);font-size:11px;color:#718077}\n",
  "@media(max-width:1040px){.links-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}\n",
  "@media(max-width:610px){.links-grid{grid-template-columns:1fr}.links-card{min-height:79px}.links-intro{padding:13px}}\n",
  "</style>\n",
  "</head>\n",
  "<body>\n",
  "<div id=\"app\" class=\"app\">\n",
  "  <aside class=\"sidebar\" aria-label=\"Admin navigation\">\n",
  "    <div class=\"brand\"><div class=\"brandmark\"><div class=\"crest\" aria-hidden=\"true\">TF<br>FAC</div><div><strong>TIN FOIL<br>FA CUP</strong><small>MISSION CONTROL</small></div></div><div class=\"internal\">PRIVATE HEADQUARTERS</div></div>\n",
  "    <div class=\"nav-group\"><small>WORKSPACE</small><button class=\"nav active\" data-nav=\"overview\" title=\"Mission Control\"><span class=\"nav-icon\" data-icon=\"layout\"></span><span>Mission Control</span></button><button class=\"nav\" data-nav=\"clubfinder\" title=\"Clubfinder audit\"><span class=\"nav-icon\" data-icon=\"search\"></span><span>Clubfinder audit</span><span class=\"count\" id=\"sidebar-club-count\">651</span></button><button class=\"nav\" data-nav=\"radar\" title=\"Club Entry Radar\"><span class=\"nav-icon\" data-icon=\"activity\"></span><span>Club Entry Radar</span></button><button class=\"nav\" data-nav=\"outreach\" title=\"Outreach desk\"><span class=\"nav-icon\" data-icon=\"mail\"></span><span>Outreach desk</span></button><button class=\"nav\" data-nav=\"ombudsman\" title=\"Ombudsman watchers\"><span class=\"nav-icon\" data-icon=\"activity\"></span><span>Ombudsman</span></button></div>\n",
  "    <div class=\"nav-group\"><small>GOVERNANCE</small><button class=\"nav\" data-nav=\"pullrequests\" title=\"GitHub PR queue\"><span class=\"nav-icon\" data-icon=\"route\"></span><span>GitHub PR queue</span></button><button class=\"nav\" data-nav=\"approvals\" title=\"Review ledger\"><span class=\"nav-icon\" data-icon=\"clipboard\"></span><span>Review ledger</span></button><button class=\"nav\" data-nav=\"sources\" title=\"Sources and safety\"><span class=\"nav-icon\" data-icon=\"shield\"></span><span>Sources &amp; safety</span></button></div>\n",
  "    <div class=\"nav-group\"><small>YOUR DESK</small><button class=\"nav\" data-nav=\"links\" title=\"Links Desk\"><span class=\"nav-icon\" data-icon=\"external\"></span><span>Links Desk</span></button></div>\n",
  "    <div class=\"nav-group\"><small>THE FUN BIT</small><button class=\"nav\" data-nav=\"ideas\" title=\"Ideas board\"><span class=\"nav-icon\" data-icon=\"info\"></span><span>Ideas board</span></button></div>\n",
  "    <div class=\"sidebar-footer\"><b><span class=\"dot\" style=\"color:#e9ba72\"></span> Production protected</b>No sends, merges, canonical changes or publication are available in this workspace.<div style=\"margin-top:12px\">TFFAC \u2022 2026\u201327</div></div>\n",
  "  </aside>\n",
  "  <main class=\"main\">\n",
  "    <header class=\"topbar\"><div class=\"breadcrumb\">TIN FOIL FA CUP <span style=\"margin:0 9px;color:#a7b4a6\">/</span> <strong id=\"crumb\">OVERVIEW</strong></div><div class=\"top-actions\"><span class=\"sync-note\" id=\"sync-label\"><span class=\"dot\" style=\"color:#bc965a\"></span> Checking sources\u2026</span><button class=\"btn small\" data-action=\"refresh-all\"><span data-icon=\"refresh\"></span> Refresh sources</button><button class=\"btn primary small\" data-nav=\"approvals\"><span data-icon=\"clipboard\"></span> Review queue</button><form method=\"POST\" action=\"/logout\" style=\"margin:0;display:inline-flex\"><button type=\"submit\" class=\"btn small\" aria-label=\"Sign out of Mission Control\">Sign out</button></form></div></header>\n",
  "    <div id=\"content\" class=\"content\"></div>\n",
  "  </main>\n",
  "</div>\n",
  "<div id=\"overlay\"></div>\n",
  "<div class=\"toast-area\" id=\"toast-area\" aria-live=\"polite\"></div>\n",
  "<input hidden type=\"file\" id=\"import-workspace\" accept=\"application/json,.json\">\n",
  "<input hidden type=\"file\" id=\"import-clubs\" accept=\"application/json,.json\">\n",
  "<input hidden type=\"file\" id=\"import-postcodes\" accept=\"text/csv,.csv,text/plain\">\n",
  "<input hidden type=\"file\" id=\"import-ombudsman\" accept=\"application/json,.json\">\n",
  "<input hidden type=\"file\" id=\"import-radar\" accept=\"application/json,.json\">\n",
  "<script>\n",
  "/* Tin Foil FA Cup \u2014 Mission Control. Authenticated pilot, never a production writer. */\n",
  "const TRUSTED_OMBUDSMAN_FEED = false; // Manual JSON imports are not attested by the Worker.\n",
  "'use strict';\n",
  "\n",
  "function missionAgeFresh(at,minutes){return !!at && Number.isFinite(Date.parse(at)) && Date.now()-Date.parse(at)<minutes*60000 && Date.now()>=Date.parse(at)-120000;}\n",
  "function missionCSV(text){\n",
  "  let rows=[],row=[],cell='',quoted=false;\n",
  "  text=String(text||'').replace(/^\\uFEFF/,'');\n",
  "  for(let i=0;i<text.length;i++){\n",
  "    const c=text[i];\n",
  "    if(c==='\"'){if(quoted&&text[i+1]==='\"'){cell+='\"';i++;}else quoted=!quoted;}\n",
  "    else if(c===','&&!quoted){row.push(cell.trim());cell='';}\n",
  "    else if((c==='\\r'||c==='\\n')&&!quoted){if(c==='\\r'&&text[i+1]==='\\n')i++;row.push(cell.trim());if(row.some(Boolean))rows.push(row);row=[];cell='';}\n",
  "    else cell+=c;\n",
  "  }\n",
  "  if(quoted)throw Error('Unclosed CSV quote.');\n",
  "  row.push(cell.trim());if(row.some(Boolean))rows.push(row);\n",
  "  if(!rows.length||rows[0].slice(0,4).join('|')!=='Club|Postcode|Entry Round|Location Status')throw Error('Expected Club, Postcode, Entry Round, Location Status columns.');\n",
  "  return rows.slice(1).filter(r=>r[0]&&r[1]).map(r=>({club:r[0],postcode:r[1].toUpperCase().replace(/\\s+/g,' ').trim(),entryRound:r[2]||'',locationStatus:r[3]||'unknown'}));\n",
  "}\n",
  "function missionUsePostcodes(text,label){\n",
  " const rows=missionCSV(text);\n",
  " if(rows.length<100)throw Error('The postcode reference has fewer than 100 records; full-queue checking is unavailable.');\n",
  " state.postcodeRows=rows;state.postcodeAt=iso();state.postcodeSource=label;state.postcodeError=null;\n",
  "}\n",
  "async function missionPullPostcodes(){\n",
  " try{missionUsePostcodes(await getText(`${RAW}/tester-club-postcodes.csv`),'GitHub tester-club-postcodes.csv');}\n",
  " catch(ex){state.postcodeError=ex.message;/* Retain a previously imported reference in this session, with its provenance. */}\n",
  "}\n",
  "async function missionPullPRs(){\n",
  " try{let r=await getJSON(`${API}/pulls?state=open&per_page=100&sort=updated&direction=desc`);if(!Array.isArray(r))throw Error('Unexpected PR response');\n",
  " state.openPRs=r.map(p=>({number:p.number,title:p.title,html_url:p.html_url,draft:p.draft,updated_at:p.updated_at,created_at:p.created_at}));state.prAt=iso();state.prError=null;}\n",
  " catch(ex){state.prError=ex.message;state.prAt=null;state.openPRs=null;}\n",
  "}\n",
  "function missionToneBadge(label,tone){return `<span class=\"mission-tag ${tone}\"><span class=\"mission-lamp\"></span>${e(label)}</span>`;}\n",
  "function missionWorkerSignal(){\n",
  " if(state.ombudsmanAttempted){\n",
  "  const r=state.liveOmbudsman;\n",
  "  if(!r)return {tone:'unknown',title:'Feed unavailable',detail:'Read-only Worker health not established',action:'ombudsman'};\n",
  "  if(!r.fresh)return {tone:'unknown',title:'Report stale',detail:'Last observed '+(r.checked_at?since(r.checked_at):'unknown'),action:'ombudsman'};\n",
  "  if(r.state==='critical')return {tone:'danger',title:'Watcher failure',detail:'Critical scheduled-run evidence; investigate',action:'ombudsman'};\n",
  "  if(r.state==='warning')return {tone:'warning',title:'Scheduling gap',detail:'Watchers not fully healthy; overall unverified',action:'ombudsman'};\n",
  "  if(r.state==='pending')return {tone:'warning',title:'Run pending',detail:'Not a confirmed recovery',action:'ombudsman'};\n",
  "  if(r.state==='healthy')return {tone:'good',title:'Watchers healthy',detail:'Recent scheduled success; overall still unverified',action:'ombudsman'};\n",
  "  return {tone:'unknown',title:'Status unknown',detail:'No reliable watcher health',action:'ombudsman'};\n",
  " }\n",
  " const s=workspace.ombudsmanSnapshot;\n",
  " if(!s)return {tone:'unknown',title:'Not connected',detail:'Worker verification unknown',action:'ombudsman'};\n",
  " const o=currentOmbudsmanState(),stale=!missionAgeFresh(s.observed_at,25);\n",
  " if(stale)return {tone:'unknown',title:'Stale evidence',detail:'Latest worker status unknown',action:'ombudsman'};\n",
  " if(TRUSTED_OMBUDSMAN_FEED && s.overall_verified===true&&['verified','healthy','recovered_verified'].includes(String(s.status||'').toLowerCase()))return {tone:'good',title:'Worker verified',detail:'Snapshot attests overall verification',action:'ombudsman'};\n",
  " if(/recover/i.test(s.status||''))return {tone:'warning',title:'Recovered \u00b7 unverified',detail:'Recovery is not all-clear',action:'ombudsman'};\n",
  " if(/incident|fail|gap/i.test(s.status||''))return {tone:'danger',title:'Incident reported',detail:'Investigate worker evidence',action:'ombudsman'};\n",
  " return {tone:'warning',title:'Verification held',detail:o.badge,action:'ombudsman'};\n",
  "}\n",
  "function missionWorkflowSignal(kind){\n",
  " if(!state.workflowAt||!missionAgeFresh(state.workflowAt,20)||!state.workflow[kind])return {tone:'unknown',title:'Status unknown',detail:'Run feed unavailable or stale',action:'ombudsman'};\n",
  " const result=computeSchedule(kind);\n",
  " if(result.unobserved)return {tone:'warning',title:`${result.unobserved} not observed`,detail:'Scheduled slots need investigation',action:'ombudsman'};\n",
  " if(result.delayed)return {tone:'warning',title:`${result.delayed} delayed`,detail:'Launch delay requires follow-up',action:'ombudsman'};\n",
  " if(!result.observed)return {tone:'unknown',title:'Not yet observed',detail:'No completed observation window',action:'ombudsman'};\n",
  " return {tone:'good',title:'Runs observed',detail:'Scheduling observation only',action:'ombudsman'};\n",
  "}\n",
  "function missionPRSignal(){\n",
  " if(!Array.isArray(state.openPRs)||!missionAgeFresh(state.prAt,20))return {tone:'unknown',title:'Queue unknown',detail:'GitHub PR source unavailable',action:'pullrequests'};\n",
  " const n=state.openPRs.length;\n",
  " return n?{tone:'warning',title:`${n}${n>=100?'+':''} open PR${n===1?'':'s'}`,detail:`${state.openPRs.filter(p=>p.draft).length} draft \u00b7 manual triage required`,action:'pullrequests'}:{tone:'good',title:'No open PRs',detail:'GitHub list fetched; no merge implied',action:'pullrequests'};\n",
  "}\n",
  "function missionClubSignal(){\n",
  " if(!state.queueLoaded)return {tone:'unknown',title:'Queue not loaded',detail:'Sample is not a complete audit',action:'clubfinder'};\n",
  " if(!missionAgeFresh(state.queueTime,60))return {tone:'unknown',title:'Queue data stale',detail:'Recheck repository source',action:'clubfinder'};\n",
  " const unresolved=state.queue.filter(x=>x.status!=='verified').length;\n",
  " return {tone:'warning',title:`${unresolved} unresolved identities`,detail:`${state.queueMeta.eligible_linked}/${state.queueMeta.eligible} eligible links recorded`,action:'clubfinder'};\n",
  "}\n",
  "\n",
  "function missionGmailNormalize(name){return String(name||'').toLowerCase().replace(/[\u2019']/g,'').replace(/\\b(?:football club|a\\.?f\\.?c\\.?|f\\.?c\\.?)\\b/g,'').replace(/[^a-z0-9]+/g,' ').trim().replace(/\\s+/g,' ')}\n",
  "function missionGmailUnique(records){return [...new Set((records||[]).map(x=>missionGmailNormalize(x.club)).filter(Boolean))]}\n",
  "function missionGmailCountAuditV6(records){ const parts={classic:[],current:[]},all=new Map(); for(const row of records||[]){const kind=row.kind==='current'?'current':'classic',raw=String(row.club||'').trim(),key=missionGmailNormalize(raw);if(!key)continue;parts[kind].push(key);if(!all.has(key))all.set(key,{n:0,c:0,r:0,name:raw});const entry=all.get(key);entry.n++;if(kind==='classic')entry.c++;else entry.r++;} const a=new Set(parts.classic),b=new Set(parts.current); const duplicates=[...all.values()].filter(v=>v.n>1).sort((x,y)=>y.n-x.n||x.name.localeCompare(y.name)); return {total:(records||[]).length,classic:parts.classic.length,current:parts.current.length,classicUnique:a.size,currentUnique:b.size,overlap:[...a].filter(k=>b.has(k)).length,combined:all.size,duplicateKeys:duplicates.length,excess:[...all.values()].reduce((n,v)=>n+v.n-1,0),top:duplicates.slice(0,8)};}function missionGmailCountAuditV6Html(records){ const a=missionGmailCountAuditV6(records); const top=a.top.length?a.top.map(v=>`${e(v.name)} (${v.n}: old ${v.c}, new ${v.r})`).join(' \u00b7 '):'None'; return `<div class=\"tiny-note\" style=\"margin-top:10px;padding:12px;border:1px solid #dddcd0;border-radius:9px;line-height:1.8;overflow-wrap:anywhere\"><strong>Count Audit v6 \u00b7 identification only</strong><div>Original: ${a.classic} messages / ${a.classicUnique} unique \u00b7 Newer: ${a.current} messages / ${a.currentUnique} unique \u00b7 Shared club keys: ${a.overlap}</div><div>Combined: ${a.combined} unique \u00b7 ${a.duplicateKeys} repeated keys \u00b7 ${a.excess} messages above one per key</div><div><strong>Most repeated club labels:</strong> ${top}</div><div>Diagnostic only; the displayed club count is unchanged. Normalised club labels can still be inaccurate.</div></div>`;}function missionGmailAuditLine(a){if(!a)return '';const s=k=>{const p=a[k]||{};return k+': '+(p.accepted||0)+'/'+(p.listed||0)+' recognised, '+(p.repliesSkipped||0)+' replies excluded, '+(p.unparseable||0)+' unparsed, '+(p.subjectSkipped||0)+' other, '+(p.idRejected||0)+' invalid IDs'+(p.bodiesMissing?' ('+p.bodiesMissing+' without a readable text body)':'')};return 'Scan audit \u00b7 '+s('classic')+' \u00b7 '+s('current');}\n",
  "const GMAIL_COUNT_KEY='tffac-mission-control-gmail-count-v1';\n",
  "const GMAIL_SYNC_KEY='tffac-mission-control-gmail-sync-v1';\n",
  "const GMAIL_SYNC_LOCK='tffac-mission-control-gmail-v1';\n",
  "const GMAIL_GRANT_HEADER='X-TFFAC-Gmail-Grant';\n",
  "const GMAIL_AUDIT_FIELDS=['listed','fetched','accepted','repliesSkipped','subjectSkipped','unparseable','bodiesMissing','idRejected'];\n",
  "const GMAIL_MESSAGES={\n",
  " sign_in_required:'Mission Control session expired. Sign in again, then reconnect Gmail read-only.',\n",
  " gmail_not_connected:'Gmail is disconnected. Connect Gmail read-only to check Sent.',\n",
  " gmail_grant_expired:'Gmail permission expired. Reconnect Gmail read-only to continue.',\n",
  " gmail_grant_rejected:'Gmail rejected the saved permission. Reconnect Gmail read-only.',\n",
  " gmail_permission:'Gmail denied read access. Disconnect and reconnect Gmail. If it persists, check the mailbox policy.',\n",
  " gmail_quota:'Gmail rate or quota limit reached. Wait before refreshing.',\n",
  " gmail_network:'Gmail request could not reach Mission Control or Gmail. Check the connection and retry.',\n",
  " gmail_upstream:'Gmail or Mission Control returned an unusable response. Try again.',\n",
  " gmail_scan_incomplete:'Scan incomplete. Check the audit for unresolved records or retry the scan.',\n",
  " gmail_connection_changed:'Gmail connection changed in another tab. Check the connection and retry.',\n",
  " gmail_sync_unavailable:'Browser coordination is unavailable. Use a secure browser with local storage and Web Locks to refresh, disconnect or clear Gmail data.',\n",
  " gmail_disconnect_unconfirmed:'Disconnect could not be confirmed. Check Gmail status and retry.',\n",
  "};\n",
  "function missionGmailLoadCount(){\n",
  " try{\n",
  "  const saved=JSON.parse(localStorage.getItem(GMAIL_COUNT_KEY)||'null');\n",
  "  const when=Date.parse(saved?.checkedAt);\n",
  "  if(saved?.version===1&&Number.isSafeInteger(saved.count)&&saved.count>=0&&Number.isFinite(when)&&\n",
  "     when<=Date.now()&&new Date(when).toISOString()===saved.checkedAt){\n",
  "   return {version:1,count:saved.count,checkedAt:saved.checkedAt};\n",
  "  }\n",
  " }catch{}\n",
  " return null;\n",
  "}\n",
  "function missionGmailState(last=missionGmailLoadCount(),connection='unknown'){\n",
  " return {last,connection,operation:null,controller:null,error:null,result:null,drafts:null,draftError:null,\n",
  "  audit:null,progress:0,saveFailed:false,grant:null,fence:missionGmailShared().fence};\n",
  "}\n",
  "// This record contains only opaque grant fingerprints and browser operation identifiers.\n",
  "function missionGmailShared(){\n",
  " try{return JSON.parse(localStorage.getItem(GMAIL_SYNC_KEY))||{};}catch{return {};}\n",
  "}\n",
  "function missionGmailAdvance(g,grant,rejected=false){\n",
  " const fence=crypto.randomUUID();\n",
  " try{localStorage.setItem(GMAIL_SYNC_KEY,JSON.stringify({fence,grant,rejected}));}\n",
  " catch{throw Error('gmail_sync_unavailable');}\n",
  " g.fence=fence;\n",
  "}\n",
  "function missionGmailLocked(task){\n",
  " if(!navigator.locks)return Promise.reject(Error('gmail_sync_unavailable'));\n",
  " return navigator.locks.request(GMAIL_SYNC_LOCK,task);\n",
  "}\n",
  "function missionGmailCurrent(g){\n",
  " return state.gmail===g&&missionGmailShared().fence===g.fence;\n",
  "}\n",
  "function missionGmailSync(event){\n",
  " if(event.key!==null&&event.key!==GMAIL_SYNC_KEY&&event.key!==GMAIL_COUNT_KEY)return;\n",
  " const g=state.gmail;\n",
  " // An explicit Disconnect takes precedence over another tab's scan start.\n",
  " if(g.operation==='disconnecting')return;\n",
  " if(missionGmailCurrent(g)){\n",
  "  const last=missionGmailLoadCount();\n",
  "  if(last?.checkedAt!==g.last?.checkedAt||last?.count!==g.last?.count){\n",
  "   g.last=last;g.result=null;g.drafts=null;render();\n",
  "  }\n",
  "  return;\n",
  " }\n",
  " g.controller?.abort();\n",
  " state.gmail=missionGmailState();\n",
  " render();\n",
  " void missionGmailStatus();\n",
  "}\n",
  "window.addEventListener('storage',missionGmailSync);\n",
  "function missionGmailBegin(operation,changes={}){\n",
  " const previous=state.gmail;\n",
  " previous.controller?.abort();\n",
  " const g={...previous,...changes,operation,controller:new AbortController(),error:null};\n",
  " state.gmail=g;render();\n",
  " return g;\n",
  "}\n",
  "function missionGmailEnd(g){\n",
  " if(state.gmail===g){g.operation=null;g.controller=null;render();}\n",
  "}\n",
  "function missionGmailIssue(g,code){\n",
  " g.error=Object.hasOwn(GMAIL_MESSAGES,code)?code:'gmail_upstream';\n",
  " g.result=null;g.drafts=null;\n",
  " if(code==='sign_in_required')g.connection='sign_in_required';\n",
  " else if(['gmail_not_connected','gmail_grant_expired','gmail_grant_rejected'].includes(code))g.connection='reconnect';\n",
  "}\n",
  "function missionGmailCountState(g){\n",
  " if(g.operation==='refreshing')return 'Refreshing';\n",
  " if(g.result)return 'Current';\n",
  " return g.last?'Stale':'Unknown';\n",
  "}\n",
  "function missionGmailTimestamp(value){\n",
  " return '<time datetime=\"'+e(value)+'\">'+e(niceDate(value))+'</time>';\n",
  "}\n",
  "function missionGmailPanel(compact=false){\n",
  " const g=state.gmail, countState=missionGmailCountState(g), clubs=g.last?.count??'Unknown';\n",
  " const today=g.result?.filter(x=>x.day===ukDay()).length;\n",
  " const instruction=g.error?GMAIL_MESSAGES[g.error]:g.connection==='disconnected'?'Disconnected. Connect Gmail read-only to check Sent.':\n",
  "  g.connection==='connected'?'Mailbox connected. Refresh to check Sent.':\n",
  "  g.connection==='reconnect'?'Reconnect Gmail read-only to continue.':'Connect Gmail read-only to check Sent.';\n",
  " const busy=g.operation==='refreshing'?'Refreshing Gmail Sent history \u00b7 '+g.progress+' recognised records\u2026':\n",
  "  g.operation==='disconnecting'?'Confirming Gmail disconnect\u2026':g.operation==='checking'?'Checking Gmail connection\u2026':'';\n",
  " const next=g.connection==='sign_in_required'?'<a class=\"btn small primary\" href=\"/login\">Sign in to Mission Control</a>':\n",
  "  g.connection==='connected'?`<button class=\"btn small\" data-action=\"gmail-refresh\" ${g.operation?'disabled':''}>${icon('refresh')} Refresh Gmail counts</button><button class=\"btn small\" data-action=\"gmail-disconnect\" ${g.operation==='disconnecting'?'disabled':''}>Disconnect Gmail</button>`:\n",
  "  '<a class=\"btn small primary\" href=\"/gmail/connect\">'+(g.connection==='reconnect'?'Reconnect Gmail read-only':'Connect Gmail read-only')+'</a>';\n",
  " const stale=g.last&&!g.result?`<p class=\"tiny-note\"><strong>Stale data</strong> \u00b7 Last complete scan ${missionGmailTimestamp(g.last.checkedAt)}.</p>`:'';\n",
  " const current=g.result?`<p class=\"tiny-note\">${g.result.length} first-contact messages \u00b7 ${today} sent today \u00b7 Checked ${missionGmailTimestamp(g.last.checkedAt)}.</p>`:'';\n",
  " const draftText=g.drafts?.complete?g.drafts.count:'Unknown';\n",
  " const draftDetail=g.draftError?GMAIL_MESSAGES[g.draftError]:g.drafts?\n",
  "  (g.drafts.complete?'Checked ':'Partial listing checked ')+missionGmailTimestamp(g.drafts.checkedAt):\n",
  "  g.operation==='drafts'?'Checking drafts\u2026':'No complete draft listing.';\n",
  " const content=`<div class=\"mission-panel-head\"><div><div class=\"eyebrow\">GMAIL \u00b7 READ-ONLY</div><h2>Clubs contacted: ${e(clubs)}</h2><p>${e(busy||instruction)}</p>${current}${stale}</div>${missionToneBadge(countState.toUpperCase(),countState==='Current'?'good':g.last?'warning':'unknown')}</div>\n",
  " <div class=\"btn-row\" style=\"margin-top:12px\">${next}<a class=\"btn small\" href=\"https://mail.google.com/mail/u/?authuser=tinfoilfacup%40gmail.com#drafts\" rel=\"noopener noreferrer\" target=\"_blank\">Open Gmail drafts</a></div>\n",
  " ${!compact?`<div class=\"grid3\" style=\"margin-top:16px\">${metric('Gmail drafts',draftText,draftDetail,'clock')}</div>`:''}\n",
  " ${g.audit?`<p class=\"tiny-note\" style=\"margin-top:9px\">${e(missionGmailAuditLine(g.audit))}</p>`:''}\n",
  " ${g.result&&!compact?missionGmailCountAuditV6Html(g.result):''}\n",
  " ${g.saveFailed?'<p class=\"tiny-note\">Browser storage is unavailable. This count may be lost on reload.</p>':''}\n",
  " <p class=\"tiny-note\" style=\"margin-top:10px\">Gmail access is read-only. Completed counts and timestamps are saved in this browser.</p>`;\n",
  " return `<section class=\"surface pad\" style=\"margin-top:17px\">${content}</section>`;\n",
  "}\n",
  "async function missionGmailRequest(g,url,options={}){\n",
  " let response;\n",
  " try{\n",
  "  const headers={...options.headers};\n",
  "  if(g.grant&&url!=='/api/gmail/status')headers[GMAIL_GRANT_HEADER]=g.grant;\n",
  "  response=await fetch(url,{credentials:'same-origin',cache:'no-store',signal:g.controller.signal,...options,headers});\n",
  " }catch{throw Error('gmail_network');}\n",
  " let data;\n",
  " try{data=await response.json();}catch{throw Error('gmail_upstream');}\n",
  " if(state.gmail!==g)throw Error('gmail_obsolete');\n",
  " if(!response.ok)throw Error(Object.hasOwn(GMAIL_MESSAGES,data?.error)?data.error:'gmail_upstream');\n",
  " if(url==='/api/gmail/status'&&data?.connected){\n",
  "  const grant=response.headers.get(GMAIL_GRANT_HEADER);\n",
  "  if(!/^[a-zA-Z0-9_-]{43}$/.test(grant||''))throw Error('gmail_upstream');\n",
  "  data.grant=grant;\n",
  " }\n",
  " return data;\n",
  "}\n",
  "async function missionGmailStatus(){\n",
  " if(state.gmail.operation)return;\n",
  " const g=missionGmailBegin('checking',{fence:missionGmailShared().fence});\n",
  " try{\n",
  "  const data=await missionGmailRequest(g,'/api/gmail/status');\n",
  "  if(typeof data?.connected!=='boolean')throw Error('gmail_upstream');\n",
  "  const apply=()=>{\n",
  "   if(!missionGmailCurrent(g))return;\n",
  "   const grant=data.grant||null,shared=missionGmailShared();\n",
  "   // A different grant belongs to a newer connection, even after a full OAuth navigation.\n",
  "   if(navigator.locks&&(shared.grant??null)!==grant)missionGmailAdvance(g,grant);\n",
  "   g.grant=grant;\n",
  "   if(grant&&shared.grant===grant&&shared.rejected)missionGmailIssue(g,'gmail_grant_rejected');\n",
  "   else g.connection=grant?'connected':g.connection==='disconnected'?'disconnected':'reconnect';\n",
  "   if(!grant){\n",
  "    g.result=null;g.drafts=null;\n",
  "    if(data.reason==='gmail_grant_expired')g.error=data.reason;\n",
  "   }\n",
  "   return g;\n",
  "  };\n",
  "  return navigator.locks?await missionGmailLocked(apply):apply();\n",
  " }catch(error){\n",
  "  if(missionGmailCurrent(g)){g.connection='unknown';missionGmailIssue(g,error.message);}\n",
  " }finally{missionGmailEnd(g);}\n",
  "}\n",
  "async function missionGmailScanIssue(g,code){\n",
  " if(!missionGmailCurrent(g))return;\n",
  " if(code==='gmail_grant_rejected'){\n",
  "  try{\n",
  "   await missionGmailLocked(async()=>{\n",
  "    if(!missionGmailCurrent(g))return;\n",
  "    const status=await missionGmailRequest(g,'/api/gmail/status');\n",
  "    if(status.grant!==g.grant)throw Error('gmail_connection_changed');\n",
  "    missionGmailAdvance(g,g.grant,true);\n",
  "    missionGmailIssue(g,code);\n",
  "   });\n",
  "  }catch(error){if(missionGmailCurrent(g))missionGmailIssue(g,error.message);}\n",
  " }else missionGmailIssue(g,code);\n",
  "}\n",
  "function missionGmailCollectPage(data,kind,totals,found){\n",
  " const a=data?.audit;\n",
  " if(!Array.isArray(data?.rows)||!a||\n",
  "    GMAIL_AUDIT_FIELDS.some(key=>!Number.isSafeInteger(a[key])||a[key]<0||a[key]>20)||\n",
  "    a.listed!==a.fetched+a.idRejected||a.fetched!==a.accepted+a.repliesSkipped+a.subjectSkipped+a.unparseable||\n",
  "    a.bodiesMissing>a.unparseable||a.accepted!==data.rows.length||\n",
  "    (data.next!==null&&(typeof data.next!=='string'||data.next.length>1400||!data.next||!a.listed||!/^[A-Za-z0-9_\\-+/=]+$/.test(data.next)))||\n",
  "    data.rows.some(row=>typeof row?.club!=='string'||row.club.length>100||!missionGmailNormalize(row.club)||\n",
  "     (row.day!==null&&(typeof row.day!=='string'||!/^\\d{4}-\\d{2}-\\d{2}$/.test(row.day))))){\n",
  "  throw Error('gmail_scan_incomplete');\n",
  " }\n",
  " for(const key of GMAIL_AUDIT_FIELDS)totals[key]=(totals[key]||0)+a[key];\n",
  " found.push(...data.rows.map(row=>({club:row.club,day:row.day,kind})));\n",
  "}\n",
  "async function missionGmailScan(g){\n",
  " const found=[];\n",
  " for(const kind of ['classic','current']){\n",
  "  let page='',seen=new Set();\n",
  "  for(let n=0;n<40;n++){\n",
  "   const url='/api/gmail/outreach?kind='+kind+(page?'&page='+encodeURIComponent(page):'');\n",
  "   const data=await missionGmailRequest(g,url);\n",
  "   if(!missionGmailCurrent(g))return;\n",
  "   missionGmailCollectPage(data,kind,g.audit[kind],found);\n",
  "   g.progress=found.length;render();\n",
  "   if(data.next===null)break;\n",
  "   if(seen.has(data.next)||n===39)throw Error('gmail_scan_incomplete');\n",
  "   seen.add(data.next);page=data.next;\n",
  "  }\n",
  " }\n",
  " if(Object.values(g.audit).some(a=>a.unparseable||a.idRejected))throw Error('gmail_scan_incomplete');\n",
  " await missionGmailLocked(async()=>{\n",
  "  if(!missionGmailCurrent(g))return;\n",
  "  const status=await missionGmailRequest(g,'/api/gmail/status');\n",
  "  if(!missionGmailCurrent(g))return;\n",
  "  if(status.grant!==g.grant)throw Error('gmail_connection_changed');\n",
  "  g.result=found;\n",
  "  g.last={version:1,count:missionGmailUnique(found).length,checkedAt:new Date().toISOString()};\n",
  "  try{localStorage.setItem(GMAIL_COUNT_KEY,JSON.stringify(g.last));g.saveFailed=false;}catch{g.saveFailed=true;}\n",
  " });\n",
  "}\n",
  "async function missionGmailCheckDrafts(g){\n",
  " g.operation='drafts';render();\n",
  " try{\n",
  "  const data=await missionGmailRequest(g,'/api/gmail/drafts');\n",
  "  if(!missionGmailCurrent(g))return;\n",
  "  if(typeof data?.complete!=='boolean'||!Number.isSafeInteger(data.count)||data.count<0||data.count>500)throw Error('gmail_upstream');\n",
  "  g.drafts={count:data.complete?data.count:null,complete:data.complete,checkedAt:new Date().toISOString()};\n",
  " }catch(error){\n",
  "  if(!missionGmailCurrent(g))return;\n",
  "  g.draftError=Object.hasOwn(GMAIL_MESSAGES,error.message)?error.message:'gmail_upstream';\n",
  "  if(['sign_in_required','gmail_not_connected','gmail_grant_expired','gmail_grant_rejected'].includes(g.draftError)){\n",
  "   await missionGmailScanIssue(g,g.draftError);\n",
  "  }\n",
  " }\n",
  "}\n",
  "async function missionGmailRefresh(){\n",
  " if(state.gmail.operation||state.gmail.connection!=='connected')return;\n",
  " const g=missionGmailBegin('refreshing',{result:null,drafts:null,draftError:null,audit:{classic:{},current:{}},progress:0});\n",
  " try{\n",
  "  await missionGmailLocked(()=>{\n",
  "   if(!missionGmailCurrent(g))return;\n",
  "   const shared=missionGmailShared();\n",
  "   if(shared.grant!==g.grant||shared.rejected)throw Error('gmail_connection_changed');\n",
  "   missionGmailAdvance(g,g.grant);\n",
  "  });\n",
  "  if(!missionGmailCurrent(g))return;\n",
  "  try{await missionGmailScan(g);}catch(error){await missionGmailScanIssue(g,error.message);}\n",
  "  if(missionGmailCurrent(g)&&g.connection==='connected')await missionGmailCheckDrafts(g);\n",
  " }catch(error){if(missionGmailCurrent(g))missionGmailIssue(g,error.message);}\n",
  " finally{missionGmailEnd(g);}\n",
  "}\n",
  "async function missionGmailDisconnect(){\n",
  " if(state.gmail.operation==='disconnecting')return;\n",
  " const g=missionGmailBegin('disconnecting',{result:null,drafts:null,draftError:null,audit:null});\n",
  " try{\n",
  "  await missionGmailLocked(async()=>{\n",
  "   if(state.gmail!==g)return;\n",
  "   const shared=missionGmailShared();\n",
  "   if((shared.grant??null)!==g.grant){\n",
  "    g.fence=shared.fence;throw Error('gmail_connection_changed');\n",
  "   }\n",
  "   missionGmailAdvance(g,g.grant,shared.rejected);\n",
  "   const ack=await missionGmailRequest(g,'/gmail/disconnect',{method:'POST',mode:'same-origin',\n",
  "    redirect:'error',referrerPolicy:'same-origin',headers:{'X-TFFAC-Action':'disconnect'}});\n",
  "   if(ack?.disconnected!==true)throw Error('gmail_disconnect_unconfirmed');\n",
  "   const status=await missionGmailRequest(g,'/api/gmail/status');\n",
  "   if(status?.connected!==false)throw Error('gmail_disconnect_unconfirmed');\n",
  "   g.connection='disconnected';g.grant=null;\n",
  "   missionGmailAdvance(g,null);\n",
  "  });\n",
  " }catch(error){\n",
  "  if(missionGmailCurrent(g)){\n",
  "   const code=error.message;\n",
  "   missionGmailIssue(g,['sign_in_required','gmail_network','gmail_connection_changed','gmail_sync_unavailable'].includes(code)?code:'gmail_disconnect_unconfirmed');\n",
  "  }\n",
  " }finally{missionGmailEnd(g);}\n",
  "}\n",
  "async function missionGmailClearCount(){\n",
  " const previous=state.gmail;\n",
  " previous.controller?.abort();\n",
  " const g=missionGmailState(null,previous.operation==='disconnecting'?'unknown':previous.connection);\n",
  " g.grant=previous.grant;\n",
  " state.gmail=g;\n",
  " try{\n",
  "  await missionGmailLocked(()=>{\n",
  "   const shared=missionGmailShared();\n",
  "   missionGmailAdvance(g,shared.grant??null,shared.rejected);\n",
  "   localStorage.removeItem(GMAIL_COUNT_KEY);\n",
  "  });\n",
  "  return true;\n",
  " }catch{return false;}\n",
  "}\n",
  "function missionOutreachSignal(){\n",
  " const g=state.gmail,status=missionGmailCountState(g);\n",
  " if(g.result)return {tone:'good',title:`${g.last.count} clubs contacted`,detail:`Complete Gmail scan \u00b7 ${niceDate(g.last.checkedAt)}`,action:'outreach'};\n",
  " if(g.last)return {tone:'warning',title:`${g.last.count} clubs contacted \u00b7 Stale`,detail:`${status==='Refreshing'?'Refreshing \u00b7 ':''}Last complete scan ${niceDate(g.last.checkedAt)}`,action:'outreach'};\n",
  " return {tone:'unknown',title:'Clubs contacted: Unknown',detail:status==='Refreshing'?'Checking Gmail Sent history\u2026':\n",
  "  g.error?GMAIL_MESSAGES[g.error]:'A complete Gmail scan is needed.',action:'outreach'};\n",
  "}\n",
  "function missionSignalCard(name,key,s){return `<button class=\"signal-card ${s.tone}\" data-nav=\"${s.action}\" aria-label=\"${e(name)}: ${e(s.title)}. Open details\"><div class=\"signal-head\"><span>${e(name)}</span>${missionToneBadge(({good:'GREEN',warning:'AMBER',danger:'RED',unknown:'UNKNOWN'})[s.tone],s.tone)}</div><strong>${e(s.title)}</strong><small>${e(s.detail)}</small><span class=\"signal-more\">Inspect ${icon('arrow')}</span></button>`;}\n",
  "function missionHealthRibbon(){\n",
  " const report=state.healthText||'',dt=state.healthSourceDate;\n",
  " const checked=dt&&missionAgeFresh(dt,24*60)&&!!state.healthAt;\n",
  " const round=report.match(/Active round:\\s*\\*\\*([^*]+)\\*\\*/i)?.[1];\n",
  " const outstanding=report.match(/Results requiring confirmation:\\s*\\*\\*(\\d+)\\*\\*/i)?.[1];\n",
  " const explicitlyHealthy=/competition chronology healthy/i.test(report);\n",
  " const tone=checked&&explicitlyHealthy&&outstanding==='0'?'good':checked?'warning':'unknown';\n",
  " const label=tone==='good'?'Healthy at last source check':tone==='warning'?'Read report \u00b7 no all-clear':'Source unavailable or stale';\n",
  " const detail=checked?`${round||'Active round unspecified'} \u00b7 ${outstanding===undefined?'Overdue results unspecified':outstanding+' results requiring confirmation'} \u00b7 checked ${niceDate(dt)}`:`A current, trustworthy competition-health source has not been established. ${dt?'Last reported '+niceDate(dt):''}`;\n",
  " return `<div class=\"health-ribbon\"><div><b>Competition health \u00b7 read-only</b><span>${e(detail)}</span></div><div>${missionToneBadge(label,tone)} ${urlLink(`${GH}/blob/main/competition-health.md`,'Source')}</div></div>`;\n",
  "}\n",
  "function missionDaily(){if(!workspace.daily||workspace.daily.date!==ukDay()){workspace.daily={date:ukDay(),completed:[]};save()}return workspace.daily;}\n",
  "const MISSION_TASKS=[\n",
  " {key:'notes',label:'Read Where We Were and Things To Do',help:'Your Writer routine stays exactly where it belongs.'},\n",
  " {key:'health',label:'Check the machinery and Ombudsman',help:'Investigate amber, red or unknown signals.'},\n",
  " {key:'prs',label:'Triage open PRs',help:'Check what remains useful before approving anything.'},\n",
  " {key:'outreach',label:'Review introductions and replies',help:'Maximum 15 new introductions; SENT needs proof.'},\n",
  " {key:'finish',label:'Finish dailies and open the Ideas Board',help:'Make space for the What Ifs.'}\n",
  "];\n",
  "function missionDailyChecklist(){\n",
  " const day=missionDaily(),count=day.completed.filter(k=>MISSION_TASKS.some(t=>t.key===k)).length;\n",
  " return `<div class=\"daily-head\"><div><strong>Morning routine</strong><small>Your own checklist \u00b7 ${e(ukDay())}</small></div><span class=\"daily-count\">${count} / ${MISSION_TASKS.length}</span></div><div class=\"progress\"><span style=\"width:${count/MISSION_TASKS.length*100}%\"></span></div><div class=\"daily-list\">${MISSION_TASKS.map(t=>`<label class=\"daily-task\"><input type=\"checkbox\" data-daily=\"${t.key}\" ${day.completed.includes(t.key)?'checked':''}><span><b>${e(t.label)}</b><small>${e(t.help)}</small></span></label>`).join('')}</div><div class=\"tiny-note\">Ticking a task is only a personal marker, not evidence that a workflow actually ran.</div>`;\n",
  "}\n",
  "function missionPriorities(){\n",
  " let a=[];\n",
  " if(!state.queueLoaded)a.push({s:'unknown',t:'Load the full Clubfinder queue',d:'Only a sample is visible until the source loads.',nav:'clubfinder'});\n",
  " const ow=missionWorkerSignal();if(ow.tone!=='good')a.push({s:ow.tone,t:ow.title==='Not connected'?'Check Ombudsman verification':ow.title,d:'Worker status must be checked independently.',nav:'ombudsman'});\n",
  " if(state.workflowError)a.push({s:'unknown',t:'GitHub run feed unavailable',d:'Run status cannot be inferred from silence.',nav:'ombudsman'});\n",
  " const pr=missionPRSignal();if(pr.tone==='warning')a.push({s:'warning',t:'Review open PR queue',d:pr.title+' \u00b7 read before deciding what to keep.',nav:'pullrequests'});\n",
  " if(pr.tone==='unknown')a.push({s:'unknown',t:'PR list not refreshed',d:'GitHub triage status is unknown.',nav:'pullrequests'});\n",
  " const outs=workspace.outreach.filter(o=>o.status==='approved'||o.status==='awaiting_sent');if(outs.length)a.push({s:'warning',t:'Verify messages in SENT',d:`${outs.length} approved item(s) without SENT proof.`,nav:'outreach'});\n",
  " for(const p of workspace.proposals.filter(p=>p.status==='awaiting_review').slice(0,2))a.push({s:'warning',t:`Correction review: ${p.club}`,d:'Source-backed proposal requires an explicit decision.',nav:'approvals'});\n",
  " if(!a.length)a.push({s:'good',t:'No local blockers in this view',d:'This is not a claim that every external service is healthy.',nav:'sources'});\n",
  " return a.slice(0,6).map(r=>`<button class=\"priority-row\" data-nav=\"${r.nav}\"><span class=\"priority-dot ${r.s}\"></span><span><b>${e(r.t)}</b><small>${e(r.d)}</small></span>${icon('chevron')}</button>`).join('');\n",
  "}\n",
  "function missionOverview(){\n",
  " const ow=missionWorkerSignal(),rs=missionWorkflowSignal('results'),dr=missionWorkflowSignal('draw'),pr=missionPRSignal(),cl=missionClubSignal(),ot=missionOutreachSignal();\n",
  " const status=ow.tone==='danger'?'Incident reported':ow.tone==='warning'?'Verification needs attention':ow.tone==='unknown'?'All-clear not established':'Verified worker snapshot \u00b7 check other signals';\n",
  " const statusTone=ow.tone==='good'?'warning':ow.tone;\n",
  " const ids=Array.isArray(workspace.ideas)?workspace.ideas.filter(x=>x.state!=='archived'):[];\n",
  " return `<div class=\"mission-head\"><div><div class=\"eyebrow\">PRIVATE TFFAC HEADQUARTERS \u00b7 ${e(ukDay())}</div><h1>Mission Control<span class=\"mission-star\">\u2733</span></h1><p>The serious business of having fun.</p></div><div class=\"mission-head-actions\"><button class=\"btn\" data-action=\"refresh-all\">${icon('refresh')} Check the instruments</button><button class=\"btn primary\" data-nav=\"outreach\">${icon('mail')} Outreach desk</button><button class=\"btn\" data-nav=\"links\">${icon('external')} Links Desk</button></div></div>\n",
  " <div class=\"mission-master ${statusTone}\"><div class=\"master-light\"></div><div><span>OVERALL POSITION \u2014 BASED ON AVAILABLE EVIDENCE</span><strong>${e(status)}</strong><small>Unknown is not healthy. An observed GitHub run is not proof of Ombudsman recovery. Each lamp has its own source.</small></div><button class=\"btn small\" data-nav=\"ombudsman\">Open detail ${icon('arrow')}</button></div>\n",
  " ${ensureSourceWarning()}\n",
  " <div class=\"section-header mission-sec\"><div><h2>The instruments</h2><p>Five seconds to see what needs looking at. Grey means we do not know.</p></div>${missionToneBadge('NO UNVERIFIED ALL-CLEAR','unknown')}</div>\n",
  " <div class=\"signal-grid\">\n",
  " ${missionSignalCard('OMBUDSMAN','worker',ow)}\n",
  " ${missionSignalCard('RESULTS WATCH','results',rs)}\n",
  " ${missionSignalCard('DRAW WATCH','draw',dr)}\n",
  " ${missionSignalCard('GITHUB PULL REQUESTS','prs',pr)}\n",
  " ${missionSignalCard('CLUBFINDER AUDIT','clubs',cl)}\n",
  " ${missionSignalCard('OUTREACH DESK','outreach',ot)}</div>\n",
  " ${missionGmailPanel(true)}\n",
  " ${missionHealthRibbon()}\n",
  " <div class=\"mission-columns\"><section class=\"surface pad\"><div class=\"mission-panel-head\"><div><h2>What needs attention?</h2><p>Plain-English action queue, not a wall of logs.</p></div>${icon('activity')}</div><div class=\"priority-list\">${missionPriorities()}</div><div class=\"mission-quicklinks\"><a href=\"${GH}/pulls\" target=\"_blank\" rel=\"noopener noreferrer\">GitHub PRs ${icon('external')}</a><a href=\"https://mail.google.com/mail/u/?authuser=tinfoilfacup%40gmail.com#drafts\" target=\"_blank\" rel=\"noopener noreferrer\">Gmail drafts ${icon('external')}</a><a href=\"https://tinfoilfacup.com/clubfinder.html\" target=\"_blank\" rel=\"noopener noreferrer\">Public Clubfinder ${icon('external')}</a></div></section>\n",
  " <section class=\"surface pad\">${missionDailyChecklist()}</section></div>\n",
  " <div class=\"mission-columns mission-bottom\"><section class=\"surface pad\"><div class=\"mission-panel-head\"><div><h2>Outreach without the tab dance</h2><p>Paste the draft beside the postcode reference; compare exact strings.</p></div>${icon('mail')}</div><div class=\"mission-feature\"><div><strong>${e(state.queueMeta.eligible_linked)} / ${e(state.queueMeta.eligible)} eligible website links</strong><small>${state.queueLoaded?\"Latest fetched queue \u00b7\":\"Historic 17 Nov snapshot \u00b7\"} website coverage, not postcode or recipient approval.</small></div><div><strong>${slotsLeft()} of 15 introductions remaining today</strong><small>Local approved slots; Gmail must be checked independently.</small></div></div><div class=\"btn-row\"><button class=\"btn primary\" data-nav=\"outreach\">Open postcode comparison ${icon('arrow')}</button></div></section>\n",
  " <section class=\"surface pad ideas-teaser\"><div class=\"mission-panel-head\"><div><h2>And then \u2026 Ideas.</h2><p>Leave room for the glorious nonsense.</p></div>${icon('info')}</div><div class=\"idea-quote\">\u201cD\u2019you think we could make these mats flip over?\u201d</div><div class=\"idea-sub\">${ids.length?`${ids.length} idea${ids.length===1?'':'s'} saved in this browser.`:'An empty board, ready for the next What If.'}</div><div class=\"btn-row\"><button class=\"btn primary\" data-action=\"new-idea\">${icon('plus')} Capture a What If</button><button class=\"btn\" data-nav=\"ideas\">Ideas Board ${icon('arrow')}</button></div></section></div>\n",
  " <div class=\"mission-safety\">${icon('shield')} This is a Google-authenticated pilot. Source monitoring is read-only; manual Ombudsman imports are not attested. No live sends, merges, fixture updates, or Boot Room controls. Existing phone controls remain untouched. ${urlLink(`${GH}/blob/main/competition-health.md`,'Read-only health source')}</div>`;\n",
  "}\n",
  "function missionPostcodesFound(txt){\n",
  " const regex=/\\b(?:GIR\\s?0AA|(?:[A-Z]{1,2}\\d[A-Z\\d]?\\s?\\d[A-Z]{2}))\\b/gi;\n",
  " const found=String(txt||'').toUpperCase().match(regex)||[];\n",
  " return [...new Set(found.map(v=>v.replace(/\\s+/g,'').replace(/^(.*)(.{3})$/,'$1 $2')))];\n",
  "}\n",
  "function missionReferenceFor(club){if(!state.postcodeRows)return [];return state.postcodeRows.filter(r=>r.club.toLowerCase()===club.toLowerCase().trim());}\n",
  "function missionComparisonState(){\n",
  " const club=state.compareClub.trim(),refs=missionReferenceFor(club),found=missionPostcodesFound(state.compareDraft),chosen=found.length===1?found[0]:found.includes(state.compareChoice)?state.compareChoice:null;\n",
  " const base={club,refs,found,chosen,match:false,ready:false,tone:'unknown',title:'Enter an exact club name and paste an email draft.'};\n",
  " if(!state.postcodeRows){base.title='Postcode reference unavailable. Refresh sources or import the CSV.';return base;}\n",
  " if(!club){base.title='Choose the exact Clubfinder club identity.';return base;}\n",
  " if(!state.queueLoaded){base.tone='warning';base.title='Full Clubfinder identity queue not loaded \u2014 hold.';return base;}\n",
  " if(!state.queue.some(r=>r.club.toLowerCase()===club.toLowerCase())){base.tone='warning';base.title='No exact Clubfinder identity \u2014 do not guess.';return base;}\n",
  " if(refs.length!==1){base.tone='warning';base.title=refs.length?'Ambiguous postcode reference rows \u2014 hold.':'No exact club in postcode reference \u2014 hold.';return base;}\n",
  " if(!state.compareDraft.trim()){base.title='Paste the draft copy to check its postcode.';return base;}\n",
  " if(!found.length){base.tone='warning';base.title='No postcode found in draft \u2014 hold.';return base;}\n",
  " if(!chosen){base.tone='warning';base.title='Multiple postcodes found. Choose the one belonging to the proposed listing.';return base;}\n",
  " base.match=chosen===refs[0].postcode;\n",
  " if(!base.match){base.tone='danger';base.title='Postcode mismatch \u2014 do not approve.';return base;}\n",
  " if(refs[0].locationStatus.toLowerCase()!=='verified'){base.tone='warning';base.title='Text matches; source location state still requires evidence.';return base;}\n",
  " base.tone='good';base.title='Exact postcode text matches the reference.';base.ready=true;return base;\n",
  "}\n",
  "function missionCompareResult(){\n",
  " const c=missionComparisonState(),r=c.refs[0];\n",
  " const opt=c.found.length>1?`<div class=\"field\"><label for=\"mc-choice\">Which postcode is the actual proposed listing?</label><select id=\"mc-choice\" class=\"select\"><option value=\"\">Select explicitly \u2014 do not infer</option>${c.found.map(p=>`<option value=\"${e(p)}\" ${state.compareChoice===p?'selected':''}>${e(p)}</option>`).join('')}</select></div>`:'';\n",
  " const stateWord={good:'Text match',danger:'Mismatch',warning:'Held',unknown:'Unknown'}[c.tone];\n",
  " return `<div class=\"compare-status ${c.tone}\"><div class=\"compare-result-head\">${missionToneBadge(stateWord,c.tone)}<strong>${e(c.title)}</strong></div><div class=\"compare-evidence-grid\"><div><small>Draft postcode</small><b>${e(c.chosen||(!c.found.length?'Not detected':c.found.length===1?c.found[0]:'Multiple found'))}</b></div><div><small>Postcode reference</small><b>${e(r?r.postcode:'Unavailable')}</b></div><div><small>Entry round</small><b>${e(r?r.entryRound:'Unavailable')}</b></div><div><small>Source location state</small><b>${e(r?r.locationStatus:'Unavailable')}</b></div></div>${opt}<p class=\"text-xs muted\">${c.ready?'Only the postcode text and named CSV reference match. This does not independently establish the current ground, qualifying role, naming, sponsorship or recipient.':'Never correct the draft automatically; review the actual club evidence and Campaign path.'}</p><div class=\"btn-row\"><button class=\"btn small\" data-action=\"record-compare\" ${c.ready?'':'disabled'}>${icon('check')} Record text comparison</button><a class=\"btn small\" href=\"https://tinfoilfacup.com/clubfinder.html\" target=\"_blank\" rel=\"noopener noreferrer\">Open Clubfinder ${icon('external')}</a></div></div>`;\n",
  "}\n",
  "function missionComparisonDesk(){\n",
  " const loaded=!!state.postcodeRows;\n",
  " return `<section class=\"surface pad comparison-desk\"><div class=\"mission-panel-head\"><div><div class=\"eyebrow\">OUTREACH / QUICK CHECK</div><h2>Postcode comparison desk</h2><p>The same two-minute check, without six browser switches. Draft copy stays in memory until you leave this view.</p></div>${missionToneBadge(loaded?`${state.postcodeRows.length} reference rows`:'Source needed',loaded?'good':'unknown')}</div>\n",
  " <div class=\"compare-grid\"><div class=\"compare-left\"><div class=\"field\"><label for=\"mc-club\">Club \u2014 exact name from Clubfinder</label><input id=\"mc-club\" list=\"mc-club-options\" placeholder=\"Start typing the club name\" value=\"${e(state.compareClub)}\"><datalist id=\"mc-club-options\">${state.queue.map(r=>`<option value=\"${e(r.club)}\"></option>`).join('')}</datalist></div><div class=\"field\"><label for=\"mc-draft\">Email draft \u2014 paste the copy to check</label><textarea id=\"mc-draft\" rows=\"8\" placeholder=\"Paste the outreach email here. A postcode in a footer or signature may be detected too, so check the selected one.\">${e(state.compareDraft)}</textarea></div><div class=\"compare-source\">${icon('database')} ${loaded?`${e(state.postcodeSource)} \u00b7 loaded ${e(niceDate(state.postcodeAt))}`:'Postcode reference not loaded. No matching or publication decision can be claimed.'}<div class=\"btn-row\" style=\"margin-top:9px\"><button class=\"btn small\" data-action=\"import-postcodes\">Import trusted CSV</button>${urlLink(`${GH}/blob/main/tester-club-postcodes.csv`,'Inspect reference source')}<button class=\"btn small\" data-action=\"compare-clear\">Clear draft</button></div></div></div><div class=\"compare-right\"><div id=\"mc-result\" aria-live=\"polite\">${missionCompareResult()}</div><div class=\"compare-history\"><strong>Recent local text checks</strong>${(workspace.postcodeChecks||[]).slice(0,4).map(c=>`<div class=\"compare-history-row\"><span>${e(c.club)} \u00b7 ${e(c.postcode)}</span><small>${e(niceDate(c.checkedAt))}</small></div>`).join('')||'<small>No comparisons recorded yet.</small>'}</div></div></div>\n",
  " <div class=\"tiny-note\" style=\"margin-top:13px\">A Gmail draft is not fetched automatically here. The Gmail connection is separate from this comparison. Pasted copy is not saved. The comparison source is a test-postcode export, not a substitute for a current ground/venue investigation.</div></section>`;\n",
  "}\n",
  "function missionIdeaForm(idea){return `<div class=\"modal-backdrop\" data-dismiss=\"1\"><div class=\"modal\" role=\"dialog\" aria-modal=\"true\" aria-label=\"Ideas board editor\"><div class=\"modal-head\"><div><div class=\"eyebrow\">THE FUN BIT / THE IDEAS BOARD</div><h2>${idea.id?'Edit this What If':'Capture a What If'}</h2></div><button class=\"icon-btn\" data-action=\"close-overlay\">${icon('close')}</button></div><form id=\"mission-idea-form\" data-id=\"${e(idea.id||'')}\"><div class=\"form-grid\"><div class=\"field full\"><label>What's the idea?</label><input name=\"title\" required maxlength=\"180\" value=\"${e(idea.title||'')}\" placeholder=\"D\u2019you think we could\u2026?\"></div><div class=\"field full\"><label>Notes, curiosities, possible rabbit holes</label><textarea name=\"notes\" rows=\"5\" maxlength=\"4000\" placeholder=\"No deadlines. No obligation to turn this into a task.\">${e(idea.notes||'')}</textarea></div><div class=\"field\"><label>Where should it sit?</label><select name=\"state\"><option value=\"spark\" ${(idea.state||'spark')==='spark'?'selected':''}>Just an idea</option><option value=\"exploring\" ${idea.state==='exploring'?'selected':''}>Exploring</option><option value=\"parked\" ${idea.state==='parked'?'selected':''}>Parked for later</option><option value=\"archived\" ${idea.state==='archived'?'selected':''}>Archived, not deleted</option></select></div></div><div class=\"form-controls btn-row\"><button type=\"button\" class=\"btn primary\" data-action=\"save-idea\">${icon('save')} Save in this browser</button><button type=\"button\" class=\"btn\" data-action=\"close-overlay\">Cancel</button></div></form><p class=\"text-xs muted\">An idea is not a PR, a task, or a production change. Back up local work from Sources & safety.</p></div></div>`;}\n",
  "function missionIdeasPage(){\n",
  " const ideas=(workspace.ideas||[]).filter(i=>state.ideasFilter==='all'?i.state!=='archived':i.state===state.ideasFilter).sort((a,b)=>(b.updatedAt||'').localeCompare(a.updatedAt||''));\n",
  " return `${pageHead('04 / THE FUN BIT','The Ideas Board','The place where the What Ifs live. Not every thought needs a deadline or a pull request.',`<button class=\"btn primary\" data-action=\"new-idea\">${icon('plus')} A new What If</button>`)}\n",
  " <div class=\"ideas-hero\"><div class=\"eyebrow\">THERE IS ALWAYS ROOM FOR ONE MORE DAFT IDEA</div><h2>Make the sensible machinery run quietly.<br>Then invent something glorious.</h2><p>From flipping Beer Mats to Barry Air: one small question can become the next adventure.</p></div>\n",
  " <div class=\"section-header\"><div><h2>Ideas in your notebook</h2><p>Local to this browser; no production work is created from an idea.</p></div><div class=\"btn-row\"><select id=\"ideas-filter\" class=\"select\"><option value=\"all\" ${state.ideasFilter==='all'?'selected':''}>Open ideas</option><option value=\"spark\" ${state.ideasFilter==='spark'?'selected':''}>Just ideas</option><option value=\"exploring\" ${state.ideasFilter==='exploring'?'selected':''}>Exploring</option><option value=\"parked\" ${state.ideasFilter==='parked'?'selected':''}>Parked</option><option value=\"archived\" ${state.ideasFilter==='archived'?'selected':''}>Archive</option></select></div></div>\n",
  " <div class=\"idea-grid\">${ideas.map(i=>`<article class=\"idea-card\"><span class=\"idea-kicker\">${e(({spark:'A WHAT IF',exploring:'DOWN THE RABBIT HOLE',parked:'PARKED, NOT FORGOTTEN',archived:'ARCHIVED'})[i.state]||'IDEA')}</span><h3>${e(i.title)}</h3><p>${e(i.notes||'A thought worth keeping.')}</p><div class=\"idea-card-foot\"><small>Updated ${e(niceDate(i.updatedAt,true))}</small><button class=\"btn small\" data-action=\"edit-idea\" data-id=\"${e(i.id)}\">${icon('file')} Open</button></div></article>`).join('')||`<div class=\"ideas-empty\">${icon('info')}<h3>The board is yours.</h3><p>Nothing captured yet. The next flying helmet, Challenge or entirely improbable invention starts with one sentence.</p><button class=\"btn primary\" data-action=\"new-idea\">${icon('plus')} Put a thought on the board</button></div>`}</div>\n",
  " <div class=\"mission-safety\">${icon('info')} Your usual \u201cIdeas\u201d section in LibreOffice stays exactly as it is. This is an optional pocket notebook beside it.</div>`;\n",
  "}\n",
  "function missionPRPage(){\n",
  " const prs=Array.isArray(state.openPRs)?state.openPRs:[],live=Array.isArray(state.openPRs)&&missionAgeFresh(state.prAt,20),choice=state.prFilter||'all';\n",
  " const items=prs.filter(p=>choice==='all'?true:choice==='draft'?p.draft:choice==='ready'?!p.draft:!!(workspace.prReviews||[]).find(n=>n.number===p.number));\n",
  " return `${pageHead('GOVERNANCE / GITHUB','Open PR triage','One place to see the outstanding work. Notes here are local only: nothing is merged, closed or edited in GitHub.',`<button class=\"btn\" data-action=\"refresh-all\">${icon('refresh')} Refresh source</button><a class=\"btn primary\" target=\"_blank\" rel=\"noopener noreferrer\" href=\"${GH}/pulls\">Open GitHub PRs ${icon('external')}</a>`)}\n",
  " <div class=\"grid4\">${metric('Open PRs',live?`${prs.length}${prs.length===100?'+':''}`:'Unknown',live?'Live GitHub response; first 100 maximum':'Repository feed unavailable','route',live?'warn':'')}${metric('Draft PRs',live?prs.filter(p=>p.draft).length:'\u2014','Not ready for normal merge review','file')}${metric('Local triage notes',(workspace.prReviews||[]).length,'Review notes in this browser only','clipboard')}${metric('Source recency',live?since(state.prAt):'Unknown',live?`Fetched ${niceDate(state.prAt)}`:'No current observation','clock')}</div>\n",
  " <div class=\"gap16\"></div>${!live?banner('GitHub PR feed not currently available','Use the official GitHub PR page. A missing feed is not proof that the PR queue is empty.','error'):prs.length===100?banner('Pagination limit','This first-stage console reads only the latest 100 open PRs. More may exist. Check GitHub for the complete queue.') :banner('Human triage only','Visual changes may be obsolete; ingestion, publication, chronology and safety changes deserve deeper review. No PR is automatically classified or closed.')}\n",
  " ${sectionHeader('Review queue',live?`${prs.length} source items loaded; inspect changed files on GitHub before deciding.`:'No trustworthy queue available.',`<select class=\"select\" id=\"pr-filter\"><option value=\"all\" ${choice==='all'?'selected':''}>All open</option><option value=\"draft\" ${choice==='draft'?'selected':''}>Drafts</option><option value=\"ready\" ${choice==='ready'?'selected':''}>Ready for review</option><option value=\"marked\" ${choice==='marked'?'selected':''}>With local notes</option></select>`)}\n",
  " <div class=\"surface\"><div class=\"table-wrap\"><table><thead><tr><th>PR and title</th><th>GitHub state</th><th>Local review note</th><th>Updated</th><th></th></tr></thead><tbody>${live?items.map(p=>{const local=(workspace.prReviews||[]).find(v=>v.number===p.number);return `<tr><td><div class=\"row-title\"><a target=\"_blank\" rel=\"noopener noreferrer\" href=\"${e(p.html_url)}\">#${p.number} \u00b7 ${e(p.title)} ${icon('external')}</a></div><div class=\"row-desc\">Open in GitHub to inspect file changes, checks and discussion.</div></td><td>${p.draft?pill('Draft','amber'):pill('Open','blue')}</td><td>${local?`<strong class=\"text-xs\">${e(({review:'Investigate',carry:'Carry forward',obsolete:'Possibly obsolete',backend:'Backend priority',later:'Defer'})[local.decision]||local.decision)}</strong><div class=\"row-desc\">${e(local.note).slice(0,130)}</div>`:'<span class=\"muted\">Not triaged locally</span>'}</td><td>${e(niceDate(p.updated_at,true))}</td><td><button class=\"btn small\" data-action=\"review-pr\" data-number=\"${p.number}\">Review note ${icon('chevron')}</button></td></tr>`}).join(''):`<tr><td colspan=\"5\">${blank('Current PR feed unavailable','Refresh sources or use the official GitHub PR page.')}</td></tr>`}</tbody></table></div>${live&&!items.length?blank('No results in this filter','Change the local filter to see other open PRs.'):''}</div>\n",
  " <div class=\"mission-safety\">${icon('shield')} Local triage is not GitHub approval or branch review. Keep production protected: inspect changes, checks and relevant history before any merge.</div>`;\n",
  "}\n",
  "function missionPRNoteModal(pr){\n",
  " if(!pr)return '';\n",
  " const note=(workspace.prReviews||[]).find(v=>v.number===pr.number)||{};\n",
  " return `<div class=\"modal-backdrop\" data-dismiss=\"1\"><div class=\"modal\" role=\"dialog\" aria-modal=\"true\" aria-label=\"Local PR triage\"><div class=\"modal-head\"><div><div class=\"eyebrow\">PULL REQUEST #${pr.number} / LOCAL TRIAGE</div><h2>${e(pr.title)}</h2></div><button class=\"icon-btn\" data-action=\"close-overlay\">${icon('close')}</button></div>${banner('No repository action','This record is only a review note. \u201cPossibly obsolete\u201d does not close a PR; carrying forward does not merge it.')}<p>${urlLink(pr.html_url,`Inspect PR #${pr.number} on GitHub`)}</p><form id=\"mission-pr-form\" data-number=\"${pr.number}\"><div class=\"form-grid\"><div class=\"field full\"><label>Provisional triage assessment</label><select name=\"decision\"><option value=\"review\" ${!note.decision||note.decision==='review'?'selected':''}>Investigate further</option><option value=\"carry\" ${note.decision==='carry'?'selected':''}>Carry useful change forward</option><option value=\"backend\" ${note.decision==='backend'?'selected':''}>Backend / ingestion priority</option><option value=\"obsolete\" ${note.decision==='obsolete'?'selected':''}>Possibly obsolete \u2014 verify before close</option><option value=\"later\" ${note.decision==='later'?'selected':''}>Defer and return later</option></select></div><div class=\"field full\"><label>What has been checked? Evidence / context</label><textarea name=\"note\" rows=\"5\" maxlength=\"2500\" placeholder=\"Changed files, earlier fixes, relevant release, outstanding tests\u2026\">${e(note.note||'')}</textarea></div></div><div class=\"form-controls btn-row\"><button type=\"button\" class=\"btn primary\" data-action=\"save-pr-note\">${icon('save')} Save local assessment</button></div></form></div></div>`;\n",
  "}\n",
  "\n",
  "function missionHandleAction(a,button){\n",
  " if(a==='review-pr'){const p=state.openPRs?.find(p=>p.number===Number(button.dataset.number));if(p)open({type:'pr-note',pr:p});return true;}\n",
  " if(a==='save-pr-note'){const f=document.getElementById('mission-pr-form');if(!f)return true;const d=new FormData(f),number=Number(f.dataset.number),pr=state.openPRs?.find(p=>p.number===number);if(!pr)return true;const decision=String(d.get('decision')||'review'),note=String(d.get('note')||'').trim();if(!note||((decision==='obsolete'||decision==='carry')&&note.length<12)){toast('Write a useful explanation before recording this decision.',true);return true;}const entry={number,decision,note,updatedAt:iso(),title:pr.title};const old=(workspace.prReviews||[]).find(x=>x.number===number);if(old)Object.assign(old,entry);else workspace.prReviews.unshift(entry);record('pr_review',`Local PR #${number} assessment: ${decision}`,note.slice(0,250));state.overlay=null;nav('pullrequests');toast('Local triage saved. GitHub PR unchanged.');return true;}\n",
  " if(a==='import-postcodes'){document.getElementById('import-postcodes').click();return true;}\n",
  " if(a==='compare-clear'){state.compareDraft='';state.compareClub='';state.compareChoice='';render();return true;}\n",
  " if(a==='record-compare'){\n",
  " const c=missionComparisonState();if(!c.ready||!c.refs[0]){toast('No exact, verified reference text match to record.',true);return true;}\n",
  " workspace.postcodeChecks.unshift({id:id(),club:c.club,postcode:c.chosen,source:state.postcodeSource,checkedAt:iso(),status:'text_match_only'});workspace.postcodeChecks=workspace.postcodeChecks.slice(0,200);\n",
  " record('postcode_text_check',`Exact draft/reference postcode text: ${c.club}`,`${c.chosen} \u00b7 this does not verify ground, recipient or eligibility`);\n",
  " toast('Text comparison noted. Ground, identity and recipient verification are separate.');render();return true;\n",
  " }\n",
  " if(a==='new-idea'){open({type:'idea-form',idea:{}});return true;}\n",
  " if(a==='edit-idea'){const idea=(workspace.ideas||[]).find(i=>i.id===button.dataset.id);if(idea)open({type:'idea-form',idea});return true;}\n",
  " if(a==='save-idea'){\n",
  " const f=document.getElementById('mission-idea-form');if(!f)return true;const d=new FormData(f),title=String(d.get('title')||'').trim();if(!title){toast('Give the idea a title.',true);return true;}\n",
  " const found=(workspace.ideas||[]).find(i=>i.id===f.dataset.id);\n",
  " const row={id:found?.id||id(),title:title.slice(0,180),notes:String(d.get('notes')||'').trim().slice(0,4000),state:String(d.get('state')||'spark'),createdAt:found?.createdAt||iso(),updatedAt:iso()};\n",
  " if(!['spark','exploring','parked','archived'].includes(row.state))row.state='spark';\n",
  " if(found)Object.assign(found,row);else workspace.ideas.unshift(row);\n",
  " record('idea',`Idea ${found?'updated':'captured'}: ${row.title}`,row.state);state.overlay=null;nav('ideas');toast('Saved to your local Ideas Board.');return true;\n",
  " }\n",
  " return false;\n",
  "}\n",
  "function missionHandleChange(el){\n",
  " if(el.id==='import-postcodes'){\n",
  " const f=el.files?.[0];if(f){if(f.size>500000){toast('CSV exceeds 500 KB limit.',true);el.value='';return true;}\n",
  " f.text().then(t=>{missionUsePostcodes(t,`Imported CSV: ${f.name}`);toast(`${state.postcodeRows.length} postcode reference rows loaded.`);render();}).catch(ex=>toast('CSV rejected: '+ex.message,true)).finally(()=>el.value='');}return true;\n",
  " }\n",
  " if(el.id==='mc-choice'){state.compareChoice=el.value;missionRefreshCompare();return true;}\n",
  " if(el.id==='pr-filter'){state.prFilter=el.value;render();return true;}\n",
  " if(el.id==='ideas-filter'){state.ideasFilter=el.value;render();return true;}\n",
  " if(el.dataset.daily){const day=missionDaily(),key=el.dataset.daily;if(!MISSION_TASKS.some(t=>t.key===key))return true;\n",
  " day.completed=el.checked?[...new Set([...day.completed,key])]:day.completed.filter(v=>v!==key);save();render();return true;}\n",
  " return false;\n",
  "}\n",
  "function missionHandleInput(el){if(el.id==='mc-club'){state.compareClub=el.value;state.compareChoice='';missionRefreshCompare();}if(el.id==='mc-draft'){state.compareDraft=el.value;state.compareChoice='';missionRefreshCompare();}}\n",
  "function missionRefreshCompare(){const node=document.getElementById('mc-result');if(node)node.innerHTML=missionCompareResult();}\n",
  "\n",
  "</script>\n",
  "<script>\n",
  "/* TFFAC Admin Control \u2014 local-first review surface, no production write APIs. */\n",
  "'use strict';\n",
  "const OWNER='anvilspringstien', REPO='tinfoilfacup', GH=`https://github.com/${OWNER}/${REPO}`;\n",
  "const RAW=`https://raw.githubusercontent.com/${OWNER}/${REPO}/main`;\n",
  "const API=`https://api.github.com/repos/${OWNER}/${REPO}`;\n",
  "const WORKSPACE_KEY='tffac-admin-control-v1';\n",
  "const ICONS={\n",
  " layout:'<rect x=\"3\" y=\"3\" width=\"7\" height=\"7\" rx=\"1\"/><rect x=\"14\" y=\"3\" width=\"7\" height=\"7\" rx=\"1\"/><rect x=\"3\" y=\"14\" width=\"7\" height=\"7\" rx=\"1\"/><rect x=\"14\" y=\"14\" width=\"7\" height=\"7\" rx=\"1\"/>',\n",
  " search:'<circle cx=\"11\" cy=\"11\" r=\"7\"/><path d=\"m20 20-4-4\"/>',\n",
  " mail:'<rect x=\"3\" y=\"5\" width=\"18\" height=\"14\" rx=\"2\"/><path d=\"m3 7 9 6 9-6\"/>',\n",
  " activity:'<path d=\"M3 12h4l3-8 4 16 3-8h4\"/>',\n",
  " clipboard:'<rect x=\"5\" y=\"5\" width=\"14\" height=\"17\" rx=\"2\"/><rect x=\"9\" y=\"2\" width=\"6\" height=\"6\" rx=\"1\"/><path d=\"M9 13h6M9 17h5\"/>',\n",
  " shield:'<path d=\"M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z\"/><path d=\"m9 12 2 2 4-4\"/>',\n",
  " refresh:'<path d=\"M20 11a8 8 0 0 0-14-5L3 9m0-6v6h6M4 13a8 8 0 0 0 14 5l3-3m0 6v-6h-6\"/>',\n",
  " arrow:'<path d=\"M5 12h14m-6-6 6 6-6 6\"/>',\n",
  " chevron:'<path d=\"m9 18 6-6-6-6\"/>',\n",
  " external:'<path d=\"M12 5h7v7m0-7-9 9\"/><path d=\"M19 13v6H5V5h6\"/>',\n",
  " filter:'<path d=\"M3 5h18l-7 8v6l-4 2v-8L3 5Z\"/>',\n",
  " file:'<path d=\"M14 2H6v20h12V8Z\"/><path d=\"M14 2v6h6M9 13h6m-6 4h6\"/>',\n",
  " plus:'<path d=\"M12 5v14M5 12h14\"/>',\n",
  " alert:'<path d=\"M12 3 2 21h20L12 3Z\"/><path d=\"M12 9v5m0 4h.01\"/>',\n",
  " check:'<path d=\"m4 12 5 5L20 6\"/>',\n",
  " clock:'<circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M12 7v6l4 2\"/>',\n",
  " close:'<path d=\"m5 5 14 14M19 5 5 19\"/>',\n",
  " download:'<path d=\"M12 3v12m-4-4 4 4 4-4M4 17v4h16v-4\"/>',\n",
  " upload:'<path d=\"M12 21V9m-4 4 4-4 4 4M4 7V3h16v4\"/>',\n",
  " eye:'<path d=\"M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z\"/><circle cx=\"12\" cy=\"12\" r=\"3\"/>',\n",
  " lock:'<rect x=\"5\" y=\"10\" width=\"14\" height=\"12\" rx=\"2\"/><path d=\"M8 10V7a4 4 0 0 1 8 0v3\"/>',\n",
  " route:'<circle cx=\"6\" cy=\"5\" r=\"2\"/><circle cx=\"18\" cy=\"19\" r=\"2\"/><path d=\"M6 7v5h11a3 3 0 0 1 0 6\"/>',\n",
  " history:'<path d=\"M3 12a9 9 0 1 0 3-7M3 3v6h6\"/><path d=\"M12 7v6l4 2\"/>',\n",
  " database:'<ellipse cx=\"12\" cy=\"5\" rx=\"9\" ry=\"3\"/><path d=\"M3 5v14a9 3 0 0 0 18 0V5M3 12a9 3 0 0 0 18 0\"/>',\n",
  " save:'<path d=\"M4 3h14l3 3v15H3V3Z\"/><path d=\"M7 3v7h9V3M7 21v-8h10v8\"/>',\n",
  " info:'<circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M12 11v6m0-10h.01\"/>',\n",
  " send:'<path d=\"m22 2-7 20-4-9-9-4 20-7Z\"/><path d=\"M22 2 11 13\"/>',\n",
  " circle:'<circle cx=\"12\" cy=\"12\" r=\"8\"/>',\n",
  " list:'<path d=\"M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01\"/>',\n",
  "};\n",
  "const icon=(name)=>`<svg width=\"16\" height=\"16\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\">${ICONS[name]||ICONS.circle}</svg>`;\n",
  "const e=(s)=>String(s??'').replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'}[c]));\n",
  "const safeUrl=u=>{try{const x=new URL(u);return /^https?:$/.test(x.protocol)?x.href:null}catch{return null}};\n",
  "const urlLink=(u,label)=>{let x=safeUrl(u);return x?`<a class=\"document-link\" href=\"${e(x)}\" target=\"_blank\" rel=\"noopener noreferrer\">${e(label||x)} ${icon('external')}</a>`:`<span class=\"muted\">${e(label||u||'Not supplied')}</span>`};\n",
  "const id=()=>typeof crypto!=='undefined'&&crypto.randomUUID?crypto.randomUUID():`t-${Date.now().toString(36)}-${Math.random().toString(36).slice(2,9)}`;\n",
  "const iso=()=>new Date().toISOString();\n",
  "const ukDay=(d=new Date())=>{const p=new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/London',day:'2-digit',month:'2-digit',year:'numeric'}).formatToParts(d);const n=k=>p.find(x=>x.type===k).value;return `${n('year')}-${n('month')}-${n('day')}`};\n",
  "const niceDate=(d,short=false)=>{if(!d)return 'Not recorded';try{return new Date(d).toLocaleString('en-GB',{timeZone:'Europe/London',day:'numeric',month:'short',year:'numeric',...(short?{}:{hour:'2-digit',minute:'2-digit'})})}catch{return String(d)}};\n",
  "const since=(d)=>{if(!d)return 'Never';const m=Math.floor((Date.now()-new Date(d).getTime())/60000);if(!Number.isFinite(m))return 'Unknown';if(m<1)return 'Just now';if(m<60)return `${m}m ago`;if(m<1440)return `${Math.floor(m/60)}h ago`;return `${Math.floor(m/1440)}d ago`};\n",
  "const summaryBaseline={eligible:651,current_clubs:40,current_verified:40,current_linked:40,eligible_linked:319,competition_updated_at:'2026-11-17T03:55:02.447396+00:00',rows:682};\n",
  "const sampleNames=[\n",
  " ['AFC Fylde','verified','https://www.afcfylde.co.uk/',1,'https://www.afcfylde.co.uk/contact-us/'],\n",
  " ['Barnet','verified','https://barnetfc.com/',1,'https://barnetfc.com/'],\n",
  " ['Ashington FC','needs_verification','https://www.ashingtonafc.com/',0],\n",
  " ['Barnoldswick Town FC','needs_verification','https://www.barnoldswicktown.com/',0],\n",
  " ['Carlisle City FC','needs_verification','https://www.carlislecityfc.co.uk/',0],\n",
  " ['Kendal Town FC','needs_verification','https://kendaltownfc.org/',0],\n",
  " ...['Beckenham Town FC','Blackstones AFC','Boro Rangers FC','Bovey Tracey FC','Bridlington Town AFC','Cirencester Town FC','Clay Cross Town FC','Corsham Town FC','Coventry United FC','Cowes Sports FC','Dearne & District FC','Droylsden FC','Dunstable FC','East Cowes Victoria Athletic FC','Enfield FC','Epsom & Ewell FC','Hallen FC','Harwich & Parkeston FC','Hayes & Yeading United FC','Hebburn Town FC'].map(x=>[x,'missing',null,0])\n",
  "];\n",
  "const seedQueue=sampleNames.map((r,i)=>({club:r[0],identities:[r[0]],status:r[1],website:r[2],current_competition:!!r[3],priority:r[3]?0:r[1]==='needs_verification'?1:2,evidence:r[4]?[{url:r[2],evidence_url:r[4],verified_on:'2026-10-21',ledger:'club_website_verified_batch_04.json'}]:[],sample:true}));\n",
  "const heldReference={\n",
  " 'Beckenham Town FC':'Senior homepage was not verified as a working destination (batch 26).',\n",
  " 'Blackstones AFC':'League points to Facebook; no independently verified senior club site (batch 26).',\n",
  " 'Boro Rangers FC':'Preferred public homepage returned 503 (batch 26).',\n",
  " 'Bovey Tracey FC':'Club homepage returned 503 on verification (batch 26).',\n",
  " 'Clay Cross Town FC':'No current club-operated site established (batch 26).',\n",
  " 'Corsham Town FC':'Usable senior homepage could not be confirmed (batch 26).',\n",
  " 'Coventry United FC':'Club landing page shows a maintenance notice (batch 26).',\n",
  " 'Epsom & Ewell FC':'Historical Cobham pairing is stale; separately validate current ground before any promotion.',\n",
  " 'Belper United FC':'Eastwood groundshare ended; do not infer venue from former host.',\n",
  " 'Southall FC':'SkyEx groundshare ended; proposed Honeycroft venue requires independent confirmation.',\n",
  " 'Romulus FC':'B72 1NL groundshare relation remains HELD_FOR_MORE_EVIDENCE.'\n",
  "};\n",
  "const defaultWorkspace=()=>({version:1,proposals:[],outreach:[],incidents:[],history:[],ideas:[],prReviews:[],postcodeChecks:[],daily:{date:null,completed:[]},ombudsmanSnapshot:null});\n",
  "function loadWorkspace(){try{const a=JSON.parse(localStorage.getItem(WORKSPACE_KEY)||'null');if(a&&a.version===1&&Array.isArray(a.proposals)&&Array.isArray(a.outreach)&&Array.isArray(a.history))return {...defaultWorkspace(),...a,ideas:Array.isArray(a.ideas)?a.ideas:[],prReviews:Array.isArray(a.prReviews)?a.prReviews:[],postcodeChecks:Array.isArray(a.postcodeChecks)?a.postcodeChecks:[],daily:a.daily&&Array.isArray(a.daily.completed)?a.daily:{date:null,completed:[]}}}catch{}return defaultWorkspace()}\n",
  "let workspace=loadWorkspace();\n",
  "let state={section:'overview',queue:seedQueue,queueMeta:summaryBaseline,queueLoaded:false,queueTime:null,queueError:null,queueFilter:'all',queueScope:'all',queueSearch:'',queuePage:0,queuePageSize:15,selectedClub:null,selectedOutreach:null,outreachTab:'introductions',reviewTab:'proposals',workflow:{results:null,draw:null},workflowError:null,workflowAt:null,healthText:'',healthAt:null,healthSourceDate:'2026-11-18T04:21:55Z',loading:false,overlay:null,postcodeRows:null,postcodeAt:null,postcodeError:null,postcodeSource:null,openPRs:null,prAt:null,prError:null,compareClub:'',compareDraft:'',compareChoice:'',ideasFilter:'all',prFilter:'all',liveOmbudsman:null,ombudsmanAttempted:false,ombudsmanConnectionError:null,gmail:missionGmailState()};\n",
  "const save=()=>{try{localStorage.setItem(WORKSPACE_KEY,JSON.stringify(workspace));return true}catch{return false}};\n",
  "function record(type,label,detail=''){workspace.history.unshift({id:id(),type,label,detail,at:iso()});if(workspace.history.length>3000)workspace.history.length=3000;save()}\n",
  "const toast=(msg,warn=false)=>{const root=document.getElementById('toast-area');const x=document.createElement('div');x.className='toast'+(warn?' warn':'');x.textContent=msg;root.append(x);setTimeout(()=>x.remove(),5200)};\n",
  "const pill=(text,tone='gray')=>`<span class=\"status ${tone}\">${e(text)}</span>`;\n",
  "function clubPill(s){return pill(({verified:'Official site verified',needs_verification:'Needs verification',missing:'Missing evidence',withdrawn:'Withdrawn',conflict:'Identity conflict',held:'Held'}[s])||'Unknown',({verified:'green',needs_verification:'amber',missing:'red',withdrawn:'dark',conflict:'red',held:'amber'}[s])||'gray')}\n",
  "function updateChrome(){document.querySelectorAll('[data-nav]').forEach(n=>n.classList.toggle('active',n.classList.contains('nav')&&n.dataset.nav===state.section));document.getElementById('crumb').textContent=({overview:'MISSION CONTROL',clubfinder:'CLUBFINDER AUDIT',radar:'CLUB ENTRY RADAR',outreach:'OUTREACH DESK',ombudsman:'OMBUDSMAN',approvals:'REVIEW LEDGER',sources:'SOURCES & SAFETY',ideas:'IDEAS BOARD',pullrequests:'GITHUB PR QUEUE',links:'LINKS DESK'})[state.section];document.getElementById('sidebar-club-count').textContent=state.queueMeta.eligible||651;document.getElementById('sync-label').innerHTML=state.loading?'<span class=\"dot\" style=\"color:#b98a49\"></span> Refreshing sources\u2026':state.queueLoaded?`<span class=\"dot\" style=\"color:#36785f\"></span> Club queue checked ${e(since(state.queueTime))}`:'<span class=\"dot\" style=\"color:#b98a49\"></span> Queue sample \u00b7 source not loaded'}\n",
  "function nav(s){if(state.section==='outreach'&&s!=='outreach'){state.compareDraft='';state.compareChoice='';}state.section=s;state.overlay=null;state.queuePage=0;render();window.scrollTo({top:0,behavior:'instant'})}\n",
  "const pageHead=(eyebrow,title,subtitle,extra='')=>`<div class=\"page-head\"><div><div class=\"eyebrow\">${eyebrow}</div><h1 class=\"page-title\">${title}</h1><p class=\"subtitle\">${subtitle}</p></div>${extra?`<div class=\"btn-row\">${extra}</div>`:''}</div>`;\n",
  "const banner=(heading,details,kind='')=>`<div class=\"info-banner ${kind}\">${icon(kind==='error'?'alert':kind==='success'?'check':'info')}<div><strong>${heading}</strong>${details?`<div>${details}</div>`:''}</div></div>`;\n",
  "const metric=(label,value,foot,ico,tone='')=>`<div class=\"metric ${tone}\"><div class=\"metric-top\"><span>${label}</span><span class=\"iconwrap\">${icon(ico)}</span></div><div class=\"metric-val\">${e(value)}</div><div class=\"metric-foot\">${foot}</div></div>`;\n",
  "const blank=(heading,desc)=>`<div class=\"empty\">${icon('list')}<b>${heading}</b>${desc}</div>`;\n",
  "const sectionHeader=(title,sub,right='')=>`<div class=\"section-header\"><div><h2>${title}</h2>${sub?`<p>${sub}</p>`:''}</div>${right}</div>`;\n",
  "const btn=(text,act,cl='')=>`<button class=\"btn ${cl}\" data-action=\"${act}\">${text}</button>`;\n",
  "function loadTimeLabel(){return state.queueLoaded?`Source updated ${niceDate(state.queueMeta.competition_updated_at)} \u00b7 fetched ${niceDate(state.queueTime)}`:`Snapshot metadata from 17 Nov 2026 \u00b7 only ${state.queue.length} sample rows until queue loads`}\n",
  "function effectiveScope(r){return r.current_competition?'Active competition':r.sample?'Sample':'Wider Clubfinder'}\n",
  "function ensureSourceWarning(){return state.queueLoaded?'':banner('Limited preview: full queue not loaded',`The ${state.queue.length} visible records are illustrative rows from the source. Use \u201cRefresh sources\u201d or import the repository JSON before reviewing the full queue. No full-queue coverage can be inferred.`,'error')}\n",
  "async function getJSON(url){const controller=new AbortController();const t=setTimeout(()=>controller.abort(),12000);try{const resp=await fetch(url,{signal:controller.signal,cache:'no-store',headers:{Accept:'application/json'}});if(!resp.ok)throw Error(`HTTP ${resp.status}`);return await resp.json()}finally{clearTimeout(t)}}\n",
  "async function getText(url){const controller=new AbortController();const t=setTimeout(()=>controller.abort(),12000);try{const resp=await fetch(url,{signal:controller.signal,cache:'no-store'});if(!resp.ok)throw Error(`HTTP ${resp.status}`);return await resp.text()}finally{clearTimeout(t)}}\n",
  "function useClubData(doc){if(!doc||!Array.isArray(doc.rows)||!Number.isInteger(doc.eligible)||doc.eligible<100||doc.rows.some(r=>!r.club||!r.status))throw Error('Incompatible Clubfinder audit schema');state.queue=doc.rows;state.queueMeta=doc;state.queueLoaded=true;state.queueTime=iso();state.queueError=null;state.queuePage=0;}\n",
  "async function pullQueue(){try{let d;try{d=await getJSON(`${RAW}/updater/club_website_audit_queue.json`)}catch(ex){let resp=await getJSON(`${API}/contents/updater/club_website_audit_queue.json`);if(!resp.content)throw ex;d=JSON.parse(atob(resp.content.replace(/\\s/g,'')))}useClubData(d)}catch(ex){state.queueError=ex.message;state.queueLoaded=false;if(!state.queue.length)state.queue=seedQueue}}\n",
  "async function pullWorkflows(){try{const [a,b]=await Promise.all(['scan-results.yml','scan-draw.yml'].map(name=>getJSON(`${API}/actions/workflows/${name}/runs?event=schedule&per_page=100`)));state.workflow={results:a.workflow_runs||[],draw:b.workflow_runs||[]};state.workflowAt=iso();state.workflowError=null}catch(ex){state.workflowError=ex.message}}\n",
  "async function pullHealth(){try{state.healthText=await getText(`${RAW}/competition-health.md`);state.healthAt=iso();const t=state.healthText.match(/Last checked:\\s*\\*\\*([^*]+)\\*\\*/i);if(t){const dt=t[1].match(/(\\d\\d)\\/(\\d\\d)\\/(\\d{4}),\\s*(\\d\\d:\\d\\d:\\d\\d)/);if(dt)state.healthSourceDate=`${dt[3]}-${dt[2]}-${dt[1]}T${dt[4]}Z`}}catch{state.healthAt=null}}\n",
  "async function missionPullOmbudsman(){\n",
  " state.ombudsmanAttempted=true;\n",
  " try{\n",
  "  const response=await fetch('/api/ombudsman',{credentials:'same-origin',cache:'no-store',redirect:'manual'});\n",
  "  if(!response.ok)throw Error('Health service not available ('+response.status+')');\n",
  "  const data=await response.json();\n",
  "  if(!data||!['healthy','warning','critical','pending','unknown'].includes(data.state)||typeof data.checked_at!=='string')throw Error('Invalid health response');\n",
  "  state.liveOmbudsman=data;\n",
  "  state.ombudsmanConnectionError=null;\n",
  " }catch(err){state.liveOmbudsman=null;state.ombudsmanConnectionError=String(err.message||'No read-only health report');}\n",
  "}\n",
  "async function refreshAll(){if(state.loading)return;state.loading=true;render();const gmailCheck=missionGmailStatus();await Promise.allSettled([pullQueue(),pullWorkflows(),pullHealth(),missionPullPostcodes(),missionPullPRs(),missionPullOmbudsman(),gmailCheck]);state.loading=false;render();const gmail=await gmailCheck;if(gmail&&gmail===state.gmail&&gmail.connection==='connected'&&!gmail.result)await missionGmailRefresh();toast('Source check completed. Unavailable feeds remain UNKNOWN; check freshness before acting.',!!state.queueError)}\n",
  "function queueCounts(){return state.queue.reduce((d,r)=>(d[r.status]=(d[r.status]||0)+1,d),{})}\n",
  "function todayOutreach(){return workspace.outreach.filter(o=>o.kind==='introduction'&&o.approvedOn===ukDay()&&['approved','awaiting_sent','sent_verified','replied'].includes(o.status))}\n",
  "const slotsLeft=()=>Math.max(0,15-todayOutreach().length);\n",
  "function heldProposals(){return workspace.proposals.filter(p=>p.status==='held'||p.status==='draft').length}\n",
  "function proposedForReview(){return workspace.proposals.filter(p=>p.status==='awaiting_review').length}\n",
  "function actionItems(){let out=[];for(let p of workspace.proposals.filter(x=>x.status==='awaiting_review').slice(0,3))out.push({title:`Review correction: ${p.club}`,sub:`${p.kind} \u00b7 submitted ${niceDate(p.submittedAt||p.updatedAt)}`,s:'amber',t:'Review',action:`proposal:${p.id}`});for(let x of workspace.outreach.filter(o=>o.status==='approved'||o.status==='awaiting_sent').slice(0,3))out.push({title:`Verify SENT: ${x.club}`,sub:`${x.kind==='reply'?'Reply':'Introduction'} \u00b7 ${e(x.recipient||'Recipient pending')}`,s:'amber',t:'Awaiting proof',action:`outreach:${x.id}`});if(!state.queueLoaded)out.push({title:'Load the full Clubfinder queue',sub:'Queue sample only; refresh the 651-club source before comprehensive review.',s:'red',t:'Source needed',action:'sources'});if(state.workflowError)out.push({title:'Check GitHub watcher feed',sub:'Action runs could not be loaded; do not infer healthy status.',s:'red',t:'Unknown',action:'ombudsman'});if(!out.length)out.push({title:'No outstanding local approvals',sub:'Review live source gaps and incoming replies as part of the daily routine.',s:'green',t:'Local queue clear',action:'approvals'});return out}\n",
  "function overview(){return missionOverview()}\n",
  "function clubFiltered(){let q=state.queue.filter(r=>{const needle=state.queueSearch.toLowerCase().trim();if(needle&&!([r.club,r.website,...(r.identities||[])].join(' ').toLowerCase().includes(needle)))return false;if(state.queueFilter!=='all'&&r.status!==state.queueFilter)return false;if(state.queueScope==='active'&&!r.current_competition)return false;if(state.queueScope==='wider'&&r.current_competition)return false;if(state.queueScope==='review'&&!heldReference[r.club]&&!workspace.proposals.some(p=>p.club===r.club&&p.status!=='approved_for_export'))return false;return true});return q.sort((a,b)=>a.priority-b.priority||a.club.localeCompare(b.club,'en-GB'))}\n",
  "function clubfinder(){let q=clubFiltered(),pages=Math.max(1,Math.ceil(q.length/state.queuePageSize));state.queuePage=Math.max(0,Math.min(state.queuePage,pages-1));const count=queueCounts(),from=state.queuePage*state.queuePageSize,rows=q.slice(from,from+state.queuePageSize);return `${pageHead('01 / CLUBFINDER','Evidence audit queue','A conservative audit across 651 eligible clubs. Existing links are not inferred to be official unless the approved evidence ledger supports them.',`<button class=\"btn\" data-action=\"import-clubs\">${icon('upload')} Import JSON</button><button class=\"btn primary\" data-action=\"new-proposal\">${icon('plus')} New proposal</button>`)}\n",
  "${ensureSourceWarning()}<div class=\"grid4\" style=\"margin-top:${state.queueLoaded?'0':'16px'}\">${metric('Eligible clubs',state.queueMeta.eligible,'The official audit scope','database')}${metric('Linked eligible',state.queueMeta.eligible_linked,'Links present \u00b7 not all approved','search','good')}${metric('Official-site verified',state.queueLoaded?count.verified||0:'\u2014','Across full identity queue, not just eligible','check')}${metric('Missing / unresolved',state.queueLoaded?(count.missing||0)+(count.needs_verification||0)+(count.conflict||0):'\u2014','Do not invent a domain or recipient','alert','warn')}</div>\n",
  "${sectionHeader('All club records',state.queueLoaded?`${state.queue.length} identities loaded. ${state.queueMeta.eligible} eligible clubs; queue includes current-competition aliases and names.`:'Partial offline preview. Full source data is required for exhaustive triage.',`<button class=\"btn small\" data-action=\"refresh-all\">${icon('refresh')} Refresh queue</button>`)}\n",
  "<div class=\"surface\"><div class=\"filters\"><div class=\"searchbox\">${icon('search')}<input id=\"club-search\" class=\"input\" placeholder=\"Search club or website\u2026\" value=\"${e(state.queueSearch)}\" aria-label=\"Search clubs\"></div><select class=\"select\" id=\"club-status\" aria-label=\"Evidence status\"><option value=\"all\">All evidence states</option>${['verified','needs_verification','missing','withdrawn','conflict'].map(s=>`<option value=\"${s}\" ${state.queueFilter===s?'selected':''}>${s.replaceAll('_',' ')}</option>`).join('')}</select><select class=\"select\" id=\"club-scope\" aria-label=\"Club scope\"><option value=\"all\">All identities</option><option value=\"active\" ${state.queueScope==='active'?'selected':''}>Current competition</option><option value=\"wider\" ${state.queueScope==='wider'?'selected':''}>Other clubs</option><option value=\"review\" ${state.queueScope==='review'?'selected':''}>Known holds / proposals</option></select></div><div class=\"table-wrap\"><table><thead><tr><th>Club</th><th>Evidence state</th><th>Website destination</th><th>Competition</th><th>Review signal</th><th></th></tr></thead><tbody>${rows.map(r=>`<tr><td><div class=\"row-title\">${e(r.club)}</div><div class=\"row-desc\">${r.identities?.length>1?`${r.identities.length} reviewed aliases`:'Canonical identity as supplied'}</div></td><td>${clubPill(r.status)}</td><td>${r.website?urlLink(r.website,r.website.replace(/^https?:\\/\\//,'').replace(/\\/$/,'').slice(0,34)):'<span class=\"muted\">No confirmed destination</span>'}</td><td>${r.current_competition?pill('Current','blue'):'<span class=\"muted\">Wider queue</span>'}</td><td>${heldReference[r.club]?pill('Hold note','amber'):workspace.proposals.some(p=>p.club===r.club)?pill('Proposal attached','blue'):'<span class=\"muted\">\u2014</span>'}</td><td class=\"td-actions\"><button class=\"btn small\" data-open=\"club:${e(encodeURIComponent(r.club))}\">Review ${icon('chevron')}</button></td></tr>`).join('')||`<tr><td colspan=\"6\">${blank('No matches','Try adjusting the scope, status or search query.')}</td></tr>`}</tbody></table></div><div class=\"pagination\"><span>${q.length?`${from+1}\u2013${Math.min(from+state.queuePageSize,q.length)} of ${q.length}`:'0 results'} \u00b7 ${state.queueLoaded?'Live repository file':'Sample only'} </span><div class=\"btn-row\"><button class=\"btn small\" data-action=\"page-prev\" ${state.queuePage===0?'disabled':''}>Previous</button><span>${state.queuePage+1} / ${pages}</span><button class=\"btn small\" data-action=\"page-next\" ${state.queuePage+1>=pages?'disabled':''}>Next</button></div></div></div>\n",
  "${banner('Fail closed, by design','Exact postcode, qualifying role, club naming, sponsorship and groundshare claims remain held until dated evidence directly supports the requested change. A review approval permits export for a separate code review \u2014 it does not patch canonical data.')}\n",
  "<div class=\"source-footer\">Repository source: ${urlLink(`${GH}/blob/main/updater/club_website_audit_queue.json`,'Club website audit queue')} \u00b7 Latest source metadata ${niceDate(state.queueMeta.competition_updated_at)}</div>`}\n",
  "function clubDrawer(name){const r=state.queue.find(x=>x.club===name);if(!r)return '';const props=workspace.proposals.filter(p=>p.club===name);const evidence=(r.evidence||[]);return `<div class=\"drawer-backdrop\" data-dismiss=\"1\"><div class=\"drawer\" role=\"dialog\" aria-modal=\"true\" aria-label=\"Club evidence\"><div class=\"drawer-header\"><div><div class=\"eyebrow\">CLUBFINDER / EVIDENCE RECORD</div><h2>${e(r.club)}</h2>${clubPill(r.status)}</div><button class=\"icon-btn\" data-action=\"close-overlay\" title=\"Close\">${icon('close')}</button></div>\n",
  "<section><div class=\"kv-list\"><div>Club identity</div><div>${e(r.identities?.join(' \u00b7 ')||r.club)}</div><div>Current competition</div><div>${r.current_competition?'Yes':'No'}</div><div>Website</div><div>${r.website?urlLink(r.website):'<span class=\"muted\">No confirmed destination</span>'}</div><div>Source updated</div><div>${niceDate(state.queueMeta.competition_updated_at)}</div><div>Audit status</div><div>${e(r.status)}</div></div></section>\n",
  "<section><h3>Evidence &amp; provenance</h3>${evidence.length?`<div class=\"evidence-list\">${evidence.map(x=>`<div class=\"state-card\"><div>${urlLink(x.evidence_url||x.url,'Open evidence source')}</div><div class=\"note\" style=\"margin-top:7px\">${e(x.ledger||'Source ledger')} \u00b7 ${e(x.verified_on||'Date not stated')}</div></div>`).join('')}</div>`:banner('No verified supporting link in this row','A linked website without matching ledger evidence remains unverified. Do not promote it on appearance alone.')}${heldReference[name]?`<div class=\"gap16\"></div>${banner('Conservative hold',e(heldReference[name]),'error')}`:''}</section>\n",
  "<section><h3>Review &amp; proposal history</h3>${props.length?props.map(p=>`<div class=\"quick-row\" data-open=\"proposal:${p.id}\"><div><strong>${e(p.kind)} \u00b7 ${e(p.proposedValue)}</strong><small>Updated ${niceDate(p.updatedAt)}</small></div>${proposalPill(p.status)}</div>`).join(''):blank('No local proposals','This record has no saved correction proposals.')}</section>\n",
  "<section><div class=\"btn-row\"><button class=\"btn primary\" data-action=\"new-proposal\" data-club=\"${e(encodeURIComponent(name))}\">${icon('plus')} Propose correction</button><button class=\"btn\" data-action=\"new-outreach\" data-club=\"${e(encodeURIComponent(name))}\">${icon('mail')} Draft outreach</button></div><p class=\"note\">These actions create local records only. Nothing changes a published fixture or Clubfinder record.</p></section></div></div>`}\n",
  "const KIND_LABEL={official_website:'Official website',club_name:'Club naming / identity',sponsorship:'Ground sponsorship',ground_postcode:'Ground / exact postcode',qualifying_role:'Qualifying ground role',groundshare:'Groundshare / host relationship',other:'Other source correction'};\n",
  "function proposalPill(s){return pill(({draft:'Draft',held:'Held for evidence',awaiting_review:'Awaiting approval',approved_for_export:'Approved for PR',rejected:'Rejected'}[s])||s,({draft:'gray',held:'amber',awaiting_review:'blue',approved_for_export:'green',rejected:'red'}[s])||'gray')}\n",
  "function proposalHolds(p){let h=[];if(!p.club?.trim())h.push('Club identity is required.');if(!state.queueLoaded)h.push('Load the full source queue before approval.');else if(!state.queue.some(r=>r.club===p.club))h.push('Exact club identity must exist in the loaded Clubfinder queue; fuzzy matches are held.');if(!p.proposedValue?.trim())h.push('Proposed replacement value is required.');if(!safeUrl(p.evidenceUrl))h.push('Direct dated supporting evidence URL (https://) is required.');if(!p.evidenceDate)h.push('Evidence capture date is required.');if(!p.reason?.trim())h.push('The change and its rationale must be documented.');if(!p.sourceType||p.sourceType==='unknown')h.push('Evidence source type must be identified (club / league / FA / official ground).');\n",
  " if(p.kind==='official_website'&&!safeUrl(p.proposedValue))h.push('Official website proposal must contain an explicit http(s) URL.');\n",
  " if(p.kind==='official_website'&&!p.officialSiteConfirmed)h.push('Confirm that this is the club-operated official destination, not a third-party guess.');\n",
  " if(p.kind==='club_name'&&!p.namingConfirmed)h.push('Club naming / alias identity requires direct confirmation, not fuzzy matching.');\n",
  " if(p.kind==='sponsorship'&&!p.sponsorConfirmed)h.push('Sponsorship or ground name must be current and explicitly supported.');\n",
  " if(['ground_postcode','qualifying_role','groundshare'].includes(p.kind)){\n",
  "  if(!/^[A-Z]{1,2}\\d[A-Z\\d]?\\s*\\d[A-Z]{2}$/i.test((p.exactPostcode||'').trim()))h.push('An exact UK postcode is mandatory; centroid and town approximations are insufficient.');\n",
  "  if(!p.qualifyingRole||p.qualifyingRole==='unknown')h.push('Explicit qualifying role (home / host / tenant / match venue) is required.');\n",
  "  if(!safeUrl(p.roleEvidenceUrl))h.push('Ground role must have its own supporting evidence link.');\n",
  "  if(!p.roleConfirmed)h.push('Confirm that venue / role evidence applies to the 2026\u201327 season or actual tie.');\n",
  " }\n",
  " if(p.kind==='groundshare'&&!p.groundshareConfirmed)h.push('Groundshare requires explicit pair + season confirmation; shared postcode alone is not proof.');\n",
  " if(p.originalStatus==='withdrawn'&&!p.withdrawalCleared)h.push('Withdrawn destination requires explicit new re-verification.');\n",
  " return h}\n",
  "function proposalForm(p={}){const club=p.club||state.selectedClub||'';return `<div class=\"modal-backdrop\" data-dismiss=\"1\"><div class=\"modal\" role=\"dialog\" aria-modal=\"true\" aria-label=\"Correction proposal\"><div class=\"modal-head\"><div><div class=\"eyebrow\">CLUBFINDER / CHANGE PROPOSAL</div><h2>${p.id?'Edit correction':'New correction proposal'}</h2></div><button class=\"icon-btn\" data-action=\"close-overlay\">${icon('close')}</button></div>\n",
  "${banner('Proposal only','Saved edits remain in your browser. Approval makes an exportable handoff for a separate reviewed PR; it cannot write production.')}\n",
  "<form id=\"proposal-form\" data-id=\"${e(p.id||'')}\" autocomplete=\"off\" style=\"margin-top:17px\"><div class=\"form-grid\">\n",
  "<div class=\"field\"><label for=\"p-club\">Club identity</label><input required id=\"p-club\" name=\"club\" list=\"club-options\" value=\"${e(club)}\" placeholder=\"Exact club name\"><datalist id=\"club-options\">${state.queue.slice(0,700).map(r=>`<option value=\"${e(r.club)}\"></option>`).join('')}</datalist></div>\n",
  "<div class=\"field\"><label for=\"p-kind\">Correction type</label><select name=\"kind\" id=\"p-kind\">${Object.entries(KIND_LABEL).map(([k,v])=>`<option value=\"${k}\" ${p.kind===k?'selected':''}>${e(v)}</option>`).join('')}</select></div>\n",
  "<div class=\"field full\"><label for=\"p-value\">Proposed value / correction</label><input required id=\"p-value\" name=\"proposedValue\" value=\"${e(p.proposedValue||'')}\" placeholder=\"Exact replacement text, URL or corrected detail\"></div>\n",
  "<div class=\"field\"><label for=\"p-type\">Evidence authority</label><select name=\"sourceType\" id=\"p-type\">${[['unknown','Not established'],['club','Club official'],['league','League official'],['fa','FA official'],['ground','Ground operator / match documentation']].map(([k,v])=>`<option value=\"${k}\" ${p.sourceType===k?'selected':''}>${v}</option>`).join('')}</select></div>\n",
  "<div class=\"field\"><label for=\"p-date\">Evidence recorded on</label><input type=\"date\" name=\"evidenceDate\" id=\"p-date\" value=\"${e(p.evidenceDate||ukDay())}\"></div>\n",
  "<div class=\"field full\"><label for=\"p-url\">Direct evidence URL</label><input name=\"evidenceUrl\" type=\"url\" id=\"p-url\" value=\"${e(p.evidenceUrl||'')}\" placeholder=\"https://club.example/official-announcement\"></div>\n",
  "<div class=\"field full\"><label for=\"p-reason\">What is changing, and why?</label><textarea name=\"reason\" id=\"p-reason\" rows=\"3\" placeholder=\"Describe original value, source conflict and reasoning\">${e(p.reason||'')}</textarea></div>\n",
  "</div><div class=\"divider\"></div><h3 style=\"margin:0 0 10px\">Evidence gates \u00b7 fail closed</h3><div class=\"form-grid\"><div class=\"field\"><label>Exact UK postcode, if location-related</label><input name=\"exactPostcode\" value=\"${e(p.exactPostcode||'')}\" placeholder=\"e.g. NN17 2AE\"></div><div class=\"field\"><label>Qualifying role at venue</label><select name=\"qualifyingRole\"><option value=\"unknown\">Not established</option>${[['home','Home club'],['host','Host venue'],['tenant','Groundshare tenant'],['actual_tie','Actual FA Cup tie venue']].map(([k,v])=>`<option value=\"${k}\" ${p.qualifyingRole===k?'selected':''}>${v}</option>`).join('')}</select></div><div class=\"field full\"><label>Separate ground / qualifying-role source URL</label><input name=\"roleEvidenceUrl\" type=\"url\" value=\"${e(p.roleEvidenceUrl||'')}\" placeholder=\"https://official-source.example/ground-or-fixture\"></div></div>\n",
  "<div class=\"checks\">${[['officialSiteConfirmed','Official club-operated site verified'],['namingConfirmed','Club name / alias identity confirmed'],['sponsorConfirmed','Current sponsorship explicitly evidenced'],['groundshareConfirmed','Groundshare pairing and season confirmed'],['roleConfirmed','Actual venue role and season confirmed'],['withdrawalCleared','Prior withdrawal explicitly cleared']].map(([k,v])=>`<label class=\"check\"><input type=\"checkbox\" name=\"${k}\" ${p[k]?'checked':''}><span>${v}</span></label>`).join('')}</div><div id=\"proposal-holds\"></div>\n",
  "<div class=\"form-controls btn-row\"><button type=\"button\" class=\"btn\" data-action=\"save-proposal\">${icon('save')} Save draft / hold</button><button type=\"button\" class=\"btn primary\" data-action=\"submit-proposal\">${icon('clipboard')} Submit for approval</button></div></form></div></div>`}\n",
  "function readProposalForm(){const f=document.getElementById('proposal-form');if(!f)return null;const d=new FormData(f);const old=workspace.proposals.find(x=>x.id===f.dataset.id)||{};const club=String(d.get('club')||'').trim();const rr=state.queue.find(r=>r.club===club);const check=k=>d.get(k)==='on';return {...old,id:old.id||id(),club,kind:d.get('kind'),proposedValue:String(d.get('proposedValue')||'').trim(),sourceType:d.get('sourceType'),evidenceDate:d.get('evidenceDate'),evidenceUrl:String(d.get('evidenceUrl')||'').trim(),reason:String(d.get('reason')||'').trim(),exactPostcode:String(d.get('exactPostcode')||'').toUpperCase().replace(/\\s+/g,' ').trim(),qualifyingRole:d.get('qualifyingRole'),roleEvidenceUrl:String(d.get('roleEvidenceUrl')||'').trim(),officialSiteConfirmed:check('officialSiteConfirmed'),namingConfirmed:check('namingConfirmed'),sponsorConfirmed:check('sponsorConfirmed'),groundshareConfirmed:check('groundshareConfirmed'),roleConfirmed:check('roleConfirmed'),withdrawalCleared:check('withdrawalCleared'),originalStatus:rr?.status||old.originalStatus||'unknown',createdAt:old.createdAt||iso(),updatedAt:iso()}}\n",
  "function saveProposal(submit=false){const p=readProposalForm();if(!p)return;const hold=proposalHolds(p);p.status=submit?(hold.length?'held':'awaiting_review'):(hold.length?'held':'draft');if(p.status==='awaiting_review')p.submittedAt=iso();const i=workspace.proposals.findIndex(x=>x.id===p.id);if(i>=0)workspace.proposals[i]=p;else workspace.proposals.unshift(p);record('proposal',`${p.status==='awaiting_review'?'Submitted':'Saved'} correction for ${p.club}`,`${KIND_LABEL[p.kind]}; ${hold.length} outstanding evidence gate(s)`);state.overlay=null;nav('approvals');toast(p.status==='awaiting_review'?'Correction submitted for local approval. Nothing has been applied.':`Correction held locally; ${hold.length} gate(s) still need evidence.`,hold.length>0)}\n",
  "function proposalDetail(p){const h=proposalHolds(p);return `<div class=\"drawer-backdrop\" data-dismiss=\"1\"><div class=\"drawer\" role=\"dialog\" aria-modal=\"true\" aria-label=\"Proposal review\"><div class=\"drawer-header\"><div><div class=\"eyebrow\">REVIEW LEDGER / PROPOSAL</div><h2>${e(p.club)}</h2>${proposalPill(p.status)}</div><button class=\"icon-btn\" data-action=\"close-overlay\">${icon('close')}</button></div><section><div class=\"kv-list\"><div>Change type</div><div>${e(KIND_LABEL[p.kind]||p.kind)}</div><div>Proposed value</div><div>${e(p.proposedValue)}</div><div>Current source</div><div>${e(p.sourceType)}</div><div>Evidence date</div><div>${e(p.evidenceDate)}</div><div>Evidence link</div><div>${urlLink(p.evidenceUrl,'Open evidence')}</div><div>Ground / role evidence</div><div>${p.roleEvidenceUrl?urlLink(p.roleEvidenceUrl,'Open venue source'):'Not provided'}</div><div>Exact postcode</div><div>${e(p.exactPostcode||'Not supplied')}</div><div>Qualifying role</div><div>${e(p.qualifyingRole||'Not established')}</div><div>Reason</div><div>${e(p.reason)}</div><div>Approver</div><div>${e(p.reviewer||'Not approved')}</div><div>Last updated</div><div>${niceDate(p.updatedAt)}</div></div></section><section><h3>Eligibility to approve</h3>${h.length?`<div class=\"hold-list\">${h.map(x=>`<div class=\"hold-item\">${icon('alert')} ${e(x)}</div>`).join('')}</div>`:banner('Evidence gates passed','Human review and a recorded approver are still required before export.','success')}</section><section><div class=\"btn-row\">${p.status==='approved_for_export'?pill('Exportable \u00b7 still not published','green'):`<button class=\"btn\" data-action=\"edit-proposal\" data-id=\"${e(p.id)}\">${icon('file')} Edit evidence</button>${p.status==='awaiting_review'&&!h.length?`<button class=\"btn primary\" data-action=\"review-proposal\" data-id=\"${e(p.id)}\">${icon('check')} Approve for PR export</button>`:''}${p.status!=='rejected'?`<button class=\"btn danger\" data-action=\"reject-proposal\" data-id=\"${e(p.id)}\">Reject</button>`:''}`}</div></section></div></div>`}\n",
  "function approveModal(p){return `<div class=\"modal-backdrop\" data-dismiss=\"1\"><div class=\"modal\" role=\"dialog\" aria-modal=\"true\" aria-label=\"Approve export handoff\"><div class=\"modal-head\"><div><div class=\"eyebrow\">HUMAN APPROVAL \u00b7 NO PRODUCTION WRITE</div><h2>Approve for PR export</h2></div><button class=\"icon-btn\" data-action=\"close-overlay\">${icon('close')}</button></div>${banner('Not a merge or publication','This approval records the reviewer\u2019s decision locally and places the proposal in the export bundle. Canonical changes require separate PR checks and merge.')}<form id=\"approval-form\" data-id=\"${e(p.id)}\"><div class=\"form-grid\" style=\"margin-top:17px\"><div class=\"field\"><label>Reviewer / approving administrator</label><input name=\"reviewer\" placeholder=\"Recorded reviewer identity\" required></div><div class=\"field\"><label>Type APPROVE to confirm</label><input name=\"confirmation\" placeholder=\"APPROVE\" required></div><div class=\"field full\"><label>Approval note</label><textarea name=\"reviewNote\" rows=\"3\" placeholder=\"What evidence did you independently check?\"></textarea></div></div><div class=\"form-controls btn-row\"><button class=\"btn primary\" type=\"button\" data-action=\"confirm-approval\">${icon('check')} Record reviewed approval</button></div></form></div></div>`}\n",
  "function confirmApproval(){const f=document.getElementById('approval-form');if(!f)return;const p=workspace.proposals.find(x=>x.id===f.dataset.id),d=new FormData(f);if(!p||proposalHolds(p).length||p.status!=='awaiting_review')return toast('This correction no longer passes the review gate.',true);if(String(d.get('confirmation')).trim()!=='APPROVE'||!String(d.get('reviewer')).trim())return toast('Provide reviewer and type APPROVE exactly.',true);p.status='approved_for_export';p.reviewer=String(d.get('reviewer')).trim();p.reviewNote=String(d.get('reviewNote')).trim();p.approvedAt=iso();p.updatedAt=iso();record('approval',`Approved correction for PR export: ${p.club}`,`${p.kind} \u00b7 reviewer ${p.reviewer} \u00b7 No production change`);state.overlay=null;nav('approvals');toast('Approval recorded. Export the handoff for separate code review.')}\n",
  "function outreachPill(s){return pill(({draft:'Draft',held:'Held',approved:'Approved \u2022 not sent',awaiting_sent:'Check SENT',sent_verified:'SENT verified',reply_logged:'Reply logged',replied:'Reply handled',rejected:'Rejected'}[s])||s,({draft:'gray',held:'amber',approved:'blue',awaiting_sent:'amber',sent_verified:'green',reply_logged:'amber',replied:'green',rejected:'red'}[s])||'gray')}\n",
  "const emailGood=t=>/^[^\\s@]+@[^\\s@]+\\.[^\\s@]{2,}$/.test(t||'');\n",
  "function outreachIssues(o,checkingId){let x=[];if(!o.club?.trim())x.push('Club identity missing.');if(!o.recipient?.trim()||!emailGood(o.recipient))x.push('Confirmed recipient email required; do not guess addresses.');if(o.kind!=='incoming_reply'&&!o.subject?.trim())x.push('Email subject required.');if(o.kind!=='incoming_reply'&&!o.body?.trim())x.push('Draft email body required.');if(o.kind==='introduction'){\n",
  " if(!state.queueLoaded)x.push('Full Clubfinder source must be loaded before introduction approval.');\n",
  " if(!state.queue.some(r=>r.club.toLowerCase()===o.club.toLowerCase()))x.push('Club is not present in the loaded Clubfinder identities.');\n",
  " if(!o.pathConfirmed||!safeUrl(o.pathEvidence))x.push('Campaign path eligibility needs an explicit source link and confirmation.');\n",
  " if(!o.recipientConfirmed||!safeUrl(o.recipientEvidence))x.push('Verify the real recipient from a cited club/league contact source.');\n",
  " const dupe=workspace.outreach.find(v=>v.id!==checkingId&&v.kind==='introduction'&&v.status!=='rejected'&&((v.recipient||'').toLowerCase()===(o.recipient||'').toLowerCase()||(v.club||'').toLowerCase()===(o.club||'').toLowerCase()));\n",
  " if(dupe)x.push('Duplicate introduction: same club or recipient exists in the local history.');\n",
  " if(!o.duplicateReviewed)x.push('Recipient and historical duplicate check must be acknowledged.');\n",
  " if(slotsLeft()===0&&!checkingId)x.push('15-introduction daily approval cap reached (UK date).');\n",
  " }\n",
  " if(o.kind==='incoming_reply'){if(!o.originalRef?.trim())x.push('Incoming reply needs a source thread or message reference.');}\n",
  " if(o.kind==='reply'){\n",
  " if(!o.originalRef?.trim())x.push('Original incoming message / thread reference is required.');\n",
  " if(!o.recipientConfirmed)x.push('Reply recipient must be confirmed from the original thread.');\n",
  " }\n",
  " return x}\n",
  "function outreachForm(o={},kind='introduction'){const k=o.kind||kind;return `<div class=\"drawer-backdrop\" data-dismiss=\"1\"><div class=\"drawer\" role=\"dialog\" aria-modal=\"true\" aria-label=\"Outreach editor\"><div class=\"drawer-header\"><div><div class=\"eyebrow\">OUTREACH / ${k==='reply'?'REPLY':k==='incoming_reply'?'INCOMING':'INTRODUCTION'}</div><h2>${o.id?'Edit outreach record':k==='reply'?'Draft a reply':k==='incoming_reply'?'Log incoming reply':'Prepare an introduction'}</h2>${pill('No sending available','blue')}</div><button class=\"icon-btn\" data-action=\"close-overlay\">${icon('close')}</button></div>${banner('Draft & approve only','Email sending is deliberately disabled. After external sending, verify the message in SENT and record the message reference before calling it sent.')}\n",
  "<form id=\"outreach-form\" data-id=\"${e(o.id||'')}\" data-kind=\"${e(k)}\" autocomplete=\"off\" style=\"margin-top:16px\"><div class=\"form-grid\"><div class=\"field\"><label>Club</label><input list=\"club-options\" name=\"club\" value=\"${e(o.club||state.selectedClub||'')}\" required placeholder=\"Exact Clubfinder name\"><datalist id=\"club-options\">${state.queue.map(r=>`<option value=\"${e(r.club)}\"></option>`).join('')}</datalist></div><div class=\"field\"><label>${k==='incoming_reply'?'From email':'To: verified email address'}</label><input name=\"recipient\" type=\"email\" value=\"${e(o.recipient||'')}\" placeholder=\"address confirmed by source\"></div>\n",
  "${k==='incoming_reply'?`<div class=\"field full\"><label>Original Gmail / message reference</label><input name=\"originalRef\" value=\"${e(o.originalRef||'')}\" placeholder=\"Message ID or Gmail link\"></div><div class=\"field full\"><label>Reply received / next action</label><textarea name=\"body\" rows=\"5\">${e(o.body||'')}</textarea></div>`:`<div class=\"field full\"><label>Subject</label><input name=\"subject\" value=\"${e(o.subject|| (k==='introduction'?'Tin Foil FA Cup \u2014 your Clubfinder listing':''))}\"></div><div class=\"field full\"><label>Email copy (editable)</label><textarea name=\"body\" rows=\"8\" placeholder=\"Your current listing:\\n\\n[details checked against Clubfinder]\\n\\n\u2026\">${e(o.body||'')}</textarea></div><div class=\"field full\"><label>Original message / thread ID ${k==='reply'?'(required)':'(optional)'}</label><input name=\"originalRef\" value=\"${e(o.originalRef||'')}\" placeholder=\"Gmail thread or message reference\"></div>`}\n",
  "${k==='introduction'?`<div class=\"field full\"><label>Proof this club appears in a Campaign path</label><input name=\"pathEvidence\" type=\"url\" value=\"${e(o.pathEvidence||'')}\" placeholder=\"https://tinfoilfacup.com/... or source file\"></div><div class=\"field full\"><label>Source for this exact email recipient</label><input name=\"recipientEvidence\" type=\"url\" value=\"${e(o.recipientEvidence||'')}\" placeholder=\"https://club-site.example/contact\"></div>`:''}\n",
  "</div><div class=\"checks\">${k==='introduction'?`<label class=\"check\"><input name=\"pathConfirmed\" type=\"checkbox\" ${o.pathConfirmed?'checked':''}><span>Clubfinder + Campaign path explicitly checked</span></label>`:''}<label class=\"check\"><input name=\"recipientConfirmed\" type=\"checkbox\" ${o.recipientConfirmed?'checked':''}><span>Recipient confirmed against original source / thread</span></label>${k==='introduction'?`<label class=\"check\"><input name=\"duplicateReviewed\" type=\"checkbox\" ${o.duplicateReviewed?'checked':''}><span>Checked duplicate club + recipient and prior sends</span></label>`:''}</div><div class=\"form-controls btn-row\"><button class=\"btn\" type=\"button\" data-action=\"save-outreach\">${icon('save')} Save local draft</button>${k!=='incoming_reply'?`<button class=\"btn primary\" type=\"button\" data-action=\"approve-outreach\">${icon('clipboard')} Check & request approval</button>`:`<button class=\"btn primary\" type=\"button\" data-action=\"log-reply\">${icon('check')} Log incoming reply</button>`}</div><div class=\"note\" style=\"margin-top:10px\">No recipient or club is auto-guessed. The daily maximum counts approved introduction slots, not replies or unapproved drafts.</div></form></div></div>`}\n",
  "function readOutreachForm(){const f=document.getElementById('outreach-form');if(!f)return null;const d=new FormData(f);const old=workspace.outreach.find(x=>x.id===f.dataset.id)||{};const check=k=>d.get(k)==='on';return {...old,id:old.id||id(),kind:f.dataset.kind,club:String(d.get('club')||'').trim(),recipient:String(d.get('recipient')||'').trim(),subject:String(d.get('subject')||'').trim(),body:String(d.get('body')||'').trim(),pathEvidence:String(d.get('pathEvidence')||'').trim(),recipientEvidence:String(d.get('recipientEvidence')||'').trim(),originalRef:String(d.get('originalRef')||'').trim(),pathConfirmed:check('pathConfirmed'),recipientConfirmed:check('recipientConfirmed'),duplicateReviewed:check('duplicateReviewed'),createdAt:old.createdAt||iso(),updatedAt:iso()}}\n",
  "function storeOutreach(approve=false,reply=false){const o=readOutreachForm();if(!o)return;const issues=outreachIssues(o,o.id);if(reply&&issues.length){toast('Incoming reply requires a club, valid sender and original message reference.',true);return}o.status=reply?'reply_logged':approve?(issues.length?'held':'draft'):'draft';if(approve&&!issues.length)o.status='draft';let n=workspace.outreach.findIndex(x=>x.id===o.id);if(n>=0)workspace.outreach[n]=o;else workspace.outreach.unshift(o);record('outreach',`${reply?'Incoming reply logged':approve?'Prepared for approval':'Saved draft'}: ${o.club}`,`${o.kind} \u00b7 ${issues.length} outstanding gate(s)`);if(approve&&!issues.length){state.overlay={type:'outreach-approval',id:o.id};renderOverlay();return}state.overlay=null;nav('outreach');toast(reply?'Incoming reply logged. Follow-up is not sent.':approve?`Held for ${issues.length} checks; draft saved.`:'Outreach draft saved locally.',approve&&issues.length>0)}\n",
  "function outreachApprovalModal(o){const issues=outreachIssues(o,o.id);return `<div class=\"modal-backdrop\" data-dismiss=\"1\"><div class=\"modal\" role=\"dialog\" aria-modal=\"true\" aria-label=\"Outreach approval\"><div class=\"modal-head\"><div><div class=\"eyebrow\">OUTREACH / FINAL REVIEW</div><h2>Approve ${o.kind==='reply'?'reply':'introduction'} draft</h2></div><button class=\"icon-btn\" data-action=\"close-overlay\">${icon('close')}</button></div><p class=\"text-sm muted\">${e(o.club)} \u00b7 ${e(o.recipient)}</p>${issues.length?banner('Review holds outstanding',issues.map(e).join(' \u00b7 '),'error'):banner('Approval does not send','This authorises your prepared copy for external sending. Only a verified SENT reference proves it left the inbox.')}\n",
  "<form id=\"outreach-approval-form\" data-id=\"${e(o.id)}\"><div class=\"form-grid\" style=\"margin-top:18px\"><div class=\"field\"><label>Approver identity</label><input name=\"reviewer\" required></div><div class=\"field\"><label>Type APPROVE</label><input name=\"confirmation\" required></div><div class=\"field full\"><label>Approval / recipient checks</label><textarea name=\"note\" rows=\"3\" placeholder=\"Confirmed details and duplicate check\"></textarea></div></div><div class=\"form-controls btn-row\"><button class=\"btn primary\" data-action=\"confirm-outreach\" type=\"button\" ${issues.length?'disabled':''}>${icon('check')} Approve, do not send</button></div></form></div></div>`}\n",
  "function confirmOutreach(){const f=document.getElementById('outreach-approval-form');if(!f)return;const o=workspace.outreach.find(x=>x.id===f.dataset.id);const d=new FormData(f);if(!o)return;if(outreachIssues(o,o.id).length)return toast('Evidence, duplicate, or capacity hold. Approval blocked.',true);if(String(d.get('confirmation')).trim()!=='APPROVE'||!String(d.get('reviewer')).trim())return toast('Reviewer identity and exact APPROVE confirmation required.',true);if(o.kind==='introduction'&&slotsLeft()===0)return toast('Daily maximum of 15 approved introductions reached.',true);o.status='approved';o.approver=String(d.get('reviewer')).trim();o.approvalNote=String(d.get('note')).trim();o.approvedOn=ukDay();o.approvedAt=iso();record('outreach_approval',`Approved ${o.kind} for ${o.club}`,`Approved by ${o.approver}. Explicitly NOT sent.`);state.overlay=null;nav('outreach');toast('Draft approved. Send externally only after your usual checks; record SENT proof afterward.')}\n",
  "function sentModal(o){return `<div class=\"modal-backdrop\" data-dismiss=\"1\"><div class=\"modal\" role=\"dialog\" aria-modal=\"true\" aria-label=\"Verify sent email\"><div class=\"modal-head\"><div><div class=\"eyebrow\">EXTERNAL SENT VERIFICATION</div><h2>Confirm message in SENT</h2></div><button class=\"icon-btn\" data-action=\"close-overlay\">${icon('close')}</button></div>${banner('This does not send an email',`Record proof that the externally sent message exists. The date of approval is ${e(o.approvedOn||'not recorded')}; introduction counts are not reduced by editing local statuses.`)}<form id=\"sent-form\" data-id=\"${e(o.id)}\" style=\"margin-top:18px\"><div class=\"form-grid\"><div class=\"field\"><label>Message sent date and time (UK local)</label><input type=\"datetime-local\" name=\"sentTime\" value=\"${e(o.sentTime||new Date().toLocaleString('sv-SE',{timeZone:'Europe/London'}).slice(0,16).replace(' ','T'))}\"></div><div class=\"field\"><label>Gmail SENT message ID / link</label><input name=\"sentProof\" placeholder=\"Message ID or Gmail link\" value=\"${e(o.sentProof||'')}\"></div><div class=\"field full\"><label class=\"check\"><input type=\"checkbox\" name=\"sentChecked\"><span>I checked SENT and confirmed this recipient and message</span></label></div></div><div class=\"form-controls\"><button type=\"button\" class=\"btn primary\" data-action=\"confirm-sent\">${icon('check')} Record SENT verification</button></div></form></div></div>`}\n",
  "function confirmSent(){const f=document.getElementById('sent-form');if(!f)return;const d=new FormData(f),o=workspace.outreach.find(x=>x.id===f.dataset.id);if(!o||!['approved','awaiting_sent'].includes(o.status))return toast('Only approved and unsent records can be verified.',true);if(!String(d.get('sentProof')||'').trim()||!d.get('sentTime')||d.get('sentChecked')!=='on')return toast('Provide message proof, actual time and the SENT confirmation.',true);o.status='sent_verified';o.sentProof=String(d.get('sentProof')).trim();o.sentTime=d.get('sentTime');o.sentVerifiedAt=iso();record('sent',`Verified SENT: ${o.club}`,`Message reference ${o.sentProof} \u00b7 verified manually`);state.overlay=null;nav('outreach');toast('SENT verification recorded. This is a manual assertion, not an inbox API verification.')}\n",
  "function outreachDetail(o){const issues=outreachIssues(o,o.id);return `<div class=\"drawer-backdrop\" data-dismiss=\"1\"><div class=\"drawer\" role=\"dialog\" aria-modal=\"true\" aria-label=\"Outreach record\"><div class=\"drawer-header\"><div><div class=\"eyebrow\">OUTREACH / ${o.kind.replaceAll('_',' ').toUpperCase()}</div><h2>${e(o.club)}</h2>${outreachPill(o.status)}</div><button class=\"icon-btn\" data-action=\"close-overlay\">${icon('close')}</button></div><section><div class=\"kv-list\"><div>Recipient / sender</div><div>${e(o.recipient||'Not supplied')}</div><div>Subject</div><div>${e(o.subject||'\u2014')}</div><div>Approved by</div><div>${e(o.approver||'Not approved')}</div><div>Approval date (UK)</div><div>${e(o.approvedOn||'\u2014')}</div><div>SENT proof</div><div>${o.sentProof?e(o.sentProof):'Not verified'}</div><div>Original thread</div><div>${e(o.originalRef||'\u2014')}</div></div></section><section><h3>Draft / reply notes</h3><div class=\"state-card\" style=\"white-space:pre-wrap;font-size:12px\">${e(o.body||'No content saved.')}</div></section><section><h3>Evidence / checks</h3><div class=\"evidence-list\">${o.pathEvidence?urlLink(o.pathEvidence,'Campaign path evidence'):''}${o.recipientEvidence?urlLink(o.recipientEvidence,'Recipient source'):''}</div>${issues.length?`<div class=\"gap16\"></div><div class=\"hold-list\">${issues.map(x=>`<div class=\"hold-item\">${icon('alert')}${e(x)}</div>`).join('')}</div>`:banner('Current draft checks appear complete','Approval remains an explicit recorded decision.','success')}</section><section><div class=\"btn-row\">${o.status==='draft'||o.status==='held'?`<button class=\"btn\" data-action=\"edit-outreach\" data-id=\"${e(o.id)}\">${icon('file')} Edit</button><button class=\"btn primary\" data-action=\"start-outreach-approval\" data-id=\"${e(o.id)}\">Approve draft</button>`:''}${['approved','awaiting_sent'].includes(o.status)?`<button class=\"btn primary\" data-action=\"open-sent\" data-id=\"${e(o.id)}\">${icon('mail')} Verify in SENT</button>`:''}${o.status==='sent_verified'?`<button class=\"btn\" data-action=\"new-reply\" data-club=\"${e(encodeURIComponent(o.club))}\" data-original=\"${e(o.sentProof)}\">Draft a reply</button>`:''}</div></section></div></div>`}\n",
  "function outreachPage(){const tab=state.outreachTab;const data=workspace.outreach.filter(o=>tab==='introductions'?o.kind==='introduction':tab==='replies'?o.kind!=='introduction':true);const pending=workspace.outreach.filter(o=>o.status==='approved').length,sent=workspace.outreach.filter(o=>o.status==='sent_verified').length;return `${pageHead('02 / OUTREACH','Outreach preparation','Prepare, check and approve club communications. No direct-send button exists; an introduction only becomes SENT after explicit evidence is recorded.',`<button class=\"btn\" data-action=\"new-reply\">${icon('mail')} Draft reply</button><button class=\"btn primary\" data-action=\"new-outreach\">${icon('plus')} New introduction</button>`)}\n",
  "<div class=\"grid4\">${metric('Introductions remaining',`${slotsLeft()}`,`${todayOutreach().length} of 15 approved today \u00b7 UK date`, 'clock','good')}${metric('Approval required',workspace.outreach.filter(o=>o.status==='draft'||o.status==='held').length,'Drafts and held records','clipboard')}${metric('Approved, not sent',pending,'Require external send and SENT evidence','alert','warn')}${metric('SENT verified',sent,'Local proof references recorded','check','good')}</div>\n",
  "<div class=\"gap16\"></div>${banner('Conservative recipient policy','Only clubs in a confirmed Campaign path should receive introductions. Verify the recipient, check prior messages by both club and address, and keep the 15-per-day limit. Replies do not use an introduction slot.')}\n",
  "${missionGmailPanel(false)}\n",
  "${missionComparisonDesk()}\n",
  "${sectionHeader('Communication queue','Recipient, duplicate and sending checks are separate steps.',`<button class=\"btn small\" data-action=\"log-incoming-reply\">${icon('plus')} Log incoming reply</button>`)}<div class=\"surface\"><div class=\"tabbar\"><button class=\"tab ${tab==='introductions'?'active':''}\" data-outreach-tab=\"introductions\">Introductions</button><button class=\"tab ${tab==='replies'?'active':''}\" data-outreach-tab=\"replies\">Replies &amp; received mail</button><button class=\"tab ${tab==='all'?'active':''}\" data-outreach-tab=\"all\">All records</button></div><div class=\"table-wrap\"><table><thead><tr><th>Club &amp; recipient</th><th>Type</th><th>Approval / send state</th><th>Updated</th><th></th></tr></thead><tbody>${data.map(o=>`<tr><td><div class=\"row-title\">${e(o.club||'Unassigned club')}</div><div class=\"row-desc\">${e(o.recipient||'No verified recipient')}</div></td><td><span class=\"tag\">${e(o.kind.replaceAll('_',' '))}</span></td><td>${outreachPill(o.status)}</td><td>${niceDate(o.updatedAt||o.createdAt,true)}</td><td class=\"td-actions\"><button class=\"btn small\" data-open=\"outreach:${e(o.id)}\">Review ${icon('chevron')}</button></td></tr>`).join('')||`<tr><td colspan=\"5\">${blank('No local outreach records','Start an introduction, log a reply or import a previous workspace backup.')}</td></tr>`}</tbody></table></div></div>\n",
  "${sectionHeader('Daily send gate','The maximum is 15 introductions approved per UK calendar day, counting reserved approval slots.')}\n",
  "<div class=\"two-col\"><div class=\"surface pad\"><div style=\"display:flex;justify-content:space-between;align-items:center\"><h3>Today\u2019s introduction allowance</h3>${pill(`${todayOutreach().length}/15`,todayOutreach().length>=15?'red':'green')}</div><div class=\"progress inline-progress\"><span style=\"width:${todayOutreach().length/15*100}%\"></span></div><p class=\"text-xs muted\">Drafts do not reserve a slot. Approval reserves one; replying does not. The browser cannot independently verify your real Gmail SENT folder.</p></div><div class=\"surface pad\"><h3>External Gmail workflow</h3><div class=\"stat-row\"><div><b>1. Approve recipient + copy</b><small>Review is logged here</small></div>${icon('clipboard')}</div><div class=\"stat-row\"><div><b>2. Send via approved mailbox</b><small>This tool never sends</small></div>${icon('lock')}</div><div class=\"stat-row\"><div><b>3. Verify in SENT</b><small>Attach message ID / link</small></div>${icon('check')}</div></div></div>`}\n",
  "function computeSchedule(kind){const minute=kind==='results'?17:37;const runs=state.workflow[kind];if(!runs)return {slots:[],state:'unavailable',unobserved:0,delayed:0,observed:0};let arr=[];const now=Date.now();for(let h=14;h>=0;h--){const current=new Date(now);current.setUTCMinutes(minute,0,0);current.setUTCHours(current.getUTCHours()-h);const target=current.getTime();if(target>now)continue;const elapsed=(now-target)/60000;const matched=runs.filter(r=>r.event==='schedule').map(r=>({...r,t:new Date(r.created_at).getTime()})).filter(r=>r.t>=target-300000&&r.t<target+75*60000).sort((a,b)=>a.t-b.t)[0];const delay=matched?Math.max(0,Math.round((matched.t-target)/60000)):null;let classification=matched?(delay>=15?'delayed':'ok'):(elapsed<95?'pending':'missing');arr.push({time:new Date(target).toISOString(),label:new Date(target).toLocaleTimeString('en-GB',{timeZone:'UTC',hour:'2-digit',minute:'2-digit'}),classification,delay,run:matched||null});}arr=arr.slice(-12);return {slots:arr,unobserved:arr.filter(r=>r.classification==='missing').length,delayed:arr.filter(r=>r.classification==='delayed').length,observed:arr.filter(r=>r.run).length,state:'observed'}}\n",
  "function smallWorkflowPill(kind){if(!state.workflow[kind])return pill('Unknown','gray');if(!state.workflowAt||Date.now()-Date.parse(state.workflowAt)>20*60000)return pill('Stale feed','amber');const c=computeSchedule(kind);return c.unobserved?pill(`${c.unobserved} gap(s)`,'red'):c.delayed?pill(`${c.delayed} delayed`,'amber'):pill('Runs observed','green')}\n",
  "function currentOmbudsmanState(){\n",
  " if(state.ombudsmanAttempted){\n",
  "  const r=state.liveOmbudsman;\n",
  "  if(!r)return {title:'Ombudsman connection unavailable',subtitle:'Mission Control could not read the protected worker feed. '+(state.ombudsmanConnectionError||'Configuration or permission check required.'),badge:'Unknown \\u00b7 no feed',tone:'amber',date:'No trusted health report'};\n",
  "  if(!r.fresh)return {title:'Ombudsman report stale',subtitle:'Last worker report is beyond the 90-minute freshness limit for the hourly :20 schedule; status is now UNKNOWN until a newer observation arrives.',badge:'Stale \\u00b7 unverified',tone:'amber',date:'Last checked '+niceDate(r.checked_at)};\n",
  "  if(r.state==='healthy')return {title:'Watchers healthy \\u00b7 overall unverified',subtitle:'Both monitored scheduled workflows recently succeeded. This does NOT establish overall competition or publication verification, and it does not prove no launch slots were missed.',badge:'Watchers healthy only',tone:'green',date:'Checked '+niceDate(r.checked_at)};\n",
  "  if(r.state==='warning')return {title:'Scheduled-launch warning \\u00b7 overall unverified',subtitle:'A watched workflow has not had a sufficiently recent scheduled launch. Last successful data may still be valid; a catch-up is not proof of a scheduled launch.',badge:'Gap observed',tone:'amber',date:'Checked '+niceDate(r.checked_at)};\n",
  "  if(r.state==='critical')return {title:'Critical watcher failure',subtitle:'An observed scheduled run failed or remained stuck. This is distinct from a missed-launch warning and requires investigation.',badge:'Critical watcher',tone:'red',date:'Checked '+niceDate(r.checked_at)};\n",
  "  if(r.state==='pending')return {title:'Watcher pending',subtitle:'An observed scheduled execution is still underway. No recovery or overall health has been established.',badge:'Pending \\u00b7 unverified',tone:'amber',date:'Checked '+niceDate(r.checked_at)};\n",
  "  return {title:'Watcher status unknown',subtitle:'The worker reported no verifiable current state; do not infer a green result.',badge:'Unknown',tone:'amber',date:'Checked '+niceDate(r.checked_at)};\n",
  " }\n",
  " const s=workspace.ombudsmanSnapshot;if(!s)return {title:'Ombudsman feed not yet connected',subtitle:'GitHub Action runs can be observed, but they do not establish that the tffc-ombudsman worker has recovered or that the overall site is verified. Import a manual Ombudsman snapshot to see its reported status; verification remains held.',badge:'Verification unknown',tone:'amber',date:'No worker snapshot'};const st=String(s.status||'unknown').toLowerCase();const age=(Date.now()-Date.parse(s.observed_at))/60000;const stale=!Number.isFinite(age)||age>25;if(stale&&TRUSTED_OMBUDSMAN_FEED&&s.overall_verified===true)return {title:'Previously verified \u00b7 feed now stale',subtitle:'The imported worker snapshot once reported overall verification, but a recent heartbeat has not been confirmed. Current health is UNKNOWN until refreshed.',badge:'Freshness hold \u00b7 stale',tone:'amber',date:`Last observed ${niceDate(s.observed_at)}`};if((st.includes('recover')||st==='recovered')&&(!TRUSTED_OMBUDSMAN_FEED||s.overall_verified!==true))return {title:'Recovered \u00b7 still unverified',subtitle:`A recovery signal is recorded, but the overall condition remains UNVERIFIED. ${stale?'The worker snapshot is now stale as well.':'Continue source checks; do not mark green from recovery alone.'}`,badge:stale?'Unverified \u00b7 stale':'Overall unverified',tone:'red',date:`Observed ${niceDate(s.observed_at)}`};if(TRUSTED_OMBUDSMAN_FEED&&s.overall_verified===true&&!stale&&['verified','healthy','recovered_verified'].includes(st))return {title:'Ombudsman verified recovery',subtitle:'The imported Ombudsman snapshot claims overall verification. Check its age and source before relying on this state.',badge:'Snapshot verified',tone:'green',date:`Observed ${niceDate(s.observed_at)}`};if(st.includes('gap')||st.includes('incident')||st.includes('fail'))return {title:'Ombudsman incident observed',subtitle:'The imported worker snapshot reports an unresolved incident. GitHub success does not resolve this state.',badge:'Unresolved incident',tone:'red',date:`Observed ${niceDate(s.observed_at)}`};return {title:'Status not independently verified',subtitle:stale?'The imported worker report is stale. Latest verification is unknown; preserve the hold.':'A worker snapshot exists, but it does not explicitly attest overall verification. Preserve the hold until confirmed.',badge:stale?'Unverified \u00b7 stale':'Overall unverified',tone:'amber',date:`Observed ${niceDate(s.observed_at)}`}}\n",
  "function watcherCard(kind,title,sub){const s=computeSchedule(kind),last=state.workflow[kind]?.[0];return `<div class=\"surface pad\"><div style=\"display:flex;justify-content:space-between;gap:10px;align-items:start\"><div><h3>${title}</h3><p class=\"text-xs muted\" style=\"margin:3px 0 0\">${sub}</p></div>${smallWorkflowPill(kind)}</div><div class=\"gap16\"></div><div class=\"calendar-grid\">${s.slots.length?s.slots.map(r=>`<div class=\"slot ${r.classification}\" title=\"${e(r.time)} \u00b7 ${r.run?`Run #${r.run.run_number}, ${r.run.conclusion||r.run.status}, delay ${r.delay}m`:`${r.classification==='missing'?'No scheduled run observed in window':'Within lateness grace period'}`}\">${r.classification==='ok'?icon('check'):r.classification==='delayed'?'!':r.classification==='missing'?'\u00d7':icon('clock')}<span>${e(r.label)}</span></div>`).join(''):'<div class=\"muted text-xs\" style=\"grid-column:1/-1;padding:15px\">No live GitHub runs loaded; status unknown.</div>'}</div><div class=\"legend\" style=\"margin-top:13px\"><div class=\"legend-item\"><i style=\"background:#68a47d\"></i> Observed</div><div class=\"legend-item\"><i style=\"background:#dfb668\"></i> Delayed \u226515m</div><div class=\"legend-item\"><i style=\"background:#d48074\"></i> Not observed</div><div class=\"legend-item\"><i style=\"background:#b7c0b7\"></i> Grace</div></div><div class=\"divider\"></div><div class=\"stat-row\"><div><b>Latest scheduled run</b><small>${last?niceDate(last.created_at):'Not available'}</small></div>${last?pill(last.conclusion||last.status||'Unknown',last.conclusion==='success'?'green':last.conclusion==='failure'?'red':'amber'):pill('Unknown','gray')}</div><div class=\"stat-row\"><div><b>GitHub Actions</b><small>Read-only run history</small></div>${urlLink(`${GH}/actions/workflows/scan-${kind==='results'?'results':'draw'}.yml`,'Open workflow')}</div></div>`}\n",
  "function ombudsmanPage(){const o=currentOmbudsmanState(),results=computeSchedule('results'),draw=computeSchedule('draw');const snaps=workspace.ombudsmanSnapshot;const live=state.liveOmbudsman;return `${pageHead('03 / OMBUDSMAN','Watcher control room','Observe scheduled workflows and incident signals. Recovery, publication and overall verification are three different facts.',`<button class=\"btn\" data-action=\"import-ombudsman\">${icon('upload')} Import worker snapshot</button><button class=\"btn primary\" data-action=\"refresh-all\">${icon('refresh')} Refresh observations</button>`)}\n",
  "<div class=\"watch-main\"><div><div class=\"eyebrow\">TFFC-OMBUDSMAN \u00b7 REPORTED STATE</div><h3>${e(o.title)}</h3><p>${e(o.subtitle)}</p><div style=\"margin-top:15px\">${pill(o.badge,o.tone)} <span class=\"tiny-note\" style=\"color:#c8d3c9;margin-left:7px\">${e(o.date)}</span></div></div><div style=\"align-self:end;z-index:1;text-align:right\"><div class=\"eyebrow\">HEARTBEAT</div><div style=\"font:700 28px Georgia,serif;color:#f4deb1\">:20</div><div style=\"font:700 17px Georgia,serif;color:#f4deb1\">Every hour (UTC)</div><small style=\"color:#d6e3d7\">Scheduled, not proof of execution</small></div></div>\n",
  "<div class=\"gap16\"></div>${state.workflowError?banner('GitHub history unavailable',e(state.workflowError)+'. Schedule gaps cannot be inferred without observed run history.','error'):banner('Observation \u2260 verified health','GitHub run data is read-only and may be delayed or truncated. A \u201cnot observed\u201d slot requires investigation; a successful workflow is not an overall Ombudsman recovery.')}<div class=\"gap16\"></div><div class=\"grid4\">${metric('Results gaps observed',state.workflow.results?results.unobserved:'\u2014','12 UTC slots \u00b7 grace 95m', 'alert',results.unobserved?'alert':'')}${metric('Draw gaps observed',state.workflow.draw?draw.unobserved:'\u2014','12 UTC slots \u00b7 grace 95m', 'alert',draw.unobserved?'warn':'')}${metric('Delayed scheduled launches',state.workflow.results&&state.workflow.draw?results.delayed+draw.delayed:'\u2014','15m+ lateness threshold', 'clock','warn')}${metric('Overall verification','NO / UNKNOWN',live?'Watcher feed cannot certify overall health':'No verified overall-health feed','shield','alert')}</div>\n",
  "<div class=\"gap16\"></div><div class=\"info-banner\">${icon('clock')}<div><strong>Observation freshness</strong><div>GitHub run history: ${state.workflowAt?e(since(state.workflowAt))+' (last read)':'not loaded'} \u00b7 Worker: ${live?.checked_at?e(since(live.checked_at))+' (protected report)':snaps?.observed_at?e(since(snaps.observed_at))+' (untrusted manual snapshot)':'not connected'} \u00b7 Competition report: ${e(since(state.healthSourceDate))} old. The protected hourly Worker report becomes stale after 90 minutes. An imported snapshot never establishes a current all-clear.</div></div></div>\n",
  "${live?`<div class=\"info-banner\"><div><strong>Protected Ombudsman feed \\u00b7 ${e(live.state.toUpperCase())}</strong><div>Checked ${e(niceDate(live.checked_at))} \\u00b7 ${live.fresh?'Fresh':'Stale / UNKNOWN'} \\u00b7 ${['results','draw'].map(n=>`${n}: ${e(live.checks?.[n]?.state||'unknown')} (${e(live.checks?.[n]?.reason||'not supplied')})${live.checks?.[n]?.catch_up?` \\u00b7 catch-up ${e(live.checks[n].catch_up.state)}`:''}`).join(' \\u00b7 ')}. This feed cannot prove complete competition health.</div></div></div><div class=\"gap16\"></div>`:''}\n",
  "${sectionHeader('Scheduled launch observations','GitHub\u2019s timestamp is compared with the hourly expected slot. No inferred worker health.')}<div class=\"two-col\">${watcherCard('results','Results watcher','scan-results.yml \u00b7 expected :17 UTC')}${watcherCard('draw','Draw watcher','scan-draw.yml \u00b7 expected :37 UTC')}</div>\n",
  "${sectionHeader('Incidents & recovery states','Keep incidents separate from local administration notes.',`<button class=\"btn small\" data-action=\"new-incident\">${icon('plus')} Record admin note</button>`)}\n",
  "<div class=\"two-col\"><div class=\"surface\"><div class=\"surface-head\"><h3>Observed/imported incidents</h3><span class=\"surface-sub\">Imported worker events / local notes</span></div><div style=\"padding:5px 20px\">${incidentRows()}</div></div><div class=\"surface pad\"><h3>Interpretation rules</h3><div class=\"stat-row\"><div><b>no_recent_scheduled_launch</b><small>Scheduled launch has not been observed; examine delay, queueing and history.</small></div>${pill('Investigate','red')}</div><div class=\"stat-row\"><div><b>Results recovered; overall unverified</b><small>Recovery event is real, but overall confidence stays held.</small></div>${pill('Unverified','amber')}</div><div class=\"stat-row\"><div><b>Published result / healthy chronology</b><small>Not equivalent to a verified worker heartbeat.</small></div>${pill('Separate','blue')}</div><div class=\"stat-row\"><div><b>Schedule delayed</b><small>Run started late; no automatic declaration of missed execution.</small></div>${pill('Warning','amber')}</div></div></div>\n",
  "${sectionHeader('Read-only competition health','Independent source; it does not override unresolved watcher evidence.')}\n",
  "<div class=\"surface pad\">${state.healthText?`<div class=\"btn-row\" style=\"justify-content:space-between\"><div>${pill(/chronology healthy/i.test(state.healthText)?'Chronology healthy in last report':'Check source text',/chronology healthy/i.test(state.healthText)?'green':'amber')} <span class=\"text-xs muted\">Last checked ${niceDate(state.healthSourceDate)} \u00b7 fetched ${niceDate(state.healthAt)}</span></div>${urlLink(`${GH}/blob/main/competition-health.md`,'Open report')}</div><pre style=\"white-space:pre-wrap;font-size:11px;line-height:1.6;color:#68776c;max-height:270px;overflow:auto;margin-top:16px\">${e(state.healthText)}</pre>`:`${banner('Historical source, not live-verified',`The latest known competition-health.md had a report time of ${niceDate(state.healthSourceDate)}. Refresh to retrieve the current text; there is no implied current green state.`)}<div class=\"gap16\"></div>${urlLink(`${GH}/blob/main/competition-health.md`,'Open the source report')}`}</div>\n",
  "<div class=\"source-footer\">Schedule sources: ${urlLink(`${GH}/blob/main/.github/workflows/scan-results.yml`,'Results YAML')} \u00b7 ${urlLink(`${GH}/blob/main/.github/workflows/scan-draw.yml`,'Draw YAML')} \u00b7 GitHub observations fetched ${state.workflowAt?niceDate(state.workflowAt):'not yet'}</div>`}\n",
  "function incidentRows(){const imported=Array.isArray(workspace.ombudsmanSnapshot?.alerts)?workspace.ombudsmanSnapshot.alerts:[];const list=[...imported.map((r,i)=>({id:`source-${i}`,source:'WORKER FEED',kind:r.type||r.code||r.status||'Alert',detail:r.message||r.description||r.details||'',at:r.timestamp||r.at||workspace.ombudsmanSnapshot.observed_at,verified:r.overall_verified===true})),...workspace.incidents.map(r=>({id:r.id,source:'LOCAL NOTE',kind:r.kind,detail:r.detail,at:r.at}))].sort((a,b)=>(b.at||'').localeCompare(a.at||''));return list.length?list.slice(0,20).map(r=>`<div class=\"activity-item\"><div class=\"activity-icon\">${icon('alert')}</div><div><b>${e(String(r.kind).replaceAll('_',' '))}</b><p>${e(r.detail||'No details recorded.')}</p><time>${e(r.source)} \u00b7 ${niceDate(r.at)}</time></div></div>`).join(''):blank('No Ombudsman feed imported','Import a manual worker report for leads to investigate; it cannot independently verify incidents. A local admin note is never treated as a worker alert.')}\n",
  "function incidentModal(){return `<div class=\"modal-backdrop\" data-dismiss=\"1\"><div class=\"modal\" role=\"dialog\" aria-modal=\"true\" aria-label=\"Local incident note\"><div class=\"modal-head\"><div><div class=\"eyebrow\">OMBUDSMAN / HUMAN NOTE</div><h2>Record investigation note</h2></div><button class=\"icon-btn\" data-action=\"close-overlay\">${icon('close')}</button></div>${banner('Local note only','Does not change the worker, GitHub schedule, alert state or verification status.')}<form id=\"incident-form\"><div class=\"form-grid\" style=\"margin-top:17px\"><div class=\"field\"><label>Category</label><select name=\"kind\"><option value=\"scheduled_gap_review\">Scheduled gap review</option><option value=\"delayed_schedule\">Delayed launch follow-up</option><option value=\"recovery_observed\">Recovery observation</option><option value=\"verification_needed\">Verification needed</option><option value=\"other\">Other</option></select></div><div class=\"field\"><label>Reference / workflow run URL</label><input name=\"reference\" type=\"url\" placeholder=\"https://github.com/...\"></div><div class=\"field full\"><label>Investigation detail</label><textarea name=\"detail\" required rows=\"4\"></textarea></div></div><div class=\"form-controls\"><button type=\"button\" class=\"btn primary\" data-action=\"save-incident\">Save note</button></div></form></div></div>`}\n",
  "function saveIncident(){const f=document.getElementById('incident-form');if(!f)return;const d=new FormData(f);if(!String(d.get('detail')||'').trim())return toast('Investigation note is required.',true);workspace.incidents.unshift({id:id(),kind:d.get('kind'),reference:String(d.get('reference')||''),detail:String(d.get('detail')).trim(),at:iso()});record('incident_note','Local Ombudsman investigation note',d.get('kind'));state.overlay=null;nav('ombudsman');toast('Local note saved. Worker state is unchanged.')}\n",
  "function approvalsPage(){let approved=workspace.proposals.filter(p=>p.status==='approved_for_export').length,tab=state.reviewTab;let list=tab==='proposals'?workspace.proposals:tab==='outreach'?workspace.outreach:workspace.history;return `${pageHead('GOVERNANCE / REVIEW','Approval & status ledger','A clear local history of proposals, approval decisions, email proof and incident notes. Exports require an independent repository review.',`<button class=\"btn\" data-action=\"export-workspace\">${icon('download')} Export workspace</button><button class=\"btn primary\" data-action=\"export-approved\" ${approved?'':'disabled'}>${icon('file')} Export ${approved} approved PR item${approved===1?'':'s'}</button>`)}\n",
  "<div class=\"grid4\">${metric('Awaiting review',proposedForReview(),'Proposed corrections pending approval','clock','warn')}${metric('Held or draft',heldProposals(),'Cannot publish without sufficient evidence','lock','alert')}${metric('Approved for PR',approved,'Still not applied to production','clipboard','good')}${metric('Recorded actions',workspace.history.length,'Local browser history only','history')}</div><div class=\"gap16\"></div>${banner('Local history is not a tamper-proof audit log','This standalone workspace saves records in this browser and exports JSON. For a multi-user operational system, use authenticated server-side storage, immutable audit events and protected reviewer identities before production use.')}\n",
  "${sectionHeader('Review queue','Each decision is traceable locally; none has a production apply action.')}<div class=\"surface\"><div class=\"tabbar\"><button class=\"tab ${tab==='proposals'?'active':''}\" data-review-tab=\"proposals\">Club corrections (${workspace.proposals.length})</button><button class=\"tab ${tab==='outreach'?'active':''}\" data-review-tab=\"outreach\">Outreach approvals (${workspace.outreach.length})</button><button class=\"tab ${tab==='history'?'active':''}\" data-review-tab=\"history\">Status history (${workspace.history.length})</button></div>\n",
  "${tab==='history'?`<div class=\"quick-list\">${workspace.history.length?workspace.history.slice(0,100).map(h=>`<div class=\"activity-item\"><div class=\"activity-icon\">${icon('history')}</div><div><b>${e(h.label)}</b><p>${e(h.detail)}</p><time>${niceDate(h.at)}</time></div></div>`).join(''):blank('No local activity','Saved actions and human approvals appear here.')}</div>`:`<div class=\"table-wrap\"><table><thead><tr><th>Record</th><th>Details</th><th>Status</th><th>Last action</th><th></th></tr></thead><tbody>${list.map(r=>{let p=tab==='proposals';return `<tr><td><div class=\"row-title\">${e(r.club)}</div><div class=\"row-desc\">${p?e(KIND_LABEL[r.kind]||r.kind):e(r.recipient||'Recipient not set')}</div></td><td>${p?e(r.proposedValue||'\u2014'):e(r.subject||r.kind||'\u2014')}</td><td>${p?proposalPill(r.status):outreachPill(r.status)}</td><td>${niceDate(r.updatedAt||r.approvedAt||r.createdAt,true)}</td><td class=\"td-actions\"><button class=\"btn small\" data-open=\"${p?'proposal':'outreach'}:${e(r.id)}\">Inspect ${icon('chevron')}</button></td></tr>`}).join('')||`<tr><td colspan=\"5\">${blank('No records yet','Create an evidence proposal or outreach draft to start a review.')}</td></tr>`}</tbody></table></div>`}</div>\n",
  "${sectionHeader('Production boundary','What a reviewed proposal can \u2014 and cannot \u2014 do.')}\n",
  "<div class=\"two-col\"><div class=\"surface pad\"><h3>Permitted in this workspace</h3>${['View versioned, public repository evidence','Draft and hold corrections','Record named human approval','Export a proposed change handoff','Log outreach and SENT proof locally'].map(t=>`<div class=\"stat-row\"><div><b>${e(t)}</b></div><span style=\"color:#317960\">${icon('check')}</span></div>`).join('')}</div><div class=\"surface pad\"><h3>Explicitly disabled</h3>${['Editing competition.json or canonical grounds','Publishing a fixture / overwriting Clubfinder','Sending emails or marking SENT without proof','Auto-promoting uncertain postcode / groundshare','Merging a PR or running publisher workflows'].map(t=>`<div class=\"stat-row\"><div><b>${e(t)}</b></div><span style=\"color:#b9574a\">${icon('lock')}</span></div>`).join('')}</div></div>`}\n",
  "function sourcePage(){return `${pageHead('GOVERNANCE / DATA SOURCES','Sources & safety','The admin layer is deliberately separate from the public Site. It reads published repository data and never acquires production-write credentials.',`<button class=\"btn\" data-action=\"import-workspace\">${icon('upload')} Restore workspace</button><button class=\"btn primary\" data-action=\"export-workspace\">${icon('download')} Back up local work</button>`)}\n",
  "${banner('This is a standalone internal workspace, not a deployed authenticated admin service','For real shared operational use, deploy behind access control on a separate administration domain, add server-side audit storage, secure Gmail/GitHub connections and explicit reviewed mutations. Do not link it from the public TFFAC navigation.')}\n",
  "${sectionHeader('Connected public read-only feeds','Refreshing makes GET requests only; no credentials are embedded.')}\n",
  "<div class=\"grid3\"><div class=\"surface pad\"><div class=\"eyebrow\">CLUBFINDER</div><h3 style=\"margin:12px 0 7px\">Club website evidence queue</h3>${pill(state.queueLoaded?'Loaded':'Fallback preview',state.queueLoaded?'green':'amber')}<div class=\"mini-stat\" style=\"margin-top:13px\"><span>Rows accessible</span><strong>${state.queueLoaded?state.queue.length:'Sample only'}</strong></div><div class=\"mini-stat\"><span>Eligible Clubfinder</span><strong>${e(state.queueMeta.eligible)}</strong></div><div class=\"mini-stat\"><span>Source modified</span><strong>${niceDate(state.queueMeta.competition_updated_at,true)}</strong></div><div class=\"gap16\"></div>${urlLink(`${GH}/blob/main/updater/club_website_audit_queue.json`,'Review source JSON')}</div>\n",
  "<div class=\"surface pad\"><div class=\"eyebrow\">WORKFLOW LAUNCHES</div><h3 style=\"margin:12px 0 7px\">GitHub Actions \u00b7 UTC</h3>${pill(state.workflow.results&&state.workflow.draw?'Read-only feed loaded':'Unavailable / not checked',state.workflow.results&&state.workflow.draw?'green':'amber')}<div class=\"mini-stat\" style=\"margin-top:13px\"><span>Results schedule</span><strong>:17 hourly</strong></div><div class=\"mini-stat\"><span>Draw schedule</span><strong>:37 hourly</strong></div><div class=\"mini-stat\"><span>Last read</span><strong>${state.workflowAt?niceDate(state.workflowAt,true):'Never'}</strong></div><div class=\"gap16\"></div>${urlLink(`${GH}/actions`,'Review workflow runs')}</div>\n",
  "<div class=\"surface pad\"><div class=\"eyebrow\">COMPETITION HEALTH</div><h3 style=\"margin:12px 0 7px\">Health markdown</h3>${pill(state.healthText?'Text loaded':'Fallback metadata',state.healthText?'green':'amber')}<div class=\"mini-stat\" style=\"margin-top:13px\"><span>Report timestamp</span><strong>${niceDate(state.healthSourceDate,true)}</strong></div><div class=\"mini-stat\"><span>Read at</span><strong>${state.healthAt?niceDate(state.healthAt,true):'Not fetched'}</strong></div><div class=\"mini-stat\"><span>Publish rights</span><strong>None</strong></div><div class=\"gap16\"></div>${urlLink(`${GH}/blob/main/competition-health.md`,'Review source report')}</div></div>\n",
  "${sectionHeader('Import & export','Bring your own trusted snapshots. No guessed or simulated evidence is marked live.')}\n",
  "<div class=\"two-col\"><div class=\"surface pad\"><h3>Data import</h3><p class=\"text-xs muted\">The club import accepts repository audit queue JSON. Ombudsman import accepts an explicitly timestamped worker snapshot with a status and optional alerts.</p><div class=\"btn-row\"><button class=\"btn small\" data-action=\"import-clubs\">${icon('upload')} Clubfinder JSON</button><button class=\"btn small\" data-action=\"import-ombudsman\">${icon('upload')} Ombudsman JSON</button><button class=\"btn small\" data-action=\"import-workspace\">${icon('upload')} Workspace backup</button></div><div class=\"divider\"></div><h3>Worker feed contract</h3><pre class=\"mono\" style=\"white-space:pre-wrap;overflow:auto;color:#576f61\">${e(JSON.stringify({observed_at:'2026-11-18T10:00:00Z',status:'recovered_unverified',overall_verified:false,alerts:[{code:'no_recent_scheduled_launch',message:'Verified worker message',timestamp:'2026-11-18T10:00:00Z'}]},null,2))}</pre><div class=\"note\">Example schema only \u2014 not actual Ombudsman readings.</div></div>\n",
  "<div class=\"surface pad\"><h3>Local-only handoffs</h3><p class=\"text-xs muted\">You can export reviewed corrections for a separate PR, and back up all local drafts, recipients and review history. JSON backups may contain email addresses. Store them securely.</p><div class=\"btn-row\"><button class=\"btn small\" data-action=\"export-approved\">${icon('download')} Approved PR proposals</button><button class=\"btn small\" data-action=\"export-workspace\">${icon('download')} Full workspace backup</button></div><div class=\"divider\"></div><h3>Safety controls</h3>${['Fail closed on uncertain identity, postcode, groundshare, sponsorship, qualifying role','Require documented evidence URLs and dates before review','Approval is locally recorded and does not patch a canonical file','Maximum 15 introduction approvals per UK day','No live email sending, worker control or repository write route'].map(x=>`<div class=\"activity-item\"><div class=\"activity-icon\" style=\"color:#367b60\">${icon('shield')}</div><div><b>${e(x)}</b></div></div>`).join('')}</div></div>\n",
  "${sectionHeader('Browser storage','Explicitly remove your locally saved drafts only when you have backed them up.')}\n",
  "<div class=\"surface pad\"><div style=\"display:flex;gap:15px;justify-content:space-between;align-items:center;flex-wrap:wrap\"><div><h3>${workspace.proposals.length} proposals \u00b7 ${workspace.outreach.length} outreach items \u00b7 ${workspace.history.length} actions</h3><p class=\"text-xs muted\" style=\"margin:5px 0 0\">Stored in this browser. Other devices and collaborators will not see these records automatically.</p></div><button class=\"btn danger\" data-action=\"reset-local\">${icon('alert')} Reset local workspace</button></div></div>`}\n",
  "function resetModal(){return `<div class=\"modal-backdrop\" data-dismiss=\"1\"><div class=\"modal\" role=\"dialog\" aria-modal=\"true\" aria-label=\"Reset local workspace\"><div class=\"modal-head\"><div><div class=\"eyebrow\">DESTRUCTIVE LOCAL ACTION</div><h2>Reset local workspace?</h2></div><button class=\"icon-btn\" data-action=\"close-overlay\">${icon('close')}</button></div>${banner('This clears drafts, review notes, imported Ombudsman snapshots and local SENT references.','It cannot restore any source or send data. Export a backup first.','error')}<div class=\"form-grid\" style=\"margin-top:16px\"><div class=\"field full\"><label>Type RESET LOCAL to confirm</label><input id=\"reset-confirm\" placeholder=\"RESET LOCAL\"></div></div><div class=\"form-controls btn-row\"><button class=\"btn\" data-action=\"export-workspace\">Back up first</button><button class=\"btn danger\" data-action=\"confirm-reset\">Clear browser data</button></div></div></div>`}\n",
  "function ideasPage(){return missionIdeasPage()}\n",
  "function pullrequestsPage(){return missionPRPage()}\n",
  "/* Club Entry Radar v1: manually imported CI artifact; strictly read-only, session-only. */\n",
  "const radar={report:null,loadedAt:null,filename:null,error:null,round:'',source:'beta',status:'all',search:'',mode:'unknown',run:null,generatedAt:null,busy:false,checkedAt:null};\n",
  "const RADAR_STATES=['verified_location','ground_recorded_coordinates_pending','missing_ground','identity_conflict'];\n",
  "function radarValidate(x){\n",
  " if(!x||x.schema_version!==1||x.read_only!==true||x.canonical_source!=='competition.json'||x.automatic_ground_promotion!==false||x.fixture_venues_used_as_home_grounds!==false||!Array.isArray(x.rounds)||x.rounds.length>50||typeof x.season!=='string')throw Error('Not an approved read-only Club Entry Radar report');\n",
  " for(const round of x.rounds){\n",
  "  if(!round||typeof round.round!=='string'||round.round.length>100||!Array.isArray(round.clubs)||round.clubs.length>1500||round.entrant_count!==round.clubs.length||!round.coverage||typeof round.coverage!=='object')throw Error('Invalid entrant totals or round');\n",
  "  for(const source of ['production','beta']){\n",
  "   const counts=round.coverage[source];\n",
  "   if(!counts||RADAR_STATES.some(key=>!Number.isSafeInteger(counts[key])||counts[key]<0)||RADAR_STATES.reduce((n,key)=>n+counts[key],0)!==round.entrant_count)throw Error('Inconsistent '+source+' ground coverage');\n",
  "  }\n",
  "  if(round.clubs.some(c=>!c||typeof c.club!=='string'||!c.club||typeof c.identity!=='string'||!c.sources||['production','beta'].some(source=>!c.sources[source]||!RADAR_STATES.includes(c.sources[source].status))))throw Error('Malformed club records');\n",
  " }\n",
  " return x;\n",
  "}\n",
  "function radarUseReport(report,meta){\n",
  " radar.report=radarValidate(report);\n",
  " radar.loadedAt=new Date().toISOString();radar.filename=meta.filename||'club-entry-radar.json';\n",
  " radar.mode=meta.mode;radar.run=meta.run||null;radar.generatedAt=meta.generatedAt||null;\n",
  " radar.round=report.rounds.at(-1)?.round||'';\n",
  " radar.source='beta';radar.status='all';radar.search='';radar.error=null;\n",
  "}\n",
  "async function radarFetchLatest(){\n",
  " if(radar.busy)return;\n",
  " radar.busy=true;radar.checkedAt=new Date().toISOString();radar.error=null;render();\n",
  " try{\n",
  "  const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),20000);\n",
  "  let response;\n",
  "  try{response=await fetch('/api/radar/latest',{credentials:'same-origin',cache:'no-store',signal:controller.signal,redirect:'error'});}finally{clearTimeout(timeout)}\n",
  "  if(!response.ok){let code='HTTP '+response.status;try{code=(await response.json()).error||code}catch{};throw Error(code)}\n",
  "  const incoming=await response.text();if(incoming.length>3500000)throw Error('Radar report exceeds 3.5 MB');\n",
  "  const body=JSON.parse(incoming);\n",
  "  if(!body||!body.report||!body.provenance||body.provenance.branch!=='main'||body.provenance.conclusion!=='success')throw Error('Missing verified main-run provenance');\n",
  "  radarUseReport(body.report,{mode:'automatic',run:body.provenance,generatedAt:body.provenance.completed_at});\n",
  "  toast('Latest successful main Radar artifact loaded read-only.');\n",
  " }catch(ex){\n",
  "  radar.error=String(ex.message||'Radar source unavailable');\n",
  "  // Never clear a known imported report when the network fails. Explicitly mark it as fallback.\n",
  "  if(radar.report&&radar.mode==='automatic')radar.mode='retained';\n",
  " }finally{radar.busy=false;render()}\n",
  "}\n",
  "async function radarImport(input){\n",
  " const file=input.files?.[0];if(!file)return;\n",
  " try{\n",
  "  if(file.size>3500000)throw Error('Report exceeds 3.5 MB limit');\n",
  "  const report=radarValidate(JSON.parse(await file.text()));\n",
  "  radarUseReport(report,{mode:'manual',filename:file.name});\n",
  "  toast('Club Entry Radar report loaded read-only.');\n",
  " }catch(ex){radar.error=String(ex.message||'Invalid report');toast('Radar import rejected: '+radar.error,true)}\n",
  " finally{input.value='';render()}\n",
  "}\n",
  "function radarTone(state){return state==='verified_location'?'green':state==='ground_recorded_coordinates_pending'?'blue':state==='identity_conflict'?'red':'amber'}\n",
  "function radarLabel(state){return ({verified_location:'Location verified in registry',ground_recorded_coordinates_pending:'Ground details recorded \u00b7 map check pending',missing_ground:'Ground details missing',identity_conflict:'Identity conflict'})[state]||'Unknown'}\n",
  "function radarPage(){\n",
  " const r=radar.report;\n",
  " const top=pageHead('CLUBFINDER / CLUB ENTRY RADAR','Clubs entering by round','Read-only canonical fixture participation compared with production and BETA home-ground records. No fixture venue becomes a home ground.',`<div class=\"btn-row\"><button class=\"btn\" data-action=\"radar-refresh\" ${radar.busy?'disabled':''}>${icon('refresh')} ${radar.busy?'Checking\u2026':'Fetch latest main report'}</button><button class=\"btn primary\" data-action=\"radar-import\">${icon('upload')} Import CI report</button></div>`);\n",
  " if(!r)return top+banner('No radar report loaded',radar.busy?'Checking the most recent successful main run\u2026':'The automatic source is unavailable or not yet checked. You can still import a JSON artifact from GitHub Actions. Unknown is not zero.')+(radar.error?banner('Automatic Radar source unavailable',e(radar.error)+' \u00b7 Manual import remains available.','error'):'')+`<section class=\"surface pad\" style=\"margin-top:16px\"><h3>Construction Law boundary</h3><p class=\"tiny-note\">Import stays in this browser tab only. No ground publication, coordinate promotion, competitor results editing, or mailbox changes. A missing report means unknown, never zero.</p><a class=\"btn\" href=\"https://github.com/anvilspringstien/tinfoilfacup/actions/workflows/club-entry-radar.yml\" rel=\"noopener noreferrer\" target=\"_blank\">Open Radar workflow</a></section>`;\n",
  " const selected=r.rounds.find(x=>x.round===radar.round)||r.rounds.at(-1),src=radar.source;\n",
  " const counts=selected.coverage[src];\n",
  " const filtered=selected.clubs.filter(c=>{\n",
  "  const info=c.sources[src];return (radar.status==='all'||info.status===radar.status)&&(!radar.search||c.club.toLowerCase().includes(radar.search.toLowerCase()));\n",
  " });\n",
  " const age=radar.generatedAt?Date.now()-Date.parse(radar.generatedAt):NaN;\n",
  " const tooOld=Number.isFinite(age)&&age>24*60*60*1000;\n",
  " const origin=radar.mode==='automatic'?'Fetched successful main CI artifact':radar.mode==='retained'?'Retained prior automatic report \u2014 REFRESH FAILED':'Manually imported CI artifact';\n",
  " const provenance=radar.run?` \u00b7 Workflow #${e(radar.run.run_number)} \u00b7 completed ${e(radar.run.completed_at)} \u00b7 commit ${e(radar.run.head_sha)}`:'';\n",
  " const freshness=tooOld?' \u00b7 STALE (>24h)':radar.mode==='retained'?' \u00b7 freshness UNKNOWN':' \u00b7 Not independently verified against the live deployment';\n",
  " const snapshot=`<div class=\"info-banner\"><div><strong>${e(origin)} \u00b7 ${e(r.season)}${tooOld?' \u00b7 STALE':''}</strong><div>Source: ${e(r.canonical_source)} \u00b7 competition revision: ${e(r.competition_updated_at||'not reported')} \u00b7 read ${e(radar.loadedAt||'unknown')}${provenance}${freshness}. File: ${e(radar.filename||'unknown')}.</div>${radar.error?`<div style=\"color:#9d4538\">Refresh failed: ${e(radar.error)}. Existing report retained; manual import available.</div>`:''}</div></div>`;\n",
  " const options=r.rounds.map(x=>`<option value=\"${e(x.round)}\" ${x.round===selected.round?'selected':''}>${e(x.round)} \u00b7 ${x.entrant_count} clubs</option>`).join('');\n",
  " const filters=`<div class=\"filters\"><div class=\"field\"><label for=\"radar-round\">Round</label><select id=\"radar-round\">${options}</select></div><div class=\"field\"><label for=\"radar-source\">Clubfinder source</label><select id=\"radar-source\"><option value=\"beta\" ${src==='beta'?'selected':''}>BETA</option><option value=\"production\" ${src==='production'?'selected':''}>Production source</option></select></div><div class=\"field\"><label for=\"radar-status\">Ground status</label><select id=\"radar-status\"><option value=\"all\">All</option>${RADAR_STATES.map(x=>`<option value=\"${x}\" ${radar.status===x?'selected':''}>${e(radarLabel(x))}</option>`).join('')}</select></div><div class=\"field\" style=\"flex:1\"><label for=\"radar-search\">Club search</label><input id=\"radar-search\" placeholder=\"Search club name\" value=\"${e(radar.search)}\"></div></div>`;\n",
  " const metrics=`<div class=\"grid4\" style=\"margin:16px 0\">${metric('Entrants',selected.entrant_count,'Canonical fixtures','database')}${metric('Recorded, map pending',counts.ground_recorded_coordinates_pending,'Ground details exist','info')}${metric('Missing grounds',counts.missing_ground,'Requires evidence review','alert','warn')}${metric('Identity conflicts',counts.identity_conflict,'Never infer matching identities','shield','alert')}</div>`;\n",
  " const rows=filtered.slice(0,300).map(c=>{const x=c.sources[src];return `<tr><td><div class=\"row-title\">${e(c.club)}</div><div class=\"row-desc\">${c.new_to_observed_rounds?'Newly observed in chronology':'Previously observed'}${c.entry_round?' \u00b7 Registry entry: '+e(c.entry_round):''}</div></td><td>${e(x.ground||'\u2014')}<div class=\"row-desc\">${e(x.postcode||'\u2014')}</div></td><td><span class=\"status ${radarTone(x.status)}\">${e(radarLabel(x.status))}</span></td></tr>`}).join('');\n",
  " return top+snapshot+metrics+`<section class=\"surface\">${filters}<div class=\"table-wrap\"><table><thead><tr><th>Entrant</th><th>Home ground \u00b7 postcode</th><th>Registry status</th></tr></thead><tbody>${rows||'<tr><td colspan=\"3\">No clubs match these filters.</td></tr>'}</tbody></table></div><div class=\"pagination\">Showing ${Math.min(filtered.length,300)} of ${filtered.length} matching entrants \u00b7 ${selected.new_to_observed_rounds} first observed in this round ${filtered.length>300?'\u00b7 first 300 shown':''}</div></section><p class=\"tiny-note\" style=\"margin-top:14px\">Registry verification status is reported, not reverified here. Ground details recorded does not mean map coordinates have been verified. No changes can be published from this page.</p>`;\n",
  "}\n",
  "\n",
  "/* Shortcuts only. External services keep their own authentication and permissions. */\n",
  "const MISSION_LINK_GROUPS = [\n",
  " {title:'Tin Foil FA Cup',description:'The public game, the separate experiment entrance and your private admin tools.',links:[\n",
  "  {title:'Public TFFAC',description:'The normal supporter entrance',url:'https://tinfoilfacup.com/',icon:'layout'},\n",
  "  {title:'BETA Shed',description:'Opt-in phone-frame experiments',url:'https://tinfoilfacup.com/beta/phone-frame-shed.html',icon:'file'},\n",
  "  {title:'Boot Room admin',description:'Owner controls \u00b7 access remains protected',url:'https://tffac-boot-room-shed.anvilspringstien.workers.dev/admin',icon:'shield'},\n",
  "  {title:'Likes admin',description:'Private read-only Likes counter',url:'https://tffac-likes-shed.anvilspringstien.workers.dev/admin',icon:'check'}\n",
  " ]},\n",
  " {title:'Outreach & replies',description:'Open the exact outreach mailbox; Gmail handles reading, drafting and sending.',links:[\n",
  "  {title:'Gmail inbox',description:'TFFAC incoming club correspondence',url:'https://mail.google.com/mail/u/?authuser=tinfoilfacup%40gmail.com#inbox',icon:'mail'},\n",
  "  {title:'Gmail drafts',description:'Review unsent introductions and replies',url:'https://mail.google.com/mail/u/?authuser=tinfoilfacup%40gmail.com#drafts',icon:'file'},\n",
  "  {title:'Gmail sent',description:'Authoritative outbound message record',url:'https://mail.google.com/mail/u/?authuser=tinfoilfacup%40gmail.com#sent',icon:'send'}\n",
  " ]},\n",
  " {title:'Code, cloud & monitoring',description:'Go directly to source control, deployments and Google Cloud settings.',links:[\n",
  "  {title:'GitHub repository',description:'anvilspringstien/tinfoilfacup',url:'https://github.com/anvilspringstien/tinfoilfacup',icon:'database'},\n",
  "  {title:'GitHub pull requests',description:'Review PRs and check status',url:'https://github.com/anvilspringstien/tinfoilfacup/pulls',icon:'route'},\n",
  "  {title:'GitHub Actions',description:'Results, draw and other workflows',url:'https://github.com/anvilspringstien/tinfoilfacup/actions',icon:'activity'},\n",
  "  {title:'Club Entry Radar runs',description:'Read-only entrant audit workflow',url:'https://github.com/anvilspringstien/tinfoilfacup/actions/workflows/club-entry-radar.yml',icon:'search'},\n",
  "  {title:'Cloudflare dashboard',description:'Workers, builds and account settings',url:'https://dash.cloudflare.com/',icon:'shield'},\n",
  "  {title:'Google Cloud Console',description:'OAuth settings and project administration',url:'https://console.cloud.google.com/',icon:'lock'}\n",
  " ]},\n",
  " {title:'Support & payments',description:'Platform destinations only. No payment or account data is connected to Mission Control.',links:[\n",
  "  {title:'Stripe dashboard',description:'Open Stripe in your own account',url:'https://dashboard.stripe.com/',icon:'database'},\n",
  "  {title:'Revolut Pro',description:'Official instructions \u00b7 Pro is in the personal mobile app',url:'https://help.revolut.com/help/more/revolut-pro/where-is-my-revolut-pro-account-in-app/',icon:'info'}\n",
  " ]},\n",
  " {title:'The other Big Boy tabs',description:'Optional daily browser staples, without introducing additional integrations.',links:[\n",
  "  {title:'X',description:'Open the social platform',url:'https://x.com/',icon:'external'},\n",
  "  {title:'BBC Football',description:'News and match coverage',url:'https://www.bbc.co.uk/sport/football',icon:'activity'},\n",
  "  {title:'Spotify',description:'Open the music player',url:'https://open.spotify.com/',icon:'external'}\n",
  " ]}\n",
  "];\n",
  "function linksPage(){\n",
  " const sections=MISSION_LINK_GROUPS.map(group=>`<section aria-label=\"${e(group.title)}\"><div class=\"links-category\"><h2>${e(group.title)}</h2><p>${e(group.description)}</p></div><div class=\"links-grid\">${group.links.map(link=>`<a class=\"links-card\" href=\"${e(link.url)}\" target=\"_blank\" rel=\"noopener noreferrer\" aria-label=\"${e(link.title)} (opens in new tab)\"><span class=\"links-card-icon\">${icon(link.icon)}</span><span class=\"links-card-body\"><strong>${e(link.title)}</strong><small>${e(link.description)}</small></span><span class=\"link-out\">${icon('external')}</span></a>`).join('')}</div></section>`).join('');\n",
  " return pageHead('YOUR DAILY DESK','Links Desk','One place for the browser tabs that keep Tin Foil FA Cup running. Plain links, no new connections.')\n",
  " +`<div class=\"links-intro\">${icon('shield')}<div><strong>Shortcuts only \u00b7 no changes to other services</strong><p>Links open in a new tab. Each service retains its own login, permissions and safeguards. No credentials are entered or stored here.</p></div></div>`\n",
  " +sections+`<div class=\"links-footnote\">Revolut Pro is accessed through the personal Revolut mobile app; its link opens official instructions, not a Business dashboard. The BETA Shed shares some live files until the planned app/Shed separation refactor.</div>`;\n",
  "}\n",
  "\n",
  "function render(){updateChrome();const root=document.getElementById('content');root.innerHTML=({overview,clubfinder,radar:radarPage,outreach:outreachPage,ombudsman:ombudsmanPage,approvals:approvalsPage,sources:sourcePage,ideas:ideasPage,pullrequests:pullrequestsPage,links:linksPage})[state.section]();renderOverlay()}\n",
  "function renderOverlay(){const root=document.getElementById('overlay');const v=state.overlay;root.innerHTML=!v?'':v.type==='club'?clubDrawer(v.name):v.type==='proposal'?proposalDetail(workspace.proposals.find(p=>p.id===v.id)||{}):v.type==='proposal-form'?proposalForm(v.proposal||{}):v.type==='approve'?approveModal(workspace.proposals.find(p=>p.id===v.id)||{}):v.type==='outreach'?outreachDetail(workspace.outreach.find(o=>o.id===v.id)||{}):v.type==='outreach-form'?outreachForm(v.record||{},v.kind):v.type==='outreach-approval'?outreachApprovalModal(workspace.outreach.find(o=>o.id===v.id)||{}):v.type==='sent'?sentModal(workspace.outreach.find(o=>o.id===v.id)||{}):v.type==='incident'?incidentModal():v.type==='reset'?resetModal():v.type==='idea-form'?missionIdeaForm(v.idea||{}):v.type==='pr-note'?missionPRNoteModal(v.pr):'';document.body.style.overflow=v?'hidden':''}\n",
  "function open(v){state.overlay=v;renderOverlay()}\n",
  "function startProposal(club){state.selectedClub=club||null;open({type:'proposal-form',proposal:{club:club||'',kind:'official_website'}})}\n",
  "function startOutreach(club,kind='introduction',original=''){state.selectedClub=club||null;open({type:'outreach-form',kind,record:{club:club||'',kind,originalRef:original||''}})}\n",
  "function downloadJSON(filename,data){const blob=new Blob([JSON.stringify(data,null,2)+'\\n'],{type:'application/json'}),url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=filename;a.click();setTimeout(()=>URL.revokeObjectURL(url),2000)}\n",
  "function exportApproved(){const approved=workspace.proposals.filter(p=>p.status==='approved_for_export');if(!approved.length)return toast('No reviewed and approved corrections to export.',true);downloadJSON(`tffac-pr-proposals-${ukDay()}.json`,{schema_version:1,mode:'PROPOSAL_ONLY_REQUIRES_SEPARATE_GITHUB_PR',production_write_authorized:false,generated_at:iso(),source_repository:GH,proposals:approved.map(p=>({...p,holds:proposalHolds(p)}))});toast(`${approved.length} approved proposal(s) exported \u2014 no repo modifications.`)}\n",
  "function exportWorkspace(){downloadJSON(`tffac-admin-backup-${ukDay()}.json`,{kind:'TFFAC_ADMIN_WORKSPACE',generated_at:iso(),...workspace});toast('Workspace JSON backup exported. Protect any personal email addresses in it.')}\n",
  "function importFile(which){document.getElementById(which).click()}\n",
  "async function doImport(element,mode){const file=element.files?.[0];if(!file)return;try{if(file.size>10_000_000)throw Error('File exceeds the 10 MB limit.');const parsed=JSON.parse(await file.text());if(mode==='clubs'){useClubData(parsed);toast(`${state.queue.length} repository identity rows imported; review metadata freshness.`);nav('clubfinder')}\n",
  " else if(mode==='workspace'){if(parsed.kind!=='TFFAC_ADMIN_WORKSPACE'||parsed.version!==1||!Array.isArray(parsed.proposals)||!Array.isArray(parsed.outreach)||!Array.isArray(parsed.history))throw Error('Not a recognised TFFAC backup.');workspace={...defaultWorkspace(),proposals:parsed.proposals,outreach:parsed.outreach,history:parsed.history,incidents:Array.isArray(parsed.incidents)?parsed.incidents:[],ombudsmanSnapshot:parsed.ombudsmanSnapshot||null,ideas:Array.isArray(parsed.ideas)?parsed.ideas:[],prReviews:Array.isArray(parsed.prReviews)?parsed.prReviews:[],postcodeChecks:Array.isArray(parsed.postcodeChecks)?parsed.postcodeChecks:[],daily:parsed.daily&&Array.isArray(parsed.daily.completed)?parsed.daily:{date:null,completed:[]}};save();toast('Local workspace restored from backup.');nav('sources')}\n",
  " else if(mode==='ombudsman'){const observed=parsed.observed_at||parsed.timestamp||null;if(!observed||!Number.isFinite(Date.parse(observed))||typeof parsed.status!=='string')throw Error('Must include valid observed_at timestamp and status string.');if(parsed.overall_verified!==undefined&&typeof parsed.overall_verified!=='boolean')throw Error('overall_verified must be an explicit boolean.');workspace.ombudsmanSnapshot={observed_at:observed,status:parsed.status,overall_verified:parsed.overall_verified===true,alerts:Array.isArray(parsed.alerts)?parsed.alerts.slice(0,200):[],source_filename:file.name};record('worker_feed',`Imported Ombudsman snapshot: ${parsed.status}`,`${observed} \u00b7 ${file.name} \u00b7 verified=${parsed.overall_verified===true}`);toast('Worker snapshot imported. Status reflects the feed, not an inferred all-clear.');nav('ombudsman')}\n",
  "}catch(ex){toast(`Import rejected: ${ex.message}`,true)}finally{element.value=''}}\n",
  "function clickAction(btn){const a=btn.dataset.action,club=decodeURIComponent(btn.dataset.club||'');if(missionHandleAction(a,btn))return;if(a==='refresh-all')return refreshAll();if(a==='gmail-refresh')return missionGmailRefresh();if(a==='gmail-disconnect')return missionGmailDisconnect();if(a==='close-overlay'){state.overlay=null;return renderOverlay()}if(a==='page-prev'){state.queuePage--;return render()}if(a==='page-next'){state.queuePage++;return render()}if(a==='new-proposal')return startProposal(club);if(a==='save-proposal')return saveProposal(false);if(a==='submit-proposal')return saveProposal(true);if(a==='edit-proposal'){const p=workspace.proposals.find(x=>x.id===btn.dataset.id);if(p)return open({type:'proposal-form',proposal:p})}if(a==='review-proposal')return open({type:'approve',id:btn.dataset.id});if(a==='confirm-approval')return confirmApproval();if(a==='reject-proposal'){const p=workspace.proposals.find(x=>x.id===btn.dataset.id);if(p){p.status='rejected';p.updatedAt=iso();record('rejection',`Correction rejected: ${p.club}`,p.kind);state.overlay=null;nav('approvals');toast('Rejected locally. No data was published.')}return}\n",
  "if(a==='new-outreach')return startOutreach(club);if(a==='new-reply')return startOutreach(club,'reply',btn.dataset.original||'');if(a==='log-incoming-reply')return startOutreach(null,'incoming_reply');if(a==='save-outreach')return storeOutreach(false);if(a==='approve-outreach')return storeOutreach(true);if(a==='log-reply')return storeOutreach(false,true);if(a==='start-outreach-approval')return open({type:'outreach-approval',id:btn.dataset.id});if(a==='confirm-outreach')return confirmOutreach();if(a==='edit-outreach'){const o=workspace.outreach.find(x=>x.id===btn.dataset.id);if(o)return open({type:'outreach-form',kind:o.kind,record:o})}if(a==='open-sent')return open({type:'sent',id:btn.dataset.id});if(a==='confirm-sent')return confirmSent();\n",
  "if(a==='new-incident')return open({type:'incident'});if(a==='save-incident')return saveIncident();if(a==='export-approved')return exportApproved();if(a==='export-workspace')return exportWorkspace();if(a==='import-clubs')return importFile('import-clubs');if(a==='import-ombudsman')return importFile('import-ombudsman');if(a==='import-workspace')return importFile('import-workspace');if(a==='reset-local')return open({type:'reset'});if(a==='confirm-reset'){if(document.getElementById('reset-confirm')?.value!=='RESET LOCAL')return toast('Type RESET LOCAL exactly.',true);workspace=defaultWorkspace();const workspaceCleared=save(),countCleared=missionGmailClearCount();return countCleared.then(cleared=>{state.overlay=null;nav('sources');toast(workspaceCleared&&cleared?'Local review records and Gmail count cleared.':'Browser storage prevented clearing all local data.',!workspaceCleared||!cleared)})}}\n",
  "document.addEventListener('click',ev=>{const navEl=ev.target.closest('[data-nav]');if(navEl){nav(navEl.dataset.nav);return}const a=ev.target.closest('[data-action]');if(a){if(a.dataset.action==='radar-import'){document.getElementById('import-radar').click();return}if(a.dataset.action==='radar-refresh'){radarFetchLatest();return}return clickAction(a)}const o=ev.target.closest('[data-open]');if(o){const [type,...rest]=o.dataset.open.split(':');const value=rest.join(':');if(['sources','ombudsman','approvals','clubfinder'].includes(type))return nav(type);if(type==='club')return open({type:'club',name:decodeURIComponent(value)});if(type==='proposal')return open({type:'proposal',id:value});if(type==='outreach')return open({type:'outreach',id:value});return}const t=ev.target.closest('[data-outreach-tab]');if(t){state.outreachTab=t.dataset.outreachTab;return render()}const rt=ev.target.closest('[data-review-tab]');if(rt){state.reviewTab=rt.dataset.reviewTab;return render()}if(ev.target.matches('[data-dismiss=\"1\"]')){state.overlay=null;renderOverlay()}});\n",
  "document.addEventListener('change',ev=>{const el=ev.target;if(missionHandleChange(el))return;if(el.id==='import-radar'){radarImport(el);return}if(el.id==='radar-round'){radar.round=el.value;radar.status='all';render();return}if(el.id==='radar-source'){radar.source=el.value;render();return}if(el.id==='radar-status'){radar.status=el.value;render();return}if(el.id==='club-status'){state.queueFilter=el.value;state.queuePage=0;render()}if(el.id==='club-scope'){state.queueScope=el.value;state.queuePage=0;render()}if(el.id==='import-clubs')doImport(el,'clubs');if(el.id==='import-workspace')doImport(el,'workspace');if(el.id==='import-ombudsman')doImport(el,'ombudsman')});\n",
  "document.addEventListener('input',ev=>{missionHandleInput(ev.target);if(ev.target.id==='radar-search'){const caret=ev.target.selectionStart;radar.search=ev.target.value;render();const field=document.getElementById('radar-search');if(field){field.focus();try{field.setSelectionRange(caret,caret)}catch{}}return}if(ev.target.id==='club-search'){const start=ev.target.selectionStart;state.queueSearch=ev.target.value;state.queuePage=0;render();const el=document.getElementById('club-search');if(el){el.focus();try{el.setSelectionRange(start,start)}catch{}}}});\n",
  "document.addEventListener('keydown',ev=>{if(ev.key==='Escape'&&state.overlay){state.overlay=null;renderOverlay()}});\n",
  "document.querySelectorAll('[data-icon]').forEach(n=>n.innerHTML=icon(n.dataset.icon));\n",
  "render();refreshAll();radarFetchLatest();\n",
  "\n",
  "</script>\n",
  "</body>\n",
  "</html>\n"
].join('');

const DASHBOARD_CSP = "default-src 'none'; script-src 'sha256-xglNUjxAy82qc+srPua4jkb1AvBcXfM4igZojI8Tq/M=' 'sha256-58FxmnfNS+rb/MLvq4/wPfI/TiaxX+kjRZaS7zktNAQ='; script-src-attr 'none'; connect-src 'self' https://api.github.com https://raw.githubusercontent.com; style-src 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self'; object-src 'none'; worker-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'; upgrade-insecure-requests";

// Authenticated dashboard: no mailbox tokens, backend writes, or admin APIs.
function privateDashboard() {
  const headers = new Headers(HEADERS);
  // Allow ONLY the two exact inline application scripts, not arbitrary inline JS.
  headers.set('Content-Security-Policy', DASHBOARD_CSP);
  headers.set('X-Robots-Tag', 'noindex, nofollow, noarchive');
  headers.set('Vary', 'Cookie');
  return new Response(DASHBOARD_HTML, {status:200, headers});
}

/**
 * TFFAC Mission Control — Google sign-in gate (diagnostic pilot v3 — Cloudflare redirect compatibility)
 * One Cloudflare Worker with read-only service binding to existing tffc-ombudsman; optional short-lived Gmail read-only integration. No Durable Objects, KV, or sending.
 * Secrets expected in Production: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,
 * SESSION_SECRET (base64-encoded 32 random bytes).
 *
 * Deploy ONLY on the exact workers.dev hostname configured below.
 * Sign-in requests ONLY openid + email; Gmail read-only consent happens separately on explicit user request.
 */

const BASE = 'https://tffac-mission-control.anvilspringstien.workers.dev';
const CALLBACK = BASE + '/oauth/callback';
const ALLOWED_EMAIL = 'tinfoilfacup@gmail.com';
const SESSION_COOKIE = '__Host-tffac_session';
const FLOW_COOKIE = '__Host-tffac_oauth';
const GMAIL_FLOW_COOKIE = '__Host-tffac_gmail_flow';
const GMAIL_COOKIE = '__Host-tffac_gmail';
const GMAIL_SCOPE = 'https://www.googleapis.com/auth/gmail.readonly';
const SESSION_SECONDS = 60 * 60; // One hour; stateless sessions cannot be revoked server-side.
const FLOW_SECONDS = 10 * 60;

const HEADERS = {
  'Cache-Control': 'no-store, private',
  'Content-Type': 'text/html; charset=utf-8',
  'Content-Security-Policy': "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'",
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'Referrer-Policy': 'no-referrer',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
};

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function page(heading, body, status = 200, extras = {}) {
  const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>TFFAC Mission Control</title><style>html{background:#0e211a;color:#e9eedc;font-family:system-ui,sans-serif}body{min-height:100vh;display:grid;place-items:center;margin:0}.card{width:min(90vw,430px);padding:2rem;border:1px solid #4f725c;border-radius:18px;background:#173127;box-shadow:0 18px 50px #0004}h1{font-size:1.6rem;margin:.2rem 0 1rem}p{line-height:1.6;color:#d0ddcd}small{color:#a9bbaa;letter-spacing:.12em}a,button{display:inline-block;padding:.72rem 1rem;border-radius:9px;border:1px solid #a7bd8d;background:#d6e6b8;color:#122519;text-decoration:none;font-weight:700;cursor:pointer}button{font:inherit}footer{font-size:.8rem;margin-top:1.7rem;color:#a9bbaa}</style></head><body><main class="card"><small>TIN FOIL FA CUP · HQ</small><h1>${escapeHtml(heading)}</h1>${body}<footer>MISSION CONTROL — The serious business of having fun.</footer></main></body></html>`;
  const h = new Headers(HEADERS);
  for (const [key, val] of Object.entries(extras)) h.set(key, val);
  return new Response(html, {status, headers:h});
}
function denied(message = 'Access not authorised.') {
  return page('Access restricted', `<p>${escapeHtml(message)}</p><p><a href="/login">Sign in with Google</a></p>`, 403);
}
function cookieValue(request, name) {
  const cookie = request.headers.get('Cookie') || '';
  for (const pair of cookie.split(';')) {
    const [key, ...val] = pair.trim().split('=');
    if (key === name) return val.join('=');
  }
  return null;
}
function setCookie(name, value, age) {
  return `${name}=${value}; Path=/; Max-Age=${age}; Secure; HttpOnly; SameSite=Lax`;
}
function clearCookie(name) { return setCookie(name, '', 0); }
function bytesToB64u(bytes) {
  return btoa(String.fromCharCode(...bytes)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}
function b64uToBytes(value) {
  if (!/^[A-Za-z0-9_-]+$/.test(value) || value.length > 20000) throw Error('Invalid encoding');
  const b64 = value.replace(/-/g, '+').replace(/_/g, '/');
  return Uint8Array.from(atob(b64 + '='.repeat((4 - b64.length % 4) % 4)), c => c.charCodeAt(0));
}
function asJson(bytes) { return JSON.parse(new TextDecoder().decode(bytes)); }
function randomString() { return bytesToB64u(crypto.getRandomValues(new Uint8Array(32))); }
function time() { return Math.floor(Date.now() / 1000); }
function equalStrings(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string' || a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}
async function sessionKey(env) {
  const encoded = env.SESSION_SECRET;
  if (typeof encoded !== 'string' || !/^[A-Za-z0-9+/]{43}=$/.test(encoded)) throw Error('Invalid server configuration');
  const bytes = Uint8Array.from(atob(encoded), c => c.charCodeAt(0));
  if (bytes.length !== 32) throw Error('Invalid server configuration');
  return crypto.subtle.importKey('raw', bytes, {name:'HMAC', hash:'SHA-256'}, false, ['sign', 'verify']);
}
async function signed(payload, key) {
  const data = bytesToB64u(new TextEncoder().encode(JSON.stringify(payload)));
  const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(data));
  return `${data}.${bytesToB64u(new Uint8Array(sig))}`;
}
async function checked(token, key, expectedKind) {
  if (typeof token !== 'string' || token.length > 4000) return null;
  const parts = token.split('.');
  if (parts.length !== 2) return null;
  try {
    const valid = await crypto.subtle.verify('HMAC', key, b64uToBytes(parts[1]), new TextEncoder().encode(parts[0]));
    if (!valid) return null;
    const value = asJson(b64uToBytes(parts[0]));
    if (value.kind !== expectedKind || value.aud !== BASE || !Number.isInteger(value.iat) ||
        !Number.isInteger(value.exp) || value.iat > time() + 30 || value.exp <= time()) return null;
    if (['oauth','gmail-oauth'].includes(expectedKind) && value.exp - value.iat !== FLOW_SECONDS) return null;
    if (expectedKind === 'session' && value.exp - value.iat !== SESSION_SECONDS) return null;
    return value;
  } catch { return null; }
}
async function pkceChallenge(verifier) {
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(verifier));
  return bytesToB64u(new Uint8Array(digest));
}
async function verifyGoogleIdToken(token, env, nonce) {
  if (typeof token !== 'string' || token.length > 10000) throw Error('Invalid ID token');
  const parts = token.split('.');
  if (parts.length !== 3) throw Error('Invalid ID token');
  const header = asJson(b64uToBytes(parts[0]));
  const claims = asJson(b64uToBytes(parts[1]));
  if (header.alg !== 'RS256' || typeof header.kid !== 'string') throw Error('Invalid token header');
  const r = await fetch('https://www.googleapis.com/oauth2/v3/certs', {headers:{'Accept':'application/json'}, redirect:'manual'});
  if (!r.ok) throw Error('Google keys unavailable');
  const json = await r.json();
  const jwk = (Array.isArray(json.keys) ? json.keys : []).find(k => k.kid === header.kid && k.kty === 'RSA' && (k.use === 'sig' || !k.use));
  if (!jwk) throw Error('Signing key not found');
  const key = await crypto.subtle.importKey('jwk', jwk, {name:'RSASSA-PKCS1-v1_5', hash:'SHA-256'}, false, ['verify']);
  const verified = await crypto.subtle.verify('RSASSA-PKCS1-v1_5', key, b64uToBytes(parts[2]), new TextEncoder().encode(`${parts[0]}.${parts[1]}`));
  if (!verified) throw Error('Invalid token signature');
  if (!['https://accounts.google.com','accounts.google.com'].includes(claims.iss) ||
      claims.aud !== env.GOOGLE_CLIENT_ID ||
      (claims.azp && claims.azp !== env.GOOGLE_CLIENT_ID) ||
      !Number.isInteger(claims.exp) || claims.exp <= time() ||
      !Number.isInteger(claims.iat) || claims.iat > time() + 60 || claims.iat < time() - 600 ||
      !equalStrings(claims.nonce, nonce) ||
      (claims.email_verified !== true && claims.email_verified !== 'true') ||
      typeof claims.sub !== 'string' || !claims.sub ||
      typeof claims.email !== 'string' || claims.email.toLowerCase() !== ALLOWED_EMAIL) throw Error('Unauthorised account');
  return {sub:claims.sub, email:ALLOWED_EMAIL};
}
async function login(env, key) {
  const state = randomString(), nonce = randomString(), verifier = randomString();
  const flow = await signed({kind:'oauth', aud:BASE, iat:time(), exp:time()+FLOW_SECONDS, state, nonce, verifier}, key);
  const url = new URL('https://accounts.google.com/o/oauth2/v2/auth');
  for (const [k,v] of Object.entries({
    response_type:'code', client_id:env.GOOGLE_CLIENT_ID, redirect_uri:CALLBACK,
    scope:'openid email', state, nonce, code_challenge:await pkceChallenge(verifier),
    code_challenge_method:'S256', prompt:'select_account', login_hint:ALLOWED_EMAIL,
  })) url.searchParams.set(k,v);
  return new Response(null, {status:302, headers:{...HEADERS, Location:url.toString(), 'Set-Cookie':setCookie(FLOW_COOKIE, flow, FLOW_SECONDS)}});
}
async function callback(request, env, key) {
  const url = new URL(request.url);
  const flow = await checked(cookieValue(request, FLOW_COOKIE), key, 'oauth');
  const queryState = url.searchParams.get('state');
  const code = url.searchParams.get('code');
  if (!flow || !equalStrings(flow.state, queryState) ||
      typeof flow.verifier !== 'string' || !/^[A-Za-z0-9_-]{43}$/.test(flow.verifier) ||
      typeof flow.nonce !== 'string' || !code || code.length > 4000 || url.searchParams.has('error')) {
    const response = denied('Google sign-in was cancelled or could not be verified.');
    response.headers.append('Set-Cookie', clearCookie(FLOW_COOKIE));
    return response;
  }
  // Cloudflare Workers does not implement redirect:'error'; use 'manual'
  // so redirects are never followed automatically, and 3xx fails the .ok check.
  // Diagnostics are intentionally restricted to fixed labels and Google error *codes*.
  // Never log a URL, user email, HTTP body, identity token, cookie, code, or secret.
  let phase = 'exchange';
  let reason = 'request_or_network_failure';
  try {
    const body = new URLSearchParams({code, client_id:env.GOOGLE_CLIENT_ID,
      client_secret:env.GOOGLE_CLIENT_SECRET, redirect_uri:CALLBACK,
      grant_type:'authorization_code', code_verifier:flow.verifier});
    const response = await fetch('https://oauth2.googleapis.com/token', {method:'POST',
      headers:{'Content-Type':'application/x-www-form-urlencoded','Accept':'application/json'},
      body:body.toString(), redirect:'manual'});
    if (!response.ok) {
      let oauthError = 'other';
      try {
        const reply = await response.json();
        if (['invalid_client','invalid_grant','invalid_request','unauthorized_client',
             'access_denied','unsupported_grant_type'].includes(reply?.error)) oauthError = reply.error;
      } catch { /* No response body or details appear in logs. */ }
      reason = `google_http_${response.status}_${oauthError}`;
      throw Error('Token exchange rejected');
    }
    phase = 'id_token';
    reason = 'unexpected_validation_failure';
    const tokens = await response.json();
    const identity = await verifyGoogleIdToken(tokens.id_token, env, flow.nonce);
    // Do NOT store or use Google's access_token/refresh_token in this sign-in-only pilot.
    const session = await signed({kind:'session', aud:BASE, iat:time(), exp:time()+SESSION_SECONDS,
      sub:identity.sub, email:identity.email}, key);
    const h = new Headers({...HEADERS, Location:BASE+'/'});
    h.append('Set-Cookie', clearCookie(FLOW_COOKIE));
    h.append('Set-Cookie', setCookie(SESSION_COOKIE, session, SESSION_SECONDS));
    return new Response(null, {status:303, headers:h});
  } catch (error) {
    if (phase === 'id_token') {
      const allowed = {
        'Invalid ID token': 'malformed_id_token',
        'Invalid token header': 'unsupported_id_token_header',
        'Google keys unavailable': 'google_keys_unavailable',
        'Signing key not found': 'google_signing_key_not_found',
        'Invalid token signature': 'invalid_id_token_signature',
        'Unauthorised account': 'id_token_claims_rejected',
      };
      reason = allowed[error?.message] || 'unexpected_validation_failure';
    }
    console.warn(`TFFAC_AUTH_PILOT phase=${phase} reason=${reason}`);
    const response = denied('Sign-in could not be validated. No access was granted.');
    response.headers.append('Set-Cookie', clearCookie(FLOW_COOKIE));
    return response;
  }
}

// On-demand, least-privilege Gmail read-only pilot. No refresh tokens, KV, DO, inbox writes or sending.
// The access token stays encrypted in a short-lived Secure, HttpOnly browser cookie.
async function gmailCryptoKey(env){
 const seed=new TextEncoder().encode('TFFAC_GMAIL_COOKIE_V1|'+env.SESSION_SECRET);
 const digest=await crypto.subtle.digest('SHA-256',seed);
 return crypto.subtle.importKey('raw',digest,{name:'AES-GCM'},false,['encrypt','decrypt']);
}
async function gmailSeal(value,env){
 const iv=crypto.getRandomValues(new Uint8Array(12));
 const payload=new TextEncoder().encode(JSON.stringify(value));
 const encrypted=await crypto.subtle.encrypt({name:'AES-GCM',iv},await gmailCryptoKey(env),payload);
 return 'v1.'+bytesToB64u(iv)+'.'+bytesToB64u(new Uint8Array(encrypted));
}
async function gmailOpen(request,env,session){
 const value=cookieValue(request,GMAIL_COOKIE);
 if(!value||value.length>3800||!value.startsWith('v1.'))return null;
 try{
  const parts=value.split('.');if(parts.length!==3)return null;
  const iv=b64uToBytes(parts[1]);if(iv.length!==12)return null;
  const decrypted=await crypto.subtle.decrypt({name:'AES-GCM',iv},await gmailCryptoKey(env),b64uToBytes(parts[2]));
  const v=asJson(new Uint8Array(decrypted));
  if(v.kind!=='gmail'||v.aud!==BASE||v.sub!==session.sub||!Number.isSafeInteger(v.exp)||v.exp<=time()+5||typeof v.token!=='string'||v.token.length>2700)return null;
  return v;
 }catch{return null;}
}
async function gmailGrantId(request){
 const input=new TextEncoder().encode('TFFAC_GMAIL_GRANT_ID|'+cookieValue(request,GMAIL_COOKIE));
 return bytesToB64u(new Uint8Array(await crypto.subtle.digest('SHA-256',input)));
}
function gmailJson(value,status=200){return Response.json(value,{status,headers:{'Cache-Control':'no-store, private','X-Content-Type-Options':'nosniff','Vary':'Cookie','Referrer-Policy':'no-referrer'}});}
async function gmailConnect(env,key,session){
 const state=randomString(),nonce=randomString(),verifier=randomString();
 const flow=await signed({kind:'gmail-oauth',aud:BASE,iat:time(),exp:time()+FLOW_SECONDS,state,nonce,verifier,sub:session.sub},key);
 const url=new URL('https://accounts.google.com/o/oauth2/v2/auth');
 for(const [k,v] of Object.entries({response_type:'code',client_id:env.GOOGLE_CLIENT_ID,redirect_uri:CALLBACK,
 scope:'openid email '+GMAIL_SCOPE,state,nonce,code_challenge:await pkceChallenge(verifier),code_challenge_method:'S256',
 access_type:'online',prompt:'select_account',login_hint:ALLOWED_EMAIL}))url.searchParams.set(k,v);
 return new Response(null,{status:302,headers:{...HEADERS,Location:url.toString(),'Set-Cookie':setCookie(GMAIL_FLOW_COOKIE,flow,FLOW_SECONDS)}});
}
async function gmailCallback(request,env,key,session,flow){
 const url=new URL(request.url),code=url.searchParams.get('code');
 if(!session||!flow||flow.sub!==session.sub||!equalStrings(flow.state,url.searchParams.get('state'))||
   typeof flow.verifier!=='string'||!/^[A-Za-z0-9_-]{43}$/.test(flow.verifier)||!code||code.length>4000||url.searchParams.has('error')){
  const r=denied('Gmail authorization could not be validated.');r.headers.append('Set-Cookie',clearCookie(GMAIL_FLOW_COOKIE));return r;
 }
 try{
  const form=new URLSearchParams({code,client_id:env.GOOGLE_CLIENT_ID,client_secret:env.GOOGLE_CLIENT_SECRET,
    redirect_uri:CALLBACK,grant_type:'authorization_code',code_verifier:flow.verifier});
  const response=await fetch('https://oauth2.googleapis.com/token',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded','Accept':'application/json'},body:form.toString(),redirect:'manual'});
  if(!response.ok)throw Error('Gmail authorization rejected');
  const data=await response.json();
  const identity=await verifyGoogleIdToken(data.id_token,env,flow.nonce);
  if(identity.sub!==session.sub||!String(data.scope||'').split(/\s+/).includes(GMAIL_SCOPE)||
     typeof data.access_token!=='string'||!data.access_token||data.access_token.length>2700||
     !Number.isFinite(data.expires_in)||data.expires_in<60)throw Error('Gmail scope/account mismatch');
  // No refresh_token requested or saved; expiry also bounded by authenticated dashboard session.
  const seconds=Math.max(30,Math.min(3500,Math.floor(data.expires_in)-45,session.exp-time()-5));
  if(seconds<30)throw Error('Session too close to expiry');
  const token=await gmailSeal({kind:'gmail',aud:BASE,sub:session.sub,exp:time()+seconds,token:data.access_token},env);
  if(token.length>3800)throw Error('Gmail cookie exceeds size limit');
  const headers=new Headers({...HEADERS,Location:BASE+'/'});
  headers.append('Set-Cookie',clearCookie(GMAIL_FLOW_COOKIE));
  headers.append('Set-Cookie',setCookie(GMAIL_COOKIE,token,seconds));
  return new Response(null,{status:303,headers});
 }catch{
  const r=denied('Gmail authorization failed. No mailbox access was granted.');
  r.headers.append('Set-Cookie',clearCookie(GMAIL_FLOW_COOKIE));return r;
 }
}
class GmailReadError extends Error {
 constructor(code,status=502){super(code);this.status=status;}
}
function gmailReadFailure(error){
 if(!(error instanceof GmailReadError))return gmailJson({error:'gmail_upstream'},502);
 // A read may finish after another tab reconnects. Only explicit actions may edit cookies.
 return gmailJson({error:error.message},error.status);
}
async function gmailFetch(token,path,params={}){
 const url=new URL('https://gmail.googleapis.com/gmail/v1/users/me/'+path);
 for(const [k,v] of Object.entries(params)){if(v)url.searchParams.set(k,String(v));}
 let response;
 try{response=await fetch(url,{headers:{Authorization:'Bearer '+token,Accept:'application/json'},redirect:'manual'});}
 catch{throw new GmailReadError('gmail_network');}
 if(response.status===401)throw new GmailReadError('gmail_grant_rejected',401);
 if(response.status===429)throw new GmailReadError('gmail_quota',429);
 if(response.status===403){
  let reason;
  try{reason=(await response.json())?.error?.errors?.[0]?.reason;}catch{}
  if(['rateLimitExceeded','userRateLimitExceeded','dailyLimitExceeded','quotaExceeded'].includes(reason)){
   throw new GmailReadError('gmail_quota',429);
  }
  throw new GmailReadError('gmail_permission',403);
 }
 if(!response.ok)throw new GmailReadError('gmail_upstream');
 try{return await response.json();}catch{throw new GmailReadError('gmail_upstream');}
}
function gmailPage(result,field,limit){
 const next=result?.nextPageToken??null;
 if(next!==null&&(typeof next!=='string'||!validGmailPageToken(next)||!next)){
  throw new GmailReadError('gmail_upstream');
 }
 const rows=result?.[field];
 // An omitted list is only usable when Gmail explicitly reports an empty result.
 if(rows===undefined&&result?.resultSizeEstimate===0&&next===null)return {rows:[],next};
 if(!Array.isArray(rows)||rows.length>limit||(!rows.length&&(next!==null||result.resultSizeEstimate>0))){
  throw new GmailReadError('gmail_upstream');
 }
 return {rows,next};
}
function validGmailPageToken(value){return value.length<=1400&&/^[A-Za-z0-9_\-+/=]*$/.test(value);}
function gmailPace(ms){return new Promise(resolve=>setTimeout(resolve,ms));}
function gmailDecodeHeader(value){
 // A number of older Outreach subjects use RFC 2047 UTF-8 encoded words (em dashes).
 return String(value||'').replace(/(=\?UTF-8\?[BQ]\?[^?]+\?=)\s+(?==\?UTF-8\?[BQ]\?)/gi,'$1').replace(/=\?UTF-8\?([BQ])\?([^?]+)\?=/gi,(_,encoding,payload)=>{
  try{
   if(encoding.toUpperCase()==='B')return new TextDecoder().decode(Uint8Array.from(atob(payload),c=>c.charCodeAt(0)));
   const str=payload.replace(/_/g,' ');const bytes=[];
   for(let i=0;i<str.length;i++){
    if(str[i]==='='&&/^[0-9a-f]{2}$/i.test(str.slice(i+1,i+3))){bytes.push(parseInt(str.slice(i+1,i+3),16));i+=2;}
    else bytes.push(str.charCodeAt(i));
   }
   return new TextDecoder().decode(Uint8Array.from(bytes));
  }catch{return '';}
 }).replace(/(\S)\s+(?=[^\s])/g,'$1 ');
}
function gmailHeader(message,name){const raw=String((message.payload?.headers||[]).find(h=>String(h.name).toLowerCase()===name.toLowerCase())?.value||'');return name.toLowerCase()==='subject'?gmailDecodeHeader(raw):raw;}
// Gmail MIME body data is base64url, and may contain trailing '=' padding.
// Do not change b64uToBytes: its strict validation protects login tokens and cookies.
function gmailDecodeBodyData(value){
 if(typeof value!=='string'||value.length<1||value.length>160000||
    !/^[A-Za-z0-9_-]+={0,2}$/.test(value))return '';
 const raw=value.replace(/=+$/,'');
 if(raw.length%4===1)return '';
 const b64=raw.replace(/-/g,'+').replace(/_/g,'/');
 try{
  const bytes=Uint8Array.from(atob(b64+'='.repeat((4-b64.length%4)%4)),c=>c.charCodeAt(0));
  return new TextDecoder().decode(bytes).slice(0,16000);
 }catch{return '';}
}
function gmailBodyText(payload){
 if(!payload)return '';
 if(payload.mimeType==='text/plain'&&typeof payload.body?.data==='string'){
  const body=gmailDecodeBodyData(payload.body.data);
  if(body)return body;
 }
 for(const part of payload.parts||[]){const t=gmailBodyText(part);if(t)return t;}
 return '';
}
function gmailClub(message,kind){
 const subject=gmailHeader(message,'Subject');
 if(kind==='classic'){
  if(/^(?:Re|Fwd):/i.test(subject.trim()))return null;
  const m=subject.match(/(?:^|[—-] )(.*?) on Tin Foil FA Cup [—-] (?:club details check|a quick introduction)$/i);
  if(!m)return null;
  return m[1].replace(/^For [^—]+ [—-] /,'').trim().slice(0,100);
 }
 if(subject.trim()!=='Keeping your club details up to date')return null;
 const body=gmailBodyText(message.payload);
 // New outreach uses 'Your current listing:' followed by 'Club NAME' (no colon).
 // Restrict extraction to that field, never an incidental sentence about a club.
 const listing=body.match(/(?:^|\n)[ \t]*Your current listing:[ \t]*\r?\n(?:[ \t]*\r?\n)*[ \t]*Club[ \t]*:?[ \t]+([^\r\n]+)/i)?.[1];
 // Older variants may greet the club's team; greetings to individuals are not club IDs.
 const greeting=body.match(/(?:^|\n)[ \t]*Hello[ \t]+([^\r\n,]{2,100}?)[ \t]+team[ \t]*,/i)?.[1];
 const club=(listing||greeting||'').trim();
 // Suspicious or empty values remain unparsed instead of becoming false club counts.
 if(!club||club.length>100||/^(?:your |the |a |if |is |we |our |club\b)/i.test(club))return null;
 return club;
}
async function gmailOutreach(request,token){
 const p=new URL(request.url).searchParams,kind=p.get('kind'),pageToken=p.get('page')||'';
 if(!['classic','current'].includes(kind)||!validGmailPageToken(pageToken))return gmailJson({error:'invalid_pagination'},400);
 const query=kind==='classic'?'in:sent subject:"on Tin Foil FA Cup" after:2026/10/01':'in:sent subject:"Keeping your club details up to date" after:2026/10/01';
 try{
  const page=gmailPage(await gmailFetch(token,'messages',{q:query,maxResults:'20',pageToken}),'messages',20);
  const ids=new Map();
  for(const entry of page.rows){
   if(typeof entry?.id==='string'&&/^[a-f0-9]{5,50}$/i.test(entry.id))ids.set(entry.id.toLowerCase(),entry.id);
  }
  const rows=[];
  const audit={listed:page.rows.length,fetched:ids.size,accepted:0,repliesSkipped:0,subjectSkipped:0,
    unparseable:0,bodiesMissing:0,idRejected:page.rows.length-ids.size};
  // Pace reads to keep paginated scans beneath the Gmail request budget.
  const format=kind==='classic'?'metadata':'full';
  const pauseMs=kind==='classic'?250:850;
  for(const id of ids.values()){
   await gmailPace(pauseMs);
   const message=await gmailFetch(token,'messages/'+encodeURIComponent(id),
     format==='metadata'?{format,metadataHeaders:'Subject'}:{format});
   const club=message&&gmailClub(message,kind);
   if(club){
    const date=new Date(Number(message.internalDate)||0);
    const day=Number.isFinite(date.valueOf())&&date.getTime()>0?new Intl.DateTimeFormat('en-CA',{timeZone:'Europe/London',year:'numeric',month:'2-digit',day:'2-digit'}).format(date):null;
    rows.push({club,day});audit.accepted++;
   }else{
    const subject=gmailHeader(message||{},'Subject').trim();
    if(/^(?:Re|Fwd):/i.test(subject))audit.repliesSkipped++;
    else if(!subject||(kind==='classic'?/on Tin Foil FA Cup/i.test(subject):/Keeping your club details up to date/i.test(subject))){
     audit.unparseable++;if(kind==='current'&&!gmailBodyText(message?.payload))audit.bodiesMissing++;
    }else audit.subjectSkipped++;
   }
  }
  return gmailJson({rows,next:page.next,audit});
 }catch(error){return gmailReadFailure(error);}
}
async function gmailDrafts(token){
 try{
  const page=gmailPage(await gmailFetch(token,'drafts',{q:'subject:"Keeping your club details up to date"',maxResults:'500'}),'drafts',500);
  return gmailJson({count:page.rows.length,complete:page.next===null});
 }catch(error){return gmailReadFailure(error);}
}
function signedIn(email) {
  return page('Welcome to Mission Control', `<p>Authenticated as <strong>${escapeHtml(email)}</strong>.</p><p>The entrance is working. Gmail has <strong>not</strong> been connected and no messages have been read.</p><p>Next: protect and serve the existing dashboard, then design separate Gmail authorisation and secure token storage.</p><form method="POST" action="/logout"><button type="submit">Sign out</button></form>`);
}
async function ombudsmanHealth(env){
  const unavailable=(reason,status=503)=>Response.json({state:'unknown',reason,checked_at:new Date(0).toISOString(),fresh:false,checks:{}},{status,headers:{'Cache-Control':'no-store, private','X-Content-Type-Options':'nosniff'}});
  if(!env?.OMBUDSMAN_SERVICE||!env?.OMBUDSMAN_STATUS_TOKEN)return unavailable('binding_or_token_not_configured');
  try{
    const response=await env.OMBUDSMAN_SERVICE.fetch(new Request('https://ombudsman.internal/health',{method:'GET',headers:{Authorization:'Bearer '+env.OMBUDSMAN_STATUS_TOKEN,Accept:'application/json'},redirect:'manual'}));
    if(!response.ok)return unavailable('ombudsman_http_'+response.status,502);
    const report=await response.json();
    const allowed=['healthy','warning','critical','pending','unknown'];
    if(!report||!allowed.includes(report.state)||!Number.isFinite(Date.parse(report.checked_at)))return unavailable('invalid_worker_report',502);
    const age=Date.now()-Date.parse(report.checked_at);
    // Ombudsman Cron is 20 * * * * (hourly at :20 UTC). Allow the full hour plus 30m of scheduling/processing tolerance.
    const fresh=age>=-120000&&age<=90*60000;
    const checks={};
    for(const name of ['results','draw']){
      const raw=report.checks?.[name]||{};
      const data={state:allowed.includes(raw.state)?raw.state:'unknown',reason:String(raw.reason||'not_reported').slice(0,70)};
      if(Number.isSafeInteger(raw.run_id))data.run_id=raw.run_id;
      if(Number.isFinite(raw.age_hours))data.age_hours=raw.age_hours;
      if(raw.catch_up&&typeof raw.catch_up.state==='string')data.catch_up={state:String(raw.catch_up.state).slice(0,30)};
      checks[name]=data;
    }
    return Response.json({source:'tffc-ombudsman',state:report.state,checked_at:report.checked_at,fresh,checks},{headers:{'Cache-Control':'no-store, private','X-Content-Type-Options':'nosniff','Vary':'Cookie'}});
  }catch{return unavailable('health_fetch_failed',502);}
}


// Radar artifact reader: authenticated private endpoint; no public or write access.
// A fine-grained GitHub token restricted to Actions:read on this repo is optional
// until the isolated Shed is explicitly configured. Never embed it in the dashboard.
const RADAR_OWNER='anvilspringstien', RADAR_REPO='tinfoilfacup';
const RADAR_API=`https://api.github.com/repos/${RADAR_OWNER}/${RADAR_REPO}`;
const RADAR_LIMIT=3500000;
function radarJson(payload,status=200){return Response.json(payload,{status,headers:{'Cache-Control':'no-store, private','Vary':'Cookie','X-Content-Type-Options':'nosniff'}})}
async function radarGithub(path,token){
 const url=RADAR_API+path;
 const response=await fetch(url,{headers:{Authorization:'Bearer '+token,Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'tffac-mission-control-radar'},redirect:'manual'});
 if(!response.ok)throw Error('github_http_'+response.status);
 return response.json();
}
function readU16(b,p){return b[p]|(b[p+1]<<8)}
function readU32(b,p){return (b[p]|b[p+1]<<8|b[p+2]<<16|b[p+3]<<24)>>>0}
// Inspect central directory and only extract the exact expected JSON member.
// No generic extraction, external filenames, redirects, or filesystem writes.
async function radarZipJson(buffer){
 const bytes=new Uint8Array(buffer);
 if(bytes.length>RADAR_LIMIT)throw Error('archive_too_large');
 let eocd=-1;for(let i=bytes.length-22;i>=Math.max(0,bytes.length-65557);i--){if(readU32(bytes,i)===0x06054b50){eocd=i;break}}
 if(eocd<0)throw Error('zip_directory_missing');
 const count=readU16(bytes,eocd+10),dirLength=readU32(bytes,eocd+12),dirOffset=readU32(bytes,eocd+16);
 if(count<1||count>8||dirOffset+dirLength>bytes.length)throw Error('zip_directory_invalid');
 let cursor=dirOffset,found=null;
 for(let i=0;i<count;i++){
  if(readU32(bytes,cursor)!==0x02014b50)throw Error('zip_entry_invalid');
  const flags=readU16(bytes,cursor+8),method=readU16(bytes,cursor+10),compressed=readU32(bytes,cursor+20),uncompressed=readU32(bytes,cursor+24),nameLen=readU16(bytes,cursor+28),extraLen=readU16(bytes,cursor+30),commentLen=readU16(bytes,cursor+32),offset=readU32(bytes,cursor+42);
  const next=cursor+46+nameLen+extraLen+commentLen;if(next>bytes.length)throw Error('zip_bounds');
  const name=new TextDecoder('utf-8',{fatal:true,ignoreBOM:false}).decode(bytes.subarray(cursor+46,cursor+46+nameLen));
  if(name==='club-entry-radar.json'){
   if(found||flags&1||![0,8].includes(method)||uncompressed>RADAR_LIMIT||compressed>RADAR_LIMIT)throw Error('zip_member_invalid');
   if(readU32(bytes,offset)!==0x04034b50)throw Error('zip_local_header_invalid');
   const start=offset+30+readU16(bytes,offset+26)+readU16(bytes,offset+28);
   if(start+compressed>bytes.length)throw Error('zip_data_bounds');
   found={method,compressed,uncompressed,start};
  }
  cursor=next;
 }
 if(!found)throw Error('radar_member_missing');
 const chunk=bytes.subarray(found.start,found.start+found.compressed);
 const decoded=found.method===0?chunk:new Uint8Array(await new Response(new Blob([chunk]).stream().pipeThrough(new DecompressionStream('deflate-raw'))).arrayBuffer());
 if(decoded.length!==found.uncompressed||decoded.length>RADAR_LIMIT)throw Error('radar_member_size');
 const text=new TextDecoder('utf-8',{fatal:true,ignoreBOM:false}).decode(decoded);
 return JSON.parse(text);
}
async function radarLatest(env){
 if(!env.GITHUB_RADAR_TOKEN)return radarJson({error:'radar_token_not_configured'},503);
 try{
  const token=env.GITHUB_RADAR_TOKEN;
  const data=await radarGithub('/actions/workflows/club-entry-radar.yml/runs?branch=main&status=success&per_page=20',token);
  const run=(data.workflow_runs||[]).find(x=>x.head_branch==='main'&&x.conclusion==='success'&&x.status==='completed'&&x.event==='workflow_dispatch');
  if(!run)return radarJson({error:'no_successful_main_dispatch'},503);
  const artifacts=await radarGithub('/actions/runs/'+run.id+'/artifacts?per_page=100',token);
  const artifact=(artifacts.artifacts||[]).find(x=>x.name==='club-entry-radar-readonly'&&!x.expired&&x.workflow_run?.id===run.id);
  if(!artifact)return radarJson({error:'report_artifact_missing_or_expired'},503);
  const zipURL=RADAR_API+'/actions/artifacts/'+artifact.id+'/zip';
  const redirect=await fetch(zipURL,{headers:{Authorization:'Bearer '+token,Accept:'application/vnd.github+json','User-Agent':'tffac-mission-control-radar'},redirect:'manual'});
  if(![302,307].includes(redirect.status))throw Error('artifact_download_http_'+redirect.status);
  const loc=redirect.headers.get('location');
  if(!loc||!/^https:\/\/[^/]+\.blob\.core\.windows\.net\//i.test(loc))throw Error('artifact_redirect_invalid');
  const archive=await fetch(loc,{redirect:'manual'});
  if(!archive.ok)throw Error('artifact_archive_http_'+archive.status);
  const body=await archive.arrayBuffer();
  if(body.byteLength>RADAR_LIMIT)throw Error('artifact_archive_too_large');
  const report=await radarZipJson(body);
  if(!report||report.schema_version!==1||report.read_only!==true||report.automatic_ground_promotion!==false||report.fixture_venues_used_as_home_grounds!==false||report.canonical_source!=='competition.json')throw Error('report_contract_invalid');
  return radarJson({report,provenance:{branch:'main',conclusion:'success',run_id:run.id,run_number:run.run_number,head_sha:run.head_sha,completed_at:run.updated_at,artifact_id:artifact.id}});
 }catch{return radarJson({error:'radar_source_unavailable'},502)}
}

export default {
  async fetch(request, env) {
    // One exact host. Prevent copies or preview domains from becoming accidental entrances.
    const url = new URL(request.url);
    if (url.origin !== BASE || request.method === 'OPTIONS') return denied();
    if (!env?.GOOGLE_CLIENT_ID || !env?.GOOGLE_CLIENT_SECRET || !env?.SESSION_SECRET) {
      return page('Locked for configuration', '<p>Missing authentication configuration. Access is denied.</p>', 503);
    }
    try {
      const key = await sessionKey(env);
      if (request.method === 'GET' && url.pathname === '/login') return login(env, key);
      if (request.method === 'GET' && url.pathname === '/oauth/callback') {
        const flow=await checked(cookieValue(request,GMAIL_FLOW_COOKIE),key,'gmail-oauth');
        if(flow&&equalStrings(flow.state,url.searchParams.get('state'))){
          const session=await checked(cookieValue(request,SESSION_COOKIE),key,'session');
          return gmailCallback(request,env,key,session,flow);
        }
        return callback(request, env, key);
      }
      if (request.method === 'GET' && url.pathname === '/gmail/connect') {
        const session=await checked(cookieValue(request,SESSION_COOKIE),key,'session');
        if(!session||session.email!==ALLOWED_EMAIL||!session.sub)return denied('Sign in to Mission Control before connecting Gmail.');
        return gmailConnect(env,key,session);
      }
      if (request.method === 'POST' && url.pathname === '/gmail/disconnect') {
        if(request.headers.get('Origin')!==BASE||request.headers.get('X-TFFAC-Action')!=='disconnect')return denied();
        const session=await checked(cookieValue(request,SESSION_COOKIE),key,'session');
        if(!session||session.email!==ALLOWED_EMAIL||!session.sub)return gmailJson({error:'sign_in_required'},401);
        const expected=request.headers.get('X-TFFAC-Gmail-Grant');
        if(expected&&expected!==await gmailGrantId(request))return gmailJson({error:'gmail_connection_changed'},409);
        const response=gmailJson({disconnected:true});
        response.headers.append('Set-Cookie',clearCookie(GMAIL_COOKIE));
        response.headers.append('Set-Cookie',clearCookie(GMAIL_FLOW_COOKIE));
        return response;
      }
      if (request.method === 'GET' && url.pathname.startsWith('/api/gmail/')) {
        const session=await checked(cookieValue(request,SESSION_COOKIE),key,'session');
        if(!session||session.email!==ALLOWED_EMAIL||!session.sub)return gmailJson({error:'sign_in_required'},401);
        const grant=await gmailOpen(request,env,session);
        if(!grant){
          const expired=!!cookieValue(request,GMAIL_COOKIE);
          const reason=expired?'gmail_grant_expired':'gmail_not_connected';
          const response=url.pathname==='/api/gmail/status'
            ?gmailJson(expired?{connected:false,reason}:{connected:false})
            :gmailJson({error:reason},401);
          return response;
        }
        const id=await gmailGrantId(request);
        if(url.pathname==='/api/gmail/status'){
          const response=gmailJson({connected:true});
          response.headers.set('X-TFFAC-Gmail-Grant',id);
          return response;
        }
        const expected=request.headers.get('X-TFFAC-Gmail-Grant');
        if(expected&&expected!==id)return gmailJson({error:'gmail_connection_changed'},409);
        if(url.pathname==='/api/gmail/outreach')return gmailOutreach(request,grant.token);
        if(url.pathname==='/api/gmail/drafts')return gmailDrafts(grant.token);
        return gmailJson({error:'not_found'},404);
      }
      if (request.method === 'POST' && url.pathname === '/logout') {
        if (request.headers.get('Origin') !== BASE) return denied();
        const result = new Response(null, {status:303, headers:{...HEADERS, Location:BASE+'/'}});
        result.headers.append('Set-Cookie', clearCookie(SESSION_COOKIE));
        result.headers.append('Set-Cookie', clearCookie(GMAIL_COOKIE));
        result.headers.append('Set-Cookie', clearCookie(GMAIL_FLOW_COOKIE));
        return result;
      }
      if (request.method === 'GET' && url.pathname === '/api/radar/latest') {
        const session=await checked(cookieValue(request, SESSION_COOKIE),key,'session');
        if(!session||session.email!==ALLOWED_EMAIL||!session.sub)return denied();
        return radarLatest(env);
      }
      if (request.method === 'GET' && url.pathname === '/api/ombudsman') {
        const session=await checked(cookieValue(request, SESSION_COOKIE),key,'session');
        if(!session||session.email!==ALLOWED_EMAIL||!session.sub)return denied();
        return ombudsmanHealth(env);
      }
      if (request.method === 'GET' && url.pathname === '/') {
        const session = await checked(cookieValue(request, SESSION_COOKIE), key, 'session');
        if (!session || session.email !== ALLOWED_EMAIL || typeof session.sub !== 'string' || !session.sub) return denied();
        return privateDashboard();
      }
      return denied();
    } catch {
      // Never expose tokens, config details, exception messages, or stack traces.
      return page('Access unavailable', '<p>Security checks could not be completed. Access remains denied.</p>', 503);
    }
  }
};
