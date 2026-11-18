# Review report: TermoPack

Made 2026-11-17 · http://localhost:8501 · 14 probe run(s) · system: none found

## Verdict: FAIL

7 error(s) found in what was checked.

7 errors · 34 warnings · 11 notes · coverage 22/64 cells done

## What was not checked

**Blocked** (8)
- `task:/|reduced-motion`: El navegador integrado no puede simular «reducir movimiento»
- `task:/|forced-colors`: El navegador integrado no puede simular colores forzados
- `task:/datos|reduced-motion`: El navegador integrado no puede simular «reducir movimiento»
- `task:/datos|forced-colors`: El navegador integrado no puede simular colores forzados
- `task:/economia|reduced-motion`: El navegador integrado no puede simular «reducir movimiento»
- `task:/economia|forced-colors`: El navegador integrado no puede simular colores forzados
- `task:/fisica|reduced-motion`: El navegador integrado no puede simular «reducir movimiento»
- `task:/fisica|forced-colors`: El navegador integrado no puede simular colores forzados

**Skipped on purpose** (34)
- `task:/|hover-and-press`: No se hizo la pasada de hover por tiempo; se revisó el foco con teclado en la Vista general
- `task:/|states-and-data`: No se probaron datos vacíos, con error o muy largos en esta pasada
- `task:/|motion`: Solo hay transiciones propias de Streamlit (barra lateral); no hay animaciones de la app
- `task:/|letter-reveals`: La app no tiene textos que aparecen letra por letra
- `task:/|text-pixels`: No hay texto sobre fotos ni degradados
- `task:/|floating-bars`: No hay barras fijas además de la barra lateral, revisada aparte
- `task:/|toggles`: Solo se operó el selector de vista en la Vista general
- `task:/datos|focus-walk`: Recorrido con Tab hecho solo en la Vista general
- `task:/datos|hover-and-press`: No se hizo la pasada de hover por tiempo; se revisó el foco con teclado en la Vista general
- `task:/datos|states-and-data`: No se probaron datos vacíos, con error o muy largos en esta pasada
- `task:/datos|motion`: Solo hay transiciones propias de Streamlit (barra lateral); no hay animaciones de la app
- `task:/datos|stress-text`: Prueba de texto largo hecha solo en la Vista general
- `task:/datos|letter-reveals`: La app no tiene textos que aparecen letra por letra
- `task:/datos|text-pixels`: No hay texto sobre fotos ni degradados
- `task:/datos|floating-bars`: No hay barras fijas además de la barra lateral, revisada aparte
- `task:/datos|toggles`: Solo se operó el selector de vista en la Vista general
- `task:/economia|focus-walk`: Recorrido con Tab hecho solo en la Vista general
- `task:/economia|hover-and-press`: No se hizo la pasada de hover por tiempo; se revisó el foco con teclado en la Vista general
- `task:/economia|states-and-data`: No se probaron datos vacíos, con error o muy largos en esta pasada
- `task:/economia|motion`: Solo hay transiciones propias de Streamlit (barra lateral); no hay animaciones de la app
- `task:/economia|stress-text`: Prueba de texto largo hecha solo en la Vista general
- `task:/economia|letter-reveals`: La app no tiene textos que aparecen letra por letra
- `task:/economia|text-pixels`: No hay texto sobre fotos ni degradados
- `task:/economia|floating-bars`: No hay barras fijas además de la barra lateral, revisada aparte
- `task:/economia|toggles`: Solo se operó el selector de vista en la Vista general
- `task:/fisica|focus-walk`: Recorrido con Tab hecho solo en la Vista general
- `task:/fisica|hover-and-press`: No se hizo la pasada de hover por tiempo; se revisó el foco con teclado en la Vista general
- `task:/fisica|states-and-data`: No se probaron datos vacíos, con error o muy largos en esta pasada
- `task:/fisica|motion`: Solo hay transiciones propias de Streamlit (barra lateral); no hay animaciones de la app
- `task:/fisica|stress-text`: Prueba de texto largo hecha solo en la Vista general
- `task:/fisica|letter-reveals`: La app no tiene textos que aparecen letra por letra
- `task:/fisica|text-pixels`: No hay texto sobre fotos ni degradados
- `task:/fisica|floating-bars`: No hay barras fijas además de la barra lateral, revisada aparte
- `task:/fisica|toggles`: Solo se operó el selector de vista en la Vista general

## Errors (7)

### The focus ring is removed and nothing replaces it
`M-IN02-1468` · IN-02 Focus ring removed or too faint · **measured** · WCAG 2.4.7 (failure F78)
- Where: /datos · 1440x900 · dark · reduced motion; /datos · 390x844 · dark · reduced motion; /datos · 768x1024 · dark · reduced motion; /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion (+7 more)
- Measured: 5 control(s), e.g. div.stApp.stAppEmbeddingId-tooaizs7qmrf > div.stAppViewContainer.appview-container > a.st-emotion-cache-hmusyd.eksftaj1
- Expected: a visible focus indicator (2 px ring, 2 px offset, not color alone)
- Evidence: `div.stApp.stAppEmbeddingId-tooaizs7qmrf > div.stAppViewContainer.appview-container > a.st-emotion-cache-hmusyd.eksftaj1`, `main#stMain`, `div.stButtonGroup.st-emotion-cache-68zbsl > div.st-emotion-cache-1eddh7x.e1aouyeq26 > button.st-emotion-cache-1mcz6sg.e1`, `div.st-emotion-cache-19exxan.e579mqo0 > div.st-emotion-cache-1k5fi8b.e579mqo1 > button.st-emotion-cache-49bqws.e579mqo2:`, `div.stApp.stAppEmbeddingId-tooanuy05zmo > div.stAppViewContainer.appview-container > a.st-emotion-cache-hmusyd.eksftaj1`, `div.stButtonGroup.st-emotion-cache-8atqhb > div.st-emotion-cache-1iw6lyw.e1aouyeq26 > button.st-emotion-cache-1b8dq7g.e1`
- Fix: replace outline: none with a :focus-visible style

### Text contrast 1:1 is below 4.5:1
`M-MS04-3512` · MS-04 Contrast judged by eye · **measured** · WCAG 1.4.3
- Where: /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion
- Measured: #1d428a on #1d428a, 14 px, 1 element(s)
- Expected: 4.5:1 (no rounding up: 4.49 fails)
- Evidence: `div.st-emotion-cache-18kk8l8.e13xtgje4:nth-of-type(2) > div.st-emotion-cache-ij0v5j.e1yqkw3v0 > p`
- Fix: darken the text or lighten the surface with a token pair that passes; check the same pair in dark mode

### Text contrast 2.28:1 is below 3.0:1
`M-MS04-5739` · MS-04 Contrast judged by eye · **measured** · WCAG 1.4.3
- Where: /datos · 1440x900 · dark · reduced motion; /datos · 390x844 · dark · reduced motion; /datos · 768x1024 · dark · reduced motion; /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion (+7 more)
- Measured: #f28c35 on #f5f7fb, 37.4 px, 1 element(s)
- Expected: 3.0:1 (no rounding up: 4.49 fails)
- Evidence: `div.st-emotion-cache-nufe5w.e1yqkw3v0 > div.tp-titulo:nth-of-type(2) > i`
- Fix: darken the text or lighten the surface with a token pair that passes; check the same pair in dark mode

### Targets smaller than 24x24 px with another target close by
`M-MS06-8122` · MS-06 Targets too small · **measured** · WCAG 2.5.8
- Where: /datos · 390x844 · dark · reduced motion; /datos · 768x1024 · dark · reduced motion; /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion; /fisica · 390x844 · dark · reduced motion (+5 more)
- Measured: 1 target(s): div.stApp.stAppEmbeddingId-tooaizs7qmrf > div.stAppViewContainer.appview-container > a.st-emotion-cache-hmusyd.eksftaj1 1x1
- Expected: at least 24x24 CSS px, or 24 px of clear space around each (WCAG 2.5.8)
- Evidence: `div.stApp.stAppEmbeddingId-tooaizs7qmrf > div.stAppViewContainer.appview-container > a.st-emotion-cache-hmusyd.eksftaj1`, `span.stTooltipIcon.st-emotion-cache-1iwapfg > span.stTooltipHoverTarget > button.st-emotion-cache-be9t1i.ef3bkur0`, `input#react-aria609684527-\:r9g\:-0`, `div.stApp.stAppEmbeddingId-tooanuy05zmo > div.stAppViewContainer.appview-container > a.st-emotion-cache-hmusyd.eksftaj1`, `input#react-aria609684527-\:r6j\:-0`, `span.stTooltipIcon.st-emotion-cache-1iwapfg > span.stTooltipHoverTarget > button.st-emotion-cache-vo6tiu.e1aouyeq3`
- Fix: raise min-width and min-height, or add padding to the hit area

