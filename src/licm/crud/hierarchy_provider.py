from sqlalchemy.orm import Session

from licm.model import hierarchy_provider as model
from licm.schema import hierarchy_provider as schema


def get_hierarchy_provider(session: Session, eid: str):
    return session.query(model.HierarchyProvider).filter(model.HierarchyProvider.eid == eid).first()


def create_hierarchy_provider(session: Session, hp: schema.HierarchyProvider):
    u = model.HierarchyProvider(eid=hp.eid, name=hp.name, description=hp.description)
    session.add(u)
    session.commit()
    session.refresh(u)
    return u
