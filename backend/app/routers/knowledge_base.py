"""Read-only endpoint(s) describing what roles/knowledge is available."""
from fastapi import APIRouter

from app.services.rag.ingestion import list_available_roles, load_role_documents
from app.schemas import RoleInfo

router = APIRouter(prefix="/api/roles", tags=["roles"])

ROLE_LABELS = {
    "aiml_engineer": "AI/ML Engineer",
    "backend_engineer": "Backend Engineer",
    "data_science": "Data Scientist",
    "frontend_engineer": "Frontend Engineer",
}


@router.get("", response_model=list[RoleInfo])
def get_roles():
    roles = list_available_roles()
    out = []
    for role in roles:
        docs = load_role_documents(role)
        out.append(
            RoleInfo(
                role_id=role,
                label=ROLE_LABELS.get(role, role.replace("_", " ").title()),
                document_count=len({c.source for c in docs}),
            )
        )
    return out
