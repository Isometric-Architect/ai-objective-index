# DataCapsule CI Bridge Limitations

The DataCapsule CI bridge is a convenience wrapper for repository owners who already maintain local corpus manifests. It should be enabled deliberately by copying or adapting the example workflow.

It does not:

- create an active workflow automatically;
- call GitHub APIs;
- post comments;
- upload to package registries;
- fetch URLs;
- crawl directories;
- inspect private file contents;
- handle tokens;
- prove legal sufficiency;
- prove privacy compliance;
- guarantee data quality;
- prove evaluation cleanliness;
- authorize actions.

The bridge should be treated as local metadata packaging. Teams still need separate review for rights, privacy, data quality, benchmark contamination, release readiness, and any external action.
