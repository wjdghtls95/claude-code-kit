---
name: design-review
description: Review how a web UI change actually looks in the browser. Use after the code review of a pull request that changes components or pages. Checks visual quality only, not logic or types.
---

Separate from the code review (logic and types): this checks **what the screen looks like**. The reference is the project's design system file if there is one (the file named by `design_system_file` in `.claude-kit.json`, otherwise the first `DESIGN_SYSTEM.md` you find in the project). If there is none, use the general checks below and say that no design system was found.

## Step 1: run the app

If the app is not running, start it with the project's own command (see the scripts in `package.json` or the README). Open the changed screen in the browser. Do not guess the command, ask if it is unclear.

## Step 2: capture screenshots

With Playwright, one desktop and one phone width:

```bash
npx playwright screenshot --browser chromium "http://localhost:<port>/<path>" /tmp/design-review.png
npx playwright screenshot --browser chromium --viewport-size="375,812" "http://localhost:<port>/<path>" /tmp/design-review-mobile.png
```

Read the screenshots, then go through the checklist.

## Step 3: design system rules

If a design system file exists, check the changed screen against its rules: colors only from its tokens, no hard-coded new colors, its spacing and type scale, its rules for motion and elevation. Any violation is a finding.

## Step 4: general visual quality

Report each as Critical (fix now) or Nit (recommended).

**Layout and spacing**
```
[ ] No arbitrary spacing values outside the project's spacing scale (a 4-point scale if none)
[ ] Gaps between cards and sections are consistent
[ ] Content does not touch the container edge (breathing room)
[ ] No horizontal overflow at 375px
```

**Typography**
```
[ ] A clear heading, body, small, mono hierarchy
[ ] Sizes come from the project's type scale
[ ] Body text has a line height of 1.5 or more
[ ] Long text is truncated or wrapped on purpose
```

**Color and contrast**
```
[ ] Body text meets WCAG AA contrast (4.5:1 or more)
[ ] Status colors (success, warning, error) are not distinguished by color alone, an icon or text helps
```

**Interaction**
```
[ ] Interactive elements have hover and focus states
[ ] A visible focus ring
[ ] Click targets are large enough (44 by 44 px at least)
[ ] Animation respects prefers-reduced-motion
```

**Empty and error states**
```
[ ] Empty data shows an empty-state UI, not a blank screen
[ ] Errors give the user feedback
[ ] There is a loading state
```

## Step 5: report

```
## Design Review: [screen] ([date])

Critical (fix now)
- [item]: [where and how, specifically]

Nit (recommended)
- [item]: [where and how, specifically]

Passed
- Design system rules: N of M checks passed (or "no design system found")
- General quality: no major issues
```

With no Critical items the change can merge. Nits can wait for the next change.
