# HealthTracker MVP requirements (HA-14)

## Goal
Deliver a usable v1.0 health-tracking MVP with a clear dashboard, persistent health records, backend services, QA, and a release-ready submission.

## In-scope v1.0 user journeys
1. A user can view the dashboard and clearly labelled health metrics.
2. A user can create and retrieve a health record.
3. Invalid or incomplete record data is rejected with an understandable error.
4. The app displays loading, empty, and failure states when data is unavailable.
5. QA verifies core journeys and release-blocking issues are resolved before submission.

## Non-functional expectations
- Validate all user-provided input.
- Use parameterized SQL for database writes/queries.
- Avoid placing real personal health information in sample/demo data.
- Keep API errors understandable without leaking internal details.
- Record test outcomes and defects in Jira.

## Acceptance criteria
- MVP scope and user journeys are reviewed by the Product Owner.
- All nine MVP stories have acceptance criteria.
- Dependencies and release constraints are recorded.
- Optional wellness notifications are explicitly excluded from v1.0 and deferred to v1.1 (HA-23).

## Dependencies
Requirements → UI/UX → Frontend → API Integration → Testing → Bug Fixes → App Store Submission. Backend and Database Setup both feed API Integration.

## Release trade-off
To target v1.0 one sprint earlier, use a temporary contractor for the compressed integration sprint and defer 5-SP wellness notifications to v1.1. This adds onboarding/cost risk but preserves QA and a dedicated hardening sprint.
