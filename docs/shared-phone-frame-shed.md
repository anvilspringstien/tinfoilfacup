# Shared phone frame Shed

`/beta/phone-frame-shed.html` is a separate, opt-in entrance. The existing
public and BETA entrances, accepted master hashes, application files, manifest,
installed entry and competition machinery remain unchanged.

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

This is a geometry and navigation proof, not a replacement installed app. Adding
the existing Keep icon still launches the existing installed entry, not this Shed
URL. Native Share/install behaviour and physical Safari/Home Screen rotation must
be accepted on devices before promoting this design. Barry Air remains its
separate demonstration Site; it has not been wired to saved Campaign data.

## Validation

Local syntax, approved journey/master lock, Keep backup/restore and installation
handover checks pass. Browser QA exercised Splash → Four Laws, the saved Newton
Aycliffe fixture, Stats launch and Close return, Challenges and Exit, and Share →
Keep → Share. Local QA disabled the external counter endpoint. Simulated screen
sizes 1680×889, 1024×768, 768×1024 and 390×669 showed the expected centred viewport.

The dedicated PR workflow repeats these journeys on a normal static server,
checks geometry and preservation of the seeded identity, and asserts zero counter
calls. No acceptance hashes are updated to accommodate the proof.

## Compact navigation trial

Campaign retains its original three-across My Campaign / My Stats / My Challenges
buttons. The approved transparent Barry Air wings form a centred 160px image
button below them. Original Campaigns, End/Resume Campaign, Reset and Hard Reset
retain the original small teal lozenges and original actions.

Keep the Magic and Share the Magic sit immediately above Support, after all three
Campaign cards, after the selected Campaign, and after Challenges’ Coming Soon
panel. They reuse Support's yellow lozenge class, centring and 20px row margins.
The existing embedded Share and installation instructions own their normal return
and handover behaviour in each module. Restored HTML snapshots have the new
buttons’ handlers rebound without duplicating rows.

The layout applies only inside the opt-in phone-frame proof. Barry Air opens its
labelled demonstration Site in the same tab and returns to this proof's saved
Campaign entrance. Identity and progress remain on tinfoilfacup.com; Barry's flight
data is still the demonstration. The badge asset is a local copy of the approved
transparent wings, with an accessible button name and keyboard focus outline.

## Desktop scrollbar refinement

The proof hides only the application document's edge scrollbar on wide, fine
pointer screens. Wheel, trackpad, keyboard and programmatic scrolling keep their
existing owners. The root keeps its full 390px width on both short and long pages,
so the scrollbar cannot squeeze or shift the composition. Phone and touch tablet
presentation, nested reading scroll areas and the Stats report are unchanged.
The browser regression compares Splash/Four Laws position and width, then checks
the long saved Campaign still responds to wheel scrolling.