### En celular el menú lateral se abre desplegado y tapa 300 de los 390 px de ancho al entrar
`H-001` · MS-12 Things the model 'sees' that are not there · **operated**
- Where: /, 390, light
- Expected: En celular el contenido se ve al cargar; el menú se abre solo al pulsarlo
- Evidence: `opendesigner/review/shots/home-390-light-carga-menu.jpg`
- Fix: app.py: st.set_page_config(initial_sidebar_state='auto') (se despliega en escritorio y se pliega en celular)

### La opción «Promedios» del selector de vista queda fuera de la tarjeta en celular: el botón va de 320 a 423 px y el contenedor termina en 330 px (93 px ocultos)
`H-002` · MS-12 Things the model 'sees' that are not there · **operated**
- Where: /, 390, light
- Expected: Las tres opciones visibles sin desplazamiento lateral
- Evidence: `opendesigner/review/shots/home-390-light-s01.jpg`, `opendesigner/review/shots/focus-home-390-s01.jpg`
- Fix: Etiquetas más cortas en celular (Temp. · Variación · Promedios) o permitir que el grupo pase a dos líneas (flex-wrap)

### Fórmulas cortadas en Fundamento físico: en 390 px la ecuación del modelo mide 363 px en un espacio de 270 px (se pierde U·A = k m c); en 768 px las tres tarjetas cortan Q, k_ef y R
`H-003` · MS-12 Things the model 'sees' that are not there · **operated**
- Where: /fisica, 390 y 768, light
- Expected: Cada fórmula completa dentro de su tarjeta
- Evidence: `opendesigner/review/shots/fisica-390-light-s00.jpg`, `opendesigner/review/shots/fisica-768-light-s00.jpg`
- Fix: Apilar las tarjetas de fórmulas en una columna por debajo de ~1100 px y separar la ecuación del modelo en dos líneas

## Warnings (34)

### Fonts downloaded but not used
`M-EN08-8945` · EN-08 Fonts downloaded but not used · **measured** · preflight 10
- Where: /datos · 1440x900 · dark · reduced motion; /datos · 390x844 · dark · reduced motion; /datos · 768x1024 · dark · reduced motion; /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion (+6 more)
- Measured: 1 of 3 loaded families draw no visible text: Source Sans (1 face(s))
- Expected: load only the families and weights the page draws (one or two families, preflight 10)
- Fix: remove the @font-face, preload or font link for these; text drawn only by ::before or ::after is not counted, so check an icon font first

### Focus ring thinner than 2 px
`M-IN02-8964` · IN-02 Focus ring removed or too faint · **operated** · guardrails 4
- Where: / · 390x844 · dark · reduced motion
- Measured: 9 stops: label.st-emotion-cache-s4rnaq.e1hn2pbo4 > span > input (Tab 2); div#modebar-26ba71 > div.modebar-group:nth-of-type(1) > button.modebar-btn (Tab 3); div#modebar-26ba71 > div.modebar-group:nth-of-type(2) > button.modebar-btn.active:nth-of-type(1) (Tab 4); div#modebar-26ba71 > div.modebar-group:nth-of-type(2) > button.modebar-btn:nth-of-type(2) (Tab 5)
- Expected: 2 px ring at a 2 px offset
- Evidence: `label.st-emotion-cache-s4rnaq.e1hn2pbo4 > span > input`, `div#modebar-26ba71 > div.modebar-group:nth-of-type(1) > button.modebar-btn`, `div#modebar-26ba71 > div.modebar-group:nth-of-type(2) > button.modebar-btn.active:nth-of-type(1)`, `div#modebar-26ba71 > div.modebar-group:nth-of-type(2) > button.modebar-btn:nth-of-type(2)`

### Duplicate ids
`M-IN03-9619` · IN-03 Names, roles and structure · **measured** · HTML
- Where: /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion
- Measured: glide-cell-0-0, glide-cell-1-0, glide-cell-2-0, glide-cell-3-0, glide-cell-4-0
- Expected: each id once (labels and aria-labelledby point at ids)
- Evidence: `#glide-cell-0-0`

### Touch targets under 44 px
`M-IN04-9748` · IN-04 Touch · **measured** · Apple HIG, Android accessibility guide
- Where: /datos · 390x844 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /fisica · 390x844 · dark · reduced motion; / · 390x844 · dark · reduced motion
- Measured: 1 target(s), e.g. div.stApp.stAppEmbeddingId-tooaizs7qmrf > div.stAppViewContainer.appview-container > a.st-emotion-cache-hmusyd.eksftaj1 at 1x1
- Expected: Apple's default control size is 44 pt (minimum 28 pt); Android recommends 48 dp
- Evidence: `div.stApp.stAppEmbeddingId-tooaizs7qmrf > div.stAppViewContainer.appview-container > a.st-emotion-cache-hmusyd.eksftaj1`, `div.stApp.stAppEmbeddingId-tooanuy05zmo > div.stAppViewContainer.appview-container > a.st-emotion-cache-hmusyd.eksftaj1`, `span.stTooltipIcon.st-emotion-cache-1iwapfg > span.stTooltipHoverTarget > button.st-emotion-cache-be9t1i.ef3bkur0`, `input#react-aria474335561-\:rq\:-0`, `div.stDownloadButton > div.st-emotion-cache-ngypfu.e1aouyeq19:nth-of-type(2) > button.st-emotion-cache-vo6tiu.e1aouyeq3`, `label.st-emotion-cache-s4rnaq.e1hn2pbo4 > span > input`
- Fix: enlarge the hit area on touch (padding, or an ::after inset)

### Controls a keyboard can reach but nobody can see
`M-IN08-7821` · IN-08 In the DOM is not the same as seen or reachable · **measured** · WCAG 2.4.7 / 1.3.2
- Where: /datos · 1440x900 · dark · reduced motion; /datos · 768x1024 · dark · reduced motion; /economia · 1440x900 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion; /fisica · 1440x900 · dark · reduced motion; /fisica · 768x1024 · dark · reduced motion (+3 more)
- Measured: 4: div > span.stTooltipHoverTarget > button.st-emotion-cache-fl5cs5.e1aouyeq20 (opacity 0); div:nth-of-type(2) > span.stTooltipHoverTarget > button.st-emotion-cache-fl5cs5.e1aouyeq20 (opacity 0); div:nth-of-type(3) > span.stTooltipHoverTarget > button.st-emotion-cache-fl5cs5.e1aouyeq20 (opacity 0)
- Expected: focusable things are visible when focused
- Evidence: `div > span.stTooltipHoverTarget > button.st-emotion-cache-fl5cs5.e1aouyeq20`, `div:nth-of-type(2) > span.stTooltipHoverTarget > button.st-emotion-cache-fl5cs5.e1aouyeq20`, `div:nth-of-type(3) > span.stTooltipHoverTarget > button.st-emotion-cache-fl5cs5.e1aouyeq20`, `div#modebar-44e5a3 > div.modebar-group:nth-of-type(1) > button.modebar-btn`, `div#modebar-44e5a3 > div.modebar-group:nth-of-type(2) > button.modebar-btn.active:nth-of-type(1)`, `div#modebar-44e5a3 > div.modebar-group:nth-of-type(2) > button.modebar-btn:nth-of-type(2)`
- Fix: hide with display: none or inert until they are meant to appear

