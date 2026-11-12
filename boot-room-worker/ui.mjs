import {trophyMatIds} from './trophy-cabinet.mjs';

export const page="<!doctype html><html lang=\"en-GB\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><meta name=\"theme-color\" content=\"#171612\"><title>The Boot Room · Tin Foil FA Cup</title><link rel=\"stylesheet\" href=\"./room.css\"><script type=\"module\" src=\"./room.js\"></script></head><body><main id=\"workbench\" class=\"workbench\">\n<section id=\"entrance\" class=\"phone-shell entrance-shell\" aria-label=\"Boot Room entrance\" hidden><div class=\"entrance-content\">\n<div class=\"entrance-brand\"><a class=\"campaign-home\" href=\"https://tinfoilfacup.com/?view=campaign\" target=\"_top\">← My Campaign</a></div><header class=\"entrance-heading\"><div><h1>The Boot Room</h1></div><img src=\"https://tinfoilfacup.com/beta/tffc-splash-logo-q80.webp\" alt=\"Tin Foil FA Cup 2026–2027 crest\"></header>\n<p class=\"entrance-intro\">Get in. Get Talking. Football. The Cup. Travel. Pies. Whatever!</p>\n<section class=\"entrance-opening\" aria-label=\"Live room status\"><div class=\"entrance-door-line\"><span id=\"entrance-state\" class=\"room-sign closed\">CHECKING THE ROOM</span><button id=\"entrance-refresh\" class=\"hours\" type=\"button\">Check ↗</button></div><p id=\"entrance-next\">Checking the live room.</p><p id=\"entrance-feedback\" role=\"status\" aria-live=\"polite\"></p></section>\n<section id=\"door-chalkboard\" class=\"opening-advert\" aria-label=\"About the experimental opening\"><p class=\"chalk-label\">BARRY’S BOOT ROOM</p><h2>Still taking shape</h2><p class=\"chalk-round\">An experimental matchday chat</p><div class=\"chalk-next\">When the doors are open, come in from My Campaign and pull up a chair. If they’re closed, check back for the next opening.</div></section>\n<div class=\"landlord-card\"><img src=\"https://tinfoilfacup.com/beta/barry-air/assets/barry-crest.webp\" alt=\"Boot Room Barry\"><div><span>YOUR MODERATOR</span><strong>Boot Room Barry</strong></div></div>\n<a class=\"primary entrance-enter\" href=\"./chat\">Continue to the Boot Room <span aria-hidden=\"true\">→</span></a>\n\n<footer class=\"entrance-footer\"><span>Buy Tickets · Eat Pies · Drink Beer · Meet People</span></footer><button id=\"entrance-rules\" class=\"entrance-house-rules\" type=\"button\">House rules</button></div><p class=\"frame-caption\">THE BOOT ROOM · A TIN FOIL FA CUP ADVENTURE</p></section>\n<p id=\"chat-loading\" class=\"chat-loading\" role=\"status\" hidden>Checking the Boot Room…</p><section id=\"chat-shell\" class=\"phone-shell\" aria-label=\"The Boot Room\" hidden><div class=\"room\"><div id=\"room-scroll\" class=\"room-scroll\"><header class=\"room-header\"><div class=\"room-top\"><span>TIN FOIL FA CUP</span><button id=\"about\" class=\"icon-button\" aria-label=\"About the Boot Room\">ⓘ</button></div><div class=\"room-title\"><div><h2>The Boot Room</h2><p>Get in. Get talking.</p></div><img src=\"https://tinfoilfacup.com/beta/tffc-splash-logo-q80.webp\" alt=\"Tin Foil FA Cup 2026–2027 crest\"></div></header><div class=\"door-line\"><span id=\"doors\" class=\"room-sign closed\">CHAIRS UP FOR NOW</span><button id=\"connect\" class=\"hours\" type=\"button\">Reconnect ↗</button></div>\n<div class=\"occasion-strip\"><span>ONE CUP. PLENTY TO TALK ABOUT.</span></div><p id=\"status\" class=\"connection-status\" role=\"status\" aria-live=\"polite\">Checking the room…</p>\n<section id=\"join\" class=\"join-panel\" hidden><h3>There’s a chair for you.</h3><p>Come through My Campaign to join a walk-in opening.</p><div id=\"walk-in-entry\" hidden><p id=\"walk-in-hint\">Your Campaign details will appear beside your posts.</p><button type=\"button\" id=\"walk-in-join\" class=\"primary\">Join the chat</button></div><details><summary>Use a private invitation</summary><form id=\"join-form\"><label for=\"invite\">Your invitation code</label><input id=\"invite\" type=\"password\" required autocomplete=\"off\"><button class=\"primary\">Pull up a chair</button></form></details><p class=\"small-print\">Campaign details come from this browser and appear beside your posts.</p></section>\n<section id=\"room\" hidden><div id=\"messages\" class=\"messages\" role=\"log\" aria-label=\"Boot Room conversation\" aria-live=\"polite\"></div></section>\n<footer class=\"room-footer\"><button id=\"logout\" type=\"button\" hidden>Leave this device</button><a class=\"entrance-back\" href=\"./\">Entrance</a><a class=\"campaign-home\" href=\"https://tinfoilfacup.com/?view=campaign\" target=\"_top\">← My Campaign</a><button id=\"rules\" type=\"button\">House rules</button></footer></div><div id=\"composer-wrap\" class=\"composer-wrap\" hidden><div id=\"reply-preview\" class=\"reply-preview\" hidden><span id=\"reply\"></span><button id=\"cancel-reply\" type=\"button\" aria-label=\"Cancel reply\">×</button></div><form id=\"composer\"><label class=\"sr-only\" for=\"text\">Your message</label><textarea id=\"text\" rows=\"1\" maxlength=\"500\" placeholder=\"Got a story? Pull up a chair…\" required disabled></textarea><button id=\"send\" type=\"submit\" aria-label=\"Send message\" disabled><svg viewBox=\"0 0 24 24\" aria-hidden=\"true\"><path d=\"m4 12 16-8-5 16-3-6-8-2Zm8 2 8-10\"/></svg></button></form><div class=\"post-attachments\"><label id=\"attach-flight-row\" class=\"attach-flight-row\" hidden><input id=\"attach-flight\" type=\"checkbox\"> <span id=\"attach-flight-label\">Attach Flight Path</span></label><label id=\"attach-trophy-row\" class=\"attach-flight-row\" hidden><input id=\"attach-trophy\" type=\"checkbox\"> Attach Trophy Cabinet</label></div><div class=\"posting-line\"><span id=\"you\"></span><span id=\"counter\">0/500</span></div><p id=\"closed-composer\" class=\"closed-composer\">Room closed · reading is always welcome</p></div></div><p class=\"frame-caption\">THE BOOT ROOM · A TIN FOIL FA CUP ADVENTURE</p></section>\n<section id=\"admin\" class=\"landlord-panel\" hidden><p class=\"eyebrow\">TIN FOIL FA CUP · BEHIND THE BAR</p><h1>Landlord’s controls</h1><p id=\"admin-status\" role=\"status\" aria-live=\"polite\">Unlock the landlord’s controls.</p><form id=\"unlock-form\"><label for=\"password\">Boot Room admin password</label><input id=\"password\" type=\"password\" autocomplete=\"current-password\" required><button class=\"primary\">Unlock</button></form><div id=\"admin-controls\" hidden><div class=\"admin-toolbar\"><button id=\"refresh\">Refresh review</button><button id=\"lock\" class=\"quiet\">Lock</button><span id=\"review-time\"></span></div><section class=\"admin-group\"><h2>Room controls</h2><p id=\"admin-door-state\" role=\"status\"></p><form id=\"doors-form\"><label for=\"next\">Next opening text</label><input id=\"next\" maxlength=\"100\" value=\"Opening time to be announced\"><label for=\"hours\">Close after this many hours (maximum 16)</label><input id=\"hours\" type=\"number\" min=\"1\" max=\"16\" step=\"0.25\" value=\"1\"><label><input type=\"checkbox\" id=\"allow-walk-in\"> Let Campaign holders walk in</label><div><button name=\"open\" value=\"yes\">Open room</button><button name=\"open\" value=\"no\" class=\"quiet\">Close room</button></div></form></section><section class=\"admin-group\"><h2>Reports to review</h2><p id=\"reports\"></p><div id=\"report-queue\"></div></section>\n<section class=\"admin-group\"><h2>Door chalkboard</h2><p>Advertised times only. Use Room controls to open or close the chat.</p><form id=\"chalk-form\"><label for=\"chalk-title\">Round or opening title</label><input id=\"chalk-title\" maxlength=\"80\" required><label for=\"chalk-date\">Date</label><input id=\"chalk-date\" maxlength=\"80\" required><label for=\"chalk-hours\">Opening hours (UK time)</label><input id=\"chalk-hours\" maxlength=\"80\" required><label for=\"chalk-followingTitle\">Following opening (optional)</label><input id=\"chalk-followingTitle\" maxlength=\"80\"><label for=\"chalk-followingDetails\">Following opening details (optional)</label><input id=\"chalk-followingDetails\" maxlength=\"160\"><button type=\"submit\">Save chalkboard</button></form><h3>Preview</h3><div id=\"chalk-preview\" class=\"opening-advert\"></div></section>\n<section class=\"admin-group\"><h2>Conversation</h2><div id=\"review\"></div></section><section class=\"admin-group\"><h2>Who’s coming in?</h2><form id=\"invite-form\"><label for=\"name\">Tester’s pigeon name</label><input id=\"name\" maxlength=\"40\" required><label for=\"invite-call-sign\">Campaign Call Sign (optional)</label><input id=\"invite-call-sign\" maxlength=\"11\" placeholder=\"TF2AC 01922\"><label><input type=\"checkbox\" id=\"invite-moderator\"> Display Moderator badge</label><button>Create one-use invitation</button></form><label for=\"new-invite\">New invitation — copy privately</label><textarea id=\"new-invite\" readonly></textarea></section><section class=\"admin-group\"><h2>Invited pigeons</h2><div id=\"people\"></div><details><summary>Test usage</summary><pre id=\"usage\"></pre></details></section></div></section>\n</main><dialog id=\"info-dialog\" aria-labelledby=\"dialog-title\"><div class=\"dialog-heading\"><h2 id=\"dialog-title\" tabindex=\"-1\"></h2><button id=\"dialog-close\" aria-label=\"Close information\">×</button></div><div id=\"dialog-content\"></div><button id=\"dialog-done\" class=\"primary\">Back to the room</button></dialog><dialog id=\"flight-preview\" class=\"flight-preview\" aria-labelledby=\"flight-preview-title\"><h2 id=\"flight-preview-title\" class=\"sr-only\" tabindex=\"-1\" autofocus>Flight Path</h2><p id=\"flight-preview-status\" role=\"status\"></p><img id=\"flight-preview-image\" alt=\"Barry Air Flight Path with an approximate Home area\" hidden><div class=\"room-preview-actions\"><button id=\"flight-preview-close\" type=\"button\">Back to the room</button><button id=\"flight-preview-share\" type=\"button\" aria-label=\"Share or save flight path\" hidden><svg aria-hidden=\"true\" viewBox=\"0 0 24 24\" width=\"20\" height=\"20\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.7\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M12 15V3m-4 4 4-4 4 4M8 10H5v11h14V10h-3\"/></svg></button></div></dialog><dialog id=\"trophy-preview\" class=\"flight-preview trophy-preview\" aria-labelledby=\"trophy-preview-title\"><h2 id=\"trophy-preview-title\"></h2><p id=\"trophy-preview-count\"></p><ul id=\"trophy-preview-mats\" class=\"trophy-preview-mats\" aria-label=\"Earned Beer Mats\"></ul><div class=\"room-preview-actions\"><button id=\"trophy-preview-close\" type=\"button\" autofocus>Back to the room</button></div></dialog><dialog id=\"delete-own-dialog\" class=\"flight-preview\" aria-labelledby=\"delete-own-title\"><h2 id=\"delete-own-title\">Delete your message?</h2><p>This also removes any attachments.</p><button id=\"delete-own-cancel\" type=\"button\" autofocus>Cancel</button> <button id=\"delete-own-confirm\" type=\"button\">Delete message</button></dialog></body></html>\n";
export const style=":root{--ink:#171612;--panel:#11110f;--cream:#f5efdd;--gold:#d3b56a;--muted:#aba697;--teal:#084c61;--line:#757468;--paper:#eee9d9}*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 25% 20%,#28251d 0, #171612 50%);color:var(--cream);font:14px/1.5 Arial,sans-serif}button,input,textarea,select{font:inherit}button,a,select{touch-action:manipulation}button{cursor:pointer}button:focus-visible,a:focus-visible,select:focus-visible,textarea:focus-visible{outline:2px solid var(--gold);outline-offset:4px}button:disabled{cursor:default}button[hidden],[hidden]{display:none!important}.workbench{min-height:100svh;max-width:1050px;margin:auto;padding:30px 28px;display:grid;grid-template-columns:280px 450px;gap:95px;align-items:center;justify-content:center}.shed{padding-bottom:20px}.brand{display:flex;gap:12px;align-items:center;text-decoration:none;color:var(--cream);font-size:13px;font-weight:bold;letter-spacing:2px;line-height:1.4;margin-bottom:48px}.brand img{width:48px;height:48px}.eyebrow{font-size:10px;letter-spacing:2px;color:var(--gold);font-weight:bold;margin:0 0 9px}.shed h1{font:normal 43px/1.07 Georgia,serif;margin:16px 0 22px;letter-spacing:-1px}.intro{color:#b9b2a2;line-height:1.8;font-size:13px}.try-panel{border-top:1px solid #4f4939;margin-top:30px;padding-top:23px}.try-panel label{display:block;font-size:9px;letter-spacing:1.8px;color:var(--gold);margin:0 0 10px}.segmented{display:flex;border:1px solid #766b51;border-radius:8px;padding:3px;gap:3px;margin-bottom:23px}.segmented button{flex:1;color:#d3cbb7;background:none;border:0;border-radius:5px;padding:9px 6px;font-size:12px}.segmented button[aria-pressed=true]{background:var(--gold);color:#211b0f;font-weight:bold}select{width:100%;background:#222119;color:var(--cream);border:1px solid #625c4c;border-radius:7px;padding:10px}.quiet-button{border:0;background:none;color:#aaa391;font-size:11px;padding:17px 0 0}.demo-note{color:#9b9484;font-size:11px;line-height:1.7;margin-top:24px}.handwritten{font:italic 19px/1.5 Georgia,serif;color:#c8b47e;margin-top:32px}.phone-shell{width:450px;padding:9px 9px 0;border:1px solid #858277;border-radius:20px;background:#141410;box-shadow:0 24px 70px #0004}.room{display:flex;flex-direction:column;height:min(835px,calc(100svh - 84px));min-height:590px;overflow:hidden;border-radius:12px;background:var(--cream)}.room-header{flex:none;background:var(--panel);padding:14px 21px 13px;color:var(--cream)}.room-top{display:flex;align-items:center;justify-content:space-between;font-size:8px;letter-spacing:2px;color:#a9a38d;margin-bottom:13px}.icon-button{border:0;background:none;color:#bcb39c;font-size:17px;padding:1px 3px;line-height:1}.room-title{display:flex;justify-content:space-between;align-items:center;gap:12px}.room-title .eyebrow{font-size:8px;letter-spacing:1.8px;margin-bottom:5px}.room-title h2{font:normal 34px/1.08 Georgia,serif;letter-spacing:-1px;margin:0}.room-title p:last-child{font-size:11px;color:#b8b09d;margin:7px 0 0}.room-title img{width:67px;height:67px;flex:none}.door-line{display:flex;justify-content:space-between;align-items:center;border-top:1px solid #4d4735;padding-top:12px;margin-top:17px}.room-sign{font-size:9px;letter-spacing:1.5px;font-weight:bold;color:#a7c6b0;display:flex;gap:7px;align-items:center}.room-sign i{width:6px;height:6px;display:block;background:#83b091;border-radius:100%;box-shadow:0 0 9px #83b09150}.room-sign.closed{color:var(--gold)}.room-sign.closed i{background:var(--gold);box-shadow:none}.hours{background:none;border:0;color:#c8b778;padding:0;font-size:10px}.hours span{margin-left:3px}.occasion-strip{display:flex;justify-content:space-between;align-items:center;flex:none;background:var(--teal);padding:9px 18px;color:#eee9d8;font-size:8px;letter-spacing:1px}.occasion-strip span:last-child{color:#c3d5d6;font-size:9px;letter-spacing:0}.messages{flex:1;min-height:0;overflow-y:auto;overscroll-behavior:contain;padding:14px 13px 17px;scrollbar-width:thin;scrollbar-color:#b9b5a5 transparent;background-image:radial-gradient(#75694612 .7px,transparent .7px);background-size:13px 13px}.date-marker{text-align:center;color:#847e6b;font-size:9px;margin:0 auto 13px}.system-note{display:flex;align-items:center;justify-content:center;gap:7px;color:#857952;font-size:9px;margin-bottom:18px}.system-note:before,.system-note:after{content:'';width:24px;border-top:1px solid #c9b984}.message-row{display:flex;align-items:flex-end;gap:6px;margin:0 0 13px}.avatar{width:24px;height:24px;flex:none;display:grid;place-items:center;border-radius:50%;background:#ded7bb;color:#5f5a40;font:bold 10px Georgia,serif;border:1px solid #b6aa83}.avatar img{width:100%;height:100%;border-radius:50%}.avatar.blue{background:#c7dadd;color:#084c61;border-color:#9cb9bd}.avatar.rose{background:#e5d1c7;color:#765241;border-color:#c9afa1}.bubble{position:relative;background:#fffdf6;max-width:85%;border:1px solid #dcd5bf;border-radius:12px 12px 12px 3px;padding:9px 11px 6px;box-shadow:0 2px 3px #554a1c06;color:#2a332d}.campaign-ident{display:block;margin-top:2px;font-weight:400;overflow-wrap:anywhere}.sender{display:flex;align-items:baseline;gap:6px;flex-wrap:wrap;font-size:10px;color:#084c61;margin-bottom:4px;line-height:1.2}.sender strong{font-size:10px}.sender .call{font:8px/1.3 monospace;color:#8b897a}.custodian{display:block;color:#837b60;font-size:8px;margin-bottom:5px}.bubble p{font-size:12px;line-height:1.45;margin:0;white-space:pre-wrap;overflow-wrap:anywhere}.message-meta{display:flex;gap:11px;align-items:center;justify-content:flex-end;color:#9b9481;font-size:8px;margin-top:4px;min-height:16px}.message-meta button{border:0;background:none;padding:2px 0;color:#8b846f;font-size:9px}.message-meta button.liked{color:#bb4246}.message-row.own{justify-content:flex-end;padding-left:29px}.own .avatar{order:2}.own .bubble{background:#dfe9e6;border-color:#c2d3cc;border-radius:12px 12px 3px 12px;max-width:91%}.own .sender strong{color:#346657}.quote{border-left:2px solid #bba260;background:#d3c99f20;padding:6px 7px;margin:0 0 7px;font-size:10px;color:#6b6959}.quote strong{display:block;font-size:9px;margin-bottom:2px;color:#6d633e}.composer-wrap{flex:none;padding:10px 13px 9px;border-top:1px solid #d4ccaf;background:#eee8d5}form{display:flex;gap:8px;align-items:flex-end}textarea{resize:none;border:1px solid #c8c1a8;border-radius:9px;background:#fffdf7;width:100%;min-height:42px;max-height:85px;padding:11px 10px;font-size:11px;line-height:18px;color:#23382f}textarea::placeholder{color:#8c8878}#send{width:42px;height:42px;flex:none;border-radius:9px;background:var(--teal);border:1px solid #054052;display:grid;place-items:center}#send svg{width:19px;height:19px;fill:none;stroke:#f4efdf;stroke-width:1.5;stroke-linejoin:round}#send:disabled{opacity:.4}.posting-line{display:flex;align-items:center;gap:5px;color:#8b846e;font-size:8px;margin-top:7px}.posting-line strong{font-weight:bold;color:#5c6d5b}.tiny{width:15px;height:15px;font-size:8px}.own-call{font:8px monospace;color:#96907c}#counter{margin-left:auto;font:8px monospace}.closed-composer{text-align:center;color:#83764f;font-size:10px;padding:12px 0}.closed-composer span{margin-right:5px}.room-footer{display:flex;justify-content:space-between;padding:9px 17px;background:#141410;color:#817b67;font-size:7px;letter-spacing:1px}.room-footer button{background:none;border:0;color:#b0a17a;font-size:8px;padding:0;letter-spacing:0}.frame-caption{text-align:center;letter-spacing:1.5px;font-size:6px;color:#92896d;padding:8px;margin:0}.reply-preview{display:flex;align-items:center;justify-content:space-between;border-left:2px solid var(--gold);padding:6px 8px;margin-bottom:7px;background:#ded7be;color:#5b594a;font-size:10px}.reply-preview b,.reply-preview span{display:block}.reply-preview b span{display:inline}.reply-preview div>span{font-size:9px;max-width:310px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.reply-preview button{border:0;background:none;color:#6a614b;font-size:20px;padding:0 3px}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}dialog{border:1px solid #9f9474;border-radius:15px;background:var(--cream);color:#343b30;width:calc(100% - 32px);max-width:380px;padding:23px;box-shadow:0 20px 90px #0008}dialog::backdrop{background:#000a}.dialog-heading{display:flex;align-items:center;justify-content:space-between;gap:12px}.dialog-heading h2{font:27px Georgia,serif;margin:0;color:#153c43}.dialog-heading button{font-size:25px;background:none;border:0;color:#70694f;padding:0 5px}#dialog-content{font-size:12px;line-height:1.8;color:#635f4e;margin:17px 0}#dialog-content p{margin:10px 0}#dialog-content ul{padding-left:18px}#dialog-content .schedule{border-top:1px solid #d3c8a9;padding:10px 0;display:flex;justify-content:space-between;gap:10px;font-size:11px}.dialog-done{width:100%;background:var(--teal);color:var(--cream);border:0;padding:11px;border-radius:7px;font-size:12px}.toast{position:fixed;bottom:25px;left:50%;transform:translateX(-50%);background:#084c61;color:var(--cream);padding:12px 18px;border:1px solid #bba45d;border-radius:8px;font-size:12px;z-index:5;box-shadow:0 5px 30px #0005}\n@media(max-width:850px){.workbench{gap:40px;grid-template-columns:230px 430px;padding:20px}.phone-shell{width:430px}.shed h1{font-size:36px}}@media(max-width:700px){body{background:var(--ink)}.workbench{display:flex;flex-direction:column;padding:12px 9px;gap:12px}.shed{width:min(100%,440px);padding:0}.brand,.shed h1,.intro,.handwritten,.demo-note{display:none}.shed>.eyebrow{font-size:8px;letter-spacing:1.8px;text-align:center;margin-bottom:8px}.try-panel{border:0;margin:0;padding:0;display:grid;grid-template-columns:1fr 123px;gap:8px}.try-panel label,.quiet-button{display:none}.segmented{margin:0}.segmented button{padding:5px 3px;font-size:10px}.try-panel select{padding:6px;font-size:10px}.phone-shell{width:min(100%,440px);padding:6px 6px 0;border-radius:17px}.room{height:calc(100svh - 125px);min-height:480px}.room-header{padding:12px 17px}.room-title h2{font-size:31px}.room-title img{width:60px;height:60px}.room-top{margin-bottom:10px}.room-title p:last-child{margin-top:6px}.door-line{margin-top:13px;padding-top:10px}.messages{padding:13px 10px}.frame-caption{padding:6px;font-size:5px;letter-spacing:1.2px}.toast{bottom:12px;width:max-content;max-width:calc(100% - 30px)}}@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}\n.workbench{grid-template-columns:260px 450px;gap:80px}.landlord-card{display:flex;align-items:center;gap:12px;border-top:1px solid #4f4939;margin-top:26px;padding-top:24px}.landlord-card img{width:67px;height:67px}.landlord-card span{display:block;color:var(--gold);font-size:8px;letter-spacing:1.4px}.landlord-card strong{font:20px Georgia,serif}.landlord-card p{font-size:10px;color:#aba391;margin:5px 0}.test-note{font-size:10px;color:#aaa28e;line-height:1.7}.room{height:min(835px,calc(100dvh - 110px));min-height:520px}#room{display:contents}.connection-status{flex:none;margin:0;padding:5px 14px;background:#e7e0cb;color:#6e654a;font-size:9px;line-height:1.4;min-height:24px}.room-sign{font-size:8px;letter-spacing:1px}.room-sign:before{content:'';width:6px;height:6px;flex:none;background:#83b091;border-radius:50%}.room-sign.closed:before{background:var(--gold)}.join-panel{flex:1;padding:28px 24px;color:#38483e}.join-panel h3{font:25px Georgia,serif;margin:0 0 12px}.join-panel p{font-size:12px}.join-panel form{display:block}.join-panel label{display:block;font-size:11px;margin:22px 0 8px}.join-panel input{width:100%;font:16px Arial;padding:12px;border:1px solid #c7bfa6;background:#fffdf6;border-radius:8px}.primary{border:1px solid #054052;background:var(--teal);color:var(--cream);border-radius:8px;padding:12px 18px;min-height:44px}.join-panel .primary{margin-top:12px;width:100%}.small-print{color:#837b65;font-size:10px!important;line-height:1.7}.message-meta{flex-wrap:wrap;gap:12px}.message-meta button{min-height:28px;font-size:10px;padding:4px 0}.message-meta .report-button{margin-left:auto}.message-meta .reported{color:#396852;font-weight:bold;opacity:1}.message-feedback{color:#6f735d;font-size:9px;margin-top:4px}.removed .bubble{background:#e7e3d6;border-style:dashed;color:#847f70}.removed .bubble p{font-style:italic}.empty-room{text-align:center;font:18px/1.6 Georgia,serif;color:#8c8062;padding:30px 14px}.empty-room small{display:block;font:11px Arial;margin-top:8px}#text{font-size:16px;line-height:20px;padding:10px;max-height:100px}#text:disabled{background:#e7e2d2;color:#8b836e}#send{min-height:44px;min-width:44px}.posting-line{font-size:9px;line-height:1.5}.closed-composer{margin:0;padding:7px 0 0;font-size:10px}.reply-preview{gap:8px}.reply-preview>span{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:10px}.reply-preview button{flex:none;min-height:28px;min-width:28px}.room-footer{gap:10px;align-items:center}.room-footer>span{font-size:6px;text-align:center}.room-footer button{min-height:28px;font-size:9px}.landlord-view{display:block;max-width:740px}.landlord-view .shed,.landlord-view .phone-shell{display:none}.landlord-panel{border:1px solid var(--line);border-radius:16px;padding:28px;background:var(--panel);color:var(--cream)}.landlord-panel h1{font:32px Georgia,serif}.landlord-panel h2{font:23px Georgia,serif;margin-top:0}.landlord-panel form{display:block}.landlord-panel label{display:block;font-size:12px;margin:14px 0 7px}.landlord-panel input,.landlord-panel textarea{width:100%;border:1px solid #766e59;border-radius:8px;background:#f5efdd;color:#23382f;padding:11px;font-size:16px}.landlord-panel button{margin:10px 6px 0 0;border:1px solid #b79c5d;border-radius:7px;background:var(--gold);color:#201b10;padding:10px 14px;min-height:44px}.landlord-panel button.quiet{background:transparent;color:var(--cream);border-color:#716b5a}.admin-toolbar{display:flex;align-items:center;flex-wrap:wrap;gap:6px}.admin-toolbar span{font-size:10px;color:#c2b998;padding-top:8px}.admin-group{border-top:1px solid #4f4939;padding-top:22px;margin-top:25px}.admin-group article{background:#ece6d4;color:#2c443b;padding:14px;border-radius:8px;margin:12px 0;overflow-wrap:anywhere;white-space:pre-wrap}.admin-group article.reported-review{border-left:4px solid #b44c42}.admin-group details{font-size:11px;color:#b6ad98;margin-top:20px}#admin-status{font-size:12px;color:var(--gold)}#review-time{font-size:10px}#reports{color:var(--gold)}#dialog-content{font-size:13px}button:disabled{cursor:default;opacity:.55}.report-button.reported:disabled{opacity:1}input:focus-visible{outline:2px solid var(--gold);outline-offset:3px}\n@media(max-width:850px){.workbench{grid-template-columns:220px 430px;gap:35px}.landlord-card{gap:8px}.landlord-card img{width:55px;height:55px}.landlord-card strong{font-size:18px}}\n@media(max-width:700px){.workbench{padding:9px;gap:0;min-height:100dvh}.shed{display:none}.phone-shell{width:min(100%,450px)}.room{height:calc(100dvh - 54px);min-height:450px}.room-title h2{font-size:31px}.room-title img{width:63px;height:63px}.room-header{padding:12px 17px}.message-meta{gap:12px}.bubble p{font-size:14px;line-height:1.45}.sender strong{font-size:11px}.message-meta button{font-size:11px;min-height:32px}.messages{padding:13px 10px}.bubble{padding:10px 11px 6px;max-width:88%}.room-footer{padding:5px 12px}.landlord-view{padding:9px}.landlord-panel{padding:20px 16px}.landlord-panel h1{font-size:28px}.connection-status{font-size:9px}.room-sign{font-size:8px}.occasion-strip{font-size:7px}}\n\n/* One reading surface: decoration scrolls, room status stays in view. */\n.room-scroll{flex:1;min-height:0;overflow-y:auto;overscroll-behavior:contain;scrollbar-width:thin;scrollbar-color:#b9b5a5 transparent;position:relative}\n.room-header{padding-bottom:16px}.door-line{position:sticky;top:0;z-index:2;min-height:42px;margin:0;padding:10px 17px;border:0;border-bottom:1px solid #4d4735;background:var(--panel);color:var(--cream);gap:12px;box-shadow:0 2px 5px #0002}\n.room-sign{font-size:10px}.hours{font-size:12px;min-height:26px}.messages{overflow:visible;min-height:180px;flex:none}.composer-wrap{flex:none}.room-footer{gap:10px;align-items:center;min-height:44px}.room-footer button{font-size:11px;min-height:30px}.bubble p{font-size:15px}.sender strong{font-size:12px}.message-meta{font-size:10px}.message-meta button{font-size:12px;min-height:34px}.bubble{padding:10px 12px 7px}.posting-line{font-size:10px}.connection-status{font-size:11px}.occasion-strip{font-size:9px}\n@media(max-width:700px){.workbench{padding:8px 9px}.room{height:calc(100dvh - 48px);min-height:320px}.room-header{padding:12px 17px 16px}.room-footer>span{display:none}.room-footer{padding:7px 14px}.messages{padding:14px 10px 18px}.composer-wrap{padding:9px 10px}.room-title h2{font-size:29px}.room-title img{width:55px;height:55px}}\n\n/* One entrance and one room, with the same centred frame on every device. */\n.workbench{display:flex;justify-content:center;align-items:center;gap:0;max-width:none}.phone-shell{flex:none}.entrance-shell{min-height:min(835px,calc(100dvh - 70px));display:flex;flex-direction:column}.entrance-content{padding:25px 24px 18px;flex:1;display:flex;flex-direction:column}.entrance-brand{font-size:9px;letter-spacing:2px;color:var(--muted);margin:0 0 23px}.entrance-heading{display:flex;justify-content:space-between;align-items:center;gap:12px}.entrance-heading h1{font:normal 36px/1.08 Georgia,serif;letter-spacing:-1px;margin:0}.entrance-heading .eyebrow{font-size:9px}.entrance-heading>div>p:last-child{font-size:12px;color:#b8b09d;margin:8px 0 0}.entrance-heading img{width:74px;height:74px;flex:none}.entrance-welcome{margin:28px 0 0}.entrance-welcome h2{font:normal 24px/1.25 Georgia,serif;margin:0 0 9px}.entrance-welcome p{font-size:13px;line-height:1.8;color:#c2baaa;margin:0}.entrance-shell .landlord-card{margin-top:22px;padding-top:19px;gap:13px}.entrance-shell .landlord-card img{width:72px;height:72px}.entrance-shell .landlord-card strong{font-size:22px}.entrance-shell .landlord-card p{font-size:11px}.entrance-opening{border-top:1px solid #4f4939;border-bottom:1px solid #4f4939;padding:16px 0;margin:23px 0 20px}.entrance-door-line{display:flex;align-items:center;justify-content:space-between;gap:12px}.entrance-opening p{font-size:15px;line-height:1.5;margin:12px 0 0;overflow-wrap:anywhere}.entrance-opening #entrance-feedback{font-size:11px;color:#b1aa99;margin-top:6px;min-height:17px}.entrance-enter{display:flex;align-items:center;justify-content:space-between;text-decoration:none;font-size:15px;padding:13px 16px}.entrance-invite{font-size:10px;line-height:1.7;color:#aaa28e;margin:12px 0 20px}.entrance-footer{margin-top:auto;display:flex;gap:12px;justify-content:space-between;align-items:center;border-top:1px solid #4f4939;padding-top:13px}.entrance-footer>span{font:italic 12px/1.5 Georgia,serif;color:#c8b47e;max-width:235px}.entrance-footer button,.entrance-back{border:0;background:none;color:#b0a17a;font-size:11px;min-height:32px;padding:0;text-decoration:none}.entrance-back{display:flex;align-items:center}.landlord-view{display:block}.landlord-view .phone-shell{display:none}\n@media(max-width:700px){.workbench{display:flex;flex-direction:column;align-items:center;justify-content:center}.entrance-shell{min-height:calc(100dvh - 28px)}.entrance-content{padding:20px 17px 12px}.entrance-brand{margin-bottom:20px}.entrance-heading h1{font-size:32px}.entrance-heading img{width:65px;height:65px}.entrance-welcome{margin-top:23px}.entrance-welcome h2{font-size:23px}.entrance-shell .landlord-card img{width:65px;height:65px}.entrance-shell .landlord-card strong{font-size:21px}.entrance-opening{margin:20px 0 16px;padding:13px 0}.entrance-invite{margin-bottom:16px}}\n\n@media(max-width:700px){.entrance-content{padding:15px 17px 10px}.entrance-brand{margin-bottom:12px}.entrance-welcome{margin-top:16px}.entrance-welcome h2{font-size:22px;margin-bottom:7px}.entrance-welcome p{line-height:1.7}.entrance-shell .landlord-card{margin-top:16px;padding-top:12px}.entrance-shell .landlord-card img{width:60px;height:60px}.entrance-opening{margin:14px 0 12px;padding:10px 0}.entrance-opening p{margin-top:8px}.entrance-invite{margin:10px 0 12px}.entrance-footer{padding-top:9px}}\n\n/* Opening notice takes centre stage; one journey on phone and desktop. */\n.entrance-shell{min-height:0}.entrance-content{padding:22px 23px 16px}.entrance-brand{margin-bottom:17px}.entrance-heading h1{font-size:36px}.entrance-heading img{width:70px;height:70px}.entrance-intro{font-size:13px;line-height:1.7;color:#c9c2af;margin:14px 0 20px;padding-bottom:19px;border-bottom:1px solid #4f4939}.opening-advert{background:radial-gradient(ellipse at top,#24302a,#17231e);border:1px solid #817355;outline:1px solid #423f30;outline-offset:4px;border-radius:3px;padding:20px 17px 13px;text-align:center;color:#f4efdc;box-shadow:inset 0 0 35px #0003;margin:0 4px 22px}.chalk-label{font-size:9px;letter-spacing:2px;color:#d3c694;margin:0 0 13px}.chalk-opens{font:italic 21px/1.3 Georgia,serif;margin:0 0 6px}.chalk-opens strong{font-weight:normal;font-size:33px}.opening-advert h2{font:normal 27px/1.15 Georgia,serif;margin:0 0 5px;letter-spacing:-.5px}.chalk-round{font-size:13px;letter-spacing:1px;margin:8px 0 12px;color:#e0d5ae}.chalk-closes{font:italic 18px/1.4 Georgia,serif;margin:0 0 17px}.chalk-closes span{font-size:14px;margin-left:3px}.chalk-next{border-top:1px solid #74817380;padding-top:13px;font-size:12px;line-height:1.7;color:#d6d8c9}.chalk-next strong{font-weight:normal;color:#f4efdc}.chalk-zone{font-size:9px;color:#aeb7a7;margin:11px 0 0}.entrance-shell .landlord-card{border-top:1px solid #4f4939;margin:0 0 17px;padding-top:17px}.entrance-shell .landlord-card img{width:55px;height:55px}.entrance-shell .landlord-card strong{font-size:23px}.entrance-enter{font-size:15px}.sample-caption{font-size:10px;color:#aca58f;text-align:center;margin:9px 0 14px}.entrance-opening{margin:0 0 15px;padding:11px 0;border-top:0}.entrance-opening p{font-size:11px;margin:5px 0}.entrance-opening #entrance-feedback{font-size:10px;min-height:0;margin:4px 0}.entrance-opening .entrance-back{font-size:11px;min-height:28px}.entrance-footer{margin-top:0}.entrance-footer>span{font:italic 15px/1.6 Georgia,serif;max-width:none}.frame-caption{letter-spacing:1.4px}.sample-notice{font-size:12px;line-height:1.6;padding:14px 18px;background:#e8e1c8;color:#5a5648;margin:0}.demo-room .sender{display:flex;flex-wrap:wrap;align-items:baseline;gap:5px}.sample-call{font-size:9px;color:#7a7869}.sample-custodian{font-size:10px;color:#7a7869;margin-top:3px;overflow-wrap:anywhere}.demo-room .message-meta{justify-content:flex-end;gap:13px}.sample-heart{color:#aa7777}.sample-intro{font-size:11px;color:#81785d;text-align:center;padding:17px 12px 3px}.demo-room .room-footer{background:var(--panel)}.demo-room .room-footer a{font-size:12px;color:var(--gold);text-decoration:none}.demo-room .bubble{max-width:87%}.demo-room .bubble p{line-height:1.5}.sample-date{color:#827c68;font-size:10px;text-align:center;margin:0 0 20px}\n@media(max-width:700px){.entrance-shell{min-height:0}.entrance-content{padding:19px 17px 14px}.entrance-heading h1{font-size:32px}.entrance-heading img{width:62px;height:62px}.entrance-brand{margin-bottom:14px}.entrance-intro{font-size:12px;margin-bottom:18px}.opening-advert{padding:18px 13px 12px}.opening-advert h2{font-size:25px}.entrance-footer>span{font-size:14px}.entrance-shell .landlord-card img{width:52px;height:52px}.entrance-shell .landlord-card strong{font-size:22px}.entrance-opening p{font-size:11px}}\n\n/* Entrance fits one viewport; chat reading geometry is unchanged. */\n.entrance-shell{width:450px;height: min(740px,calc(100dvh - 40px));min-height:610px;padding:8px 8px 0;position:relative;box-shadow:0 24px 70px #0004}.entrance-content{padding:15px 19px 8px;gap:0;min-height:0}.entrance-brand{font-size:8px;margin-bottom:8px;letter-spacing:1.8px}.entrance-heading h1{font-size:34px;line-height:1.1}.entrance-heading img{width:58px;height:58px}.entrance-intro{font-size:10.2px;line-height:1.4;white-space:nowrap;margin:9px 0 10px;padding:0;border:0;color:#c9c2af}.entrance-opening{border:0;margin:0 0 13px;padding:10px 0 0;border-top:1px solid #4f4939}.entrance-door-line{gap:8px;justify-content:space-between}.entrance-opening .room-sign{font-size:17px;letter-spacing:1.2px;font-weight:700}.entrance-opening .hours{font-size:10px;min-height:24px}.entrance-opening p{font-size:10px;margin:3px 0 0}.entrance-opening p:empty{display:none}.entrance-opening #entrance-feedback{min-height:0;margin:3px 0 0;font-size:10px}.opening-advert{margin:0 4px 13px;padding:13px 13px 10px;flex:1;display:flex;flex-direction:column;justify-content:center;min-height:0}.chalk-label{font-size:8px;margin:0 0 5px;letter-spacing:1.7px}.chalk-opens{font-size:17px;margin:0 0 3px;line-height:1.2}.chalk-opens strong{font-size:28px}.opening-advert h2{font-size:23px;line-height:1.15;margin:0}.chalk-round{font:normal 27px/1.1 Georgia,serif;letter-spacing:-.4px;margin:7px 0 6px;color:#fff6d8}.chalk-closes{font-size:16px;margin:0 0 9px;line-height:1.3}.chalk-closes span{font-size:12px}.chalk-next{padding-top:8px;font-size:11px;line-height:1.5}.chalk-zone{font-size:8px;margin:5px 0 0}.entrance-shell .landlord-card{padding-top:10px;margin:0 0 10px;gap:10px;flex:none}.entrance-shell .landlord-card img{width:44px;height:44px}.entrance-shell .landlord-card span{font-size:8px}.entrance-shell .landlord-card strong{font-size:21px}.entrance-enter{padding:10px 14px;font-size:14px;min-height:42px}.sample-caption{font-size:9px;line-height:1.5;margin:5px 0 8px;color:#aaa28c}.sample-caption a{color:#c7ba8f;text-decoration:none;white-space:nowrap}.entrance-footer{border-top:1px solid #4f4939;padding-top:8px;margin-top:0;justify-content:center}.entrance-footer>span{font:italic 13px/1.4 Georgia,serif;white-space:nowrap;max-width:none}.entrance-house-rules{position:absolute;right:19px;top:13px;background:none;border:0;color:#aaa28c;font-size:9px;padding:0;min-height:20px}.entrance-shell .frame-caption{font-size:6px;margin:6px 0 9px;letter-spacing:1.2px;flex:none}\n@media(max-width:700px){.entrance-shell{width:min(100%,450px);height:calc(100dvh - 16px);min-height:600px}.entrance-content{padding:12px 15px 6px}.entrance-brand{margin-bottom:6px;font-size:7px}.entrance-heading h1{font-size:30px}.entrance-heading img{width:53px;height:53px}.entrance-intro{font-size:9px;margin:8px 0 9px}.entrance-opening{padding-top:8px;margin-bottom:12px}.entrance-opening .room-sign{font-size:16px}.opening-advert{padding:11px 10px 9px;margin-bottom:12px}.opening-advert h2{font-size:22px}.chalk-round{font-size:26px;margin:6px 0}.entrance-shell .landlord-card{padding-top:9px;margin-bottom:9px}.entrance-shell .landlord-card img{width:40px;height:40px}.entrance-shell .landlord-card strong{font-size:20px}.entrance-footer>span{font-size:12px}.entrance-footer{padding-top:7px}.entrance-house-rules{right:17px;top:10px;font-size:8px}}\n@media(max-height:620px){.entrance-shell{height:auto;min-height:600px}.opening-advert{flex:none}}\n\n.workbench:has(.entrance-shell:not([hidden])){padding:20px}@media(max-width:700px){.workbench:has(.entrance-shell:not([hidden])){padding:8px 9px}}\n\n@media(min-width:701px){.entrance-shell{height:calc(100dvh - 40px);max-height:940px}}\n\n/* Keep programmatic dialog focus quiet while retaining keyboard control outlines. */\n#dialog-title:focus{outline:none;box-shadow:none}#info-dialog h2,#info-dialog button{-webkit-tap-highlight-color:transparent}\n/* Equal 12px gaps around the entrance motto (caption margin + padding below). */\n.entrance-shell .entrance-content{padding-bottom:0}.entrance-shell .entrance-footer{padding-top:12px}\n\n/* A fixed trusted route uses the existing saved Campaign journey. */\n.campaign-home{color:#d1bd80;text-decoration:none;font-size:11px;line-height:1.4;display:inline-flex;align-items:center;min-height:32px}.campaign-home:hover{text-decoration:underline}.campaign-home:focus-visible{outline:2px solid #d1bd80;outline-offset:3px}.entrance-brand .campaign-home{font-size:10px;min-height:20px;letter-spacing:0}.entrance-brand{margin-top:-5px;margin-bottom:1px}.room-footer{flex-wrap:wrap;column-gap:12px;row-gap:0}.room-footer .campaign-home{font-size:11px}\n" + `
/* Match the visible Campaign card inside its 390 × 693 landscape frame. */
#door-chalkboard .chalk-label,#door-chalkboard .chalk-zone{font-size:10px}
#door-chalkboard .chalk-round{font-size:29px}
#door-chalkboard .chalk-opens{font-size:19px}
#door-chalkboard .chalk-closes{font-size:18px}
#door-chalkboard .chalk-next{font-size:13px}
/* Match the Campaign's 390 × 693 desktop composition. */
@media (min-width: 700px) and (pointer: fine) and (hover: hover) {
  #entrance, #chat-shell, .phone-shell.demo-room { width: min(100%, 56.25svh); }
}

@media (min-width: 700px) and (pointer: coarse) and (hover: none) {
  #entrance, #chat-shell, .phone-shell.demo-room { width: clamp(320px, 53.94dvh, 374px); }
}

#entrance, #chat-shell { container-type: inline-size; }
.entrance-shell .entrance-intro, .entrance-footer > span { white-space: normal; }

@container (max-width: 330px) {
  .entrance-shell .entrance-content { padding-inline: 12px; }
  .entrance-shell .entrance-heading h1 { font-size: clamp(22px, 10cqw, 30px); }
  .entrance-shell .entrance-heading img { width: 42px; height: 42px; }
  .entrance-door-line .room-sign { font-size: 12px; letter-spacing: 1px; }
  .entrance-door-line .hours { white-space: nowrap; }
  #door-chalkboard { padding-inline: 10px; }
  #door-chalkboard .chalk-round { font-size: 22px; }
  #door-chalkboard .chalk-opens, #door-chalkboard .chalk-closes { font-size: 15px; }
  #chat-shell .messages { padding-inline: 7px; }
  #chat-shell .message-row .bubble { max-width: calc(100% - 24px); min-width: 0; padding-inline: 8px; }
  #chat-shell .message-row .avatar { width: 18px; height: 18px; flex: 0 0 18px; }
  #chat-shell .bubble p { font-size: 14px; }
}

/* Keep the frame inside short browser windows, including desktop zoom. */
#entrance { min-height: 0; max-height: calc(100svh - 40px); overflow-y: auto; }
#entrance .entrance-content { flex-shrink: 0; }
@media (max-width: 700px) {
  #entrance { max-height: calc(100svh - 16px); }
}

/* The Shed shell sizes the canvas; these pages fill that canvas. */
html[data-frame="shed"], html[data-frame="shed"] body {
  height: 100%; overflow: hidden;
}
[data-frame="shed"] #workbench {
  --campaign-gutter: clamp(6px, 1.2vh, 13px);
  width: 100%; height: 100%; min-height: 0; padding: 0;
}
[data-frame="shed"] #entrance, [data-frame="shed"] #chat-shell {
  width: calc(100% - 2 * var(--campaign-gutter));
  height: calc(100% - 2 * var(--campaign-gutter));
  min-height: 0; max-height: none; max-width: 628px;
  border: 1px solid #818181; border-radius: 12px;
}
@media (min-width: 700px) {
  [data-frame="shed"] #entrance, [data-frame="shed"] #chat-shell { max-width: 550px; }
}
[data-frame="shed"] #entrance { overflow: auto; scrollbar-width: none; }
[data-frame="shed"] #chat-shell { display: flex; flex-direction: column; }
[data-frame="shed"] #chat-shell[hidden] { display: none; }
.chat-loading { align-self: center; justify-self: center; color: var(--muted); }
[data-frame="shed"] #chat-shell .room { flex: 1; min-height: 0; height: auto; }

.post-attachments{display:flex;flex-wrap:wrap;column-gap:12px}
.attach-flight-row[hidden]{display:none}
.attach-flight-row{display:flex;align-items:center;gap:6px;width:max-content;max-width:100%;min-height:30px;color:#335950;font-size:12px;cursor:pointer}
.attach-flight-row input{accent-color:#084c61}
.sender .view-attachment{border:0;background:none;color:#084c61;padding:2px 0;font-size:10px;text-decoration:underline;text-underline-offset:2px}
.flight-preview{width:min(440px,calc(100% - 24px));max-height:calc(100dvh - 24px);padding:12px;border:1px solid #b1aa91;border-radius:10px;background:#f5efdd;color:#273a32;text-align:center}
.flight-preview::backdrop{background:#0009}
.flight-preview h2:not(.sr-only){margin:0 0 6px;font-size:18px}
.flight-preview p:empty{display:none}
.flight-preview img{display:block;width:auto;max-width:100%;max-height:calc(100dvh - 120px);margin:0 auto 10px}
.flight-preview button{color:#084c61;min-height:32px}
.room-preview-actions{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);align-items:center;gap:8px}
.room-preview-actions button:first-child{grid-column:2;min-height:44px;padding-inline:12px;border:1px solid #b1aa91;border-radius:5px;background:#f5efdd}
#flight-preview-share{grid-column:3;justify-self:end;min-width:44px;min-height:44px;display:grid;place-items:center;border:0;background:transparent}
#flight-preview-share[hidden]{display:none}
#flight-preview-share:focus-visible{outline:2px solid #084c61;outline-offset:2px}
.trophy-preview{background:#1b1814;color:#f5efdd;border-color:#77684e}
.trophy-preview h2{overflow-wrap:anywhere}
.trophy-preview p{margin:4px 0 10px;color:#e0c99a}
.trophy-preview-mats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:0 auto 12px;padding:0;max-width:330px;list-style:none}
.trophy-preview-mats li{aspect-ratio:1;border:1px solid #554b3d;border-radius:9px;padding:4px;overflow:hidden}
.trophy-preview .trophy-preview-mats img{display:block;width:100%;height:100%;object-fit:contain;margin:0;max-height:none}
`;
export const script=`const $=id=>document.getElementById(id);let socket,me,replyTo=null,secret='',generation=0,pendingText=null,currentView=null,rendered=false,roomButtons=[];
const reportsInFlight=new Map();
if(location.hostname==='fix-boot-room-frame-return-20261106-tffac-boot-room-shed.anvilspringstien.workers.dev'){
 for(const link of document.querySelectorAll('.campaign-home'))link.href='https://tinfoilfacup.com/beta/phone-frame.html?view=campaign';
}
const roomPrefix=location.pathname.startsWith('/beta/boot-room/')?'/beta/boot-room':'';
const roomPath=location.pathname.slice(roomPrefix.length);
const frameMode=roomPrefix?new URLSearchParams(location.search).get('frame'):null;
const frameQuery=['shed','campaign'].includes(frameMode)?'frame='+frameMode:'';
const campaignHome=frameMode==='shed'?'/beta/phone-frame-shed.html?view=campaign&bootRoomFrame=1':roomPrefix?'/beta/phone-frame.html?view=campaign':'https://tinfoilfacup.com/?view=campaign';
if(roomPrefix)for(const link of document.querySelectorAll('.campaign-home'))link.href=campaignHome;
let campaign=null;
let campaignFragment='';
if((roomPath==='/'||roomPath==='/chat')&&location.hash?.startsWith('#campaign=')){
 const fragment=location.hash;
 const raw=fragment.slice('#campaign='.length);
 if(roomPath==='/chat')history.replaceState(null,'',location.pathname+location.search);
 try{campaign=JSON.parse(decodeURIComponent(raw));if(campaign?.callSign)campaignFragment=fragment;}catch{}
}
if(frameQuery||campaignFragment)for(const link of document.querySelectorAll('.entrance-back'))link.href=roomPrefix+'/'+(frameQuery?'?'+frameQuery:'')+campaignFragment;
function identityText(person){
 const c=person.campaign;
 if(!c)return '';
 return [c.callSign,person.moderator?'Moderator':'',c.custodian,c.fixture].filter(Boolean).join(' · ');
}
const status=text=>{$('status').hidden=!text;$('status').textContent=text;$('admin-status').textContent=text;};
async function api(path,body,admin=false){const r=await fetch(roomPrefix+path,{method:body?'POST':'GET',headers:body?{'content-type':'application/json',...(admin?{authorization:'Bearer '+secret}:{})}:{},body:body?JSON.stringify(body):undefined,cache:'no-store',redirect:'error'});const d=await r.json();if(!r.ok)throw Object.assign(Error(d.error||'Request failed'),{status:r.status});return d;}
function currentCampaignName(callSign){
 try{
  const saved=JSON.parse(localStorage.getItem('tinFoilFACupJourney_v7')||'null');
  const number=Number(saved?.searchNumber);
  if(saved?.originName&&!saved.ended&&Number.isSafeInteger(number)&&number>0&&callSign==='TF2AC '+String(number).padStart(5,'0')&&typeof saved.pigeonName==='string'){
   return saved.pigeonName.replace(/\\s+/g,' ').trim().slice(0,20)||'Pigeon '+callSign.slice(-5);
  }
 }catch{}
 return campaign?.callSign===callSign?campaign.name:null;
}
function joinCampaign(){return {...campaign,name:currentCampaignName(campaign.callSign)};}
function button(label,fn){const b=document.createElement('button');b.type='button';b.textContent=label;b.onclick=fn;return b;}
function send(a){if(!socketFresh||socket?.readyState!==WebSocket.OPEN||document.visibilityState==='hidden'){status('Reconnect before posting.');return false;}socket.send(JSON.stringify(a));return true;}
function currentFlightCache(){
 try{
  const saved=JSON.parse(localStorage.getItem('tinFoilFACupJourney_v7')||'null');
  const cached=JSON.parse(localStorage.getItem('tffc.barry.boot-flight.v1')||'null');
  if(!saved?.originName||saved.ended||!cached||cached.callSign!==me?.campaign?.callSign)return null;
  const key=[saved.originName,saved.postcode,saved.searchNumber,saved.selectedAt||''].join('|');
  return cached.identity===key&&cached.route?{...cached,origin:saved.originName}:null;
 }catch{return null;}
}
const trophyMatIds=${JSON.stringify(trophyMatIds)};
function currentTrophyCabinet(){
 const callSign=me?.campaign?.callSign;
 if(!callSign)return null;
 try{
  const saved=JSON.parse(localStorage.getItem('tinFoilFACupJourney_v7')||'null');
  const deck=JSON.parse(localStorage.getItem('tffc.challengeDeck.v1')||'null');
  const number=Number(saved?.searchNumber);
  if(!saved?.originName||saved.ended||!Number.isSafeInteger(number)||number<=0||
     callSign!=='TF2AC '+String(number).padStart(5,'0')||deck?.version!==1||!deck.completed)return null;
  // Use the same Campaign key as My Challenges so a previous Campaign cannot be shared.
  const savedCallSign=saved.callSign||'Tango Foxtrot 2 Alpha Charlie '+callSign.slice(-5);
  const key=[saved.originName.trim(),String(saved.selectedAt||savedCallSign).trim()].join('|');
  return deck.campaignKey===key?trophyMatIds.filter(id=>Boolean(deck.completed[id])):null;
 }catch{return null;}
}
function flightCacheNeedsRefresh(cache){
 return cache&&cache.version!==2&&!Number.isSafeInteger(cache.route.milesFlown);
}
let flightPreviewEpoch=0,flightPreviewURL,flightPreviewFile;
const flightPreview=$('flight-preview'),flightPreviewImage=$('flight-preview-image');
const flightPreviewShare=$('flight-preview-share'),flightPreviewStatus=$('flight-preview-status');
$('flight-preview-close').onclick=()=>flightPreview.close();
flightPreview.onclose=()=>{
 flightPreviewEpoch++;
 if(flightPreviewURL)URL.revokeObjectURL(flightPreviewURL);
 flightPreviewURL=flightPreviewFile=null;
 flightPreviewImage.removeAttribute('src');
 flightPreviewImage.hidden=flightPreviewShare.hidden=true;
};
flightPreviewShare.onclick=async()=>{
 if(!flightPreviewFile||!flightPreview.open)return;
 const epoch=flightPreviewEpoch,files=[flightPreviewFile];
 if(navigator.share&&navigator.canShare?.({files})){
  try{await navigator.share({files});return;}
  catch(error){if(error.name==='AbortError'||epoch!==flightPreviewEpoch||!flightPreview.open)return;}
 }
 const download=document.createElement('a');
 download.href=flightPreviewURL;
 download.download=flightPreviewFile.name;
 download.click();
};
async function viewFlightPath(message){
 const epoch=++flightPreviewEpoch;
 flightPreviewImage.hidden=flightPreviewShare.hidden=true;
 flightPreviewStatus.textContent='Unfolding the flight map…';
 flightPreview.showModal();
 try{
  const route=await api('/api/flight-path?post='+encodeURIComponent(message.id));
  const {bootRoomFlightImage}=await import(roomPrefix+'/flight-path-share.mjs?v=5');
  const {callSign,origin,custodian}=message.campaign||{};
  const author={name:message.name,callSign,origin,custodian};
  const blob=await bootRoomFlightImage(route,author);
  if(epoch!==flightPreviewEpoch||!flightPreview.open)return;
  flightPreviewFile=new File([blob],'barry-air-flight-path.png',{type:'image/png'});
  flightPreviewURL=URL.createObjectURL(blob);
  const mileage=Number.isSafeInteger(route.milesFlown)
   ? route.milesFlown.toLocaleString('en-GB')+' miles flown'
   : 'Miles flown unavailable';
  flightPreviewImage.alt=[author.name,callSign,mileage,origin&&'Campaign: '+origin,custodian&&'Custodian: '+custodian,'Barry Air Flight Path with an approximate Home area'].filter(Boolean).join(' · ');
  flightPreviewImage.src=flightPreviewURL;
  flightPreviewImage.hidden=flightPreviewShare.hidden=false;
  flightPreviewStatus.textContent='';
 }catch{
  if(epoch===flightPreviewEpoch&&flightPreview.open)flightPreviewStatus.textContent='This Flight Path is unavailable.';
 }
}
const trophyPreview=$('trophy-preview');
$('trophy-preview-close').onclick=()=>trophyPreview.close();
function viewTrophyCabinet(message){
 const ids=message.trophyCabinet;
 $('trophy-preview-title').textContent=message.name+'’s Trophy Cabinet';
 $('trophy-preview-count').textContent=ids.length+' of '+trophyMatIds.length+' completed';
 const grid=$('trophy-preview-mats');
 grid.replaceChildren();
 for(const id of ids){
  const tile=document.createElement('li'),img=document.createElement('img');
  img.alt='Beer Mat '+id;
  img.loading='lazy';
  img.decoding='async';
  img.src='https://tinfoilfacup.com/beta/assets/challenge-thumbs/mat-'+id+'-front.webp';
  tile.append(img);
  grid.append(tile);
 }
 trophyPreview.showModal();
}
const deleteDialog=$('delete-own-dialog');
let deletePostId=null;
$('delete-own-cancel').onclick=()=>deleteDialog.close();
$('delete-own-confirm').onclick=()=>{
 if(deletePostId&&send({type:'delete-own',id:deletePostId}))deleteDialog.close();
};
deleteDialog.onclose=()=>{deletePostId=null;};
function confirmDeletePost(id){
 deletePostId=id;
 deleteDialog.showModal();
}
function showChat(){
 $('chat-loading').hidden=true;
 $('chat-shell').hidden=false;
}
function render(d){
 me=d.you;currentView=d;$('join').hidden=true;$('room').hidden=false;$('logout').hidden=!me;
 $('doors').textContent=d.open?'ROOM OPEN · until '+new Date(d.until).toLocaleTimeString('en-GB',{hour:'2-digit',minute:'2-digit'}):'ROOM CLOSED';$('doors').className='room-sign'+(d.open?'':' closed');
 $('you').textContent=me?'Posting as '+me.name+(me.campaign?' · '+identityText(me):''):'';roomOpen=d.open;
 const list=$('messages'),scroller=$('room-scroll'),oldTop=scroller.scrollTop||0,nearBottom=!rendered||((scroller.scrollHeight||0)-oldTop-(scroller.clientHeight||0)<70);list.replaceChildren();roomButtons=[];
 if(!d.messages.length){const empty=document.createElement('p');empty.className='empty-room';empty.textContent='First in? Pick a good chair.';const note=document.createElement('small');note.textContent='The conversation will appear here.';empty.append(note);list.append(empty);}
 for(const m of d.messages){
  const row=document.createElement('article');row.className='message-row'+(me&&m.person===me.id?' own':'')+(m.deleted?' removed':'');
  const avatar=document.createElement('span');avatar.className='avatar'+(me&&m.person===me.id?' blue':'');avatar.textContent=m.name.slice(0,1).toUpperCase();avatar.setAttribute('aria-hidden','true');
  const bubble=document.createElement('div');bubble.className='bubble';const sender=document.createElement('div');sender.className='sender';const name=document.createElement('strong');name.textContent=m.name;sender.append(name);
  if(m.hasFlightPath&&!m.deleted){const view=button('View Flight Path',()=>viewFlightPath(m));view.className='view-attachment';sender.append(view);}
  if(m.trophyCabinet&&!m.deleted){const view=button('View Trophy Cabinet',()=>viewTrophyCabinet(m));view.className='view-attachment';sender.append(view);}
  if(m.campaign){const details=document.createElement('small');details.textContent=identityText(m);details.className='campaign-ident';sender.append(details);}
  bubble.append(sender);
  if(m.replyTo){const parent=d.messages.find(p=>p.id===m.replyTo),quote=document.createElement('div');quote.className='quote';const who=document.createElement('strong');who.textContent=parent?.name||'Earlier message';const excerpt=document.createElement('span');excerpt.textContent=parent?.text.slice(0,90)||'Earlier message is no longer available';quote.append(who,excerpt);bubble.append(quote);}
  const text=document.createElement('p');text.textContent=m.text;bubble.append(text);const meta=document.createElement('div');meta.className='message-meta';
  const time=document.createElement('time');time.textContent=new Date(m.at).toLocaleTimeString('en-GB',{hour:'2-digit',minute:'2-digit'});meta.append(time);
  if(me&&!m.deleted){
   const reply=button('Reply',()=>{replyTo=m.id;$('reply').textContent='Replying to '+m.name+' · '+m.text.slice(0,70);$('reply-preview').hidden=false;$('text').focus();});
   const heart=button((m.hearted?'♥ ':'♡ ')+m.hearts,()=>send({type:'heart',id:m.id,liked:!m.hearted}));heart.className=m.hearted?'liked':'';heart.setAttribute('aria-label',(m.hearted?'Remove heart from ':'Heart ')+m.name+'’s message');
   if(reportsInFlight.get(m.id)===m.reported)reportsInFlight.delete(m.id);
   const pending=reportsInFlight.has(m.id);
   const report=button(pending?'Sending…':m.reported?'Undo report':'Report',()=>{
    if(reportsInFlight.has(m.id))return;
    if(send({type:'report',id:m.id,reported:!m.reported})){
     reportsInFlight.set(m.id,!m.reported);report.textContent='Sending…';report.disabled=true;
     status(m.reported?'Withdrawing your report…':'Sending your report to the landlord…');
    }
   });
   report.className='report-button'+(m.reported?' reported':'');
   report.setAttribute('aria-label',m.reported?'Undo report on '+m.name+'’s message':'Report '+m.name+'’s message');
   meta.append(reply,heart,report);
   roomButtons.push({button:reply,requiresOpen:true},{button:heart,requiresOpen:true},{button:report,pending});
   if(m.person===me.id){
    const remove=button('Delete',()=>confirmDeletePost(m.id));
    remove.setAttribute('aria-label','Delete your message');
    meta.append(remove);
    roomButtons.push({button:remove});
   }
  }
  bubble.append(meta);if(m.reported&&!m.deleted){const receipt=document.createElement('div');receipt.className='message-feedback';receipt.textContent='Sent privately to the landlord.';bubble.append(receipt);}row.append(avatar,bubble);list.append(row);
 }
 availability();showChat();scroller.scrollTop=nearBottom?scroller.scrollHeight:oldTop;rendered=true;
}
let connectionEpoch=0,connecting=false,socketFresh=false,roomOpen=false;
const isRoom=()=>roomPath==='/chat';
const isEntrance=()=>roomPath==='/';
let entranceEpoch=0;
async function refreshEntrance(){
 if(!isEntrance()||document.visibilityState==='hidden')return;
 const epoch=++entranceEpoch;$('entrance-refresh').disabled=true;$('entrance-feedback').textContent='Checking the doors…';
 try{const d=await api('/api/doors');if(epoch!==entranceEpoch)return;
 if(d.chalkboard)paintChalkboard($('door-chalkboard'),d.chalkboard);
 $('entrance-state').textContent=d.open?'ROOM NOW OPEN':'ROOM NOW CLOSED';$('entrance-state').className='room-sign'+(d.open?'':' closed');
 $('entrance-next').textContent=d.open?'Open until '+new Date(d.until).toLocaleTimeString('en-GB',{hour:'2-digit',minute:'2-digit'})+' · Pull up a chair.':(d.next==='Opening time to be announced'?'':d.next);
 if(!campaignFragment){
 document.querySelector('.entrance-enter').textContent=d.walkIn?'Campaign holders: enter from My Campaign':d.open?'Invited pigeons: enter →':'Invited pigeons: read →';document.querySelector('.entrance-enter').href=d.walkIn?campaignHome:roomPrefix+'/chat'+(frameQuery?'?'+frameQuery:'');
 }
 $('entrance-feedback').textContent='';
 }catch(e){if(epoch!==entranceEpoch)return;$('entrance-state').textContent='STATUS UNAVAILABLE';$('entrance-state').className='room-sign closed';$('entrance-next').textContent='Please check the doors again.';$('entrance-feedback').textContent='We couldn’t check the room just now.';if(!campaignFragment)document.querySelector('.entrance-enter').textContent='Go to the Boot Room →';}
 finally{if(epoch===entranceEpoch)$('entrance-refresh').disabled=false;}
}
const refreshPage=()=>isEntrance()?refreshEntrance():connect();
function availability(){$('composer-wrap').hidden=!me||!roomOpen;const live=socketFresh&&socket?.readyState===WebSocket.OPEN&&document.visibilityState!=='hidden',enabled=live&&roomOpen;$('send').disabled=!enabled;$('text').disabled=!enabled;const cache=currentFlightCache(),needsRefresh=flightCacheNeedsRefresh(cache);$('attach-flight-row').hidden=!cache;$('attach-flight-label').textContent=needsRefresh?'Reopen Barry Air to refresh your Flight Path.':'Attach Flight Path';$('attach-flight').disabled=!enabled||!cache||!!needsRefresh;if(!cache||needsRefresh)$('attach-flight').checked=false;
 const cabinet=currentTrophyCabinet();
 $('attach-trophy-row').hidden=!cabinet;
 $('attach-trophy').disabled=!enabled||!cabinet;
 if(!cabinet)$('attach-trophy').checked=false;
 for(const c of roomButtons)c.button.disabled=!live||(c.requiresOpen&&!roomOpen)||!!c.pending;$('closed-composer').hidden=enabled;$('closed-composer').textContent=live?'Room closed · reading is always welcome':'Connection paused · your draft stays here';}
function disconnect(){connectionEpoch++;connecting=false;socketFresh=false;reportsInFlight.clear();const old=socket;socket=null;old?.close();availability();if(me)$('doors').textContent='CONNECTION PAUSED · room status needs checking';}
async function connect(enterFromChalkboard=false){
 if(!isRoom()||document.visibilityState==='hidden'||connecting)return;
 disconnect();connecting=true;const epoch=connectionEpoch;let joined=false;status('Checking the room…');
 try{
  let d=await api('/api/state');if(epoch!==connectionEpoch)return;
  if(campaign&&d.you.campaign?.callSign!==campaign.callSign){
   $('logout').hidden=false;
   showChat();
   status('This browser is already signed into the room. Leave that session to join with this Campaign.');
   return;
  }
  if(roomPrefix&&d.you.walkIn){
   const callSign=d.you.campaign.callSign;
   const name=currentCampaignName(callSign);
   if(name&&name!==d.you.name){
    d=await api('/api/campaign-name',{callSign,name});
    if(epoch!==connectionEpoch)return;
   }
  }
  render(d);
  const ws=new WebSocket(location.origin.replace(/^http/,'ws')+roomPrefix+'/api/socket');socket=ws;
  ws.onopen=()=>{if(socket===ws)status('Connected. Checking the latest room status…');};
  ws.onmessage=e=>{
   if(socket!==ws||epoch!==connectionEpoch)return;
   const data=JSON.parse(e.data);
   if(data.type==='snapshot'){socketFresh=true;render(data);status(data.open?'Connected to the Boot Room.':'');}
   else if(data.type==='ack'){if(data.action==='report'){reportsInFlight.delete(data.id);if(currentView)render(currentView);}if(data.action==='message'&&$('text').value===pendingText){$('text').value='';replyTo=null;$('reply').textContent='';$('reply-preview').hidden=true;pendingText=null;$('attach-flight').checked=false;$('attach-trophy').checked=false;$('counter').textContent='0/500';}status(data.action==='report'?(data.reported?'Report received by the landlord.':'Report withdrawn.'):data.action==='delete-own'?'Message deleted.':'Delivered.');}
   else {reportsInFlight.clear();if(currentView)render(currentView);status(data.error);}
  };
  ws.onclose=()=>{if(socket!==ws)return;disconnect();status('Connection closed. Reconnect when ready.');};
  ws.onerror=()=>{if(socket!==ws)return;disconnect();status('Connection unavailable. Try reconnecting.');};
 }catch(e){
  if(epoch!==connectionEpoch)return;
  if(!campaign||e.status!==401){
   if(!me){$('room').hidden=true;$('join').hidden=false;}
   showChat();
   status(e.message);
   return;
  }
  try{
   const doors=await api('/api/doors');
   if(epoch!==connectionEpoch)return;
   $('walk-in-join').disabled=!doors.walkIn;
   if(enterFromChalkboard===true&&doors.open&&doors.walkIn){
    $('walk-in-join').disabled=true;
    try{await api('/api/walk-in',{campaign:joinCampaign()});joined=true;}
    finally{if(epoch===connectionEpoch)$('walk-in-join').disabled=false;}
    return;
   }
   if(roomPrefix&&!doors.open){
    const history=await api('/api/read-closed');
    if(epoch!==connectionEpoch)return;
    render(history);
    status('');
    return;
   }
   $('room').hidden=true;$('join').hidden=false;
   $('doors').textContent=doors.open?'ROOM OPEN':'ROOM CLOSED';
   showChat();
   status(doors.walkIn?'Walk-ins are open. Join as your Campaign pigeon.':doors.open?'Walk-ins are currently closed.':'The Boot Room is closed. Check the chalkboard for the next opening.');
  }catch(error){
   if(epoch!==connectionEpoch)return;
   if(!me){$('room').hidden=true;$('join').hidden=false;}
   showChat();
   status(error.message);
  }
 }
 finally{if(epoch===connectionEpoch){connecting=false;if(joined)await connect();}}
}
async function joinWalkIn(){
 const button=$('walk-in-join');button.disabled=true;
 try{await api('/api/walk-in',{campaign:joinCampaign()});await connect();}
 catch(e){status(e.message);}
 finally{button.disabled=false;}
}
$('walk-in-join').onclick=joinWalkIn;
if($('join-form'))$('join-form').onsubmit=async e=>{e.preventDefault();try{await api('/api/join',{invite:$('invite').value.trim(),campaign});$('invite').value='';await connect();}catch(x){status(x.message);}};
$('connect').onclick=connect;$('logout').onclick=async()=>{disconnect();me=null;roomOpen=false;await api('/api/logout',{});$('room').hidden=true;$('join').hidden=false;$('logout').hidden=true;$('composer-wrap').hidden=true;status('This device has left. You can join again from My Campaign when walk-ins are open.');};
$('composer').onsubmit=e=>{e.preventDefault();const cache=$('attach-flight').checked?currentFlightCache():null;
 const flightPath=cache&&!flightCacheNeedsRefresh(cache)?cache.route:null;
 if($('attach-flight').checked&&!flightPath){status('Reopen Barry Air to refresh your Flight Path.');return;}
 const message={type:'message',text:$('text').value,replyTo};
 if(flightPath){
  message.flightPath=flightPath;
  if(!me.campaign.origin)message.campaignOrigin=cache.origin;
 }
 if($('attach-trophy').checked){
  const trophyCabinet=currentTrophyCabinet();
  if(!trophyCabinet){status('Reopen My Challenges to refresh your Trophy Cabinet.');return;}
  message.trophyCabinet=trophyCabinet;
 }
 if(flightPath&&JSON.stringify(message).length>4096){status(message.trophyCabinet?'These attachments are too large to send together.':'This Flight Path is too large to attach. You can send the message without it.');return;}
 pendingText=message.text;send(message);};
$('cancel-reply').onclick=()=>{replyTo=null;$('reply').textContent='';$('reply-preview').hidden=true;};
$('text').oninput=()=>{$('counter').textContent=$('text').value.length+'/500';$('text').style.height='auto';$('text').style.height=Math.min($('text').scrollHeight,100)+'px';};
function lock(){chalkDirty=false;generation++;secret='';$('password').value='';$('new-invite').value='';$('admin-controls').hidden=true;$('unlock-form').hidden=false;for(const id of ['people','reports','report-queue','review','usage','review-time'])$(id).replaceChildren();}
async function admin(a){const g=generation;const d=await api('/api/admin',a,true);if(g!==generation)throw Error('Landlord view locked');return d;}
const chalkFields=['title','date','hours','followingTitle','followingDetails'];
let chalkDirty=false;
const ukTime=ms=>new Date(ms).toLocaleString('en-GB',{timeZone:'Europe/London',dateStyle:'medium',timeStyle:'short'});
function paintChalkboard(host,board){
 const line=(tag,text,className)=>{
  const el=document.createElement(tag);el.textContent=text;el.className=className;host.append(el);
 };
 host.replaceChildren();
 line('p','BARRY’S NEXT OPENING','chalk-label');
 line('h2',board.title||'Still taking shape','chalk-round');
 if(board.date)line('p',board.date,'chalk-opens');
 if(board.hours)line('p',board.hours+' UK time','chalk-closes');
 if(board.followingTitle)line('p','Coming up: '+board.followingTitle,'chalk-next');
 if(board.followingDetails)line('p',board.followingDetails,'chalk-zone');
}
function chalkValues(){return Object.fromEntries(chalkFields.map(key=>[key,$('chalk-'+key).value.trim()]));}
function paintQueue(d){
 const queue=$('report-queue');queue.replaceChildren();
 const grouped=new Map();
 for(const report of d.reports){
  const entries=grouped.get(report.message)||[];
  entries.push(report);grouped.set(report.message,entries);
 }
 $('reports').textContent=grouped.size?grouped.size+' post(s) to review':'No reports to review.';
 for(const [id,reports] of grouped){
  const message=d.messages.find(m=>m.id===id);
  if(!message||message.deleted)continue;
  const card=document.createElement('article');card.className='reported-review';
  const summary=document.createElement('strong');summary.textContent=message.name+' · '+reports.length+' report(s)';
  const excerpt=document.createElement('p');excerpt.textContent=message.text;
  const when=document.createElement('p');when.textContent='Latest report: '+ukTime(Math.max(...reports.map(r=>r.at)));
  card.append(summary,excerpt,when,button('Dismiss reports',()=>moderate({type:'dismiss-reports',id})),button('Remove post',()=>moderate({type:'delete',id})));
  queue.append(card);
 }
}
$('chalk-form').oninput=()=>{chalkDirty=true;paintChalkboard($('chalk-preview'),chalkValues());};
$('chalk-form').onsubmit=async e=>{
 e.preventDefault();
 const submit=e.submitter;
 submit.disabled=true;
 try{await admin({type:'chalkboard',board:chalkValues()});chalkDirty=false;await review();status('Chalkboard saved.');}
 catch(error){status(error.message);}
 finally{submit.disabled=false;}
};
async function review(){const d=await admin({type:'status'});
 $('admin-door-state').textContent=d.open?'Open until '+ukTime(d.until)+(d.walkIn?' · Walk-ins enabled':''):'Room closed';
 if(!chalkDirty){
  for(const key of chalkFields)$('chalk-'+key).value=d.chalkboard?.[key]||'';
  paintChalkboard($('chalk-preview'),d.chalkboard||{});
 }
 paintQueue(d);$('unlock-form').hidden=true;$('admin-controls').hidden=false;$('usage').textContent=JSON.stringify(d.usage,null,2);$('people').replaceChildren();for(const p of d.people){const row=document.createElement('p');row.textContent=p.name+(p.callSign?' · '+p.callSign:'')+(p.suspended?' · suspended':'');if(p.suspended&&p.walkIn)row.append(button('Lift suspension',()=>moderate({type:'reinstate',id:p.id})));if(!p.suspended)row.append(button('Suspend',()=>moderate({type:'suspend',id:p.id})));$('people').append(row);}$('review').replaceChildren();for(const m of d.messages){const a=document.createElement('article');a.textContent=m.name+': '+m.text;if(d.reports.some(r=>r.message===m.id)){a.prepend(document.createTextNode('REPORTED · '));a.className='reported-review';}if(!m.deleted)a.append(button('Remove message',()=>moderate({type:'delete',id:m.id})));$('review').append(a);}$('review-time').textContent='Checked '+new Date().toLocaleTimeString('en-GB');status('Landlord view updated.');}
async function moderate(a){try{await admin(a);await review();}catch(e){status(e.message);}}
$('unlock-form').onsubmit=async e=>{e.preventDefault();secret=$('password').value;$('password').value='';try{await review();}catch(x){lock();status(x.message);}};
$('refresh').onclick=async()=>{const b=$('refresh');b.disabled=true;b.textContent='Checking…';status('Checking reports and conversation…');try{await review();}catch(e){status(e.message);}finally{b.disabled=false;b.textContent='Refresh review';}};$('lock').onclick=lock;
$('invite-form').onsubmit=async e=>{e.preventDefault();const g=generation;try{const d=await api('/api/invite',{name:$('name').value,callSign:$('invite-call-sign').value.trim().toUpperCase(),moderator:$('invite-moderator').checked},true);if(g!==generation)return;$('new-invite').value=d.invite;await review();status('Invitation created. Share privately; it works once.');}catch(x){status(x.message);}};
$('doors-form').onsubmit=e=>{e.preventDefault();moderate({type:'doors',open:e.submitter.value==='yes',until:Date.now()+Number($('hours').value)*3600000,next:$('next').value,walkIn:$('allow-walk-in').checked});};
window.addEventListener('pagehide',()=>{entranceEpoch++;disconnect();lock();});window.addEventListener('pageshow',e=>{if(e.persisted){lock();refreshPage();}});
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden'){entranceEpoch++;if(isRoom())disconnect();}else refreshPage();});
window.addEventListener('offline',()=>{if(isRoom()){disconnect();showChat();status('Offline · your draft is kept here.');}if(isEntrance()){entranceEpoch++;$('entrance-state').textContent='OFFLINE · STATUS NEEDS CHECKING';$('entrance-refresh').disabled=false;}});window.addEventListener('online',refreshPage);
const info=(title,text)=>{$('dialog-title').textContent=title;$('dialog-content').textContent=text;$('info-dialog').showModal();$('dialog-title').focus({preventScroll:true});};
$('about').onclick=()=>info('Boot Room Barry','A little football. A little company. A disproportionate amount of pie talk. The landlord opens the room around the action. When the doors close, you can still read and report messages.');
$('rules').onclick=()=>info('House rules','Keep it friendly. Football banter is welcome; abuse and personal details are not. Use Report to send a private flag to the landlord. Messages are kept for up to seven days, with the latest 200 retained.');
$('dialog-close').onclick=$('dialog-done').onclick=()=>$('info-dialog').close();
$('entrance-refresh').onclick=refreshEntrance;$('entrance-rules').onclick=()=>$('rules').onclick();
if(roomPath==='/admin'){$('workbench').className+=' landlord-view';$('admin').hidden=false;$('join').hidden=true;status('Unlock the landlord’s controls.');}else if(isEntrance()){$('entrance').hidden=false;if(campaignFragment){const primary=document.querySelector('.entrance-enter');primary.href=roomPrefix+'/chat?enter=1'+(frameQuery?'&'+frameQuery:'')+campaignFragment;primary.textContent='Continue to the Boot Room →';}$('dialog-done').textContent='Back to the entrance';refreshEntrance();}else{
 $('chat-shell').hidden=true;
 $('chat-loading').hidden=false;
 if(campaign&&typeof campaign.name==='string'){
  const detail=document.createElement('p');
  detail.textContent='Joining as '+campaign.name+' · '+identityText({campaign});
  $('walk-in-entry').hidden=false;
  $('walk-in-entry').prepend(detail);
 }
 connect(roomPrefix!==''&&new URLSearchParams(location.search).get('enter')==='1');
}`;
