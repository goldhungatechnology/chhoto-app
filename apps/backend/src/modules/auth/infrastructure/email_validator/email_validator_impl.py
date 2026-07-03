from src.modules.auth.domain.interfaces.email_validator_interface import (
    IEmailDomainValidator,
)


class EmailDomainValidatorImpl(IEmailDomainValidator):
    """
    Implementation of the IEmailDomainValidator interface.
    This implementation checks if the email domain exists by performing a DNS lookup.
    """

    async def domain_exists(self, email: str) -> bool:
        """
        Check if the domain of the given email address exists.
        """
        import dns.exception
        import dns.resolver

        try:
            domain = email.split("@")[1]
            dns.resolver.resolve(domain, "MX")
            return True
        except (IndexError, dns.exception.DNSException):
            return False