### Spacing off the 4 px grid (22 value(s), 83 of 163 uses)
`M-MS01-7182` · MS-01 Spacing judged by eye · **measured** · tokens
- Where: /datos · 1440x900 · dark · reduced motion; /datos · 390x844 · dark · reduced motion; /datos · 768x1024 · dark · reduced motion; /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion (+6 more)
- Measured: 8.8px x10; 12.8px x10; 1.6px x10; 6px x8; 11.2px x6; 3.2px x4
- Expected: multiples of 4 px
- Evidence: `div.stPageLink > div.st-emotion-cache-1ofqig9.evng2kd0 > a.st-emotion-cache-1ew5you.evng2kd1`, `div > span.stTooltipHoverTarget > button.st-emotion-cache-fl5cs5.e1aouyeq20`, `div.st-emotion-cache-k2h9z6.ef3bkur2 > div.st-emotion-cache-rhumdg.e1yqkw3v0 > div.tp-logo:nth-of-type(1)`, `div.stVerticalBlock.st-emotion-cache-1a7fwqm > div.st-emotion-cache-1vfi2s9.e399r295:nth-of-type(4) > div.stVerticalBloc`, `div.stVerticalBlock.st-emotion-cache-1p8n0nm > div.st-emotion-cache-1vfi2s9.e399r295 > div.stVerticalBlock.st-key-card_c`, `span.katex-html:nth-of-type(2) > span.base:nth-of-type(1) > span.mord.mathnormal:nth-of-type(2)`
- Fix: use the spacing tokens; 1-2 px values are usually borders or browser defaults

### 15 font sizes
`M-MS02-1035` · MS-02 Type scale drift · **measured** · preflight 7
- Where: /datos · 1440x900 · dark · reduced motion; /datos · 390x844 · dark · reduced motion; /datos · 768x1024 · dark · reduced motion; /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion (+6 more)
- Measured: 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13, 14, 14.5, 16, 18, 23, 37.5; within 10% of each other: 9/9.5, 9.5/10, 10/10.5, 10.5/11
- Expected: about 8 sizes at most, all from one scale, none within 10% of another (preflight 7)
- Fix: map each size to the nearest step of one scale

### 4 typefaces on one page
`M-MS02-1236` · MS-02 Type scale drift · **measured** · DC-L02-03
- Where: /fisica · 1440x900 · dark · reduced motion; /fisica · 390x844 · dark · reduced motion; /fisica · 768x1024 · dark · reduced motion
- Measured: Manrope on 62 element(s); math on 100 element(s); KaTeX_Main on 76 element(s); KaTeX_Math on 41 element(s)
- Expected: one family for the interface, plus a mono for code; a second text face only with a named job, such as display headings on a marketing page (DC-L02-03; quality.md Q3: one or two typefaces)
- Evidence: `div.stApp.stAppEmbeddingId-tooaizs7qmrf > div.stAppViewContainer.appview-container > a.st-emotion-cache-hmusyd.eksftaj1`, `semantics > mrow > mi:nth-of-type(1)`, `span.katex-html:nth-of-type(2) > span.base:nth-of-type(1) > span.mopen:nth-of-type(3)`, `span.katex-html:nth-of-type(2) > span.base:nth-of-type(1) > span.mord.mathnormal:nth-of-type(2)`
- Fix: move the text set in the extra faces to the main family; a face used on a handful of elements is usually a leftover

### 5 font weights on one page
`M-MS02-5059` · MS-02 Type scale drift · **measured** · DC-L19-24
- Where: /datos · 1440x900 · dark · reduced motion; /datos · 390x844 · dark · reduced motion; /datos · 768x1024 · dark · reduced motion; /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion (+6 more)
- Measured: 400 on 24 element(s), 500 on 6 element(s), 600 on 5 element(s), 700 on 3 element(s), 800 on 3 element(s); 400 and 500 are one step apart, which can read as a mistake rather than a level; 500 and 600 are one step apart, which can read as a mistake rather than a level
- Expected: three weights at most in a system, and two in any one view, clearly apart, such as 400 and 600 (DC-L19-24; it marks two neighbouring weights reading as a mistake as inferred)
- Evidence: `div.stApp.stAppEmbeddingId-tooaizs7qmrf > div.stAppViewContainer.appview-container > a.st-emotion-cache-hmusyd.eksftaj1`, `span.st-emotion-cache-1ylwq8i.evng2kd2:nth-of-type(2) > div.st-emotion-cache-1f2ydu4.e1yqkw3v0 > p`, `div.tp-lab:nth-of-type(2) > div:nth-of-type(2) > b`, `div.tp-top > div.tp-estado:nth-of-type(2) > div.tp-avatar`, `div.tp-top > div.tp-miga:nth-of-type(1) > b`, `div.stApp.stAppEmbeddingId-tooanuy05zmo > div.stAppViewContainer.appview-container > a.st-emotion-cache-hmusyd.eksftaj1`
- Fix: give each weight a job (body, labels, headings) and merge the near ones; try size or space before a third weight

### Font sizes between whole pixels
`M-MS02-5955` · MS-02 Type scale drift · **measured** · preflight 7
- Where: /datos · 1440x900 · dark · reduced motion; /datos · 390x844 · dark · reduced motion; /datos · 768x1024 · dark · reduced motion; /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion (+6 more)
- Measured: 9.3 px x1; 9.9 px x2; 10.2 px x1; 10.6 px x1; 10.9 px x1; 11.5 px x2
- Expected: whole-pixel sizes from the scale: a fluid size (clamp, vw) or an rem step that does not land on a pixel gives a different size at every width, so nothing matches (preflight 7)
- Evidence: `span.st-emotion-cache-1ylwq8i.evng2kd2:nth-of-type(2) > div.st-emotion-cache-1f2ydu4.e1yqkw3v0 > p`, `div.st-emotion-cache-k2h9z6.ef3bkur2 > div.st-emotion-cache-rhumdg.e1yqkw3v0 > div.tp-seccion:nth-of-type(3)`, `div.st-emotion-cache-rhumdg.e1yqkw3v0 > div.tp-tip > b`, `div.tp-uni:nth-of-type(1) > div > b`, `div.st-emotion-cache-nufe5w.e1yqkw3v0 > div.tp-top > div.tp-miga:nth-of-type(1)`, `div.st-emotion-cache-k2h9z6.ef3bkur2 > div.st-emotion-cache-nufe5w.e1yqkw3v0 > div.tp-titulo:nth-of-type(2)`
- Fix: step the size at breakpoints instead of a fluid clamp, or round the scale to whole pixels; 13.33 px on a button is the browser default

### Text smaller than 12 px
`M-MS02-1083` · MS-02 Type scale drift · **measured**
- Where: /datos · 1440x900 · dark · reduced motion; /datos · 390x844 · dark · reduced motion; /datos · 768x1024 · dark · reduced motion; /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion (+7 more)
- Measured: 9 px: 'EXPERIMENTO 01' in div.st-emotion-cache-nufe5w.e1yqkw3v0 > div.tp-ceja:nth-of-type(1) > span
- Expected: at least 12 px
- Evidence: `div.st-emotion-cache-nufe5w.e1yqkw3v0 > div.tp-ceja:nth-of-type(1) > span`, `span.vlist-t.vlist-t2 > span.vlist-r:nth-of-type(1) > span.vlist-s:nth-of-type(2)`
- Fix: raise it to a text style

### Body text outside 45-75 characters a line
`M-MS07-0256` · MS-07 Line length and line height · **measured** · WCAG 1.4.8 (AAA)
- Where: /economia · 1440x900 · dark · reduced motion; /fisica · 768x1024 · dark · reduced motion
- Measured: div.st-emotion-cache-k2h9z6.ef3bkur2 > div.st-emotion-cache-vickrq.e1yqkw3v0 > p: about 27 characters a line
- Expected: 45 to 75 characters for body text
- Evidence: `div.st-emotion-cache-k2h9z6.ef3bkur2 > div.st-emotion-cache-vickrq.e1yqkw3v0 > p`, `div.st-emotion-cache-k2h9z6.ef3bkur2 > div.st-emotion-cache-nufe5w.e1yqkw3v0 > p`
- Fix: max-width: 65ch on the text block, or a wider column

