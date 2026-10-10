# Social, news and fundamental intelligence ingestion

## Principle

**X is a first-class market information source, not the only source.** Truth Social, official agencies, central banks, institutional commentary and licensed market news are also essential. Capture important market-moving statements and identify affected forex, XAUUSD and crypto instruments. Social content can arrive first, but a popular post is not automatically a verified event.

## Supported source classes

- X: important official accounts, economists, financial journalists, researchers and approved market observers.
- Truth Social: market-moving statements and political/trade-policy developments.
- Institutional research: ING Economics and other research publishers to the extent permitted by contract/terms.
- Primary publishers: Fed, ECB, BoJ, BLS, US Treasury, national statistics agencies, regulators and central banks.
- Licensed market news and economic-calendar feeds.
- Crypto primary sources: exchanges, ETF issuers, project teams, regulators and permitted market-data feeds.

Use official APIs, licensed datasets and terms-compliant access. Avoid relying on brittle prohibited scraping or storing copyrighted text without permission.

## Pipeline

~~~text
observe item → timestamp & source identity → store permitted payload
→ extract people/entities/topics/events → verify source and claim type
→ deduplicate/attach to canonical event → map affected instruments
→ assign relevance, severity and novelty → explain transmission channels
→ observe market reaction → show concise card / alert when justified
→ archive original link, derivation, correction and outcome
~~~

## Trust and filtering

Rank based on source trust, novelty, market relevance, time sensitivity, asset exposure, event significance, corroboration and observed price/volatility response. Mark **unverified**, **reported**, **officially confirmed**, **analysis/opinion**, **corrected** and **retracted** states separately.

A single policy announcement covered by X, Truth Social, major news providers and financial economists should create **one canonical event** with linked evidence rather than a duplicate card for every article. Corroboration improves verification, not independent model sample count.

## Example UX (fictional)

Collapsed:

> High impact | US trade-policy statement | USD, USDCAD, EURUSD, XAUUSD | Source: Official account | Updated 14:32 UTC

Expanded:

> What was said? Why might traders care? Which transmission pathways could strengthen or weaken each currency? What changed in market prices? Which additional reliable sources confirm the claim?

Full view:

> Timestamped source timeline, original links, relevant macro and market snapshots, historical analogues, trade ideas and corrections.

## Risks and edge cases

Spoofed accounts, edited/deleted posts, malicious screenshots, engagement manipulation, translated statements, multiple languages, late publishing, unsupported provider outages, economic release corrections, forex market closures and crypto weekend trading must be handled explicitly.

**The historical database stores items that were not prominent enough for the live dashboard, subject to rights and retention rules.** Visibility thresholds and storage eligibility are separate decisions.
