# McDonalds KVS Simulator

Welcome to Mcdonalds KVS Simulator! This project is made due to my poor performance being an initiator within a few months of starting a part time job at Mcdonalds. To somewhat simulate what it would be like during a rush hour, this program is configured to keep pumping in orders no matter what. Unfortunately, i am unable to create a minigame like the one they give during training. But with imagination, this simple simulator should be more than enough to simulate and remember the recipes.

This program is currently configured for the McDonalds Argentina kitchen menu (verified against mcdonalds.com.ar), plus two built-in training modes — Modo Memoria and Modo Enfoque — that embed evidence-based memorization techniques directly into the simulator (see `METODO-MEMORIA.md`). If you would like to change the menu, see 'Configuration' below.

  

## WARNING

THIS PROJECT IS EXPRESSLY INDEPENDENT AND HAS NO AFFILIATION, ASSOCIATION, OR ENDORSEMENT BY MCDONALD'S CORPORATION OR ANY OF ITS SUBSIDIARIES. MCDONALD'S IS NOT RESPONSIBLE FOR, AND DOES NOT ENDORSE OR SUPPORT, THIS PROJECT OR ITS CONTENTS.

  

## Configuration

All available configurations can be done inside './lib/generateorder.js'.
|Parameter|Explanation|Type|Default Value|
|--|--|--|--|
|maxOrderLength|Maximum amount of items a single order could have|Int|5|
|mixOrderLength|Minimum amount of items a single order could have|Int|1|
|singleItemMaxMount|Maximum amount of a single item could have in an order|Int|4|
|singleItemMinAmount|Minimum amount of a single item could have in an order|Int|1|
|Itemlist|List of items that can be put in queue|Array (String)|Mcdonalds Argentina kitchen menu|
|OrderTypes|Type of order (Only for display)|Array (String)|Drive Through, Bag, Tray, Delivery|
|OrderStorage|Current order state (Only for display|Array (String)|Paid, Stored|

`maxOrderlength` is a ceiling, not a flat range: order length ramps up progressively from `START_ORDER_LENGTH` (2 items, right at the top of `generateorder.js`) by one extra item every `LEVELS_PER_EXTRA_ITEM` levels (8), until it reaches `maxOrderlength` around level 25. `singleItemMaxAmount` ramps the same way — it starts fixed at 1 (a single "Big Mac", not "3 Big Mac") and only starts allowing higher quantities every `LEVELS_PER_EXTRA_QTY` levels (6). `level` goes up by 1 per order **served**, not per minute, so both of these are paced in served orders — a couple of Turno Intensivo runs' worth of practice, not one. This is intentional — orders start short and simple like a real onboarding shift and only get busier with sustained practice, instead of throwing a 4-item order with big quantities at you from level 1.

  
  

## Shortcuts

List of available shortcuts to use within program

### `enter`

Serves the order. Depending on if the side is on or off, when you press enter, an order will be served while another will be added to the queue.

### `p`

Toggles side on or off.

### `o`

Pushes a new order to the queue. Depending on if the side is on or off, when you press 'o', an order will not be pushed in to the queue.

### `m`

Toggles **Modo Memoria**. Each order hides itself a few seconds after it spawns (less time as your level goes up), forcing active recall instead of re-reading. Hold `Espacio` to peek at everything that's currently hidden for 1.5s — every peek is logged.

### `f`

Toggles **Modo Enfoque**. New orders are drawn only from the items you peek/miss the most (falling back to a curated list of classic look-alike items) so you can drill exactly what's failing, per the interference/discrimination technique in `METODO-MEMORIA.md`.

### `Espacio` (Space)

Peeks at every currently-hidden order for 1.5s while Modo Memoria is on, then a 4s cooldown before you can peek again. Only does something while Modo Memoria is active.

### `e`

Toggles **Modo Estación**. Before serving an order whose items have a known real recipe, you must pick the correct bread and condiment steps from a mix of real-and-decoy options, sourced from the official McDonald's training guide. See `ESTACION-INICIADOR.md`.

### `b`

Toggles **Modo Panes**, the lightweight version covering the whole menu: before serving, pick just the bread type (no condiments) for each item that has one. Combines with Modo Estación without asking about the same item twice.

### `c`

Opens/closes **Modo Cronómetro**, a self-contained drill separate from the order queue (it doesn't touch `sideOn`/`orders`, and while it's open the other shortcuts are inert so you don't accidentally serve or toggle something behind it). One item at a time: you see it for 2 seconds, it disappears completely, and you pick its bread from memory. Real elapsed time is measured from the moment the item appears to the moment you click an answer, against a 5-second target — that target is a personal goal to train toward, not a number from the official guide (the guide's own 5s standard is about monitor-alarm reaction time, a different thing; see the shift-summary text). Attempts/hits/best time persist across reloads (`localStorage`, key `mcdonalds-kvs:cronometro`).

### `v`

Opens/closes **Modo Evaluación**, a bounded, formal exam (as opposed to Cronómetro's open-ended practice loop) — same isolation rules as Cronómetro (mutually exclusive with it and with Reconocimiento Visual, other shortcuts inert while it's open). It's 10 fixed questions: 7 are the same "memorize + pick the bread in 5s or less" drill as Cronómetro, and 3 are multiple-choice questions on celiac (SIN TACC) order procedure — who's allowed to prepare one, what till key sequence to use, cross-contamination rules, pan celíaco thaw/expiry times — sourced from the official "GE Opciones para Celíacos" guide (Oct. 2021), see `src/lib/celiacos.js` for the verified question bank with citations. Ends with a pass/fail score (70% threshold, a practice convention, not a number from either guide) and keeps a history of past attempts (`localStorage`, key `mcdonalds-kvs:evaluaciones`).

### `r`

Opens/closes **Modo Reconocimiento Visual**, same isolation rules as the other two (mutually exclusive with Cronómetro and Evaluación, other shortcuts inert while it's open). Unlike the other modes, this one isn't testing order/recipe recall — it's a visual-memory drill built directly from cognitive-science research on how visual expertise actually forms, since generic "brain training" (n-back, dot-grids) has poor evidence of transferring to real skills:

- Visual pattern expertise is domain-specific (chess-expert chunking studies, radiologist perceptual-expertise research) — so this drill flashes the *real* `OrderCard` component, not an abstract shape, to train recognition of the actual ticket you'll be reading on shift.
- Two round types, both established experimental paradigms: **recognition memory** ("was this product on the ticket?", with confusable-menu-item distractors, not random ones) and **change detection** (Luck & Vogel's paradigm — you see the ticket again and say whether anything changed, with real "nothing changed" trials mixed in so guessing "yes" doesn't work).
- Item count ramps from 2 up to a hard cap of 4, and flash duration shrinks as you level up — both calibrated to the well-replicated ~3–4 item visual working-memory capacity limit (Luck & Vogel), not an arbitrary number.
- Items you get wrong are weighted to reappear more (same interference/discrimination idea as Modo Enfoque, its own separate table). Attempts/accuracy persist across reloads (`localStorage`, keys `mcdonalds-kvs:visual-stats` and `mcdonalds-kvs:visual-confusion`).

See `METODO-MEMORIA.md` for the full science-backed rationale behind the memory modes and a suggested practice routine, and `ESTACION-INICIADOR.md` for the real station procedure Modo Estación is built from.

  

## `standalone.html` — versión sin instalación

`standalone.html` es una copia funcionalmente equivalente de toda la app (menú, Turno Intensivo, Modo Memoria, Modo Enfoque, Modo Estación, Modo Panes) empaquetada en un único archivo HTML. No necesita `npm install`, `npm start`, Node ni conexión a internet: se abre haciendo doble clic y funciona directamente en el navegador. React, ReactDOM y el CSS de Tailwind ya usado por la app están incluidos dentro del archivo (no se cargan desde ningún CDN), así que también funciona sin wifi.

Se genera desde el mismo código fuente (`src/`) compilando el JSX con Babel y generando el CSS de Tailwind real para las clases usadas — no es una reescritura aparte a mantener a mano. Si cambia algo en `src/`, `standalone.html` hay que regenerarlo (no se actualiza solo).

## Available Scripts

  

In the project directory, you can run:

  

### `npm start`

  

Runs the app in the development mode.\

Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

  

The page will reload when you make changes.\

You may also see any lint errors in the console.

  

### `npm run build`

  

Builds the app for production to the `build` folder.\

It correctly bundles React in production mode and optimizes the build for the best performance.

  

The build is minified and the filenames include the hashes.\

Your app is ready to be deployed!