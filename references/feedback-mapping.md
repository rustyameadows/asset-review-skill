# Feedback Mapping

Read this reference after Codex/ChatGPT returns browser annotations to the agent. The static review page does not read annotations and has no feedback code.

## Interpretation order

1. Read the browser annotations returned by Codex/ChatGPT.
2. Use the page URL, visible label, semantic figure, and stable asset ID to resolve the target.
3. Classify the feedback.
4. Summarize the proposed actions before changing source work.
5. Edit the sources, rebuild the static view, and refresh the page.

## Classification

- `approval`: explicit acceptance of a fingerprinted asset version
- `rejection`: explicit instruction to stop or discard a direction
- `asset-specific revision`: a requested change scoped to one or more named assets
- `global revision`: a treatment or production change applying across a set
- `comparison preference`: selection of one version or direction over another
- `question`: a request for information that does not yet authorize an edit
- `project instruction`: a workflow, delivery, or scope instruction

## Mapping evidence

Prefer evidence in this order:

1. Focus or comparison page URL.
2. Stable figure ID or asset ID on the annotated element.
3. Unique visible label or filename inside the figure caption.
4. Comparison side plus the comparison's declared asset IDs.
5. Spatial proximity within a uniquely identified static figure.

Never rely only on card index, viewport coordinates, or an ambiguous filename.

## Scope rules

- Treat “this” on a focused asset as asset-specific unless the text states otherwise.
- Treat “all,” “the remaining sizes,” or “across the set” as a possible global revision and enumerate the affected IDs.
- Treat an annotation spanning multiple selected cards as multi-asset feedback.
- Do not infer approval from the absence of comments.
- Do not alter approved assets for a global request without naming that consequence in the action summary.
- Ask for clarification when two plausible mappings would lead to materially different edits.

## Action summary format

```text
Review received:
- Approve: social-square-v3, email-hero-v2
- Reject: display-banner-v1
- Revise: loosen the crop on story-v2
- Global: apply the square version's typography to the remaining social assets
- Question: confirm whether the retail screen requires legal copy
```

After summarizing, make or delegate authorized revisions, regenerate the static site, and refresh the open page. Create a separate round only when preserving the earlier presentation is useful.
