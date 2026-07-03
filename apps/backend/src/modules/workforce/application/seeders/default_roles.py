DEFAULT_ROLES = [
    {
        "name": "owner",
        "description": "Owner role with full access to all resources and permissions.",
        "is_system_role": True,
        ## organization_id will be set in the seeder based on the organization being seeded
    },
    {
        "name": "admin",
        "description": "Admin role with elevated permissions to manage resources and users.",
        "is_system_role": True,
        ## organization_id will be set in the seeder based on the organization being seeded
    },
    {
        "name": "member",
        "description": "Member role with limited access to resources and permissions.",
        "is_system_role": True,
        ## organization_id will be set in the seeder based on the organization being seeded
    },
    {
        "name": "team lead",
        "description": "Team Lead role with permissions to manage team resources and users.",
        "is_system_role": True,
        ## organization_id will be set in the seeder based on the organization being seeded
    },
    {
        "name": "supervisor",
        "description": "Supervisor role with permissions to oversee team activities and manage resources.",
        "is_system_role": True,
        ## organization_id will be set in the seeder based on the organization being seeded
    },
    {
        "name": "sales",
        "description": "Sales role with permissions to manage sales-related resources and activities.",
        "is_system_role": True,
        ## organization_id will be set in the seeder based on the organization being seeded
    },
]
