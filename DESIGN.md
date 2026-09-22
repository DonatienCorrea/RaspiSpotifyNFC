# Visual Direction

TapTune is presented as a workshop field guide: warm paper, ink-black type, cobalt system marks, orange physical signals, and green playback. The page deliberately avoids a generic dark-tech landing page and uses the physical tap-to-play loop as its visual grammar.

## Product UI instructions

Use this document as the source of truth for every TapTune surface, including the Raspberry Pi web UI, documentation, simulator screens, and future product pages. A page should feel like another page in the same workshop field guide, not like a separate SaaS dashboard.

- **Typography:** Load Space Grotesk for expressive headings and labels, DM Sans for readable copy, and DM Mono only for UIDs, URIs, code, timestamps, and system labels. Use tight, editorial heading tracking and generous line-height for body copy.
- **Color:** Use paper `#f4f1e8` as the default canvas, paper deep `#e8e3d5` for secondary surfaces, ink `#182027` for primary text and dark bands, cobalt `#1945e8` for system marks and primary actions, signal orange `#f06328` for physical input and attention, playback green `#20734f` for successful playback states, muted `#5c635f`, and line `#c9c5b9`.
- **Composition:** Prefer a centered `1160px` shell, visible rules, small uppercase mono section indexes, asymmetrical editorial layouts, and generous vertical spacing. Organize functional pages as a field guide: a clear title, a short explanation, a working surface, then inspectable records or next steps.
- **Surfaces:** Prefer flat paper, ink, cobalt, or orange blocks with 1px rules. Avoid gradients, glassmorphism, large rounded cards, excessive shadows, and generic dashboard chrome. Small square corners or no radius are the default; use a modest radius only where it improves an input control.
- **Product language:** Talk about tags, taps, playback, physical input, handoffs, and the signal path. Keep labels concrete and friendly. Show technical values as inspectable system details rather than hiding them behind decorative UI.
- **Controls:** Buttons use the existing `.button` language: compact, bold, rectangular, and high-contrast. Inputs use paper-white surfaces, ink borders, and mono text for identifiers. Quick actions may use outlined controls, but they should still look like field-guide tools rather than pills.
- **Status:** Use orange for attention and input, green for healthy playback or saved state, and cobalt for system information. Status must be understandable through text as well as color.
- **Interaction:** Links and buttons need explicit hover and `:focus-visible` states. Keep motion limited to short color/position changes and honor `prefers-reduced-motion`.
- **Responsive behavior:** Preserve the reading order on narrow screens. Collapse columns into one flow, keep controls full-width when useful, and never let UIDs or URIs overflow the viewport.

When adding a new surface, start from the tokens and patterns in `docs/styles.css` instead of inventing a new palette or component language.
