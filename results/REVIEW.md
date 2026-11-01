# Do the model's answers make sense? A read of the first 40 items

Written by Claude (an AI model), not by a domain expert. It covers the first 40 items (1,200 comparisons). Nothing here changes the
scores; it is a check on whether the recorded answers are sensible.

## What was read

- **Closely, 10 items** (gold hypothesis, the negatives that beat it, and the model's visible reply and the start and end of its
  thinking for the comparisons it lost, plus a few it won; one thinking trace read in full):
  GWAI (Astronomy), soil carbon (Earth Science), payment-card fraud (Business), supernova detection (Astronomy), fairness of AI in
  healthcare (Law), fairness in recommender systems (Business), shallow-network approximation bounds (Math), AF-Cluster /
  AlphaFold2 (Biology), MICU super-resolution (Material Science), facial-expression GNN (Math). They were chosen to include items where
  gold lost in both orders, lost in one, won easily, and won barely.
- **By script, all 1,200 comparisons:** format, whether the thinking agrees with the final answer, position effects, wording.
- Not read: the full thinking of every call, and the other 30 items beyond the scripted checks.

## Findings

1. **The replies are coherent and consistent.** Every reply is in the requested format. Where the thinking states its final choice
   explicitly (1,009 of 1,200 calls), it matches the final answer in all 1,009; none contradicts it. The domain statements I could check
   were right (what MSA clustering does in AF-Cluster; that metric entropy and n-widths are the standard "fundamental measures" of
   approximation theory; why a federated-learning proposal answers a privacy question, not a bias one). I found no invented content in the
   items I read.
2. **Most losses are not nonsense; they follow from how the model judges.** In 92% of replies the reason given is specificity,
   concreteness or testability (96% of the replies that picked a negative, 89% of those that picked gold). When the gold hypothesis is a
   short, general sentence that restates the research question (GWAI, fraud detection, supernova detection, MICU, recommender-system
   fairness), the model calls it "essentially a restatement of the research question" and prefers a negative that adds a concrete
   mechanism. In the supernova and soil-carbon items the winning negatives are the gold's own idea with detail added, so preferring them is
   defensible.
3. **It wins when the negative drifts from the question.** When it picks gold the stated reason is usually scope: the negative
   answers a different question (privacy instead of bias; a Selective-Kernel block that is not an edge mechanism; a method that
   ignores the "research gaps" part of the question). So the standard it applies changes from pair to pair (specificity in one,
   alignment in another). Each argument is sound alone, but they are not one rule.
4. **It does not follow the prompt's own rule.** The prompt says "Additional detail, complexity, or breadth is neither an advantage
   nor a disadvantage by itself". The model quotes this in its thinking in 32% of calls. In the fraud item it quotes it, says "I should
   focus on the general direction, not on whether more detail is better", and then picks the detailed option because it "addresses the
   'how'". The ranking is therefore partly a measure of how detailed a hypothesis is.
5. **Position effect, mild.** When the two orders were swapped, the winner changed in 100 of 600 pairs (17%); in those, the second
   position won 60 times and the first 40. Gold was chosen more often as candidate 2 (gold-second accuracy 77.5% vs 62.5%).
6. **Gold phrased as a paper summary did worse.** In 8 items the gold starts "The paper hypothesizes / posits ..."; gold was chosen in
   52% of those comparisons vs 66% for the other 32 items. Eight items is too few to call this an effect.
7. **Known data property.** Gold is shorter than the negative in 98% of comparisons (median gold 46 words). The model picked the longer
   text only 38% of the time, so it is not simply preferring length; it prefers concrete mechanisms, and does pick gold 63% of the time.
8. **Bookkeeping quirk.** 7 of 1,200 calls report more reasoning tokens than completion tokens; token totals are the provider's
   figures and are approximate.

## Caveat on the first heuristic

A first, cruder script flagged 118 "mismatches" between the thinking and the answer. They were false alarms (it compared the last
candidate *mentioned*, which is often the one being criticised). The explicit-statement check above is the one to trust.
