# Historical XSL provenance

Investigation date: 2026-11-09. The file was `mathml2docx/MML2OMML.XSL` in older revisions.

- Introduced by commit `0c85e595475bc181be8512dbf398dc02d0e13511` on 2024-01-23.
- Neither the file nor commit records a download URL, copyright owner, or redistribution grant.
- Size: 155,527 bytes.
- SHA-256: `5558e69d8bd6534927c4176bd5d5032d0d4bdc17bdaab7de580ca41e996a609b`.
- At investigation time, it was byte-for-byte identical to [AbiWord's copy](https://github.com/AbiWord/abiword/blob/master/plugins/openxml/omml_xslt/mml2omml.xsl).

That match demonstrates the existence of another public copy. It does not identify
the site used by this project's author, the original author, or permission to
redistribute it. This repository's MIT notice does not establish rights to a
third-party file. [Microsoft's general redistribution policy](https://www.microsoft.com/en-us/legal/intellectualproperty/copyright/permissions)
requires permission in applicable terms, but that general policy alone does not
establish this particular file's license or determine whether an infringement occurred.

Version 1.0.0 removes the file and loading code. `mathml2docx/math.py` constructs
OMML directly; the old stylesheet code and templates were not translated or copied.
Optional [latex2mathml](https://github.com/roniemartinez/latex2mathml) is installed
separately under its own MIT license rather than vendored into this package.

These changes do not alter Git history or previously distributed 0.x packages.
Historical distribution rights and the treatment of those copies remain separate work.

See [licensing scope](10-licensing.md) for project/dependency notices and functional
limits. Distribution checks enforce XSL exclusion and the presence of LICENSE and
third-party notices, independently of the historical investigation.
