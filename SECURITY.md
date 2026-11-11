# Security boundary

This public repository has no access to the Elora application database, credentials or login system. Its network tool only reads the anonymous public catalogue. It does not send authentication cookies or tokens.

Do not submit credentials, private customer records or security exploit details to a public issue. Report a suspected vulnerability privately to the repository owner through GitHub private vulnerability reporting.

Public releases are assembled from an explicit file manifest into a fresh directory, without private repository Git history. Schema checks and a credential-pattern scan are additional checks, not a substitute for reviewing the exact release contents.
