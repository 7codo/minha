import requests
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
import urllib3

# Suppress only the single warning from urllib3 needed, if verify=False is used
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AnemSettings(BaseSettings):
    """Pydantic settings model for ANEM automation environment variables"""

    n1: str = Field(..., description="Wassit number", alias="N1")
    n2: str = Field(..., description="Piece Identite number", alias="N2")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def fetch_candidate_validation(n1: str, n2: str) -> dict:
    """
    Fetch candidate validation from ANEM API with given n1 (wassitNumber) and n2 (identityDocNumber).

    Args:
        n1 (str): Wassit number (n1).
        n2 (str): Piece Identite number (n2).

    Returns:
        dict: JSON response from the API.
    """
    url = "https://ac-controle.anem.dz/AllocationChomage/api/validateCandidate/query?wassitNumber=320600000120&identityDocNumber=100001144000120009"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9,ar;q=0.8",
        "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "referer": "https://minha.anem.dz/",
    }

    response = requests.get(
        url, headers=headers, verify=False
    )  # Disables SSL verification
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()


if __name__ == "__main__":
    # Simple main guard for interactive/manual testing
    settings = AnemSettings()  # Loads from .env or environment
    try:
        result = fetch_candidate_validation(settings.n1, settings.n2)
        print("Validation response:", result)
    except requests.exceptions.SSLError as ssl_err:
        print(
            "SSL verification failed. Try adding the server's certificate to your trusted store."
        )
        print("SSL Error details:", ssl_err)
    except Exception as e:
        print("Error during fetch:", e)
