"""
Group Management Routes
CRUD operations for academic groups
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from backend.database import get_db
from backend.models.group import Group
from backend.models.user import User
from backend.schemas.group import GroupCreate, GroupUpdate, GroupResponse
from backend.dependencies import require_teacher, get_current_user

router = APIRouter()


@router.get("/", response_model=List[GroupResponse])
async def list_groups(
    skip: int = 0,
    limit: int = 100,
    year_level: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all groups with pagination and optional filtering by year level

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        year_level: Filter by year level (1-4)
        db: Database session
        current_user: Authenticated user

    Returns:
        List of groups with their students
    """
    query = db.query(Group).options(joinedload(Group.students))

    if year_level is not None:
        if year_level < 1 or year_level > 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Year level must be between 1 and 4"
            )
        query = query.filter(Group.year_level == year_level)

    groups = query.offset(skip).limit(limit).all()
    return groups


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get group by ID

    Args:
        group_id: Group database ID
        db: Database session
        current_user: Authenticated user

    Returns:
        Group information with its students
    """
    group = db.query(Group).options(joinedload(Group.students)).filter(Group.id == group_id).first()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with ID {group_id} not found"
        )

    return group


@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Create a new group (Teacher or Admin)

    Args:
        group_data: Group creation data
        db: Database session
        current_user: Authenticated teacher/admin

    Returns:
        Created group information
    """
    # Validate year level
    if group_data.year_level < 1 or group_data.year_level > 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Year level must be between 1 and 4"
        )

    # Create new group
    new_group = Group(
        name=group_data.name,
        year_level=group_data.year_level
    )

    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    # Load the group with students for the response
    created_group = db.query(Group).options(joinedload(Group.students)).filter(Group.id == new_group.id).first()

    return created_group


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: int,
    group_data: GroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Update group information (Teacher or Admin)

    Args:
        group_id: Group database ID
        group_data: Updated group data
        db: Database session
        current_user: Authenticated teacher/admin

    Returns:
        Updated group information
    """
    group = db.query(Group).filter(Group.id == group_id).first()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with ID {group_id} not found"
        )

    # Update fields if provided
    update_data = group_data.model_dump(exclude_unset=True)

    # Validate year level if provided
    if 'year_level' in update_data and (update_data['year_level'] < 1 or update_data['year_level'] > 4):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Year level must be between 1 and 4"
        )

    for field, value in update_data.items():
        setattr(group, field, value)

    db.commit()
    db.refresh(group)

    # Load the updated group with students for the response
    updated_group = db.query(Group).options(joinedload(Group.students)).filter(Group.id == group.id).first()

    return updated_group


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Delete a group (Teacher or Admin)

    Args:
        group_id: Group database ID
        db: Database session
        current_user: Authenticated teacher/admin

    Returns:
        No content
    """
    group = db.query(Group).filter(Group.id == group_id).first()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with ID {group_id} not found"
        )

    # Check if group has students
    if group.students:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete group that has students assigned to it"
        )

    db.delete(group)
    db.commit()

    return None
