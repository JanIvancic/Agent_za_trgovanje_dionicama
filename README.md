# Automatizirani agent za trgovanje dionicama

Ovaj projekt implementira automatizirani agent za trgovanje dionicama. Agent koristi RSI (Relative Strength Index) kao indikator za odlučivanje kada kupiti ili prodati dionice. Također koristi stop-loss mehanizam za smanjenje potencijalnih gubitaka.

## Glavne značajke

- **Izbor dionica**: Agent prati izabrani set dionica definiran u listi `SYMBOLS`.
- **RSI**: RSI se koristi za identifikaciju prekupljenih i preprodanih uvjeta. Dionica se kupuje kada RSI padne ispod `RSI_BUY_THRESHOLD` i prodaje kada pređe `RSI_SELL_THRESHOLD`.
- **Stop-loss**: Kada tržišna cijena dionice padne ispod definiranog praga u odnosu na prosječnu cijenu ulaza, stop-loss mehanizam automatski prodaje dionice.
- **Provjera vremena tržišta**: Agent redovito provjerava je li tržište otvoreno koristeći `is_market_open()` funkciju. Ako je tržište zatvoreno, agent pauzira i čeka da se ponovno otvori.
- **Automatska prodaja pri zatvaranju tržišta**: Agent automatski prodaje sve dionice koje drži 5 minuta prije zatvaranja tržišta.

Za pristup Alpaca tržištu, koristi se API ključ i tajna koju program učitava iz `.env` datoteke. Sve transakcije su na papirnatom tržištu, što znači da nema stvarnog trgovanja dionicama.

Program kontinuirano radi, provjeravajući svaku dionicu svake minute i donosi odluke o kupnji ili prodaji na temelju izračunatog RSI-a i stop-loss pravila.