### Lines longer than 80 characters
`M-MS07-8266` · MS-07 Line length and line height · **measured** · WCAG 1.4.8 (AAA)
- Where: /economia · 1440x900 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion; /fisica · 1440x900 · dark · reduced motion; /fisica · 768x1024 · dark · reduced motion
- Measured: div.st-emotion-cache-k2h9z6.ef3bkur2 > div.st-emotion-cache-nufe5w.e1yqkw3v0 > div.tp-nota is about 136 characters wide
- Expected: at most 80 (WCAG 1.4.8, AAA); 45-75 is the usual target
- Evidence: `div.st-emotion-cache-k2h9z6.ef3bkur2 > div.st-emotion-cache-nufe5w.e1yqkw3v0 > div.tp-nota`
- Fix: set max-width: 65ch on the text block

### Colors that look the same but are typed differently (1 group)
`M-MS08-7497` · MS-08 Color drift from the tokens · **measured** · STD-visual-details-26
- Where: /datos · 1440x900 · dark · reduced motion; /datos · 390x844 · dark · reduced motion; /datos · 768x1024 · dark · reduced motion; /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion (+6 more)
- Measured: #dce4f3 x11 = #e2e7f0 x3 (15 opaque colors in all)
- Expected: one value per color, named once and reused (STD-visual-details-26: never a parallel set; preflight 2: count the values that do not come from one system)
- Evidence: `div.tp-top > div.tp-estado:nth-of-type(2) > div.tp-avatar`, `div.st-emotion-cache-k2h9z6.ef3bkur2 > div.st-emotion-cache-nufe5w.e1yqkw3v0 > div.tp-nota`, `div.st-emotion-cache-rhumdg.e1yqkw3v0 > div.tp-lab:nth-of-type(2) > div.ico:nth-of-type(1)`
- Fix: keep the most used value in each group and replace the others with it: the first step towards a palette

### La etiqueta «Límite · 10.0 °C» tapa la curva del EPS entre 55 y 60 min (su fondo cubre la línea)
`H-004` · MS-12 Things the model 'sees' that are not there · **seen**
- Where: /, todos los tamaños, light
- Expected: Ningún rótulo encima de los datos
- Evidence: `opendesigner/review/shots/home-768-light-s01.jpg`, `opendesigner/review/shots/home-1440-light-s01.jpg`
- Fix: ui/graficos.py: mover la anotación a 'top left' o quitar annotation_bgcolor

### Rótulos cortados en los gráficos de Evaluación económica: nombres en el cuadrante (Térmica Aluminizada, cipiente Aislante) y el valor S/ 1.80 de la barra
`H-005` · MS-12 Things the model 'sees' that are not there · **seen**
- Where: /economia, 390 y 768, light
- Expected: Nombres y valores completos
- Evidence: `opendesigner/review/shots/economia-390-light-s03.jpg`, `opendesigner/review/shots/economia-768-light-s01.jpg`
- Fix: Más margen lateral en los ejes (range con holgura) y textposition 'inside' en la barra más larga; nombres cortos en pantallas angostas

### Las tablas muestran la palabra None en celdas vacías (Puntaje y S/ por °C evitado del control; R cond. y U·A cond. del control)
`H-006` · MS-12 Things the model 'sees' that are not there · **seen**
- Where: / y /fisica, 1440, light
- Expected: Celda vacía o un guion
- Evidence: `opendesigner/review/shots/home-1440-light-s01.jpg`, `opendesigner/review/shots/fisica-1440-light-s01.jpg`
- Fix: Convertir None a NaN antes de st.dataframe (pd.to_numeric) o usar column_config con format y None→'—'

### En Fundamento físico aparecen dos elementos activos en la barra lateral: Fundamento físico y Guía del experimento
`H-007` · MS-12 Things the model 'sees' that are not there · **seen**
- Where: /fisica, 1440, light
- Expected: Un solo elemento marcado como página actual
- Evidence: `opendesigner/review/shots/fisica-1440-light-s00.jpg`
- Fix: Quitar el resaltado de página activa al enlace «Guía del experimento» o apuntarlo a una sección propia

### En celular la tabla de costos solo muestra Material y Precio; Usos, Limpieza, Otros y Control quedan fuera y hay que desplazar la tabla de lado
`H-008` · MS-12 Things the model 'sees' that are not there · **seen**
- Where: /economia, 390, light
- Expected: Poder editar todos los costos sin desplazamiento lateral escondido
- Evidence: `opendesigner/review/shots/economia-390-light-s00.jpg`
- Fix: En pantallas angostas, editar un material a la vez (selector + 5 campos) o columnas más estrechas con nombres cortos

### La última fila (Control) de las tablas de ranking y de resultados físicos queda cortada por la altura de la tabla
`H-009` · MS-12 Things the model 'sees' that are not there · **seen**
- Where: /economia y /fisica, 1440, light
- Expected: Todas las filas visibles
- Evidence: `opendesigner/review/shots/economia-1440-light-s01.jpg`, `opendesigner/review/shots/fisica-1440-light-s01.jpg`
- Fix: Dar a st.dataframe una altura que quepa todas las filas (height=(n+1)*35+3)

### 7 letter-spacing values
`M-MS17-1983` · MS-17 Tracking and kerning that break words · **measured** · preflight 5
- Where: /datos · 1440x900 · dark · reduced motion; /datos · 390x844 · dark · reduced motion; /datos · 768x1024 · dark · reduced motion; /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion (+6 more)
- Measured: -0.035em, -0.02em, 0.16em, 0.181em, 0.2em, 0.205em, 0.22em
- Expected: about 4: one for body, one or two for display sizes, one for capitals; each comes with its text style [inferred]
- Fix: fold letter-spacing into the type tokens and remove the per-element values

### Capitals with no tracking
`M-MS17-7795` · MS-17 Tracking and kerning that break words · **measured** · kerning.md
- Where: /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion
- Measured: 10.9 px at 0em, e.g. div.st-emotion-cache-nufe5w.e1yqkw3v0 > div > span.tp-chip
- Expected: capitals tracked open, about 0.06em
- Evidence: `div.st-emotion-cache-nufe5w.e1yqkw3v0 > div > span.tp-chip`
- Fix: letter-spacing: 0.06em

### Display text not tightened
`M-MS17-9550` · MS-17 Tracking and kerning that break words · **measured** · kerning.md
- Where: /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion
- Measured: 36.8 px at 0em, e.g. div.tp-pesos > div:nth-of-type(1) > div.n:nth-of-type(2)
- Expected: -0.01em or tighter at display sizes (about -0.01 to -0.02em, unless the face has a display cut)
- Evidence: `div.tp-pesos > div:nth-of-type(1) > div.n:nth-of-type(2)`
- Fix: letter-spacing: -0.01em

