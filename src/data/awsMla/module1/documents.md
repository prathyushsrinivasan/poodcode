## Retrieval data and training data have different jobs

A policy assistant needs to answer “Can I return an opened item?” using the current policy. Retrieval augmented generation (RAG) retrieves relevant evidence and places it in the generation context. The document remains an external source that can be updated. Supervised fine-tuning instead changes model parameters using examples of desired behavior. It can teach a response pattern but is not a reliable substitute for retrieving frequently changing policy facts.

Start with extraction. A PDF can contain selectable text, scanned images, headings, tables and footnotes. OCR may be needed for scans. Preserve relationships: flattening a table can separate a fee from its product category. Store the original source and a structured extracted representation so errors can be traced and corrected. Keep domain terms such as `ZX-41`, units, negation and section headings. Aggressive normalization that removes hyphens or the word “not” can destroy the very information retrieval needs.

A tokenizer divides input into model-specific units, often subword pieces. Tokens are neither always words nor a fixed number of characters. Chunk and context budgets must use the relevant model's tokenization. Text, images and audio require compatible extraction and embedding paths; text chunk settings do not automatically describe how a multimodal model handles images or video.

## Work through chunk boundaries and overlap

Consider this short policy:

```text
Returns
Unopened items may be returned within 30 days.
Opened items are accepted only if defective.
Proof of purchase is required for every return.

Shipping
Express delivery costs $12.
```

A cut immediately before “only if defective” can separate the exception from the rule. A chunk containing the whole manual can include the answer but mix it with unrelated shipping and warranty material. Good chunks are small enough to retrieve precisely and large enough to preserve a complete claim with its qualifiers. Section-aware chunking keeps the return rule and its exception together. Some overlap can retain context across boundaries, but it adds repeated content and storage and can fill the top retrieved results with near-duplicates.

For a toy fixed-size strategy of 100 tokens with 20-token overlap, the second chunk starts at token 81 if the first covers tokens 1–100. The stride is `100 - 20 = 80`, not 100. Actual parsers can respect sentence or section boundaries, so their output may differ. Fixed-size, semantic and hierarchical strategies make different tradeoffs; there is no universal best chunk size.

Test with representative questions and known supporting sections. For “Can I return an opened item?”, check whether the retrieved evidence includes the defective-item condition and proof requirement. Keep the embedding model, corpus and test questions fixed while comparing chunk strategies. If retrieval finds the correct section but the answer ignores its exception, the failure is in grounding or generation rather than missing retrieval.

## Embeddings, metadata and access boundaries

An embedding maps content into a numeric representation useful for similarity. Generate document and query vectors through compatible model paths. A model replacement generally requires rebuilding the corresponding document vectors and index configuration. Reusing an old index merely because the new vectors have the same dimension does not establish compatibility. Track model ID, version, preprocessing and distance metric.

Each chunk also needs metadata. A small conceptual record might look like this; it is not a Bedrock import schema:

```json
{
  "document_id": "returns-policy",
  "version": "2026-10",
  "section": "opened-items",
  "source_uri": "s3://example-policies/returns.pdf",
  "tenant_id": "retailer-a",
  "allowed_group": "support",
  "effective_from": "2026-10-01"
}
```

Use metadata to retrieve the correct tenant, document version and authorized content. Derive filters from a trusted identity and enforce them in the application and retrieval path. A client-provided tenant field is not authorization, and a prompt asking the model to ignore confidential chunks is too late if those chunks were already retrieved. Update and deletion workflows must remove stale indexed chunks as well as the original document.

Redact unnecessary personally identifiable information before embedding or downstream processing, while preserving task-relevant meaning. Replacing an email with a consistent placeholder can preserve that two mentions refer to the same person. Hashing a known email is not guaranteed anonymization: predictable values can be guessed and linked. Protect any reversible mapping and apply access and retention rules to embeddings, logs and evaluation sets too.

## Prepare customization examples and evaluate honestly

Supervised customization uses input/output examples that demonstrate the intended task. Continued pretraining uses domain material to adapt language representations. Distillation uses a teacher's behavior or outputs to train a student. These are distinct data-generation objectives, and supported formats depend on the chosen model and customization method. Validate the current Bedrock model-specific schema before uploading.

A conceptual instruction pair could ask for a JSON return decision and provide a correct JSON response. Valid JSON is only the first gate: the answer must follow the input, match policy, avoid unnecessary personal data and obey the output contract. A teacher's fluent answer can still be factually wrong, so distillation requires quality filtering rather than blind copying.

Separate training and evaluation by source and near-duplicate content before tuning prompts or customization. Putting paraphrases of the same policy question in both can overstate generalization. Keep a held-out set with ordinary requests, exceptions, unanswerable questions and access-boundary cases. For this assistant, first establish clean extraction, tested chunks, consistent embeddings and controlled retrieval. Add customization when a measured behavioral problem justifies it.
