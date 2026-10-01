def get_resolution_suggestion(category: str) -> str:
    suggestions = {
        "Network": (
            "Check network connectivity, router status, VPN configuration, "
            "DNS settings, and recent network changes."
        ),
        "Database": (
            "Check database server health, connection settings, "
            "available storage, active connections, and recent database changes."
        ),
        "Application": (
            "Check application logs, service health, API dependencies, "
            "recent deployments, and application configuration."
        ),
        "Security": (
            "Review security alerts, authentication logs, affected accounts, "
            "and recent suspicious activity."
        ),
        "Hardware": (
            "Check device power, physical connections, hardware diagnostics, "
            "and recently installed hardware or drivers."
        ),
        "Access/Login": (
            "Verify user credentials, account status, permissions, "
            "authentication services, and password policies."
        )
    }

    return suggestions.get(
        category,
        "Investigate the ticket details and review relevant system logs."
    )