### Tracking gets looser as text gets bigger
`M-MS17-7580` · MS-17 Tracking and kerning that break words · **measured** · preflight 5
- Where: / · 1440x900 · dark · reduced motion; / · 390x844 · dark · reduced motion; / · 768x1024 · dark · reduced motion
- Measured: 28.8 px is tracked -0.02em but 21.6 px is tracked -0.027em (2 pair(s) like this)
- Expected: tracking tightens as size grows: body near 0, display text slightly negative, only capitals and tiny labels open (preflight 5; the system's tracking per size)
- Evidence: `div.st-emotion-cache-k2h9z6.ef3bkur2 > div.st-emotion-cache-nufe5w.e1yqkw3v0 > div.tp-kpi-val:nth-of-type(2)`, `div.st-emotion-cache-nufe5w.e1yqkw3v0 > div.tp-kpi-val:nth-of-type(2) > span.tp-kpi-nombre`, `div.tp-logo:nth-of-type(1) > div > div.marca:nth-of-type(1)`
- Fix: give the large sizes the tighter value; set tracking with each text style, not per element

### Padding smaller than the space between the items inside
`M-MS22-0010` · MS-22 No breathing room: text crowds its neighbours or its box · **measured** · tokens
- Where: /datos · 1440x900 · dark · reduced motion; /datos · 390x844 · dark · reduced motion; /datos · 768x1024 · dark · reduced motion; /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion (+6 more)
- Measured: div.stVerticalBlock.st-emotion-cache-1a7fwqm > div.st-emotion-cache-1vfi2s9.e399r295:nth-of-type(5) > div.stVerticalBloc: 19.59 px padding around items 24.19 px apart; div.stVerticalBlock.st-emotion-cache-1a7fwqm > div.st-emotion-cache-1vfi2s9.e399r295:nth-of-type(7) > div.stVerticalBloc: 19.59 px padding around items 204.77 px apart
- Expected: the space inside a group at most the space around it (HOW-IT-WORKS section 7: inner spacing smaller than outer)
- Evidence: `div.stVerticalBlock.st-emotion-cache-1a7fwqm > div.st-emotion-cache-1vfi2s9.e399r295:nth-of-type(5) > div.stVerticalBloc`, `div.stVerticalBlock.st-emotion-cache-1a7fwqm > div.st-emotion-cache-1vfi2s9.e399r295:nth-of-type(7) > div.stVerticalBloc`, `div.stVerticalBlock.st-emotion-cache-1p8n0nm > div.st-emotion-cache-1vfi2s9.e399r295 > div.stVerticalBlock.st-key-card_c`, `div.stVerticalBlock.st-emotion-cache-1a7fwqm > div.st-emotion-cache-1vfi2s9.e399r295:nth-of-type(8) > div.stVerticalBloc`, `div.stVerticalBlock.st-emotion-cache-1p8n0nm > div.st-emotion-cache-1vfi2s9.e399r295 > div.stVerticalBlock.st-key-card_b`, `div.stVerticalBlock.st-emotion-cache-1p8n0nm > div.st-emotion-cache-1vfi2s9.e399r295 > div.stVerticalBlock.st-key-card_f`
- Fix: raise the padding to 28 px (a step of your spacing scale) or lower the gap to 20 px (a step of your spacing scale)

### Text blocks closer than 4 px to each other
`M-MS22-1194` · MS-22 No breathing room: text crowds its neighbours or its box · **measured** · tokens
- Where: /datos · 1440x900 · dark · reduced motion; /datos · 390x844 · dark · reduced motion; /datos · 768x1024 · dark · reduced motion; /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion (+6 more)
- Measured: div.tp-logo:nth-of-type(1) > div > div.lema:nth-of-type(2) sits 0.2 px from the text of div.tp-logo:nth-of-type(1) > div > div.marca:nth-of-type(1) (vertical; the boxes are 4 px apart); div.st-emotion-cache-k2h9z6.ef3bkur2 > div.st-emotion-cache-nufe5w.e1yqkw3v0 > div.tp-titulo:nth-of-type(2) sits 1.97 px from the text of div.st-emotion-cache-k2h9z6.ef3bkur2 > div.st-emotion-cache-nufe5w.e1yqkw3v0 > div.tp-ceja:nth-of-type(1) (vertical; the boxes are 5.59 px apart); div.st-emotion-cache-k2h9z6.ef3bkur2 > div.st-emotion-cache-nufe5w.e1yqkw3v0 > div.tp-sub:nth-of-type(3) sits 0.97 px from the text of div.st-emotion-cache-k2h9z6.ef3bkur2 > div.st-emotion-cache-nufe5w.e1yqkw3v0 > div.tp-titulo:nth-of-type(2) (vertical; the boxes are 4.8 px apart)
- Expected: at least 4 px of visible space between neighbouring text, counting half the line height; usually a step of the scale
- Evidence: `div.tp-logo:nth-of-type(1) > div > div.lema:nth-of-type(2)`, `div.st-emotion-cache-k2h9z6.ef3bkur2 > div.st-emotion-cache-nufe5w.e1yqkw3v0 > div.tp-titulo:nth-of-type(2)`, `div.st-emotion-cache-k2h9z6.ef3bkur2 > div.st-emotion-cache-nufe5w.e1yqkw3v0 > div.tp-sub:nth-of-type(3)`, `button.st-emotion-cache-vo6tiu.e1aouyeq3 > div.st-emotion-cache-hqqroh.ev2q1el1 > div.st-emotion-cache-kbmnb4.ev2q1el2:n`, `button.st-emotion-cache-1hmnkzn.e1aouyeq2 > div.st-emotion-cache-hqqroh.ev2q1el1 > div.st-emotion-cache-kbmnb4.ev2q1el2:`
- Fix: add a gap from the scale between them: gap or margin-block-start of 8 px (a step of your spacing scale)

### Uneven space between sections
`M-MS24-2739` · MS-24 Uneven vertical rhythm between sections · **measured** · tokens
- Where: /datos · 1440x900 · dark · reduced motion; /datos · 390x844 · dark · reduced motion; /datos · 768x1024 · dark · reduced motion; /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion (+6 more)
- Measured: 41.98 px before div.stMainBlockContainer.block-container:nth-of-type(1) > div.stVerticalBlock.st-emotion-cache-1a7fwqm > div.stElementCo; 24.94 px before div.stMainBlockContainer.block-container:nth-of-type(1) > div.stVerticalBlock.st-emotion-cache-1a7fwqm > div.st-emotion-; 32 px before div.stMainBlockContainer.block-container:nth-of-type(1) > div.stVerticalBlock.st-emotion-cache-1a7fwqm > div.st-emotion-
- Expected: the same space between sections down the page, or a bigger one only where a new part starts, on purpose
- Evidence: `div.stMainBlockContainer.block-container:nth-of-type(1) > div.stVerticalBlock.st-emotion-cache-1a7fwqm > div.stElementCo`, `div.stMainBlockContainer.block-container:nth-of-type(1) > div.stVerticalBlock.st-emotion-cache-1a7fwqm > div.st-emotion-`
- Fix: one section spacing token, for example padding-block: 32 px (a step of your spacing scale); check each larger break is meant

### Boxes side by side with different corner radii
`M-MS25-2080` · MS-25 Boxes that sit together with different corner radii · **measured** · preflight 45
- Where: /datos · 1440x900 · dark · reduced motion; /datos · 390x844 · dark · reduced motion; /datos · 768x1024 · dark · reduced motion; / · 1440x900 · dark · reduced motion; / · 390x844 · dark · reduced motion; / · 768x1024 · dark · reduced motion
- Measured: div.stElementContainer.element-container:nth-of-type(2) > div.stButtonGroup.st-emotion-cache-68zbsl > div.st-emotion-cac: button.st-emotion-cache-1mcz6sg.e1 8 px, button.st-emotion-cache-1mcz6sg.e1 0 px, button.st-emotion-cache-1mcz6sg.e1 0 px
- Expected: one radius for boxes that sit together as a set
- Evidence: `div.stButtonGroup.st-emotion-cache-68zbsl > div.st-emotion-cache-1eddh7x.e1aouyeq26 > button.st-emotion-cache-1mcz6sg.e1`
- Fix: use one radius token for the set

### Text runs out of its box
`M-ST12-4939` · ST-12 Text runs out of its box or is cut off by the box around it · **measured**
- Where: /fisica · 1440x900 · dark · reduced motion; /fisica · 390x844 · dark · reduced motion; /fisica · 768x1024 · dark · reduced motion
- Measured: semantics > mrow > mo:nth-of-type(6) (text): "−" goes 10 px below a 1 px tall box; msup > mrow > mo (text): "−" goes 7 px below a 1 px tall box; semantics > mrow > mo:nth-of-type(1) (text): "⋅" goes 11 px below a 2 px tall box; semantics > mrow > mo:nth-of-type(2) (text): "⋅" goes 11 px below a 2 px tall box
- Expected: every line of text inside its own box, at 320 px, at 200% text and with longer words
- Evidence: `semantics > mrow > mo:nth-of-type(6)`, `msup > mrow > mo`, `semantics > mrow > mo:nth-of-type(1)`, `semantics > mrow > mo:nth-of-type(2)`
- Fix: let the text wrap: remove the fixed width or height and white-space: nowrap, set min-width: 0 on flex and grid children, and overflow-wrap: anywhere for long words

### Text cut off by the box around it when every word is 30% longer (a German stand-in)
`M-ST14-7615` · ST-14 Copy that only fits in English · **measured**
- Where: / · 1440x900 · dark · stress: translate · reduced motion
- Measured: span > div.stMarkdownEllipsis.st-emotion-cache-1bja2d5 > p (label): "Desviaciónung estándarung" loses 32.97 px inside div.st-emotion-cache-3ye0ev.e1hn2pbo3 > span > div.stMarkdownEllipsis.st-emotion-cache-1bja2d5 (overflow: hidden); g > g:nth-of-type(4) > text (text): "Controlung (Sinu empaqueung)" loses 17.89 px inside div.plot-container.plotly > div.user-select-none.svg-container > svg:nth-of-type(2) (overflow: hidden)
- Expected: no text cut by a parent's overflow: hidden; nobody can scroll to it
- Evidence: `span > div.stMarkdownEllipsis.st-emotion-cache-1bja2d5 > p`, `g > g:nth-of-type(4) > text`
- Fix: remove the fixed height or overflow: hidden on the parent, or let it grow (min-height instead of height)

### Text runs out of its box when every word is 30% longer (a German stand-in)
`M-ST14-4059` · ST-14 Copy that only fits in English · **measured**
- Where: / · 1440x900 · dark · stress: translate · reduced motion
- Measured: span.st-emotion-cache-1ylwq8i.evng2kd2:nth-of-type(2) > div.st-emotion-cache-1f2ydu4.e1yqkw3v0 > p (text): "Datosun delu experimentoungsun · 156" goes 45.22 px past a 210.41 px wide box; span.st-emotion-cache-1ylwq8i.evng2kd2 > div.st-emotion-cache-116j2w.e1yqkw3v0 > p (text): "Explorarung lau evaluaciónungu →" goes 6.67 px past a 213.27 px wide box
- Expected: every line of text inside its own box, at 320 px, at 200% text and with longer words
- Evidence: `span.st-emotion-cache-1ylwq8i.evng2kd2:nth-of-type(2) > div.st-emotion-cache-1f2ydu4.e1yqkw3v0 > p`, `span.st-emotion-cache-1ylwq8i.evng2kd2 > div.st-emotion-cache-116j2w.e1yqkw3v0 > p`
- Fix: let the text wrap: remove the fixed width or height and white-space: nowrap, set min-width: 0 on flex and grid children, and overflow-wrap: anywhere for long words

### One block lacks a control its twins have
`M-ST15-2625` · ST-15 One block lacks a control its twins have · **measured**
- Where: /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion
- Measured: 2 of 4 block divs have "download as csv"; missing on div.stVerticalBlock.st-key-card_cuad > div.stElementContainer.element-container:nth-of-type(2) > div.st-emotion-cache-uw, div.stVerticalBlock.st-key-card_barras > div.stElementContainer.element-container:nth-of-type(2) > div.st-emotion-cache-
- Expected: blocks of one kind offer the same controls
- Evidence: `div.stVerticalBlock.st-key-card_cuad > div.stElementContainer.element-container:nth-of-type(2) > div.st-emotion-cache-uw`
- Fix: render the control from the block's component, not per page; or say why this one differs

### A transition animates layout
`M-TM09-6116` · TM-09 Motion that is slow or janky · **measured** · STD-enter-exit-origin-24
- Where: /datos · 1440x900 · dark · reduced motion; /datos · 390x844 · dark · reduced motion; /datos · 768x1024 · dark · reduced motion; /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion (+7 more)
- Measured: section#stSidebar: max-width over 300 ms
- Expected: animate transform and opacity; layout properties cause reflow and jank
- Evidence: `section#stSidebar`
- Fix: animate transform: scale/translate, or measure and animate to a fixed height

### A transition animates layout
`M-TM09-6116` · TM-09 Motion that is slow or janky · **measured** · STD-enter-exit-origin-24
- Where: /datos · 1440x900 · dark · reduced motion; /economia · 1440x900 · dark · reduced motion; /fisica · 1440x900 · dark · reduced motion; / · 1440x900 · dark · stress: translate · reduced motion; / · 1440x900 · dark · reduced motion
- Measured: div.st-emotion-cache-1e2j9e0.e1ccv4an2:nth-of-type(1) > div.st-emotion-cache-10p9htt.e1ccv4an4:nth-of-type(1) > div.st-e: left over 300 ms
- Expected: animate transform and opacity; layout properties cause reflow and jank
- Evidence: `div.st-emotion-cache-1e2j9e0.e1ccv4an2:nth-of-type(1) > div.st-emotion-cache-10p9htt.e1ccv4an4:nth-of-type(1) > div.st-e`
- Fix: animate transform: scale/translate, or measure and animate to a fixed height

## Notes (11)

### Button labels that do not start with a verb
`M-CP02-2529` · CP-02 A button label that is not a verb · **measured** · DC-L06-22
- Where: /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion; / · 1440x900 · dark · reduced motion; / · 390x844 · dark · reduced motion; / · 768x1024 · dark · reduced motion
- Measured: div.stElementContainer.element-container:nth-of-type(7) > div.stButton.st-emotion-cache-8atqhb > button.st-emotion-cache: "play_arrowAnalizar alternativas"
- Expected: a button says what it does: a verb first ("Compare prices", not "Pricing details")
- Evidence: `div.stElementContainer.element-container:nth-of-type(7) > div.stButton.st-emotion-cache-8atqhb > button.st-emotion-cache`, `div.stElementContainer.element-container:nth-of-type(2) > div.stButton.st-emotion-cache-8atqhb > button.st-emotion-cache`
- Fix: start with the action; a word list decided this, so read each one

### Before launch: share image, favicon or indexing
`M-EN09-0433` · EN-09 Share card and llms.txt out of step with the page · **measured**
- Where: /datos · 1440x900 · dark · reduced motion; /datos · 390x844 · dark · reduced motion; /datos · 768x1024 · dark · reduced motion; /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion (+6 more)
- Measured: missing a share image (og:image), a meta description
- Expected: a public page has a share image, a favicon and a description; noindex only on drafts

### Controls placed outside the page box
`M-IN08-2014` · IN-08 In the DOM is not the same as seen or reachable · **measured**
- Where: /datos · 1440x900 · dark · reduced motion; /datos · 390x844 · dark · reduced motion; /datos · 768x1024 · dark · reduced motion; /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion (+7 more)
- Measured: div.stApp.stAppEmbeddingId-tooaizs7qmrf > div.stAppViewContainer.appview-container > a.st-emotion-cache-hmusyd.eksftaj1
- Expected: a skip link that appears on focus is fine; anything else is off-canvas content
- Evidence: `div.stApp.stAppEmbeddingId-tooaizs7qmrf > div.stAppViewContainer.appview-container > a.st-emotion-cache-hmusyd.eksftaj1`, `div.stPageLink > div.st-emotion-cache-1ofqig9.evng2kd0 > a.st-emotion-cache-1ew5you.evng2kd1`, `div.stPageLink > div.st-emotion-cache-1ofqig9.evng2kd0 > a.st-emotion-cache-1cfcdwv.evng2kd1`, `div.stApp.stAppEmbeddingId-tooanuy05zmo > div.stAppViewContainer.appview-container > a.st-emotion-cache-hmusyd.eksftaj1`, `div.stApp.stAppEmbeddingId-tooa2utonokk > div.stAppViewContainer.appview-container > a.st-emotion-cache-hmusyd.eksftaj1`, `div.stPopover.st-emotion-cache-8atqhb > div > button.st-emotion-cache-1hmnkzn.e1aouyeq2`
- Fix: Tab to it and confirm it appears

### 3 color families on one page
`M-MS08-1758` · MS-08 Color drift from the tokens · **measured** · DC-L01-08
- Where: /datos · 1440x900 · dark · reduced motion; /datos · 768x1024 · dark · reduced motion; /economia · 1440x900 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion; /fisica · 1440x900 · dark · reduced motion; /fisica · 768x1024 · dark · reduced motion (+2 more)
- Measured: blue (#18233f, #a9b8d6, #1d428a) x22; orange (#f28c35) x3; green (#3baa6a) x1
- Expected: grays, one accent with one job, and status colors (DC-L01-08), with the danger color only on the part that is going wrong (making.md section 12: "More visual" means more information, not more colour)
- Evidence: `div.tp-top > div.tp-miga:nth-of-type(1) > b`, `div.tp-logo:nth-of-type(1) > div > div.lema:nth-of-type(2)`, `div.tp-estado:nth-of-type(2) > span > span.dot`
- Fix: pick the one accent; turn decorative colors gray; keep status colors for status, and red only on the part that is going wrong

### Negative margins in use
`M-MS11-5224` · MS-11 Overlaps, clipping and stacking · **measured**
- Where: /datos · 1440x900 · dark · reduced motion; /datos · 390x844 · dark · reduced motion; /datos · 768x1024 · dark · reduced motion; /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion (+7 more)
- Measured: div.stApp.stAppEmbeddingId-tooaizs7qmrf > div.stAppViewContainer.appview-container > a.st-emotion-cache-hmusyd.eksftaj1 marginTop -1 px
- Expected: usually a workaround that overlaps neighbours
- Evidence: `div.stApp.stAppEmbeddingId-tooaizs7qmrf > div.stAppViewContainer.appview-container > a.st-emotion-cache-hmusyd.eksftaj1`, `div.stApp.stAppEmbeddingId-tooanuy05zmo > div.stAppViewContainer.appview-container > a.st-emotion-cache-hmusyd.eksftaj1`, `div.stApp.stAppEmbeddingId-tooa2utonokk > div.stAppViewContainer.appview-container > a.st-emotion-cache-hmusyd.eksftaj1`

### «Priorizar costo» y «Priorizar temperatura» no quedan alineados: en celular van en líneas distintas y en escritorio con distinta altura
`H-010` · MS-12 Things the model 'sees' that are not there · **seen**
- Where: /economia, 390 y 1440, light
- Expected: Ambos rótulos en una línea bajo los extremos del deslizador
- Evidence: `opendesigner/review/shots/economia-390-light-s01.jpg`, `opendesigner/review/shots/economia-1440-light-s00.jpg`
- Fix: Un solo bloque HTML con display:flex; justify-content:space-between

### En pantallas táctiles las barras de herramientas de Plotly y de las tablas quedan siempre visibles y se montan sobre el gráfico y los títulos
`H-011` · MS-12 Things the model 'sees' that are not there · **seen**
- Where: todas las páginas, 390, light
- Expected: Herramientas que no tapen títulos
- Evidence: `opendesigner/review/shots/home-390-light-s03.jpg`, `opendesigner/review/shots/datos-390-light-s00.jpg`
- Fix: config={'displayModeBar': False} en celular o margen superior en las tarjetas

### En tablet (768 px) los cuatro indicadores van uno debajo de otro y ocupan casi una pantalla
`H-012` · MS-12 Things the model 'sees' that are not there · **seen**
- Where: /, 768, light
- Expected: 2 x 2 en tablet
- Evidence: `opendesigner/review/shots/home-768-light-s00.jpg`
- Fix: ui/estilo.py: bajar el corte de una columna de 900 px a 560 px

### La barra superior se parte en dos líneas en celular (migas de pan y Motor Python activo)
`H-013` · MS-12 Things the model 'sees' that are not there · **seen**
- Where: todas las páginas, 390, light
- Expected: Una línea
- Evidence: `opendesigner/review/shots/home-390-light-s00.jpg`
- Fix: Ocultar «Motor Python activo» por debajo de 480 px

### Siblings of one kind with two different gaps
`M-MS23-8003` · MS-23 Items of one kind spaced unevenly · **measured** · tokens
- Where: / · 1440x900 · dark · reduced motion; / · 390x844 · dark · reduced motion; / · 768x1024 · dark · reduced motion
- Measured: main#stMain > div.stMainBlockContainer.block-container:nth-of-type(1) > div.stVerticalBlock.st-emotion-cache-1a7fwqm: div items 16, 32, 16, 32, 32 px apart
- Expected: one gap, or a larger one only where a new group starts
- Evidence: `main#stMain > div.stMainBlockContainer.block-container:nth-of-type(1) > div.stVerticalBlock.st-emotion-cache-1a7fwqm`
- Fix: if it is not a group break, one gap on the parent (32 px (a step of your spacing scale))

### canvas on the page: its motion is not in the animation list
`M-TM05-3836` · TM-05 Motion the page cannot list · **measured**
- Where: /datos · 1440x900 · dark · reduced motion; /datos · 390x844 · dark · reduced motion; /datos · 768x1024 · dark · reduced motion; /economia · 1440x900 · dark · reduced motion; /economia · 390x844 · dark · reduced motion; /economia · 768x1024 · dark · reduced motion (+7 more)
- Measured: 6 found
- Expected: sample frames over time and look at them; the probe cannot read this motion

## Coverage

| Cell | Status | Evidence |
|---|---|---|
| `/|390x844|light` | done | opendesigner/review/probes/home-390-light.json, opendesigner/review/shots/home-390-light-carga-menu.jpg, opendesigner/review/shots/home-390-light-s00.jpg |
| `/|768x900|light` | done | opendesigner/review/probes/home-768-light.json, opendesigner/review/shots/home-768-light-s00.jpg, opendesigner/review/shots/home-768-light-s01.jpg |
| `/|1440x900|light` | done | opendesigner/review/probes/home-1440-light.json, opendesigner/review/shots/home-1440-light-s00.jpg, opendesigner/review/shots/home-1440-light-s01.jpg |
| `/datos|390x844|light` | done | opendesigner/review/probes/datos-390-light.json, opendesigner/review/shots/datos-390-light-s00.jpg, opendesigner/review/shots/datos-390-light-s01.jpg |
| `/datos|768x900|light` | done | opendesigner/review/probes/datos-768-light.json, opendesigner/review/shots/datos-768-light-s00.jpg |
| `/datos|1440x900|light` | done | opendesigner/review/probes/datos-1440-light.json, opendesigner/review/shots/datos-1440-light-s00.jpg |
| `/economia|390x844|light` | done | opendesigner/review/probes/economia-390-light.json, opendesigner/review/shots/economia-390-light-s00.jpg, opendesigner/review/shots/economia-390-light-s01.jpg |
| `/economia|768x900|light` | done | opendesigner/review/probes/economia-768-light.json, opendesigner/review/shots/economia-768-light-s00.jpg, opendesigner/review/shots/economia-768-light-s01.jpg |
| `/economia|1440x900|light` | done | opendesigner/review/probes/economia-1440-light.json, opendesigner/review/shots/economia-1440-light-s00.jpg, opendesigner/review/shots/economia-1440-light-s01.jpg |
| `/fisica|390x844|light` | done | opendesigner/review/probes/fisica-390-light.json, opendesigner/review/shots/fisica-390-light-s00.jpg, opendesigner/review/shots/fisica-390-light-s01.jpg |
| `/fisica|768x900|light` | done | opendesigner/review/probes/fisica-768-light.json, opendesigner/review/shots/fisica-768-light-s00.jpg |
| `/fisica|1440x900|light` | done | opendesigner/review/probes/fisica-1440-light.json, opendesigner/review/shots/fisica-1440-light-s00.jpg, opendesigner/review/shots/fisica-1440-light-s01.jpg |
| `task:/|scroll-walk` | done | opendesigner/review/shots |
| `task:/|focus-walk` | done | opendesigner/review/focus/focus-home-390.json |
| `task:/|hover-and-press` | skipped | No se hizo la pasada de hover por tiempo; se revisó el foco con teclado en la Vista general |
| `task:/|states-and-data` | skipped | No se probaron datos vacíos, con error o muy largos en esta pasada |
| `task:/|motion` | skipped | Solo hay transiciones propias de Streamlit (barra lateral); no hay animaciones de la app |
| `task:/|stress-text` | done | opendesigner/review/probes/home-1440-light-stress-translate.json |
| `task:/|reduced-motion` | blocked | El navegador integrado no puede simular «reducir movimiento» |
| `task:/|forced-colors` | blocked | El navegador integrado no puede simular colores forzados |
| `task:/|console-and-network` | done | Sin errores en la consola al cargar y recorrer las páginas |
| `task:/|letter-reveals` | skipped | La app no tiene textos que aparecen letra por letra |
| `task:/|text-pixels` | skipped | No hay texto sobre fotos ni degradados |
| `task:/|floating-bars` | skipped | No hay barras fijas además de la barra lateral, revisada aparte |
| `task:/|toggles` | skipped | Solo se operó el selector de vista en la Vista general |
| `task:/datos|scroll-walk` | done | opendesigner/review/shots |
| `task:/datos|focus-walk` | skipped | Recorrido con Tab hecho solo en la Vista general |
| `task:/datos|hover-and-press` | skipped | No se hizo la pasada de hover por tiempo; se revisó el foco con teclado en la Vista general |
| `task:/datos|states-and-data` | skipped | No se probaron datos vacíos, con error o muy largos en esta pasada |
| `task:/datos|motion` | skipped | Solo hay transiciones propias de Streamlit (barra lateral); no hay animaciones de la app |
| `task:/datos|stress-text` | skipped | Prueba de texto largo hecha solo en la Vista general |
| `task:/datos|reduced-motion` | blocked | El navegador integrado no puede simular «reducir movimiento» |
| `task:/datos|forced-colors` | blocked | El navegador integrado no puede simular colores forzados |
| `task:/datos|console-and-network` | done | Sin errores en la consola al cargar y recorrer las páginas |
| `task:/datos|letter-reveals` | skipped | La app no tiene textos que aparecen letra por letra |
| `task:/datos|text-pixels` | skipped | No hay texto sobre fotos ni degradados |
| `task:/datos|floating-bars` | skipped | No hay barras fijas además de la barra lateral, revisada aparte |
| `task:/datos|toggles` | skipped | Solo se operó el selector de vista en la Vista general |
| `task:/economia|scroll-walk` | done | opendesigner/review/shots |
| `task:/economia|focus-walk` | skipped | Recorrido con Tab hecho solo en la Vista general |
| `task:/economia|hover-and-press` | skipped | No se hizo la pasada de hover por tiempo; se revisó el foco con teclado en la Vista general |
| `task:/economia|states-and-data` | skipped | No se probaron datos vacíos, con error o muy largos en esta pasada |
| `task:/economia|motion` | skipped | Solo hay transiciones propias de Streamlit (barra lateral); no hay animaciones de la app |
| `task:/economia|stress-text` | skipped | Prueba de texto largo hecha solo en la Vista general |
| `task:/economia|reduced-motion` | blocked | El navegador integrado no puede simular «reducir movimiento» |
| `task:/economia|forced-colors` | blocked | El navegador integrado no puede simular colores forzados |
| `task:/economia|console-and-network` | done | Sin errores en la consola al cargar y recorrer las páginas |
| `task:/economia|letter-reveals` | skipped | La app no tiene textos que aparecen letra por letra |
| `task:/economia|text-pixels` | skipped | No hay texto sobre fotos ni degradados |
| `task:/economia|floating-bars` | skipped | No hay barras fijas además de la barra lateral, revisada aparte |
| `task:/economia|toggles` | skipped | Solo se operó el selector de vista en la Vista general |
| `task:/fisica|scroll-walk` | done | opendesigner/review/shots |
| `task:/fisica|focus-walk` | skipped | Recorrido con Tab hecho solo en la Vista general |
| `task:/fisica|hover-and-press` | skipped | No se hizo la pasada de hover por tiempo; se revisó el foco con teclado en la Vista general |
| `task:/fisica|states-and-data` | skipped | No se probaron datos vacíos, con error o muy largos en esta pasada |
| `task:/fisica|motion` | skipped | Solo hay transiciones propias de Streamlit (barra lateral); no hay animaciones de la app |
| `task:/fisica|stress-text` | skipped | Prueba de texto largo hecha solo en la Vista general |
| `task:/fisica|reduced-motion` | blocked | El navegador integrado no puede simular «reducir movimiento» |
| `task:/fisica|forced-colors` | blocked | El navegador integrado no puede simular colores forzados |
| `task:/fisica|console-and-network` | done | Sin errores en la consola al cargar y recorrer las páginas |
| `task:/fisica|letter-reveals` | skipped | La app no tiene textos que aparecen letra por letra |
| `task:/fisica|text-pixels` | skipped | No hay texto sobre fotos ni degradados |
| `task:/fisica|floating-bars` | skipped | No hay barras fijas además de la barra lateral, revisada aparte |
| `task:/fisica|toggles` | skipped | Solo se operó el selector de vista en la Vista general |

## Re-run

Fix, then run the same cells again and `review.py check` on the new probe files: it prints what was resolved and what is new. Do not mark a cell done from memory.


---

## Re-verificación después de las correcciones (2026-11-17)

Se corrigió el código y se volvieron a medir las mismas 12 celdas (4 páginas × 390, 768 y 1440 px) en una instancia nueva de la app. Los hallazgos que se registraron a mano arriba (los que dicen *operated* o *seen*) siguen apareciendo en la lista porque la herramienta no tiene un estado «resuelto»; esta tabla dice cómo quedó cada uno.

| Hallazgo | Estado | Evidencia |
|---|---|---|
| Menú lateral tapa 300 de 390 px en celular | **Resuelto**: `initial_sidebar_state="auto"`; medido 0 px tapados al cargar | `shots/despues-home-390.jpg` |
| «Promedios» fuera de la tarjeta (93 px ocultos) | **Resuelto**: el selector pasa a una segunda fila (`wrap=True`); medido 60–163 px dentro de 330 px | `shots/despues-home-390.jpg` |
| Fórmulas cortadas en Fundamento físico | **Resuelto**: ecuación del modelo en dos líneas y tarjetas apiladas bajo 1350 px; medido 0 fórmulas con desborde en 390 y 768 px | `shots/despues-fisica-768.jpg` |
| Rótulo «Límite» tapa la curva del EPS | **Resuelto**: rótulo arriba a la izquierda y sin fondo | `shots/despues-home-768.jpg` |
| Rótulos cortados en los gráficos de costos | **Resuelto**: nombres hacia el centro, más margen y valor de la barra dentro; el recorte medido de 2.8 px desapareció | `shots/despues-economia-390-graficos.jpg` |
| «None» en las tablas | **Resuelto**: celdas vacías con «—» | `shots/despues-economia-1440.jpg`, `shots/despues-fisica-1440.jpg` |
| Dos elementos activos en la barra lateral | **Resuelto**: «Guía del experimento» ya no se marca | `shots/despues-fisica-1440.jpg` |
| Tabla de costos incómoda en celular | **Mejorado**: columna Material fija, columnas angostas y un aviso «Desliza la tabla…» solo en pantallas angostas. Sigue necesitando deslizar en 390 px | `shots/despues-economia-390-tabla.jpg` |
| Última fila de tablas cortada | **Resuelto**: altura calculada para todas las filas | `shots/despues-economia-1440.jpg` |
| «Priorizar costo / temperatura» desalineados | **Resuelto**: una sola línea con los extremos a cada lado | — |
| Barras de herramientas sobre los gráficos en táctil | **Resuelto en gráficos** (`displayModeBar: False`); la barra de las tablas es de Streamlit y se mantiene | — |
| Indicadores en una columna en tablet | **Resuelto**: 2 × 2 hasta 560 px | `shots/despues-home-768.jpg` |
| Barra superior en dos líneas en celular | **Resuelto**: «Motor Python activo» se oculta bajo 480 px | `shots/despues-home-390.jpg` |
| Subtítulos grises con contraste 4.23:1 | **Resuelto** (medido): `st.caption` usa #5F6B85 (5.35:1) | — |
| «Configurar experimento» cortado en 768 px | **Resuelto** (medido) | `shots/despues-home-768.jpg` |

**Además:** R² y U·A se mostraban redondeados (1.00) en la tabla física; ahora usan 4 decimales (0.9994).

### Los 4 errores medidos que quedan

1. **Anillo de foco eliminado** y 2. **objetivo de 1 × 1 px**: son el mismo enlace interno de Streamlit (`a.st-emotion-cache-hmusyd`, de 1 × 1 px y fuera de la vista), no un control de la app. No se puede cambiar sin modificar Streamlit.
3. **Contraste 1:1** en Evaluación económica: es el número «60» encima del deslizador. Se lee bien sobre fondo blanco (ver capturas); la medición toma como fondo el círculo del deslizador. Falso positivo.
4. **Punto naranja del título (2.28:1)**: es el acento decorativo del logo. Se mantiene a propósito; no es texto que haya que leer.

### Lo que sigue sin revisar

Igual que antes: «reducir movimiento» y «colores forzados» (el navegador integrado no los simula), el paso del mouse, datos vacíos o con error, y el recorrido con teclado y la prueba de textos largos fuera de la Vista general. Las advertencias de práctica (cantidad de tamaños y pesos de letra, espaciados fuera de la grilla de 4 px) son en su mayoría estilos internos de Streamlit y quedan como sugerencias.
