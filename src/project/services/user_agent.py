from random_user_agent.params import SoftwareName, OperatingSystem
from random_user_agent.user_agent import UserAgent


class RandomUserAgent:
    def __init__(self) -> None:
        software_names = [SoftwareName.CHROME.value]
        operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]

        self.user_agent_rotator = UserAgent(
            software_names=software_names,
            operating_systems=operating_systems,
            limit=100,
        )

    def get(self) -> str:
        return self.user_agent_rotator.get_random_user_agent()