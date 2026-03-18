# GK & CRYPTO MOONBOYS — WEBSITES TO SAVE
# Complete list of all URLs the agent crawls every 2 hours.
# These are the only sources used for official update detection.
# Grouped by category for the update-detector.py classifier.

---

## CATEGORY: gkdata-real
*Official GK, GraffPUNKS, and Crypto Moonboys websites.*

### Primary (Highest Priority — crawl first)
- https://graffpunks.substack.com/
- https://substack.com/@graffpunks/posts
- https://graffpunks.live/
- https://gkniftyheads.com/
- https://graffitikings.co.uk/

### Social & Media
- https://www.youtube.com/@GKniftyHEADS
- https://www.youtube.com/@A.IChunks
- https://www.facebook.com/GraffPUNKS.Network/
- https://medium.com/@GKniftyHEADS
- https://medium.com/@games4punks
- https://medium.com/@HODLWARRIORS
- https://medium.com/@graffpunksuk
- https://medium.com/@GRAFFITIKINGS
- https://x.com/GraffPunks
- https://x.com/GKNiFTYHEADS
- https://x.com/GraffitiKings

### NFT Platforms
- https://neftyblocks.com/collection/gkstonedboys
- https://neftyblocks.com/collection/noballgamess
- https://nfthive.io/collection/noballgamess
- https://dappradar.com/nft-collection/crypto-moonboys
- https://wax.atomichub.io/market/sale/wax-mainnet/THE-CRYPTO-MOONBOYS-40_144940240

### Collaborators & Extended Canon
- https://medium.com/@iamcharliebuster
- https://medium.com/@treefproject
- https://substack.com/@treefproject/posts
- https://substack.com/@noballgames/posts
- https://www.instagram.com/iamcharliebuster/
- https://x.com/nftbuster
- https://medium.com/@boneidolink
- https://deliciousagainpeter.com/
- https://www.instagram.com/delicious_again_peter/
- https://www.instagram.com/boneidolink/
- https://www.facebook.com/boneidolink/
- https://www.facebook.com/people/AI-Chunks/61587528591225/
- https://www.reddit.com/user/graffpunks/

---

## CATEGORY: news-real
*Crypto market news, political news, and general breaking news.*

- https://www.coindesk.com/
- https://cointelegraph.com/
- https://beincrypto.com/
- https://decrypt.co/
- https://theblock.co/
- https://bitcoinmagazine.com/
- https://cryptoslate.com/
- https://blockworks.co/

---

## CATEGORY: graffiti-news-real
*Street art news, graffiti contests, and urban art events.*

- https://streetartnews.net/
- https://www.graffitistreet.com/news/
- https://www.graffitiartmagazine.com/
- https://arrestedmotion.com/

---

## CATEGORY: fishing-real
*UK carp fishing forums and news — agent looks for catches >40lb in 70 hours.*

- https://www.bigcarp.co.uk/
- https://www.carpology.net/
- https://www.totalcarp.co.uk/
- https://www.carpforum.co.uk/
- https://www.fishingmagic.com/
- https://www.angling-direct.co.uk/blogs/news

---

## CATEGORY: rave-real
*UK drum & bass nightclub listings and DJ events.*

- https://www.residentadvisor.net/events/uk/london/genre/drum-bass
- https://www.ticketmaster.co.uk/discover/concerts-music/drum-and-bass
- https://www.skiddle.com/whats-on/genre/drum-bass/

---

## CATEGORY: lady-ink-hint
*Any mention of Lady-INK, street art muse figures, female graffiti artists.*

*(Monitored via gkdata-real sources above — keyword matched.)*

---

## NOTES FOR update-detector.py

- Crawl all URLs in each category.
- Compare page content hashes against `crawl-snapshot.json`.
- Any hash change triggers change detection for that URL.
- Classify detected change by the URL's category label above.
- For `fishing-real`: only flag if text contains keywords like "lb", "carp", "catch", "mirror", "common" near a weight value ≥40.
- For `news-real`: only flag crypto, political, or street art news published within the last 2 hours.
- For `gkdata-real`: flag any new post, image, NFT listing, or page text change.
- For `rave-real`: flag any new event or DJ booking in the next 30 days.
