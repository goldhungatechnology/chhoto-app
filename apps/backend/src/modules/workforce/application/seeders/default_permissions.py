ORGANIZATION_PERMISSIONS = [
    {
        "name": "View Organization details",
        "key": "organization.view",
        "description": "Permission to view organization details",
        "category": "organization",
        "is_system_permission": True,
    },
    {
        "name": "Edit Organization details",
        "key": "organization.edit",
        "description": "Permission to edit organization details",
        "category": "organization",
        "is_system_permission": True,
    },
    {
        "name": "Delete Organization",
        "key": "organization.delete",
        "description": "Permission to delete the organization",
        "category": "organization",
        "is_system_permission": True,
    },
]

DEFAULT_PERMISSIONS = [
    *ORGANIZATION_PERMISSIONS,
]
