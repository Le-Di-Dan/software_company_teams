# Release Readiness — {{App name}} {{version}}

> Owner: release-manager · Gate G3 · Every row needs evidence. Any ❌ blocks the gate.

| Area | Item | Owner | Status | Evidence |
|---|---|---|---|---|
| Quality | All features passes=true, E2E green on iOS + Android | qa-engineer | | |
| Quality | Crash-free in TestFlight / closed test | qa-engineer | | |
| Security | Security clearance signed; no open Critical/High in state/security-findings.json | security-lead | | |
| Apple | `company/compliance/apple-app-store.md` audit: 0 blockers | store-compliance-officer | | |
| Google | `company/compliance/google-play.md` audit: 0 blockers | store-compliance-officer | | |
| Legal | Privacy policy + terms published at public URLs | privacy-legal-counsel / devops | | |
| Privacy | App Privacy labels + Data safety form drafted & matching code | store-compliance-officer | | |
| Listing | Name, subtitle, keywords, description, screenshots, preview | aso-marketing-specialist | | |
| Review | Demo account + review notes for Apple/Google reviewers | release-manager | | |
| Google | Closed test: ≥12 testers opted-in ≥14 consecutive days | release-manager + PO | | |
| Builds | Signed iOS archive (Xcode 26+ SDK), signed AAB (target API per current Play rule) | release-manager | | |
| Ops | Crash reporting, analytics, backend monitoring live | devops-engineer | | |

## PO checklist (only the PO can do these)
- [ ] Apple Developer Program (individual) active, agreements/tax/banking signed if monetized
- [ ] Google Play Console (personal) verified; closed-test testers recruited
- [ ] Reviewed this document; run `! bash scripts/approve-release.sh`; submit in App Store Connect / Play Console
