# QIRA Task Packet

A QIRA task packet records the local review request:

- task id, title, and goal
- owner-consent metadata
- input source
- intended change type
- allowed review scope
- forbidden actions
- claim ceiling

The task packet keeps review scope local and offline. It marks GitHub API calls, external repository mutation, merge, and deploy actions as unavailable for ROE-9.
