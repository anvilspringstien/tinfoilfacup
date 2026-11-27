# Shared phone frame — public launch

The public and installed entrances select the white-disc Splash explicitly.
The normal Shed uses the same phone-frame launcher and selects its own Splash.

| Entry | Splash document |
| --- | --- |
| `/` or `/index.html` | `/beta/public-splash.html` |
| Installed landing `/beta/phone-frame.html` | `/beta/public-splash.html` |
| `/beta/` or `/beta/index.html` | `/beta/shed-splash.html` |
| Opt-in `/beta/phone-frame-shed.html` | `/beta/shed-splash.html` |

The root retains its white-disc fallback and sharing metadata. Older cached
shells that request `/beta/index.html` inside a frame resolve to the Splash
for their parent route. The Shed uses the accepted #756 Astral Portal layers
and its first-paint composite. The standalone Astral Portal and Floating Cup
pages retain their existing URLs, Splash geometry and independent controls.

Both entrances use the same Four Laws and Campaign wrapper, Clubfinder data
and navigation enhancements. Campaign and Challenge storage, Pigeon identities,
manifest identities and installation scope are shared as before. The installed
handover opens the Public experience, and shared links and QR codes continue
to use the canonical public URL. Keep and Share close within the opening
Campaign frame. Refresh retains the shell path. Desktop Stats retains the
opening shell in its popup, and native iPhone Stats carries a fixed return
route for the Public or Shed entrance. The Shed Boot Room uses the existing
framed Shed return.

The owner reproduced the narrow desktop appearance by changing Chrome zoom
from 100% to 67% at the same URL. The routing correction leaves the shared
frame dimensions and Splash styles intact.

Above 700px wide, the existing application renders in a real 390 × 693.333px
viewport (9:16), scaled uniformly to the available height and centred. Rotation
changes the scale, not the arrangement. On phones, the viewport follows the
available screen dimensions as before. Long pages retain their existing scroll
owners within that viewport. The outer shell adds no second border.

Stats keeps its existing 980px report/print layout in a separate tab, fitted into
the same outer phone shape. The shell intercepts only the existing blank/Stats
popup calls, returns the real embedded Window to the original generator, and
preserves opener and Close behaviour. External websites and donation popups
continue through the native browser operation.

Physical Safari/Home Screen installation and rotation still need device
acceptance. Browser regressions exercise the cookies-only handover into empty
installed storage, retained identity, Cabinet and mileage, and zero new counter
allocations. Barry Air remains a separate demonstration Site, without saved
Campaign integration; the public badge opens only the local Coming Soon teaser.

## Validation

Local syntax, approved journey/master lock, Keep backup/restore and installation
handover checks pass. Browser QA exercised Splash → Four Laws, the saved Newton
Aycliffe fixture, Stats launch and Close return, Challenges and Exit, and Share →
Keep → Share. Local QA disabled the external counter endpoint. Simulated screen
sizes 1680×889, 1024×768, 768×1024 and 390×669 showed the expected centred viewport.

The dedicated PR workflow repeats these journeys on a normal static server,
checks geometry and preservation of the seeded identity, and asserts zero counter
calls. No acceptance hashes are updated to accommodate the proof.

## Compact navigation

The three primary Campaign buttons use an enamel finish: a fine inset brass rim, a static gloss and a
small raised shadow. Their existing base colours, dimensions, type, spacing and
handlers are preserved. This accepted finish applies to the public, installed
and Shed entrances. It adds no assets or animation.

Campaign retains its original three-across My Campaign / My Stats / My Challenges
buttons. The approved transparent Barry Air wings form a centred 240px image
button below them, with the original contour drop shadow. Original Campaigns,
Reset, End/Resume Campaign and Hard Reset
retain the original small teal lozenges and original actions, with each wrapped
row centred.

Keep the Magic and Share the Magic sit immediately above Support, after all three
Campaign cards, after the selected Campaign, and after Challenges’ Coming Soon
panel. They retain Support's yellow colour, centring and 20px row margins, with 6px
rounded square corners. The redundant admin Share link and its separator are
hidden; Challenges retains its underlying Share handler for the new buttons.
The disabled Challenges Coming Soon button is red with white text.
The existing embedded Share and installation instructions own their normal return
and handover behaviour in each module. Restored HTML snapshots have the new
buttons’ handlers rebound without duplicating rows.

The layout applies within the shared public, installed and Shed frames. The badge
opens an accessible local dialog headed Barry Air / Coming Soon with a Pigeon
Control teaser. Close, Escape and outside click return to the focused badge
without changing route or Campaign identity. There is no outward Barry Air link.
The badge asset remains the approved transparent wings. Stats popups and refreshes
use the route of their originating shell, so public Stats stays on the public
entrance and installed Stats stays within its existing scope.

## Desktop scrollbar refinement

The proof hides only the application document's edge scrollbar on wide, fine
pointer screens. Wheel, trackpad, keyboard and programmatic scrolling keep their
existing owners. The root keeps its full 390px width on both short and long pages,
so the scrollbar cannot squeeze or shift the composition. Phone and touch tablet
presentation, nested reading scroll areas and the Stats report are unchanged.
The browser regression compares Splash/Four Laws position and width, then checks
the long saved Campaign still responds to wheel scrolling.


## Entrance boundary acceptance

Run the entrance browser regression against the real root, installed shell,
and normal Shed. Verify the decoded crest in the child document, then select
a fresh Campaign from Four Laws and return to the saved Campaign. Check the
enamel navigation and Barry Air on each route. Check Refresh, Stats, and the
Keep and Share return from the normal Shed. The test intercepts the counter
request and uses a mock number, and checks that returns issue no new number.

The motion regression exercises the same-origin Shed child frame. Confirm
no prompt on load, motion only after the explicit control, and an unchanged
still crest when permission is declined. The regression simulates the
browser prompt. Physical hosted iPhone acceptance is required after an
authorised merge. Check Big Boy in Incognito at 100% and 67% zoom against the
same entry and confirm neither zoom changes which shell or crest is selected.
