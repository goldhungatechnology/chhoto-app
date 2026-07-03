from abc import ABC, abstractmethod


class IEmailDomainValidator(ABC):
    """
    Interface for validating email domains.
    """

    @abstractmethod
    async def domain_exists(self, email: str) -> bool:
        """
        Check if the domain of the given email address exists.
        """
