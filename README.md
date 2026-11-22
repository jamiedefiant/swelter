# SWELTER $500 product test

Five landing pages, one product (zero-sugar electrolyte sticks), five different promises. $100 of Meta ads per page. The winner is the page with the most add-to-carts, boxes per cart and reservations per dollar.

- `docs/` is the live site (GitHub Pages). Pages: `/hydrate/ /creatine/ /collagen/ /focus/ /night/`
- `build.py` regenerates every page and ad from the `VARIANTS` list. Edit copy there, run `python3 build.py`, commit, push.
- `docs/assets/config.js` holds the Meta Pixel ID and the Google Form that logs events.
- `ads/` holds ad creative (HTML source + PNG exports).
- No payment is ever taken. Checkout opens a "reserve, no charge" step that collects an email.
