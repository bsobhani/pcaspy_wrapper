This package makes pcaspy IOCs host PVs in PV Access (or more specifically PVXS, via p4p).

To use, simply replace lines like `import pcaspy` with `import pcaspy_wrapper`, and replace lines like `from pcaspy import ...` with `from pcaspy_wrapper import ...`

In many cases this will simply "just work". In some cases however, some modification (usually small) will be needed due to some small differences in features of Channel Access and PV Access.

Notably, PV Access does not have read callbacks, so if a pcaspy IOC makes use of read callbacks, updates should be triggered in some other way. For example, if a read callback is used to trigger an update for a PV, then to make it work for PV Access it is often sufficient to simply give that PV a scan field.
