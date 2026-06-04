# Repository Deployment Matrix

Use this file before every release. Do not infer a destination from the current working directory.

| Component | Local directory | GitHub destination | Production destination | Rule |
| --- | --- | --- | --- | --- |
| Marketing site | `marketing-site/` | `buykori-marketing-site` | `buykori.app` via Vercel | Push only marketing files. |
| Client portal | `client-portal/` | `buykori-client-portal` | `client.buykori.app` via Vercel | Run `npm run lint` and `npm run build` first. |
| Admin portal | `admin-portal/` | `buykori-admin-portal` | `admin.buykori.app` via Vercel | Push only when admin UI changed. |
| Backend API | workspace root: `app/`, `migrations/`, `tests/` | None in the approved flow | `api.buykori.app` server | Do not push backend code to GitHub. Direct server deploy needs explicit approval. |

## Preflight

Run the read-only report before any release:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\ops\deploy_preflight.ps1 -Target all
```

Use a specific target when releasing one component:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\ops\deploy_preflight.ps1 -Target marketing
powershell -ExecutionPolicy Bypass -File scripts\ops\deploy_preflight.ps1 -Target client
powershell -ExecutionPolicy Bypass -File scripts\ops\deploy_preflight.ps1 -Target admin
powershell -ExecutionPolicy Bypass -File scripts\ops\deploy_preflight.ps1 -Target backend
```

`-Target backend` intentionally prints a GitHub-push warning. It does not deploy anything.

## Backend Release Checklist

1. Review `git diff -- app migrations tests`.
2. Run `pytest -q`.
3. Run `git diff --check`.
4. Run `alembic heads`.
5. Confirm the migration order.
6. Ask for explicit approval before a direct production server deploy.
7. Preview local-only uploads with `python deploy\changed_deploy.py --base origin/main --working-tree --dry-run`.
8. Deploy with `python deploy\changed_deploy.py --base origin/main --working-tree`.
9. After deploy, verify `/status`, migrations, Supervisor services, and one tracking smoke event.

## Frontend Release Checklist

1. Enter the exact frontend repo directory.
2. Run `git status -sb`.
3. Review `git diff`.
4. For the client portal, run `npm run lint` and `npm run build`.
5. Push only the intended frontend repository.
6. Verify the production domain after the Vercel deployment finishes.
